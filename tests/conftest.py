"""Share an isolated in-memory database across API tests."""

import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["LLM_PROVIDER"] = "demo"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from research_engine.database import ReportRecord, SessionLocal
from research_engine.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        with SessionLocal() as session:
            session.execute(delete(ReportRecord))
            session.commit()
        yield test_client
