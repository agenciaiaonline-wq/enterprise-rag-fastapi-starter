# Security Policy

- Never index unredacted customer PII into shared public or multi-tenant vector collections without enforcing `tenant_id` payload filters on every query.
- Keep vector database credentials, LLM API keys, and object storage tokens strictly in server environment variables (`.env` excluded by `.gitignore`).
- Report security concerns responsibly via [Golden Nodalix Studio on LinkedIn](https://www.linkedin.com/in/agency-golden-nodalix-880598438/).
