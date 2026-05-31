import json
import math
from collections import Counter

import numpy as np
from openai import OpenAI

from .config import CHROMA_PATH, EMBEDDING_MODEL, FAISS_PATH, RECORDS_PATH


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in text.replace("\n", " ").split() if token.strip()]


class HybridRetriever:
    def __init__(self, client: OpenAI, embedding_model: str = EMBEDDING_MODEL):
        self.client = client
        self.embedding_model = embedding_model
        self.records: list[dict] = []

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=self.embedding_model, input=texts)
        return [item.embedding for item in response.data]

    def save(self) -> None:
        RECORDS_PATH.write_text(json.dumps(self.records, indent=2), encoding="utf-8")

    def load(self) -> None:
        if RECORDS_PATH.exists():
            self.records = json.loads(RECORDS_PATH.read_text(encoding="utf-8"))

    def index(self, chunks: list[dict]) -> None:
        if not chunks:
            self.records = []
            self.save()
            return
        embeddings = self.embed([chunk["text"] for chunk in chunks])
        self.records = [
            {**chunk, "embedding": embedding}
            for chunk, embedding in zip(chunks, embeddings)
        ]
        self.save()
        self._index_faiss()
        self._index_chroma()

    def _index_faiss(self) -> None:
        try:
            import faiss
        except ImportError:
            return
        matrix = np.array([record["embedding"] for record in self.records], dtype="float32")
        faiss.normalize_L2(matrix)
        index = faiss.IndexFlatIP(matrix.shape[1])
        index.add(matrix)
        faiss.write_index(index, FAISS_PATH)

    def _index_chroma(self) -> None:
        try:
            import chromadb
        except ImportError:
            return
        chroma = chromadb.PersistentClient(path=CHROMA_PATH)
        try:
            chroma.delete_collection("enterprise_knowledge")
        except Exception:
            pass
        collection = chroma.create_collection("enterprise_knowledge")
        collection.add(
            ids=[record["id"] for record in self.records],
            documents=[record["text"] for record in self.records],
            embeddings=[record["embedding"] for record in self.records],
            metadatas=[{"source": record["source"]} for record in self.records],
        )

    def bm25_scores(self, query: str) -> dict[str, float]:
        query_terms = tokenize(query)
        documents = [tokenize(record["text"]) for record in self.records]
        doc_count = max(len(documents), 1)
        avg_len = sum(len(document) for document in documents) / doc_count
        document_frequency = Counter(term for document in documents for term in set(document))
        scores = {}
        for record, document in zip(self.records, documents):
            term_counts = Counter(document)
            score = 0.0
            for term in query_terms:
                if term not in term_counts:
                    continue
                idf = math.log(1 + (doc_count - document_frequency[term] + 0.5) / (document_frequency[term] + 0.5))
                tf = term_counts[term]
                denom = tf + 1.5 * (1 - 0.75 + 0.75 * len(document) / max(avg_len, 1))
                score += idf * ((tf * 2.5) / denom)
            scores[record["id"]] = score
        return scores

    def vector_scores(self, query: str) -> dict[str, float]:
        if not self.records:
            return {}
        query_embedding = np.array(self.embed([query])[0])
        scores = {}
        for record in self.records:
            embedding = np.array(record["embedding"])
            score = float(np.dot(query_embedding, embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(embedding)))
            scores[record["id"]] = score
        return scores

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        self.load()
        bm25 = self.bm25_scores(query)
        vector = self.vector_scores(query)
        candidates = []
        max_bm25 = max(bm25.values(), default=1) or 1
        for record in self.records:
            bm25_score = bm25.get(record["id"], 0) / max_bm25
            vector_score = vector.get(record["id"], 0)
            score = 0.45 * bm25_score + 0.55 * vector_score
            candidates.append(
                {
                    **record,
                    "bm25_score": bm25_score,
                    "vector_score": vector_score,
                    "score": score,
                }
            )
        return self.rerank(query, sorted(candidates, key=lambda item: item["score"], reverse=True)[: top_k * 3])[:top_k]

    def rerank(self, query: str, candidates: list[dict]) -> list[dict]:
        query_terms = set(tokenize(query))
        for candidate in candidates:
            overlap = len(query_terms.intersection(tokenize(candidate["text"])))
            candidate["score"] = candidate["score"] + min(overlap * 0.03, 0.18)
        return sorted(candidates, key=lambda item: item["score"], reverse=True)
