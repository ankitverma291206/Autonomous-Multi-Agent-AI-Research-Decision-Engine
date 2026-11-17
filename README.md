# Fieldnote — Autonomous Research & Decision Engine

Turn a complex question into a structured preliminary decision brief. The Week 1 app includes a Next.js report viewer, typed FastAPI endpoints, a configurable LLM adapter, PostgreSQL report history, request tracing, and API tests.

## Run the complete demo

Requires Docker Desktop with Compose. Python and Node are not required on the host.

```powershell
Copy-Item .env.example .env
$adminPassword = [Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
$appPassword = [Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
@("POSTGRES_PASSWORD=$adminPassword", "APP_DB_PASSWORD=$appPassword", "LLM_PROVIDER=demo", "LLM_BASE_URL=https://api.openai.com/v1", "LLM_API_KEY=", "LLM_MODEL=gpt-4o-mini") | Set-Content -Encoding ascii .env
docker compose up --build
```

Open [http://localhost:3000](http://localhost:3000). The default `LLM_PROVIDER=demo` produces deterministic briefs without API credentials. Reports are persisted in the PostgreSQL `postgres_data` volume. The API connects as a restricted `research_app` role; the separate bootstrap database password is only used by PostgreSQL initialization. Published ports bind to loopback for local development. Stop with `Ctrl+C`; run `docker compose down` to stop and remove containers. `docker compose down -v` also deletes saved report data.

## Use a hosted OpenAI-compatible model

In `.env`, set `LLM_PROVIDER=openai_compatible`, provide `LLM_API_KEY`, and set `LLM_MODEL`. `LLM_BASE_URL` defaults to `https://api.openai.com/v1`; compatible services can override it. Restart the API after editing `.env`:

```powershell
docker compose up --build
```

The provider is asked for JSON and its output is validated against the report schema. The app does not browse the web yet. Reports have no verified sources and display a clear evidence notice; do not treat them as sourced research.

## API

- `GET /health` — service status and report mode.
- `POST /api/reports` — create and persist a report. JSON body: `{"query":"Should a small business invest in solar panels?"}`.
- `GET /api/reports` — latest 50 reports.
- `GET /api/reports/{id}` — retrieve one saved report.
- `GET /docs` — interactive OpenAPI page.

Invalid requests return a structured `422` error. Each response includes an `X-Request-ID`; API logs include the request ID, route, status, and duration.

## Run API tests locally

Requires Python 3.11+.

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest
```

## Repository map

```text
src/research_engine/  FastAPI routes, schemas, LLM adapter, persistence
frontend/             Next.js query form and report viewer
tests/                API contract and persistence tests
docs/                 Architecture notes
```

## Week 1 status

- **Day 1:** repository, environment, and Docker setup.
- **Day 2:** FastAPI backend and typed request models.
- **Day 3:** LLM integration and structured report output.
- **Day 4:** Next.js query form and report viewer.
- **Day 5:** PostgreSQL persistence for research reports.
- **Day 6:** request tracing, error handling, and API tests.
- **Day 7:** end-to-end Compose demo, bug fixes, and local Git commit.

The current brief is a first-week foundation, not the full autonomous research workflow. Search, document ingestion, evidence verification, and real citations are future milestones. The local stack is not hardened for public deployment; see [Security notes](docs/security.md).
