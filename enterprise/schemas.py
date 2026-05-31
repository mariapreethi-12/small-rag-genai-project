from pydantic import BaseModel, Field


class Source(BaseModel):
    id: str
    source: str
    score: float
    bm25_score: float = 0
    vector_score: float = 0
    text: str


class AskRequest(BaseModel):
    question: str
    conversation_id: str = "default"
    top_k: int = Field(default=5, ge=1, le=12)


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]
    conversation_id: str
    agent_trace: list[str]


class IngestRequest(BaseModel):
    paths: list[str] = Field(default_factory=list)
    urls: list[str] = Field(default_factory=list)
    github_repos: list[str] = Field(default_factory=list)


class IngestResponse(BaseModel):
    documents: int
    chunks: int
    sources: list[str]


class EvalRequest(BaseModel):
    questions: list[str]
    expected_keywords: list[str] = Field(default_factory=list)


class EvalResult(BaseModel):
    question: str
    answer: str
    cited_sources: int
    keyword_hits: int


class EvalResponse(BaseModel):
    results: list[EvalResult]
    average_cited_sources: float
    average_keyword_hits: float
