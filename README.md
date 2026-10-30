# Document Analysis Agent

A local RAG (Retrieval-Augmented Generation) agent that lets you ask questions about your own documents. Ingest files once — then query them in plain English, either through a direct CLI agent or through an MCP server/agent pair.

**Supported formats:** TXT · PDF · DOCX · Excel (`.xlsx`, `.xls`) · CSV

**LLM / Embedding providers:** Gemini · OpenAI · NVIDIA (wired into the main pipeline). Groq has an API key slot in `_config.py` but is **not yet connected** to `core/llm.py` or `core/embedder.py`.

---

## How It Works

```text
Your file
   ↓
Load & extract text  (loaders/)
   ↓
Split into chunks    (splitter)
   ↓
Embed each chunk
   ↓
Store in ChromaDB    (core/vector_store.py)
   ↓
Ask a question
   ↓
Embed the question → find top-n similar chunks → send to LLM → answer with citations
```

You can ask questions two ways:

1. **Direct CLI** (`_agent.py`) — calls `core/rag.py` in-process.
2. **MCP server + agent** (`mcp_server.py` + `mcp_agent.py`) — exposes the RAG pipeline as MCP tools (`ask_documents`, `search_documents`, `list_documents`) that a tool-calling LLM drives over stdio.

---

## Project Structure

```structure
.
├── database/            # ChromaDB file embeddings will be stored here
├── documents/           # move your files here
|
├── core/
│   ├── embedder.py      # Text → embedding vector (Gemini or OpenAI or NVIDIA)
│   ├── llm.py           # Send context + question to LLM, return answer
│   ├── rag.py           # Full pipeline: embed question → retrieve → ask LLM
│   └── vector_store.py  # ChromaDB operations: add, query, delete, list, upsert
│
├── loaders/
│   ├── __init__.py      # Maps file extensions to loader functions
│   ├── txt_loader.py
│   ├── pdf_loader.py
│   ├── docx_loader.py
│   ├── csv_loader.py
│   └── excel_loader.py
|
├── test/
│   ├── chunk_counts.py      # Standalone: precheck if embedding possible within daily limit
│   ├── show_files.py        # Standalone: list all ingested files and their chunk counts
│   ├── llm_models.py        # Standalone: quick test if a single chat model responds
│   ├── embedding_models.py  # Standalone: quick test if a single embedding model responds
|
├── _config.py           # choose provider, model names, API keys, DB path
├── _ingest.py           # Ingest a file into ChromaDB
├── _agent.py            # Interactive Q&A loop (direct, no MCP)
├── mcp_server.py         # Exposes the RAG pipeline as MCP tools
├── mcp_agent.py          # Interactive Q&A loop that talks to mcp_server.py over MCP
│
```

> `test/llm_models.py` and `test/embedding_models.py` are **not part of the main pipeline**. They're small, one-off scripts for manually sanity-checking a provider/model combo before wiring it into `_config.py`. Edit the `PROVIDER` and `MODEL` variables at the top of each file and run it directly, e.g. `python test/llm_models.py`.

---

## Setup

### 1. Install dependencies

```bash
pip install chromadb langchain-text-splitters pypdf python-docx \
            pandas openpyxl google-genai openai python-dotenv mcp
```

### 2. Create a `.env` file

```env
GEMINI_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here    # only needed if using OpenAI
NVIDIA_API_KEY=your_nvidia_key_here    # only needed if using NVIDIA
GROQ_API_KEY=your_groq_key_here        # loaded, but not yet wired into the pipeline
```

### 3. Choose your providers

Open `_config.py`. Chat and embedding providers are set **independently**:

```python
LLM_PROVIDER = "nvidia"        # "gemini" | "openai" | "nvidia"
EMBEDDING_PROVIDER = "gemini"  # "gemini" | "openai" | "nvidia"
```

This lets you, for example, use NVIDIA for chat while still embedding with Gemini.

> ⚠️ `"groq"` is **not a valid value** for either setting yet — `GROQ_API_KEY` is loaded but there's no Groq branch in `core/llm.py` or `core/embedder.py`. Setting either provider to `"groq"` will raise an error for now.

---

## Configuration (`_config.py`)

| Setting | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `"nvidia"` | Provider used for answering questions: `"gemini"`, `"openai"`, or `"nvidia"` |
| `EMBEDDING_PROVIDER` | `"gemini"` | Provider used for embeddings: `"gemini"`, `"openai"`, or `"nvidia"` |
| `EMBEDDING_MODELS` | per-provider dict | Embedding model, selected automatically from `EMBEDDING_PROVIDER` |
| `CHAT_MODELS` | per-provider dict | Chat model, selected automatically from `LLM_PROVIDER` |
| `CHROMA_PATH` | `./database` | Where ChromaDB stores data on disk |
| `COLLECTION_NAME` | `"documents"` | Files collection name |

Both `EMBEDDING_MODELS` and `CHAT_MODELS` are dictionaries keyed by provider name — edit the value for your chosen provider directly in `_config.py` to change the specific model used.

---

## Usage

### Ingest a file

```bash
python _ingest.py
```

You will be prompted to enter a file path. Enter one path at a time; type `exit` when done.

```text
Enter file path (or 'exit' to quit): documents/report.pdf
Loading documents/report.pdf ...
   Extracted 14320 characters.
   Split into 38 chunks (chunk_size=6000, overlap=600).
   Embedding chunks ...
   38/38
✅ Stored 38 chunks from 'report.pdf' in database.
```

Re-ingesting the same file automatically replaces the old version. If a file would need more embedding requests than `DAILY_BUDGET` (900), ingestion stops before calling the embedding API and the vector store is left untouched — use `test/chunk_counts.py` to check a file beforehand.

### Ask questions — direct CLI

```bash
python _agent.py
```

```text
🤖 Type 'exit' to quit.

Ask? What were the key findings in the report?

Agent:
The report identified three main findings ... [report.pdf § 4]
```

### Ask questions — via MCP

Run the MCP agent, which spawns `mcp_server.py` over stdio and drives it with your configured `LLM_PROVIDER`:

```bash
python mcp_agent.py
```

```text
🔌 Connected to MCP server. Available tools:
   - ask_documents
   - search_documents
   - list_documents

🤖 Type 'exit' to quit.

Ask? What files do I have?
   → tool: list_documents({})

Agent:
- report.pdf: 38 chunks
- sales_data.xlsx: 12 chunks
```

MCP tools exposed by `mcp_server.py`:

| Tool | Purpose |
|---|---|
| `ask_documents(question)` | Runs the full RAG pipeline and returns a finished, cited answer |
| `search_documents(question, n_results=5)` | Returns raw matching chunks without generating an answer |
| `list_documents()` | Lists every ingested file and its chunk count |

Answers include citations in the format `[filename § chunk_number]` so you know exactly where each fact came from.

### List ingested files

```bash
python test/show_files.py
```

```text
📁 ChromaDB collection 'documents'
-------------------------------------------------------
   report.pdf                          →  38 chunks
   sales_data.xlsx                     →  12 chunks
   notes.txt                           →   5 chunks
-------------------------------------------------------
   3 files, 55 total chunks
```

### Check if a file fits your daily quota before ingesting

```bash
python test/chunk_counts.py
```

Enter a file path to see the projected chunk count, estimated token usage, and whether it fits inside `DAILY_BUDGET` in one day.

---

## How Answers Are Generated

1. Your question is embedded into a vector using the same model used during ingestion.
2. ChromaDB finds the top-n most semantically similar chunks from all ingested documents (default 5).
3. Those chunks — tagged with their source file and chunk index — are passed to the LLM as context.
4. The LLM is instructed to answer only from the provided context and cite every fact.
5. If no relevant chunks exist, it replies: *"I don't know."*

---

## Notes

- The vector database persists on disk at `./database`. You do not need to re-ingest files between sessions.
- Chunk size during ingestion is 6,000 characters with a 600-character (10%) overlap, configured in `_ingest.py`.
- All files are chunked and embedded uniformly regardless of format.
- The direct agent (`_agent.py`) and the RAG pipeline (`core/rag.py`) have no memory between questions; each query is independent. The MCP agent (`mcp_agent.py`) keeps conversation history only within a single question's tool-calling loop (capped at `MAX_STEPS`), not across questions.
