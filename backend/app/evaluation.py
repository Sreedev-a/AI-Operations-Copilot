from __future__ import annotations
from datetime import datetime, timezone
from .agent import investigate

def run_evaluation(incidents):
    cases=[]
    for i in incidents:
        result=investigate(i); predicted=result["hypotheses"][0]["title"]; used=[x["tool"] for x in result["trace"] if x["tool"]]
        expected=set(i["expected_tools"]); actual=set(used)
        cases.append({"incident_id":i["id"], "root_cause_correct":predicted==i["root_cause"], "tool_selection":len(expected&actual)/len(expected|actual), "evidence_coverage":len(result["evidence"])/len(expected), "unnecessary_calls":len(actual-expected), "recommendation_correct":result["recommendation"]["action"]==i["recommended_action"], "latency_ms":result["latency_ms"]})
    n=len(cases)
    return {"id":f"eval-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}", "created_at":datetime.now(timezone.utc).isoformat(), "total_cases":n,
      "metrics":{"root_cause_accuracy":sum(x["root_cause_correct"] for x in cases)/n,"tool_selection_accuracy":sum(x["tool_selection"] for x in cases)/n,"evidence_coverage":sum(x["evidence_coverage"] for x in cases)/n,"average_tool_calls":sum(len(i["expected_tools"]) for i in incidents)/n,"recommendation_accuracy":sum(x["recommendation_correct"] for x in cases)/n,"average_latency_ms":sum(x["latency_ms"] for x in cases)/n}, "cases":cases}
