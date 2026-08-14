# NayaTel AI Customer Support Assistant
## NOTE: FEW THINGS TO BE UPDATED IN README
## (IF NOT CLARIFIED IN README PLEASE SEE docs/)
A Retrieval-Augmented Generation (RAG) chatbot that answers customer questions using
NayaTel's own documentation — FAQs, pricing, manuals, troubleshooting guides, and blog
content — instead of relying on an LLM's general training knowledge. Answers are
grounded in retrieved source documents and cited, and the assistant explicitly declines
to answer when a question falls outside its knowledge base.

---

## Features

- Retrieval-augmented answers grounded in NayaTel's actual documentation (no invented
  prices, policies, or procedures)
- Source attribution — every answer cites the document(s) and page(s) it was drawn from
- Per-session conversation history, so follow-up questions ("how much does it cost?")
  resolve correctly against prior context
- Relevance gating — out-of-scope questions are declined rather than answered from the
  model's general knowledge
- NayaTel-inspired chat UI with a working backend/frontend integration
- FastAPI backend with interactive Swagger docs for direct testing

---

## Architecture

```
User Question
     │
     ▼
FastAPI (/api/chat)
     │
     ▼
RAGPipeline.answer()
     │
     ├─► History            — recall/store per-session conversation turns
     ├─► Retriever           — embed query → vector search → top-k chunks
     ├─► Relevance gate       — reject if nothing sufficiently relevant was found
     ├─► Prompt builder       — context + history + strict instructions → prompt
     └─► LLMClient            — GPT-5-mini generates the grounded answer
     │
     ▼
{"answer": "...", "sources": [...]}
```

**Ingestion (offline, run via `ingest.py`):**
```
Raw PDFs (data/raw/<category>/*.pdf)
     │
     ▼
Load (PyMuPDF) → Clean → Chunk (token-based, ~650 tokens / 80 overlap)
     │
     ▼
Checkpoint to JSONL (data/processed/cleaned, data/processed/chunks)
     │
     ▼
Embed (sentence-transformers, local) → Store in ChromaDB (data/processed/vector_db)
```

---

## Tech Stack

| Layer | Tool | Why |
|---|---|---|
| PDF parsing | PyMuPDF (`fitz`) | Fast, reliable text extraction across varied PDF sources |
| Chunking | `tiktoken` (token-based) | Consistent chunk sizing independent of sentence/line irregularities in extracted PDF text |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) NOTE: MODEL CHANGED | Free, local, no API dependency; sufficient quality for a single-domain corpus |
| Vector DB | ChromaDB | Minimal setup, persists vectors + text + metadata together, ideal for a project at this scale |
| LLM | OpenAI `gpt-5-mini` | Cost-efficient, well-suited to well-defined, context-constrained generation tasks |
| Backend | FastAPI | Async-friendly, automatic request validation and OpenAPI docs |
| Frontend | HTML/CSS/JS chat UI | NayaTel-inspired interface, lightweight to build within timeline |

---

## Project Structure

```
nayatel-ai-assistant/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── routes/
│   │   │   └── chat.py
│   │   ├── rag/
│   │   │   ├── pipelines.py      # UtilityPipelines (ingestion) + RagPipelines (orchestration)
│   │   │   ├── ingest.py         # ingestion entry point / orchestrator
│   │   │   ├── retriver.py       # vector search + query embedding
│   │   │   ├── history.py        # per-session conversation history
│   │   │   └── prompt.py         # prompt template + system instructions
│   │   ├── llm/
│   │   │   └── client.py         # LLMClient (generation) + EmbeddingClient
│   │   └── models/
│   │       └── schemas.py        # Pydantic request/response models
│   │
│   ├── data/
│   │   ├── raw/                  # source PDFs, organized by category folder
│   │   └── processed/            # cleaned/chunked JSONL checkpoints + vector DB
│   │
│   ├── requirements.txt
│   └── .env
│
├── frontend/
├── docs/
├── README.md
└── .gitignore
```

---

## Installation

```bash
git clone <repo-url>
cd nayatel-ai-assistant/backend

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt --break-system-packages
```

## Environment Variables

Create `backend/.env`:

```
OPENAI_API_KEY=your_key_here
```

See `.env.example` for the expected format.

## Building the Knowledge Base

Place source PDFs under `backend/data/raw/<category>/`, one folder per category
(e.g. `faq/`, `payment/`, `manuals/`, `blog/`). Then run ingestion:

```bash
python -m app.rag.ingest
```

This cleans, chunks, embeds, and stores everything in the local vector database.
Re-run with a forced rebuild if source PDFs change:

```bash
python -m app.rag.ingest --force
```

## Running the Backend

```bash
uvicorn app.main:app --reload
```

Interactive API docs available at `http://localhost:8000/docs`.

## Running the Frontend

Open `frontend/index.html` directly, or serve it with any static file server
(e.g. `python -m http.server` or the VS Code Live Server extension).

---

## API Endpoints

### `POST /api/chat`

**Request:**
```json
{
    "message": "How can I get a new connection?",
    "session_id": "123"
}
```

**Response:**
```json
{
    "answer": "To get a new connection...",
    "sources": [
        {"title": "New Connection FAQ", "page": 2}
    ]
}
```

### `GET /api/health`

```json
{"status": "healthy"}
```

---

## Example Queries

- "What internet packages are available?"
- "How do I pay my bill?"
- "What should I do if my internet isn't working?"
- "What's the difference between 2.4GHz and 5GHz?"
- "Does NayaTel offer Starlink packages?" *(out-of-scope — assistant correctly declines)*

---

## Evaluation

Retrieval was validated against a set of representative questions spanning every
document category (FAQ, payment, manuals, blog, pricing), checking that the correct
source document appeared in the top-k retrieved chunks. Two chunking strategies were
tested — sentence-based micro-chunks and token-based chunks (~650 tokens, 80 overlap)
— with token-based chunking producing noticeably better category-correct retrieval and
was adopted as the final approach.

Hallucination resistance was tested with deliberately out-of-scope questions (e.g.
asking about a competitor's product not in the knowledge base); the assistant
correctly declines to answer rather than inventing information, guided by both a
similarity-based relevance gate and explicit system prompt instructions.

---

## Limitations

- **Relevance gate is not fully reliable on vector similarity alone.** In testing,
  similarity scores between clearly in-scope and out-of-scope questions sometimes
  overlapped, given the narrow, single-domain nature of the corpus (all documents are
  NayaTel/ISP-related, sharing significant vocabulary). The system prompt's explicit
  instructions currently provide a meaningful second layer of protection against
  hallucination beyond the similarity threshold.
- **Conversation history is in-memory only** and does not persist across server
  restarts or scale across multiple server instances.
- **No authentication** — sessions are identified by a client-supplied `session_id`
  with no verification.
- **Category inference relies on manual folder organization** of source PDFs rather
  than automated document classification.

---

## Future Improvements

- Persistent, database-backed session storage
- Automated re-ingestion triggered by source-file changes (hash-based change detection)
- A re-ranking step after initial vector retrieval to improve relevance precision
- Evaluation of larger/alternative embedding models for better in-scope/out-of-scope
  separation on this narrow domain
- Per-category retrieval routing, given the variety of document types (manuals vs.
  FAQ vs. blog vs. pricing)
- Multilingual (Urdu) support
- Human-agent escalation path for low-confidence or unresolved queries
- Usage analytics and query logging for continuous improvement
- Production deployment (containerization, managed hosting)

---

## Author's Note

Built as a 2-3 day internship project demonstrating an end-to-end RAG system: document
ingestion, chunking strategy experimentation, local embeddings, vector search, relevance
gating, grounded generation, conversation history, and a working full-stack demo.
