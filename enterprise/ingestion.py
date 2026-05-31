import csv
import subprocess
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

from .config import DATA_DIR, STORE_DIR


def read_pdf(path: Path) -> str:
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()


def read_structured(path: Path) -> str:
    rows = []
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            rows.append("; ".join(f"{key}: {value}" for key, value in row.items()))
    return "\n".join(rows)


def read_file(path: Path) -> dict | None:
    suffix = path.suffix.lower()
    if suffix in {".md", ".txt", ".py", ".js", ".ts", ".json", ".yaml", ".yml"}:
        text = path.read_text(encoding="utf-8", errors="ignore").strip()
    elif suffix == ".pdf":
        text = read_pdf(path)
    elif suffix == ".csv":
        text = read_structured(path)
    else:
        return None
    if not text:
        return None
    return {"source": str(path), "text": text}


def load_local_documents(paths: list[str] | None = None) -> list[dict]:
    candidates: list[Path] = []
    roots = [Path(path) for path in paths] if paths else [DATA_DIR]
    for root in roots:
        if root.is_file():
            candidates.append(root)
        elif root.exists():
            candidates.extend(
                path for path in root.rglob("*")
                if path.is_file() and ".venv" not in path.parts and ".git" not in path.parts
            )
    documents = []
    for path in candidates:
        document = read_file(path)
        if document:
            documents.append(document)
    return documents


def load_web_documents(urls: list[str]) -> list[dict]:
    documents = []
    for url in urls:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for element in soup(["script", "style", "nav", "footer"]):
            element.decompose()
        text = " ".join(soup.get_text(" ").split())
        if text:
            documents.append({"source": url, "text": text})
    return documents


def clone_github_repo(repo_url: str) -> Path:
    parsed = urlparse(repo_url)
    repo_name = Path(parsed.path).stem or "repo"
    destination = STORE_DIR / "cloned_repos" / repo_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        subprocess.run(["git", "-C", str(destination), "pull"], check=True)
    else:
        subprocess.run(["git", "clone", "--depth", "1", repo_url, str(destination)], check=True)
    return destination


def load_github_documents(repo_urls: list[str]) -> list[dict]:
    documents = []
    for repo_url in repo_urls:
        repo_path = clone_github_repo(repo_url)
        documents.extend(load_local_documents([str(repo_path)]))
    return documents


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 180) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = max(start + 1, end - overlap)
    return chunks


def build_chunks(documents: list[dict]) -> list[dict]:
    chunks = []
    for document in documents:
        for index, chunk in enumerate(chunk_text(document["text"])):
            chunks.append(
                {
                    "id": f"{document['source']}:{index + 1}",
                    "source": document["source"],
                    "text": chunk,
                }
            )
    return chunks
