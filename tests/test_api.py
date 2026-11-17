def test_health_includes_mode_and_request_id(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "report_mode": "demo"}
    assert response.headers["x-request-id"]


def test_query_validation_is_typed_and_actionable(client):
    response = client.post("/api/reports", json={"query": "short"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"

    whitespace = client.post("/api/reports", json={"query": "             "})
    assert whitespace.status_code == 422


def test_create_report_persists_and_returns_structured_report(client):
    response = client.post(
        "/api/reports",
        json={"query": "Should a small business invest in solar panels?"},
    )

    assert response.status_code == 201
    report = response.json()
    assert report["query"] == "Should a small business invest in solar panels?"
    assert report["confidence"] == "low"
    assert report["sources"] == []
    assert "No external sources were searched" in report["evidence_notice"]

    detail = client.get(f"/api/reports/{report['id']}")
    listing = client.get("/api/reports")
    assert detail.status_code == 200
    assert detail.json()["id"] == report["id"]
    assert listing.status_code == 200
    assert listing.json()["reports"][0]["id"] == report["id"]


def test_unknown_report_returns_not_found(client):
    response = client.get("/api/reports/no-such-report")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_provider_failure_returns_structured_gateway_error(client, monkeypatch):
    from research_engine.llm import LLMResponseError

    async def fail_generation(_query):
        raise LLMResponseError("provider response was invalid")

    monkeypatch.setattr("research_engine.main.generate_report", fail_generation)
    response = client.post("/api/reports", json={"query": "Should we expand into a new market?"})

    assert response.status_code == 502
    assert response.json()["error"]["code"] == "llm_error"
