import argparse
import json
import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from pypdf import PdfReader


PROJECT_DIR = Path(__file__).parent
DATA_DIR = PROJECT_DIR / "data"
INDEX_PATH = PROJECT_DIR / "vector_store.json"


def load_documents(data_dir: Path) -> list[dict]:
    documents = []
    for path in sorted(data_dir.glob("*.txt")) + sorted(data_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8").strip()
        if text:
            documents.append({"source": path.name, "text": text})
    for path in sorted(data_dir.glob("*.pdf")):
        reader = PdfReader(path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        if text:
            documents.append({"source": path.name, "text": text})
    return documents


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = max(end - overlap, start + 1)
    return chunks


def embed_texts(client: OpenAI, texts: list[str], model: str) -> list[list[float]]:
    response = client.embeddings.create(model=model, input=texts)
    return [item.embedding for item in response.data]


def build_index(client: OpenAI, embedding_model: str) -> list[dict]:
    documents = load_documents(DATA_DIR)
    if not documents:
        raise SystemExit("No .txt or .md files found in the data folder.")

    records = []
    for document in documents:
        for i, chunk in enumerate(chunk_text(document["text"])):
            records.append(
                {
                    "id": f"{document['source']}:{i + 1}",
                    "source": document["source"],
                    "chunk": chunk,
                }
            )

    embeddings = embed_texts(client, [record["chunk"] for record in records], embedding_model)
    for record, embedding in zip(records, embeddings):
        record["embedding"] = embedding

    INDEX_PATH.write_text(json.dumps(records, indent=2), encoding="utf-8")
    return records


def load_index() -> list[dict]:
    if not INDEX_PATH.exists():
        raise SystemExit("Vector store not found. Run `python app.py index` first.")
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def cosine_similarity(a: list[float], b: list[float]) -> float:
    va = np.array(a)
    vb = np.array(b)
    return float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb)))


def retrieve(client: OpenAI, question: str, records: list[dict], embedding_model: str, top_k: int) -> list[dict]:
    query_embedding = embed_texts(client, [question], embedding_model)[0]
    scored = [
        {**record, "score": cosine_similarity(query_embedding, record["embedding"])}
        for record in records
    ]
    return sorted(scored, key=lambda record: record["score"], reverse=True)[:top_k]


def format_context_block(contexts: list[dict]) -> str:
    return "\n\n".join(
        f"[{item['id']} | score: {item.get('score', 0):.3f}]\n{item['chunk']}"
        for item in contexts
    )


def answer_question(client: OpenAI, question: str, contexts: list[dict], chat_model: str) -> str:
    context_block = format_context_block(contexts)
    prompt = f"""
Answer the question using only the context below.
If the context does not contain the answer, say you do not know.
Cite sources with the chunk id in square brackets.

Context:
{context_block}

Question: {question}
"""
    response = client.responses.create(
        model=chat_model,
        input=prompt.strip(),
    )
    return response.output_text


def main() -> None:
    load_dotenv()
    embedding_model = os.getenv("RAG_EMBEDDING_MODEL", "text-embedding-3-small")
    chat_model = os.getenv("RAG_CHAT_MODEL", "gpt-4.1-mini")

    parser = argparse.ArgumentParser(description="Small OpenAI-powered RAG demo.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("index", help="Embed files from ./data and save vector_store.json")

    ask_parser = subparsers.add_parser("ask", help="Ask a question against the indexed files")
    ask_parser.add_argument("question", help="Question to answer")
    ask_parser.add_argument("--top-k", type=int, default=3, help="Number of chunks to retrieve")

    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is missing. Copy .env.example to .env and add your API key.")

    try:
        client = OpenAI()
    except OpenAIError as error:
        raise SystemExit(f"Could not initialize OpenAI client: {error}") from error

    if args.command == "index":
        records = build_index(client, embedding_model)
        print(f"Indexed {len(records)} chunks from {DATA_DIR}.")
        return

    records = load_index()
    contexts = retrieve(client, args.question, records, embedding_model, args.top_k)
    print(answer_question(client, args.question, contexts, chat_model))


if __name__ == "__main__":
    main()
