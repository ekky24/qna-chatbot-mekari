# Q&A Chatbot for Fraud Detection - Mekari Assessment

A Question and Answer chatbot application designed to assist with fraud detection and analysis. This system leverages Retrieval-Augmented Generation (RAG) technology combined with Model Context Protocol (MCP) to provide accurate, context-aware responses based on fraud-related documents and transaction data.

## Overview

This project implements an AI-powered chatbot that can answer questions about credit card fraud, query transaction databases, and retrieve relevant information from fraud manual documents. The system is built using LlamaIndex AI frameworks and provides both a REST API (Flask) and a web-based user interface (Streamlit).

### Key Features

- **Intelligent Q&A**: Answers questions about credit card fraud definitions, methods, and prevention strategies
- **Database Integration**: Direct querying of fraud transaction datasets through MCP tools
- **Document Retrieval**: RAG-based search through fraud manual documents (PDF format)
- **Context-Aware Responses**: Uses semantic similarity and vector embeddings for accurate information retrieval
- **Web Interface**: Streamlit-based chat interface
- **REST API**: Flask-based API for programmatic access
- **Evaluation System**: Automated evaluation using semantic similarity metrics
- **Scalable Architecture**: Modular design with separate components for RAG building, serving, and evaluation

## Architecture

The system consists of several key components:

1. **RAG Builder** (`build_rag.py`): Processes fraud documents and creates vector embeddings for retrieval
2. **MCP Server** (`mcp/server.py`): Provides tools for database queries and document search
3. **Flask API** (`app.py`): Main application server with chat endpoints
4. **Streamlit UI** (`ui.py`): Web-based chat interface
5. **Evaluation System** (`evaluate.py`): Automated testing and performance measurement

## Prerequisites

- Python 3.8 or higher
- Ollama server running locally (for LLM and embeddings)
- MySQL database with fraud transaction data
- Required Python packages (see `requirements.txt`)

### External Dependencies

- **Ollama**: Local LLM server (models: `qwen3:14b`, `qwen3-embedding:4b`)
- **MySQL Database**: Contains credit card transaction data (fraudulent and legitimate)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ekky24/qna-chatbot-mekari.git
   cd qna-chatbot-mekari
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Ollama**:
   - Install Ollama from [ollama.ai](https://ollama.ai)
   - Pull required models:
     ```bash
     ollama pull qwen3:4b
     ollama pull qwen3-embedding:4b
     ```
   - Start Ollama server

4. **Configure Database**:
   - Set up MySQL database
   - Import fraud transaction data from `raw_data/fraud_dataset/`
   - Update database connection settings in `mcp/db_connector.py`

5. **Build RAG Index**:
   ```bash
   python build_rag.py
   ```

## Configuration

Update `config.py` with specific settings:

- `MODEL_URL`: Ollama server URL (default: `http://192.168.98.202:11434`)
- `MCP_SERVER_URL`: MCP server URL (default: `http://localhost:4000/sse`)
- `SERVICE_URL`: Flask API URL (default: `http://localhost:5000`)
- Database connection settings in `mcp/db_connector.py`

## Usage

### Starting the System

1. **Start MCP Server**:
   ```bash
   python mcp/server.py
   ```

2. **Start Flask API**:
   ```bash
   python app.py
   ```

3. **Start Streamlit UI** (in a new terminal):
   ```bash
   streamlit run ui.py
   ```

### API Endpoints

- `GET /init`: Initialize the agent and MCP client
- `GET /list_tools`: List available MCP tools
- `POST /chat`: Send a message and receive a response
  ```json
  {
    "msg": "What is credit card fraud?"
  }
  ```

## Project Structure

```
qna-chatbot-mekari/
├── app.py                 # Main Flask application
├── build_rag.py          # RAG index builder
├── config.py             # Configuration settings
├── evaluate.py           # Evaluation script
├── ui.py                 # Streamlit web interface
├── requirements.txt      # Python dependencies
├── README.md             # This file
├── mcp/
│   ├── server.py         # MCP server with tools
│   ├── db_connector.py   # Database connection utilities
│   └── __pycache__/
├── storage_qwen3/        # Vector store persistence
│   ├── default__vector_store.json
│   ├── docstore.json
│   ├── graph_store.json
│   ├── image__vector_store.json
│   └── index_store.json
├── raw_data/
│   ├── fraud_dataset/    # CSV files with transaction data
│   │   ├── fraudTest.csv
│   │   └── fraudTrain.csv
│   └── fraud_document/   # Fraud manual documents
│       └── fraud_docs.pdf
├── utils/
│   └── connect_llm.py    # LLM connection utilities
└── __pycache__/
```

## Evaluation

The system includes automated evaluation using semantic similarity:

```bash
python evaluate.py
```

This script tests the chatbot against predefined question-answer pairs and calculates average similarity scores using the configured embedding model.

## Technologies Used

- **LlamaIndex**: RAG framework and vector indexing
- **Ollama**: Local LLM and embedding models (Qwen3)
- **Flask**: REST API framework
- **Streamlit**: Web UI framework
- **Model Context Protocol (MCP)**: Tool integration protocol
- **MySQL**: Transaction database
- **FAISS**: Vector similarity search (via LlamaIndex)