# RAG Chatbot

A production-ready RAG (Retrieval-Augmented Generation) chatbot using AWS Bedrock, ChromaDB, FastAPI, and LangChain.

## Tech Stack
- **LLM**: AWS Bedrock — Claude 3 Haiku
- **Embeddings**: AWS Bedrock — Amazon Titan Embed Text v2
- **Vector Store**: ChromaDB (standalone)
- **Database**: PostgreSQL (conversation history)
- **Framework**: FastAPI + LangChain >= 0.3.0
- **Observability**: OpenTelemetry (console locally, extendable to Datadog)
- **Auth**: JWT (Bearer token)

## Quick Start

### 1. Copy env file
```bash
cp .env.example .env
# Fill in your AWS credentials and secrets
```

### 2. Start infrastructure
```bash
docker-compose up -d
```

### 3. Install dependencies
```bash
uv sync
```

### 4. Run the server
```bash
uv run main.py
```

API docs available at: http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /api/v1/auth/register | No | Register user |
| POST | /api/v1/auth/login | No | Login, get JWT |
| POST | /api/v1/ingest/ | Yes | Upload PDF/MD document |
| POST | /api/v1/chat/ | Yes | Ask a question |
| GET | /api/v1/chat/conversations | Yes | List conversations |
| GET | /api/v1/chat/conversations/{id} | Yes | Get message history |

## Run Tests
```bash
uv run pytest Test/ -v
```
