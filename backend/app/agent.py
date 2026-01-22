from __future__ import annotations
import time
from datetime import datetime, timezone
from .tools import execute

def investigate(incident: dict):
    started = time.perf_counter(); trace=[]; evidence=[]
    def step(kind, summary, tool=None, detail=None):
        trace.append({"id": len(trace)+1, "timestamp": datetime.now(timezone.utc).isoformat(), "step": kind, "summary": summary, "tool": tool, "status": "success", "latency_ms": detail.get("latency_ms", 0) if detail else 0, "detail": detail})
    step("Incident intake", f"Classified {incident['severity']} incident affecting {incident['service']}")
    step("Plan investigation", f"Selected {len(incident['expected_tools'])} diagnostic tools")
    for tool in incident["expected_tools"]:
        result=execute(tool, incident); step("Tool execution", f"Executed {tool} diagnostics", tool, result)
        evidence.append({"source": tool, "summary": evidence_summary(tool, incident), "supports": True})
    alternatives = [
        {"rank": 1, "title": incident["root_cause"], "confidence": 91, "level": "High", "supporting_evidence": [x["summary"] for x in evidence], "contradicting_evidence": ["No broad infrastructure outage detected"]},
        {"rank": 2, "title": "Upstream dependency degradation", "confidence": 24, "level": "Low", "supporting_evidence": ["User-visible latency increased"], "contradicting_evidence": ["Dependency health remained nominal"]},
        {"rank": 3, "title": "Transient network failure", "confidence": 11, "level": "Low", "supporting_evidence": ["Requests exceeded thresholds"], "contradicting_evidence": ["Failures align with deterministic service evidence"]},
    ]
    step("Hypothesis update", f"Ranked primary cause: {incident['root_cause']}")
    step("Recommendation", f"Proposed simulated action: {incident['recommended_action']}")
    report = report_for(incident, evidence, trace)
    return {"incident_id": incident["id"], "state": "awaiting_approval", "trace": trace, "evidence": evidence, "hypotheses": alternatives,
            "recommendation": {"action": incident["recommended_action"], "reason": f"Addresses the highest-ranked cause: {incident['root_cause']}", "service": incident["service"], "risk": "Medium", "expected_outcome": "Restore normal error rate and latency", "simulated": True},
            "report": report, "usage": {"mode":"demo", "message":"Demo mode — no external model usage"}, "latency_ms": round((time.perf_counter()-started)*1000,2)}

def evidence_summary(tool, incident):
    return {"logs": f"Logs contain errors consistent with {incident['root_cause'].lower()}", "health": f"{incident['service']} is degraded while core dependencies respond", "deployments": "A recent v2.4.1 deployment aligns with symptom onset", "knowledge": "A runbook describes the observed failure signature", "history": "A related historical incident has a matching resolution", "database": "Read-only database diagnostics isolated connection and query behavior"}[tool]

def report_for(i, evidence, trace):
    timeline="\n".join(f"- {x['timestamp']}: {x['summary']}" for x in trace)
    ev="\n".join(f"- {x['summary']}" for x in evidence)
    return f"# Incident Report — {i['id']}\n\n## Incident Summary\n{i['title']} affected `{i['service']}` in {i['environment']}.\n\n## Impact\nElevated failures and latency for dependent requests.\n\n## Timeline\n{timeline}\n\n## Root Cause\n{i['root_cause']}\n\n## Contributing Factors\nRecent operational change and insufficient early-warning thresholds.\n\n## Evidence\n{ev}\n\n## Resolution\nProposed simulated action: {i['recommended_action']} (human approval required).\n\n## Preventive Actions\n- Add a regression guardrail\n- Alert earlier on saturation\n- Exercise the runbook quarterly\n\n## Agent Investigation Summary\nDeterministic demo agent collected {len(evidence)} evidence items using allowlisted, read-only tools."
