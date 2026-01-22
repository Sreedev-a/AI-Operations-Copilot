from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)
def test_health_and_seed_data():
    assert client.get("/health").json()["status"]=="ok"
    assert len(client.get("/api/incidents").json())==20
def test_create_and_investigate():
    r=client.post("/api/incidents",json={"title":"Custom payment failure","description":"Payments are returning errors after a change","service":"payment-api","severity":"SEV-2"})
    assert r.status_code==201
    result=client.post(f"/api/incidents/{r.json()['id']}/investigate").json()
    assert result["hypotheses"] and result["trace"] and result["recommendation"]["simulated"]
def test_approval_requires_valid_decision():
    ident=client.get("/api/incidents").json()[0]["id"]
    client.post(f"/api/incidents/{ident}/investigate")
    assert client.post(f"/api/incidents/{ident}/approval",json={"decision":"approve"}).json()["simulated"]
    assert client.post(f"/api/incidents/{ident}/approval",json={"decision":"destroy"}).status_code==422
def test_knowledge_retrieval():
    results=client.get("/api/knowledge",params={"q":"database connection pool timeout"}).json()
    assert results[0]["title"]=="Database Connection Pool Runbook"
def test_evaluation_is_measured():
    result=client.post("/api/evaluations/run").json()
    assert result["total_cases"]==20
    assert result["metrics"]["root_cause_accuracy"]==1
