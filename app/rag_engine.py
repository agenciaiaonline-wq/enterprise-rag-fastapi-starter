"""Tenant-isolated document chunking, lexical similarity retrieval, and invoice field extraction."""

from dataclasses import dataclass
import math
import re
from typing import Dict, List, Optional


TOKEN_PATTERN = re.compile(r"[a-z0-9]{2,}")


@dataclass(frozen=True)
class DocumentChunk:
    tenant_id: str
    document_name: str
    page: int
    text: str


@dataclass(frozen=True)
class RankedCitation:
    document_name: str
    page: int
    excerpt: str
    score: float


def tokenize(text: str) -> List[str]:
    return TOKEN_PATTERN.findall(text.lower())


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 60) -> List[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []
    chunks: List[str] = []
    start = 0
    step = max(1, chunk_size - overlap)
    while start < len(cleaned):
        chunks.append(cleaned[start : start + chunk_size])
        start += step
    return chunks


class TenantKnowledgeStore:
    """In-memory multi-tenant vector-ready store isolating retrieval by tenant_id."""

    def __init__(self) -> None:
        self._by_tenant: Dict[str, List[DocumentChunk]] = {}

    def ingest(self, tenant_id: str, document_name: str, pages: List[str]) -> int:
        bucket = self._by_tenant.setdefault(tenant_id, [])
        added = 0
        for page_idx, page_text in enumerate(pages, start=1):
            for piece in chunk_text(page_text):
                bucket.append(
                    DocumentChunk(
                        tenant_id=tenant_id,
                        document_name=document_name,
                        page=page_idx,
                        text=piece,
                    )
                )
                added += 1
        return added

    def search(self, tenant_id: str, question: str, top_k: int = 5) -> List[RankedCitation]:
        chunks = self._by_tenant.get(tenant_id, [])
        q_tokens = set(tokenize(question))
        if not chunks or not q_tokens:
            return []

        scored: List[RankedCitation] = []
        for chunk in chunks:
            c_tokens = set(tokenize(chunk.text))
            if not c_tokens:
                continue
            overlap = len(q_tokens & c_tokens)
            if overlap == 0:
                continue
            cosine_approx = overlap / math.sqrt(len(q_tokens) * len(c_tokens))
            scored.append(
                RankedCitation(
                    document_name=chunk.document_name,
                    page=chunk.page,
                    excerpt=chunk.text[:220],
                    score=round(min(1.0, cosine_approx), 4),
                )
            )

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]


def parse_invoice_text(document_id: str, raw_text: str) -> dict:
    """Extract vendor, invoice number, currency, total, and due date from raw OCR text."""
    vendor_match = re.search(r"Vendor:\s*([^\r\n]+)", raw_text, re.IGNORECASE)
    inv_match = re.search(r"Invoice\s*(?:#|No\.?):\s*([A-Z0-9-]+)", raw_text, re.IGNORECASE)
    total_match = re.search(r"Total(?:\s+Due)?:\s*(USD|EUR|GBP)?\s*\$?([\d,]+\.\d{2})", raw_text, re.IGNORECASE)
    due_match = re.search(r"Due\s*Date:\s*(\d{4}-\d{2}-\d{2})", raw_text, re.IGNORECASE)

    amount_raw = total_match.group(2).replace(",", "") if total_match else "0.00"
    currency = (total_match.group(1) or "USD").upper() if total_match else "USD"
    due_date: Optional[str] = due_match.group(1) if due_match else None

    return {
        "vendor_name": vendor_match.group(1).strip() if vendor_match else "Unverified Vendor",
        "invoice_number": inv_match.group(1).strip() if inv_match else f"INV-{document_id}",
        "currency": currency,
        "total_amount": float(amount_raw),
        "due_date": due_date,
    }
