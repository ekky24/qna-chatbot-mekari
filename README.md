# Q&A Chatbot for Fraud Detection — Mekari Assessment

An AI-powered Question & Answer chatbot for credit card fraud detection and analysis. The system combines **Retrieval-Augmented Generation (RAG)** with **Model Context Protocol (MCP)** to answer questions grounded in both a fraud manual document and a live transaction database, with real-time token streaming and visible reasoning traces in the UI.

---

## Key Features

| Feature | Description |
|---|---|
| **Streaming responses** | Token-by-token output streamed from Ollama via Server-Sent Events |
| **Live reasoning trace** | Model thinking is shown in a collapsible panel as it generates |
| **Tool-use transparency** | Tool calls (DB query, document search) are surfaced in the UI while the agent works |
| **Document retrieval** | RAG over a fraud manual PDF using vector embeddings |
| **Database querying** | Natural-language queries translated to SQL against a MySQL transaction table |
| **REST API** | Flask endpoints for programmatic access |
| **Evaluation** | Automated benchmarking with semantic similarity scoring |

---

## Architecture

```
┌─────────────┐    SSE stream    ┌──────────────────┐    MCP/SSE    ┌─────────────────┐
│  Streamlit  │ ◄──────────────► │   Flask API       │ ◄───────────► │   MCP Server    │
│   ui.py     │                  │   app.py          │               │  mcp/server.py  │
└─────────────┘                  └──────────────────┘               └────────┬────────┘
                                          │                                   │
                                    LlamaIndex                         ┌──────┴──────┐
                                   FunctionAgent                       │  MySQL DB   │
                                          │                            │  RAG Index  │
                                    Ollama LLM                        └─────────────┘
                                  (streaming + thinking)
```

### Components

| File | Role |
|---|---|
| `app.py` | Flask API — `/init`, `/chat`, `/chat/stream` endpoints; runs all async agent work on a single persistent event loop |
| `ui.py` | Streamlit chat UI — SSE consumer with live thinking panel and tool-status badges |
| `mcp/server.py` | FastMCP server exposing `read_transaction` (SQL) and `search_fraud_manuals` (RAG) tools |
| `mcp/db_connector.py` | MySQL connection helpers |
| `utils/connect_llm.py` | LlamaIndex agent setup and `stream_agent_response` async generator |
| `build_rag.py` | One-time script to embed the fraud PDF and persist the vector index |
| `evaluate.py` | Benchmark runner — measures semantic similarity against reference Q&A pairs |
| `config.py` | Central configuration (URLs, model names, system prompt) |

---

## Prerequisites

- Python 3.10+ (tested on 3.12)
- [Ollama](https://ollama.ai) running locally
- MySQL server with the `qna_chatbot` database
- Conda (recommended) or a virtual environment

### Required Ollama models

```bash
ollama pull gemma4:12b-mlx        # chat LLM (streaming + thinking)
ollama pull qwen3-embedding:4b    # embeddings for RAG
```

---

## Installation

```bash
git clone https://github.com/ekky24/qna-chatbot-mekari.git
cd qna-chatbot-mekari

conda create -n qna-chatbot python=3.12
conda activate qna-chatbot

pip install -r requirements.txt
```

### Database setup

1. Create the `qna_chatbot` database in MySQL.
2. Import the transaction data from `dataset/fraudTrain.csv` and `dataset/fraudTest.csv`.
3. Update credentials in `mcp/db_connector.py` if they differ from the defaults (`root` / `P@ssw0rd` / `localhost:3306`).

### Build the RAG index

Run once after cloning (or whenever the source PDF changes):

```bash
conda activate qna-chatbot
python build_rag.py
```

This reads `raw_data/fraud_document/fraud_docs.pdf`, generates embeddings with `qwen3-embedding:4b`, and persists the vector store under `mcp/storage_qwen3/`.

---

## Configuration

All runtime settings live in `config.py`:

| Variable | Default | Description |
|---|---|---|
| `MODEL_URL` | `http://localhost:11434` | Ollama server URL |
| `MCP_SERVER_URL` | `http://localhost:4000/sse` | MCP server SSE endpoint |
| `SERVICE_URL` | `http://localhost:5000` | Flask API URL |
| `MODEL_NAME` | `gemma4:12b-mlx` | Chat LLM (must support streaming & thinking) |
| `EMBEDDING_MODEL_NAME` | `qwen3-embedding:4b` | Embedding model for RAG |

---

## Running the System

Start each component in a separate terminal, in order:

### 1 — MCP Server (port 4000)

```bash
conda activate qna-chatbot
python mcp/server.py
```

### 2 — Flask API (port 5000)

```bash
conda activate qna-chatbot
python app.py
```

### 3 — Streamlit UI (port 8501)

```bash
conda activate qna-chatbot
streamlit run ui.py
```

Open **http://localhost:8501** in your browser.

---

## API Reference

### `GET /init`
Initializes the LlamaIndex agent and connects to the MCP server. Must be called once before `/chat` or `/chat/stream`.

**Response:** `{"success": true}`

---

### `GET /list_tools`
Returns the list of tools available to the agent.

**Response:** `["read_transaction", "search_fraud_manuals"]`

---

### `POST /chat`
Blocking endpoint — waits for the full response before returning.

**Request:**
```json
{ "msg": "What is credit card fraud?" }
```
**Response:**
```json
{ "response": "Credit card fraud refers to…" }
```

---

### `POST /chat/stream`
Streaming endpoint — returns a `text/event-stream` (SSE) response with three event types:

| Event type | Payload | Description |
|---|---|---|
| `status` | `"Calling tool: read_transaction"` | Agent is executing a tool |
| `thinking` | `"<partial reasoning text>"` | Model reasoning delta |
| `token` | `"<partial response text>"` | Response token delta |

The stream ends with `data: [DONE]`.

**Example with curl:**
```bash
curl -N -X POST http://localhost:5000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"msg": "How many fraud transactions happened in January 2020?"}'
```

---

## Evaluation

Run the benchmark against five reference question-answer pairs:

```bash
conda activate qna-chatbot
python evaluate.py
```

Scores are computed using cosine similarity between the chatbot's response embeddings and the reference answers via `qwen3-embedding:4b`.

---

## Project Structure

```
qna-chatbot-mekari/
├── app.py                     # Flask API + persistent async event loop
├── build_rag.py               # RAG index builder (run once)
├── config.py                  # Central configuration
├── evaluate.py                # Evaluation / benchmarking script
├── ui.py                      # Streamlit chat interface
├── requirements.txt
├── dataset/
│   ├── fraudTrain.csv         # Training transaction data
│   └── fraudTest.csv          # Test transaction data
├── raw_data/
│   └── fraud_document/
│       └── fraud_docs.pdf     # Fraud manual source document
├── mcp/
│   ├── server.py              # FastMCP server (SQL + RAG tools)
│   ├── db_connector.py        # MySQL helpers
│   └── storage_qwen3/         # Persisted vector index
└── utils/
    └── connect_llm.py         # Agent factory + streaming generator
```

---

## Technologies

- **[LlamaIndex](https://www.llamaindex.ai/)** — RAG framework, FunctionAgent, workflow streaming
- **[Ollama](https://ollama.ai/)** — Local LLM runtime (`gemma4:12b-mlx`, `qwen3-embedding:4b`)
- **[FastMCP](https://github.com/jlowin/fastmcp)** — MCP server implementation
- **[Flask](https://flask.palletsprojects.com/)** — REST API with SSE streaming
- **[Streamlit](https://streamlit.io/)** — Chat web interface
- **MySQL** — Transaction database
- **FAISS** — Vector similarity search (via LlamaIndex)
