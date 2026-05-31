from openai import OpenAI

from .config import CHAT_MODEL
from .memory import add_message, get_history


class ResearchAgent:
    name = "ResearchAgent"

    def __init__(self, retriever):
        self.retriever = retriever

    def run(self, question: str, top_k: int) -> tuple[list[dict], str]:
        sources = self.retriever.retrieve(question, top_k=top_k)
        return sources, f"{self.name}: retrieved {len(sources)} candidate evidence chunks."


class CitationAgent:
    name = "CitationAgent"

    def run(self, sources: list[dict]) -> tuple[str, str]:
        context = "\n\n".join(
            f"[{source['id']} | hybrid={source['score']:.3f} | bm25={source['bm25_score']:.3f} | vector={source['vector_score']:.3f}]\n{source['text']}"
            for source in sources
        )
        return context, f"{self.name}: prepared citation-grounded context."


class AnsweringAgent:
    name = "AnsweringAgent"

    def __init__(self, client: OpenAI, model: str = CHAT_MODEL):
        self.client = client
        self.model = model

    def run(self, question: str, conversation_id: str, context: str) -> tuple[str, str]:
        history = get_history(conversation_id)
        history_block = "\n".join(f"{item['role']}: {item['content']}" for item in history)
        prompt = f"""
You are an enterprise knowledge assistant.
Use only the provided context to answer.
If the answer is not in the context, say you do not know.
Always cite sources with bracketed ids.

Conversation memory:
{history_block}

Retrieved context:
{context}

Question:
{question}
"""
        response = self.client.responses.create(model=self.model, input=prompt.strip())
        answer = response.output_text
        add_message(conversation_id, "user", question)
        add_message(conversation_id, "assistant", answer)
        return answer, f"{self.name}: generated grounded answer with conversation memory."


class MultiAgentKnowledgeAssistant:
    def __init__(self, client: OpenAI, retriever):
        self.research_agent = ResearchAgent(retriever)
        self.citation_agent = CitationAgent()
        self.answering_agent = AnsweringAgent(client)

    def answer(self, question: str, conversation_id: str, top_k: int) -> dict:
        trace = []
        sources, step = self.research_agent.run(question, top_k)
        trace.append(step)
        context, step = self.citation_agent.run(sources)
        trace.append(step)
        answer, step = self.answering_agent.run(question, conversation_id, context)
        trace.append(step)
        return {"answer": answer, "sources": sources, "trace": trace}
