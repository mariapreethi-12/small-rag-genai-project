# Small RAG Gen AI Project

This is a tiny Retrieval-Augmented Generation project in Python. It reads `.txt`
and `.md` files from `data/`, embeds them with OpenAI, retrieves the most relevant
chunks for a question, and generates an answer with source citations.

## Files

- `app.py` - command-line RAG app.
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

## How It Works

1. Loads Markdown and text files from `data/`.
2. Splits documents into overlapping chunks.
3. Creates embeddings for each chunk.
4. Saves a simple JSON vector store.
5. Embeds the user question.
6. Retrieves the most similar chunks with cosine similarity.
7. Sends the retrieved context to a chat model to generate a grounded answer.

## Notes

- Add your own `.md` or `.txt` files to `data/`, then rerun `python app.py index`.
- Change models in `.env` with `RAG_EMBEDDING_MODEL` and `RAG_CHAT_MODEL`.
- This is intentionally small and readable. For production, use a real vector
  database, add tests, handle larger files, and store metadata more carefully.
