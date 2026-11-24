"""
Private Corporate RAG & Document Extraction API (Sanitized Example)
Zero-retention multi-tenant document Q&A with citations and strict JSON invoice extraction.
"""

from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.rag_engine import TenantKnowledgeStore, parse_invoice_text

app = FastAPI(
    title="Golden Nodalix Corporate RAG API",
    version="1.1.0",
    description="Zero-retention private document Q&A with citations and structured PDF extraction.",
)

knowledge_store = TenantKnowledgeStore()
knowledge_store.ingest(
    tenant_id="demo-corp",
    document_name="sample_policy_2026.pdf",
    pages=[
        "Corporate procurement policy requires two approvals for vendor contracts above USD 5,000.",
        "Customer PII and API credentials must never leave private VPC boundaries.",
        "Annual SLA reviews occur every Q4 with signed vendor compliance attestations.",
    ],
)


class Citation(BaseModel):
    document_name: str
    page: int
    excerpt: str
    score: float = Field(ge=0.0, le=1.0)


class IngestRequest(BaseModel):
    tenant_id: str = Field(min_length=2)
    document_name: str = Field(min_length=2)
    pages: List[str] = Field(min_length=1)


class IngestResponse(BaseModel):
    tenant_id: str
    document_name: str
    chunks_indexed: int


class RagQueryRequest(BaseModel):
    tenant_id: str
    question: str
    top_k: int = Field(default=5, ge=1, le=20)


class RagQueryResponse(BaseModel):
    answer: str
    citations: List[Citation]


class InvoiceExtractionRequest(BaseModel):
    document_id: str
    raw_text: str


class InvoiceExtractionResponse(BaseModel):
    vendor_name: str
    invoice_number: str
    currency: str = "USD"
    total_amount: float
    due_date: Optional[str] = None


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "private-corporate-rag"}


@app.post("/ingest", response_model=IngestResponse)
def ingest_document(payload: IngestRequest) -> IngestResponse:
    chunks = knowledge_store.ingest(payload.tenant_id, payload.document_name, payload.pages)
    return IngestResponse(
        tenant_id=payload.tenant_id,
        document_name=payload.document_name,
        chunks_indexed=chunks,
    )


@app.post("/query", response_model=RagQueryResponse)
def query_knowledge_base(payload: RagQueryRequest) -> RagQueryResponse:
    matches = knowledge_store.search(payload.tenant_id, payload.question, payload.top_k)
    if not matches:
        return RagQueryResponse(
            answer=f"No grounded records matched '{payload.question}' inside tenant '{payload.tenant_id}'.",
            citations=[],
        )

    lead_excerpt = matches[0].excerpt
    return RagQueryResponse(
        answer=f"Grounded summary for '{payload.tenant_id}': {lead_excerpt}",
        citations=[
            Citation(
                document_name=m.document_name,
                page=m.page,
                excerpt=m.excerpt,
                score=m.score,
            )
            for m in matches
        ],
    )


@app.post("/extract-invoice", response_model=InvoiceExtractionResponse)
def extract_invoice(payload: InvoiceExtractionRequest) -> InvoiceExtractionResponse:
    parsed = parse_invoice_text(payload.document_id, payload.raw_text)
    return InvoiceExtractionResponse(**parsed)
