import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STORE_DIR = BASE_DIR / "enterprise_store"
STORE_DIR.mkdir(exist_ok=True)

EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "text-embedding-3-small")
CHAT_MODEL = os.getenv("RAG_CHAT_MODEL", "gpt-4.1-mini")
API_KEY = os.getenv("APP_API_KEY", "dev-local-key")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{STORE_DIR / 'assistant.db'}")
CHROMA_PATH = os.getenv("CHROMA_PATH", str(BASE_DIR / "chroma_db"))
FAISS_PATH = os.getenv("FAISS_PATH", str(STORE_DIR / "faiss.index"))
RECORDS_PATH = STORE_DIR / "records.json"
