"""FastAPI app exposing typed report creation and history endpoints."""

import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from research_engine.config import FRONTEND_ORIGIN, LLM_PROVIDER
from research_engine.database import Base, ReportRecord, engine, get_session, list_reports
from research_engine.llm import EVIDENCE_NOTICE, LLMResponseError, LLMUnavailable, generate_report
from research_engine.schemas import ReportList, ResearchReport, ResearchRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("research_engine.api")


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Research Decision Engine API",
    description="Create and review structured preliminary decision briefs.",
    version="0.2.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def request_tracing(request: Request, call_next):
    request_id = str(uuid4())
    request.state.request_id = request_id
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("request_failed request_id=%s method=%s path=%s", request_id, request.method, request.url.path)
        raise
    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request_complete request_id=%s method=%s path=%s status=%s duration_ms=%s",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, exc: RequestValidationError):
    details = [
        {"field": ".".join(str(part) for part in error["loc"]), "message": error["msg"]}
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"error": {"code": "invalid_request", "details": details}})


@app.exception_handler(LLMUnavailable)
async def llm_unavailable_handler(_: Request, exc: LLMUnavailable):
    return JSONResponse(status_code=503, content={"error": {"code": "llm_unavailable", "message": str(exc)}})


@app.exception_handler(LLMResponseError)
async def llm_response_error_handler(_: Request, exc: LLMResponseError):
    logger.warning("llm_response_invalid message=%s", exc)
    return JSONResponse(status_code=502, content={"error": {"code": "llm_error", "message": str(exc)}})


@app.exception_handler(SQLAlchemyError)
async def database_error_handler(_: Request, exc: SQLAlchemyError):
    logger.exception("database_operation_failed")
    return JSONResponse(status_code=503, content={"error": {"code": "database_unavailable", "message": "Report storage is temporarily unavailable."}})


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception("unhandled_error request_id=%s", request_id, exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "internal_error", "message": "An unexpected error occurred.", "request_id": request_id}},
    )


@app.get("/health", tags=["operations"])
def health_check() -> dict[str, str]:
    """Report the API status and configured report-generation mode."""
    return {"status": "ok", "report_mode": LLM_PROVIDER}


@app.post("/api/reports", response_model=ResearchReport, status_code=201, tags=["reports"])
async def create_report(payload: ResearchRequest, session: Session = Depends(get_session)) -> ResearchReport:
    """Generate a structured preliminary report and persist it."""
    content, mode = await generate_report(payload.query)
    report_id = str(uuid4())
    created_at = datetime.now(timezone.utc)
    report = ResearchReport(
        id=report_id,
        query=payload.query,
        **content,
        sources=[],
        evidence_notice=EVIDENCE_NOTICE,
        mode=mode,
        created_at=created_at,
    )
    session.add(
        ReportRecord(
            id=report_id,
            query=payload.query,
            report=report.model_dump(mode="json"),
            created_at=created_at,
        )
    )
    session.commit()
    return report


@app.get("/api/reports", response_model=ReportList, tags=["reports"])
def get_reports(session: Session = Depends(get_session)) -> ReportList:
    """List the latest 50 saved reports."""
    records = list_reports(session)
    return ReportList(reports=[ResearchReport.model_validate(record.report) for record in records])


@app.get("/api/reports/{report_id}", response_model=ResearchReport, tags=["reports"])
def get_report(report_id: str, session: Session = Depends(get_session)) -> ResearchReport:
    """Get a saved report by its ID."""
    record = session.get(ReportRecord, report_id)
    if record is None:
        return JSONResponse(status_code=404, content={"error": {"code": "not_found", "message": "Report not found."}})  # type: ignore[return-value]
    return ResearchReport.model_validate(record.report)
