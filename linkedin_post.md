# LinkedIn Post Draft

I built a small Retrieval-Augmented Generation (RAG) GenAI project and turned it into a working portfolio demo.

This project helped me understand how a GenAI application can answer questions from private documents instead of relying only on the model's general knowledge.

What I built:

- A Python RAG pipeline that reads Markdown, text, and PDF files
- Document chunking with overlap
- OpenAI embeddings for semantic search
- Cosine similarity retrieval
- Grounded answer generation with citations
- A Streamlit web app with file upload, retrieval scores, and evidence preview

What I learned:

- How RAG connects document retrieval with LLM answer generation
- Why chunking strategy matters for answer quality
- How embeddings help match a user question to the right document section
- How citations make GenAI outputs more trustworthy
- How to keep API keys secure with `.env` and `.gitignore`

Challenge I faced:

At first, the project was only a command-line script. I wanted it to feel more like a real product demo, so I added a Streamlit UI, PDF support, document upload, and a retrieved evidence panel. That made the project easier to explain and much stronger for recruiters to review.

Result:

The app can index my knowledge files, answer questions from them, and show exactly which source chunk was used to generate the answer.

GitHub project:
https://github.com/mariapreethi-12/small-rag-genai-project

Tech stack:
Python, OpenAI API, Streamlit, NumPy, pypdf, RAG, Embeddings

#GenAI #RAG #Python #OpenAI #Streamlit #MachineLearning #AIProjects #PortfolioProject
