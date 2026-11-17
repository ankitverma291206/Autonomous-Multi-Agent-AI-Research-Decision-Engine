# Core Project Requirements

## Project goal

Build an **Autonomous Multi-Agent AI Research & Decision Engine**: a portfolio-grade AI engineering system that investigates complex questions using multiple sources, evaluates evidence, performs analysis, and produces a cited decision report. The project should demonstrate working engineering, not just a collection of technologies or API calls.

## Core user workflow

Given a question such as whether a company should invest in EV charging infrastructure in India over the next five years, the system should:

1. Plan the research and split it into manageable subtasks.
2. Gather relevant information from multiple sources.
3. Retrieve and extract supporting passages and structured facts.
4. Identify conflicting claims and assess source credibility.
5. Run appropriate Python-based calculations or statistical analysis.
6. Verify that report claims are supported by evidence; seek more evidence when they are not.
7. Produce a structured report with citations and confidence indicators.
8. Require human approval before consequential actions.

## Intended architecture

- Orchestrator for task planning, dependencies, retries, and recovery.
- Specialized web research, document retrieval, data analysis, and verification agents.
- Report generation with citation and quality checks.
- Interactive dashboard and exportable report.
- Observability for agent decisions, tool calls, latency, and token cost.

## Engineering priorities

- Build and benchmark hybrid retrieval (keyword + vector search, with reranking) against a baseline.
- Verify citations and evidence support; do not present unsupported claims as facts.
- Handle failures with bounded retries, clear status, and graceful recovery.
- Include authentication, rate limiting, caching, and deployment monitoring as the system matures.
- Keep the system modular and document architectural decisions.
- Treat knowledge graphs and LoRA/QLoRA fine-tuning as advanced extensions, only if they add measurable value.

## Suggested stack (not mandatory)

Python, LangGraph, FastAPI, PostgreSQL, Qdrant or FAISS, Next.js/Tailwind, Docker, and AWS or GCP. Candidate models include Llama, Qwen, Gemini, or OpenAI. Candidate evaluation/observability tools include Ragas and LangSmith. Choose tools to serve the requirements; do not add them merely for a resume keyword.

## Evaluation and portfolio evidence

Measure and report at least:

- Citation correctness and evidence support.
- Retrieval recall/quality versus a baseline.
- End-to-end task completion/success rate.
- Latency and cost per research task.

The repository should ultimately include a live demo, architecture diagram, documented experiments, automated test suite, and honest evaluation results. Resume claims must reflect measured results from the actual implementation.

## Suggested delivery sequence

1. Core research engine: search, document ingestion, retrieval, and cited reports.
2. Orchestration: specialized agents, planning, tools, retries, and failure recovery.
3. Evidence intelligence: verification, conflict handling, and optionally knowledge graph or fine-tuning experiments.
4. Production readiness: evaluation, security, monitoring, deployment, and documentation.

## Guiding principle

Prioritize one deeply engineered, deployed, and benchmarked project over several shallow AI demos. Prefer features that can be demonstrated and measured. Treat the eight-week timeline in the source plan as an ambitious estimate, not a fixed deadline.
