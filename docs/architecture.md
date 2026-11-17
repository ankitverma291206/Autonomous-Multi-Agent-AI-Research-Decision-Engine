# Week 1 Architecture

```text
Browser
  -> Next.js query form and report viewer :3000
      -> FastAPI typed API :8000
          -> demo report generator (default) or OpenAI-compatible JSON endpoint
          -> SQLAlchemy sessions -> PostgreSQL :5432
```

## Current behavior

- `POST /api/reports` validates a 10–2,000 character question, creates a structured report, and stores it.
- `GET /api/reports` and `GET /api/reports/{id}` load report history from PostgreSQL.
- The demo provider works without credentials and returns a visibly low-confidence starter brief.
- The optional OpenAI-compatible provider requests JSON, validates each field with Pydantic, and returns a controlled error if generation or validation fails.
- Reports explicitly state that no external sources were searched. The source list is empty until research retrieval is implemented.
- Middleware assigns a request ID, adds it to the response, and logs route, status, and duration. Validation, provider, storage, and unexpected errors have structured responses.

## Decisions and next boundaries

- Python + FastAPI for typed API contracts and the data/AI workload; Next.js for the interaction layer.
- SQLAlchemy abstracts PostgreSQL for the Compose application and SQLite for local API tests.
- SQLAlchemy `create_all` is used for this first-week schema. A migration system should replace it before the schema changes become substantial.
- No orchestration or search framework is wired in yet. Next, define workflow state, source adapters, evidence records, and citation checks before adding autonomous agents.
- LLM output is not treated as sourced research. Claims need retrieval evidence and verification in the next milestone.
