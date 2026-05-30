# Small RAG Gen AI Project

This is a recruiter-friendly Retrieval-Augmented Generation project in Python.
It reads `.txt`, `.md`, and `.pdf` files from `data/`, embeds them with OpenAI,
retrieves the most relevant chunks for a question, and generates grounded answers
with source citations.

It includes both:

- A command-line app for simple demos.
- A Streamlit web app with uploads, retrieval scores, and cited evidence.

## Files

- `app.py` - command-line RAG app.
- `streamlit_app.py` - interactive web UI.
- `data/` - put your knowledge base files here.
- `vector_store.json` - generated after indexing.
- `.env.example` - environment variable template.
- `requirements.txt` - Python dependencies.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and set your `OPENAI_API_KEY`.

## Run

Index the sample document:

```powershell
python app.py index
```

Ask a question:

```powershell
python app.py ask "What does Acme Learning do?"
```

Try another:

```powershell
python app.py ask "What support do enterprise customers receive?"
```

## Run the Web Demo

```powershell
streamlit run streamlit_app.py
```

The web app lets you:

- Upload `.md`, `.txt`, and `.pdf` files.
- Rebuild the vector index.
- Ask questions over the indexed documents.
- Inspect retrieved chunks and similarity scores.
- See citations in the generated answer.

## How It Works

1. Loads Markdown, text, and PDF files from `data/`.
2. Splits documents into overlapping chunks.
3. Creates embeddings for each chunk.
4. Saves a simple JSON vector store.
5. Embeds the user question.
6. Retrieves the most similar chunks with cosine similarity.
7. Sends the retrieved context to a chat model to generate a grounded answer.

## Architecture

```mermaid
flowchart LR
    A["Documents: md, txt, pdf"] --> B["Chunking"]
    B --> C["OpenAI Embeddings"]
    C --> D["JSON Vector Store"]
    E["User Question"] --> F["Query Embedding"]
    F --> G["Cosine Similarity Retrieval"]
    D --> G
    G --> H["Context + Question"]
    H --> I["OpenAI Chat Model"]
    I --> J["Grounded Answer with Citations"]
```

## Recruiter Talking Points

- Built a complete RAG pipeline from document ingestion to answer generation.
- Added transparent retrieval with source citations and similarity scores.
- Supports multiple document formats, including PDFs.
- Provides both CLI and web UI experiences.
- Keeps secrets out of Git with `.env` and `.gitignore`.
- Uses a simple JSON vector store to keep the project easy to understand.

## Notes

- Add your own `.md`, `.txt`, or `.pdf` files to `data/`, then rerun
  `python app.py index` or use the web app's Rebuild Index button.
- Change models in `.env` with `RAG_EMBEDDING_MODEL` and `RAG_CHAT_MODEL`.
- This is intentionally small and readable. For production, use a real vector
  database, add tests, handle larger files, and store metadata more carefully.
