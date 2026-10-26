# Document Analysis Agent

A local RAG (Retrieval-Augmented Generation) agent that lets you ask questions about your own documents. Ingest files once — then query them in plain English.

**Supported formats:** TXT · PDF · DOCX · Excel (`.xlsx`, `.xls`) · CSV

---

## How It Works

```text
Your file
   ↓
Load & extract text  (loaders/)
   ↓
Split into chunks    (splitter)
   ↓
Embed each chunk     (Gemini / OpenAI)
   ↓
Store in ChromaDB    (core/vector_store.py)
   ↓
Ask a question
   ↓
Embed the question → find top-5 similar chunks → send to LLM → answer with citations
```

---

## Project Structure

```text
.
├── _config.py          # Provider, model names, API keys, DB path
├── _ingest.py          # Ingest a file into ChromaDB
├── _agent.py           # Interactive Q&A loop
├── show_files.py       # List all ingested files and their chunk counts
│
├── core/
│   ├── embedder.py     # Text → embedding vector (Gemini or OpenAI)
│   ├── llm.py          # Send context + question to LLM, return answer
│   ├── rag.py          # Full pipeline: embed question → retrieve → ask LLM
│   └── vector_store.py # ChromaDB operations: add, query, delete, list
│
└── loaders/
    ├── __init__.py     # Maps file extensions to loader functions
    ├── txt_loader.py
    ├── pdf_loader.py
    ├── docx_loader.py
    ├── csv_loader.py
    └── excel_loader.py
```

---

## Setup

### 1. Install dependencies

```bash
pip install chromadb langchain-text-splitters pypdf python-docx \
            pandas openpyxl google-genai openai python-dotenv
```

### 2. Create a `.env` file

```env
GEMINI_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here   # only needed if using OpenAI
```

### 3. Choose your provider

Open `_config.py` and set `PROVIDER`:

```python
PROVIDER = "gemini"   # or "openai"
```

That single line controls which API is used for both embedding and chat.

---

## Configuration (`_config.py`)

| Setting | Default | Description |
|---|---|---|
| `PROVIDER` | `"gemini"` | Which API to use: `"gemini"` or `"openai"` |
| `EMBED_MODEL` | `gemini-embedding-001` / `text-embedding-3-small` | Embedding model, chosen automatically by provider |
| `CHAT_MODEL` | `gemini-3.1-flash-lite` / `gpt-4.1-mini` | LLM for answering questions |
| `CHROMA_PATH` | `./database` | Where ChromaDB stores data on disk |
| `COLLECTION_NAME` | `"documents"` | ChromaDB collection name |

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
   Splited into 38 chunks.
   Embedding chunks ...
✅ Stored 38 chunks from 'report.pdf' in database.
```

Re-ingesting the same file automatically replacest he old version.

### Ask questions

```bash
python _agent.py
```

```text
🤖 Type 'exit' to quit.

Ask? What were the key findings in the report?

Agent:
The report identified three main findings ... [report.pdf § 4]
```

Answers include citations in the format `[filename § chunk_number]` so you know exactly where each fact came from.

### List ingested files

```bash
python show_files.py
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

---

## How Answers Are Generated

1. Your question is embedded into a vector using the same model used during ingestion.
2. ChromaDB finds the 5 most semantically similar chunks from all ingested documents.
3. Those chunks — tagged with their source file and chunk index — are passed to the LLM as context.
4. The LLM is instructed to answer only from the provided context and cite every fact.
5. If no relevant chunks exist, it replies: *"I don't know."*

---

## Notes

- The vector database persists on disk at `./database`. You do not need to re-ingest files between sessions.
- Chunk size is 500 characters with a 50-character overlap (configured in `_ingest.py`).
- All files are chunked and embedded uniformly regardless of format.
- The agent has no memory between questions; each query is independent.
