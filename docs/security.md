# Security Review — Week 1

## Local development controls

- Secrets are read from environment variables. `.env*` files are ignored by Git and excluded from both Docker build contexts; `.env.example` contains blank password and API-key fields only.
- Compose requires separate generated PostgreSQL bootstrap and app-role passwords instead of using a known fallback.
- The API connects as `research_app`, a database role that can create/use objects in the application schema but is not a PostgreSQL superuser.
- The API and UI ports bind to `127.0.0.1`, not every host network interface. PostgreSQL has no published host port.
- The browser bundle receives only the API URL. The model API key is injected into the API container and is not sent to the browser.
- LLM provider response bodies and authorization headers are not logged. Application logs record request ID, route, status, and duration.
- The frontend lockfile audit currently reports no known npm vulnerabilities. The Python image upgrades pip during build to avoid a vulnerable pip version inherited from the base image.

## Remaining before public deployment

- The API has no user authentication or authorization. Keep it on loopback for this demo; add identity, authorization, and rate limits before exposing it to other machines or the internet.
- Add HTTPS at the public ingress, a managed secrets store, database backups, schema migrations, and production-grade dependency/image update scanning.
- Review data retention and provider privacy before sending research questions to an external LLM. The question is sent to the configured provider when `LLM_PROVIDER=openai_compatible`.
- `LLM_BASE_URL` is configurable for compatible providers. Only set it to a trusted endpoint; the API key is sent to that configured URL.

## Review scope

This review covers the repository source/configuration and local Compose setup. It does not certify the host, Docker daemon, third-party provider, or a future production deployment.
