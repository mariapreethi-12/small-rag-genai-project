import json

from fastapi import Depends, FastAPI, Header, HTTPException
from openai import OpenAI

from .agents import MultiAgentKnowledgeAssistant
from .config import API_KEY, EMBEDDING_MODEL
from .ingestion import build_chunks, load_github_documents, load_local_documents, load_web_documents
from .memory import analytics_summary, record_event
from .retrieval import HybridRetriever
from .schemas import AskRequest, AskResponse, EvalRequest, EvalResponse, EvalResult, IngestRequest, IngestResponse, Source


app = FastAPI(
    title="Enterprise Multi-Agent Knowledge Assistant",
    description="FastAPI service for multi-agent RAG with hybrid retrieval, citations, memory, analytics, and evaluation.",
    version="1.0.0",
)


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key header.")


def client() -> OpenAI:
    return OpenAI()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "enterprise-rag-assistant"}


@app.post("/ingest", response_model=IngestResponse, dependencies=[Depends(require_api_key)])
def ingest(payload: IngestRequest, openai_client: OpenAI = Depends(client)) -> IngestResponse:
    documents = []
    documents.extend(load_local_documents(payload.paths))
    documents.extend(load_web_documents(payload.urls))
    documents.extend(load_github_documents(payload.github_repos))
    chunks = build_chunks(documents)
    retriever = HybridRetriever(openai_client, EMBEDDING_MODEL)
    retriever.index(chunks)
    record_event("ingest", json.dumps({"documents": len(documents), "chunks": len(chunks)}))
    return IngestResponse(
        documents=len(documents),
        chunks=len(chunks),
        sources=sorted({document["source"] for document in documents}),
    )


@app.post("/ask", response_model=AskResponse, dependencies=[Depends(require_api_key)])
def ask(payload: AskRequest, openai_client: OpenAI = Depends(client)) -> AskResponse:
    retriever = HybridRetriever(openai_client, EMBEDDING_MODEL)
    assistant = MultiAgentKnowledgeAssistant(openai_client, retriever)
    result = assistant.answer(payload.question, payload.conversation_id, payload.top_k)
    record_event("ask", json.dumps({"conversation_id": payload.conversation_id, "top_k": payload.top_k}))
    return AskResponse(
        answer=result["answer"],
        conversation_id=payload.conversation_id,
        agent_trace=result["trace"],
        sources=[
            Source(
                id=source["id"],
                source=source["source"],
                score=source["score"],
                bm25_score=source["bm25_score"],
                vector_score=source["vector_score"],
                text=source["text"],
            )
            for source in result["sources"]
        ],
    )


@app.post("/evaluate", response_model=EvalResponse, dependencies=[Depends(require_api_key)])
def evaluate(payload: EvalRequest, openai_client: OpenAI = Depends(client)) -> EvalResponse:
    retriever = HybridRetriever(openai_client, EMBEDDING_MODEL)
    assistant = MultiAgentKnowledgeAssistant(openai_client, retriever)
    results = []
    for question in payload.questions:
        result = assistant.answer(question, "evaluation", 5)
        answer_lower = result["answer"].lower()
        keyword_hits = sum(1 for keyword in payload.expected_keywords if keyword.lower() in answer_lower)
        results.append(
            EvalResult(
                question=question,
                answer=result["answer"],
                cited_sources=len(result["sources"]),
                keyword_hits=keyword_hits,
            )
        )
    record_event("evaluate", json.dumps({"questions": len(payload.questions)}))
    return EvalResponse(
        results=results,
        average_cited_sources=sum(item.cited_sources for item in results) / max(len(results), 1),
        average_keyword_hits=sum(item.keyword_hits for item in results) / max(len(results), 1),
    )


@app.get("/analytics", dependencies=[Depends(require_api_key)])
def analytics() -> dict:
    return analytics_summary()
