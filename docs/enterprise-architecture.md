# Enterprise Multi-Agent Knowledge Assistant

This upgrade turns the original RAG demo into an enterprise-style architecture.

## Capabilities

- Ingests PDFs, Markdown, text, CSV files, websites, and GitHub repositories.
- Uses a multi-agent flow:
  - `ResearchAgent` retrieves relevant evidence.
  - `CitationAgent` prepares citation-ready context.
  - `AnsweringAgent` generates source-grounded answers with memory.
- Uses hybrid retrieval:
  - BM25 lexical scoring.
  - OpenAI vector similarity.
  - Lightweight reranking based on query-term overlap.
- Supports optional FAISS and ChromaDB indexing when dependencies are installed.
- Exposes a FastAPI backend with API-key authentication.
- Tracks conversation memory and analytics in SQLite locally.
- Includes Docker and Docker Compose scaffolding for API + PostgreSQL.

## API

Run locally:

```powershell
.\.venv\Scripts\python.exe -m uvicorn enterprise.api:app --reload
```

Open:

```text
http://localhost:8000/docs
```

Use this header:

```text
X-API-Key: dev-local-key
```

## Endpoints

- `GET /health`
- `POST /ingest`
- `POST /ask`
- `POST /evaluate`
- `GET /analytics`

## Privacy Note

Ingestion sends document text to the embedding model provider. Do not ingest
personal, confidential, or company-private documents unless you have permission
to process them with the configured model provider.

## AWS Deployment Roadmap

For a portfolio-ready enterprise deployment:

1. Containerize the FastAPI service with `Dockerfile`.
2. Push the image to Amazon ECR.
3. Deploy the service on ECS Fargate or AWS App Runner.
4. Use RDS PostgreSQL for conversation memory and analytics.
5. Store uploaded documents in S3.
6. Store secrets in AWS Secrets Manager.
7. Add CloudWatch logs and alarms.
8. Place the API behind an Application Load Balancer.
9. Add Cognito or API Gateway authorizers for production authentication.

## Why This Is Recruiter-Friendly

This project now shows product thinking and system design, not only a notebook demo:

- API backend
- Agent separation
- Hybrid retrieval
- Vector store integration points
- Evaluation workflow
- Auth and analytics
- Deployment scaffolding
