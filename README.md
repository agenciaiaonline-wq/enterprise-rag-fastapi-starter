# Private Corporate RAG & Document Extraction Copilot (FastAPI + Qdrant)

[![CI](https://img.shields.io/badge/CI-unittest-10b981?style=flat-square)](.github/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?style=flat-square&logo=fastapi&logoColor=white)](app/main.py)
[![Docker](https://img.shields.io/badge/Docker-Non--Root_Container-2496ED?style=flat-square&logo=docker&logoColor=white)](Dockerfile)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)

> **Zero-retention private document intelligence & structured invoice/contract JSON extraction for legal, finance, healthcare, and operations teams.**

Benchmarked against enterprise self-hosted RAG & OCR extraction patterns (`enterprise-rag-boilerplate`, `invoice-extractor`), this codebase provides strict multi-tenant scoping (`tenant_id`), deterministic chunk retrieval with grounded citations, and structured invoice JSON extraction.

---

## Architecture

```mermaid
flowchart LR
    DOC["PDF / Contracts / Invoices"] --> PARSE["Chunking & Tenant Parser"]
    PARSE --> QDR["Tenant Vector Store (Qdrant Ready)"]
    USER["Internal Portal / n8n Webhook"] --> API["FastAPI (/ingest, /query, /extract-invoice)"]
    API --> QDR
    API --> LLM["LLM Router (OpenAI-Compatible / Local Ollama)"]
    API --> OUT["Verified Citations + Strict Pydantic JSON"]
```

---

## API Endpoints

| Method & Route | Purpose |
| :--- | :--- |
| `GET /health` | Service readiness probe |
| `POST /ingest` | Chunk and index tenant-scoped document pages |
| `POST /query` | Retrieve strictly tenant-isolated citations (`top_k`) + grounded summary |
| `POST /extract-invoice` | Extract vendor, invoice ID, currency, total amount, and due date into typed JSON |

---

## Quick Start

```bash
cp .env.example .env
python3 -m unittest discover -s tests -v
docker compose -f docker-compose.example.yml up -d
# Interactive Swagger UI: http://127.0.0.1:8000/docs
```

---

## Request Custom RAG Deployment (`USD 4,500 - 12,000`)
- **LinkedIn Studio:** [Golden Nodalix Studio](https://www.linkedin.com/in/agency-golden-nodalix-880598438/)
- **Profile Hub:** [agenciaiaonline-wq](https://github.com/agenciaiaonline-wq)
- **Email:** `studio@example.com`
