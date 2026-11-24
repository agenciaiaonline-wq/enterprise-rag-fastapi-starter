import unittest

from app.rag_engine import TenantKnowledgeStore, parse_invoice_text


class RagEngineTests(unittest.TestCase):
    def test_tenant_isolation_prevents_cross_tenant_leakage(self) -> None:
        store = TenantKnowledgeStore()
        store.ingest("tenant-alpha", "alpha_contract.pdf", ["Retainer fee is USD 2500 monthly."])
        store.ingest("tenant-beta", "beta_hr.pdf", ["Remote onboarding handbook policy."])

        alpha_hits = store.search("tenant-alpha", "retainer fee", top_k=3)
        beta_cross_hits = store.search("tenant-beta", "retainer fee", top_k=3)

        self.assertEqual(len(alpha_hits), 1)
        self.assertEqual(alpha_hits[0].document_name, "alpha_contract.pdf")
        self.assertEqual(beta_cross_hits, [])

    def test_invoice_extractor_parses_structured_fields(self) -> None:
        ocr_text = (
            "Vendor: Northwind Cloud Infrastructure LLC\n"
            "Invoice No: NW-2026-089\n"
            "Total Due: USD $4,250.75\n"
            "Due Date: 2026-12-30\n"
        )
        parsed = parse_invoice_text("089", ocr_text)
        self.assertEqual(parsed["vendor_name"], "Northwind Cloud Infrastructure LLC")
        self.assertEqual(parsed["invoice_number"], "NW-2026-089")
        self.assertEqual(parsed["currency"], "USD")
        self.assertEqual(parsed["total_amount"], 4250.75)
        self.assertEqual(parsed["due_date"], "2026-12-30")


if __name__ == "__main__":
    unittest.main()
