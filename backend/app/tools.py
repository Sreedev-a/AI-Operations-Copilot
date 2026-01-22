from __future__ import annotations
import re, time
from .data import CASES, logs_for
from .store import store

ALLOWED_TOOLS = {"logs", "health", "deployments", "knowledge", "history", "database"}

def _words(text): return set(re.findall(r"[a-z0-9]+", text.lower()))
def retrieve(query: str, limit: int = 3):
    q = _words(query)
    ranked = sorted(store.knowledge, key=lambda d: len(q & _words(d["title"]+" "+d["content"])), reverse=True)
    return [{**d, "score": round(len(q & _words(d["title"]+" "+d["content"]))/max(len(q),1), 3)} for d in ranked[:limit]]

def execute(name: str, incident: dict, params: dict | None = None):
    if name not in ALLOWED_TOOLS: raise ValueError("Tool is not allowlisted")
    started = time.perf_counter(); service = incident["service"]
    if name == "logs": output = {"events": logs_for(incident), "matches": 2}
    elif name == "health": output = {"service": service, "state": "degraded", "uptime": 99.91, "error_rate": 18.4, "p95_ms": 1840, "dependencies": {"database": "healthy", "redis": "healthy"}}
    elif name == "deployments": output = {"deployments": [{"version": "v2.4.1", "commit": "8bd31fa", "deployed_at": incident["created_at"], "status": "completed"}, {"version": "v2.4.0", "commit": "12a42cd", "deployed_at": "2026-08-17T08:10:00Z", "status": "superseded"}]}
    elif name == "knowledge": output = {"documents": retrieve(incident["root_cause"])}
    elif name == "history": output = {"incidents": [{"title": title, "root_cause": root, "resolution": action, "similarity": .91} for title, svc, root, action, _ in CASES if svc == service][:3]}
    else: output = {"available": True, "connections": 92, "max_connections": 100, "pool_usage": 0.96, "slow_queries": 1, "note": "Read-only simulated diagnostics"}
    return {"tool": name, "input": {"service": service, **(params or {})}, "output": output, "status": "success", "latency_ms": round((time.perf_counter()-started)*1000, 2)}
