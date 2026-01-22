from __future__ import annotations

from datetime import datetime, timedelta, timezone

SERVICES = ["payment-api", "auth-service", "order-service", "recommendation-service", "notification-worker", "postgres-primary", "redis-cache", "ml-inference-api", "gateway-service"]

CASES = [
    ("Database connection exhaustion", "payment-api", "Database connection pool exhaustion", "rollback deployment", ["logs", "deployments", "database", "history"]),
    ("Expired provider API token", "payment-api", "Expired payment provider API token", "rotate API token", ["logs", "health", "knowledge"]),
    ("Redis unavailable", "redis-cache", "Redis primary became unavailable", "restart service", ["health", "logs", "history"]),
    ("Checkout deployment regression", "order-service", "Deployment regression in checkout validation", "rollback deployment", ["deployments", "logs", "history"]),
    ("Recommendation worker memory leak", "recommendation-service", "Unbounded feature cache memory leak", "restart service", ["health", "logs", "knowledge"]),
    ("Incorrect auth environment variable", "auth-service", "Incorrect JWT issuer environment variable", "rollback deployment", ["deployments", "logs", "knowledge"]),
    ("Shipping API rate limited", "order-service", "External shipping API rate limiting", "increase backoff", ["logs", "health", "knowledge"]),
    ("Notification disk capacity", "notification-worker", "Disk capacity exhausted by retry payloads", "clear cache", ["health", "logs", "knowledge"]),
    ("Model inference timeout", "ml-inference-api", "GPU inference queue saturation", "scale replica count", ["health", "logs", "history"]),
    ("Order schema mismatch", "order-service", "Database schema migration missing", "rollback deployment", ["logs", "deployments", "database"]),
    ("Gateway DNS resolution failure", "gateway-service", "Cluster DNS resolution failure", "restart service", ["logs", "health", "knowledge"]),
    ("Auth certificate expiration", "auth-service", "Upstream TLS certificate expired", "rotate certificate", ["logs", "health", "knowledge"]),
    ("Notification queue backlog", "notification-worker", "Consumer throughput below enqueue rate", "scale replica count", ["health", "logs", "history"]),
    ("Worker process crash loop", "notification-worker", "Malformed event caused worker crash loop", "restart service", ["logs", "health", "history"]),
    ("Catalog cache stampede", "redis-cache", "Cache expiry synchronization caused stampede", "increase cache jitter", ["health", "logs", "knowledge"]),
    ("Authentication service failure", "auth-service", "Identity database connection failure", "increase connection pool", ["database", "logs", "health"]),
    ("Payment readiness failure", "payment-api", "Readiness probe path changed", "rollback deployment", ["deployments", "health", "logs"]),
    ("Slow ledger query", "postgres-primary", "Missing index on ledger lookup", "add database index", ["database", "logs", "knowledge"]),
    ("Gateway CORS rejection", "gateway-service", "Misconfigured allowed origins", "rollback deployment", ["logs", "deployments", "knowledge"]),
    ("Dependency version regression", "recommendation-service", "Incompatible feature client version", "rollback deployment", ["deployments", "logs", "history"]),
]

DOCS = [
    ("Database Connection Pool Runbook", "Connection acquisition timeouts with a healthy database usually indicate pool exhaustion. Compare configuration changes, active connections, and pool utilization. Roll back unsafe pool reductions and verify recovery."),
    ("Payment API Architecture", "The payment API depends on PostgreSQL, Redis, and a fictional payment provider. Requests use a bounded SQLAlchemy connection pool and idempotency keys."),
    ("Deployment Rollback Procedure", "A rollback is a sensitive simulated action. Confirm the last known-good version, obtain human approval, execute the rollback, then verify error rate and latency."),
    ("Redis Troubleshooting Guide", "Check reachability, memory pressure, evictions, replication state, and synchronized key expiry. Prefer jittered TTLs to prevent cache stampedes."),
    ("Authentication Service Runbook", "Validate issuer and audience settings, certificate validity, database health, and recent configuration deployments."),
    ("API Timeout Troubleshooting", "Separate upstream latency from local saturation using traces, queue depth, dependency health, and timeout logs. Apply bounded retries with jitter."),
]

def incidents() -> list[dict]:
    now = datetime.now(timezone.utc)
    rows = []
    for i, (title, service, root, action, tools) in enumerate(CASES, 1):
        status = ["Investigating", "Resolved", "Awaiting Approval", "New"][i % 4]
        rows.append({
            "id": f"INC-{2026000+i}", "title": title, "description": f"Production symptoms detected for {service}. Automated triage requested.",
            "service": service, "environment": "production" if i % 4 else "staging", "severity": f"SEV-{1 + (i % 4)}",
            "status": status, "created_at": (now - timedelta(hours=i * 3)).isoformat(), "investigator": "AI Copilot",
            "ai_state": "Diagnosis complete" if status != "New" else "Queued", "root_cause": root, "recommended_action": action, "expected_tools": tools,
        })
    return rows

def logs_for(incident: dict) -> list[dict]:
    return [
        {"timestamp": incident["created_at"], "service": incident["service"], "level": "ERROR", "message": f"request failed: {incident['root_cause'].lower()}", "trace_id": f"tr-{incident['id'][-4:]}a"},
        {"timestamp": incident["created_at"], "service": incident["service"], "level": "ERROR", "message": "dependency request exceeded configured threshold", "trace_id": f"tr-{incident['id'][-4:]}b"},
    ]
