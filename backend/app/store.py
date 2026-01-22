from __future__ import annotations
import json
from pathlib import Path
from threading import Lock
from .data import DOCS, incidents

class Store:
    def __init__(self):
        self.lock = Lock(); self.reset()
    def reset(self):
        self.incidents = {x["id"]: x for x in incidents()}
        self.knowledge = [{"id": i+1, "title": x[0], "content": x[1], "chunks": 1} for i, x in enumerate(DOCS)]
        self.investigations = {}; self.approvals = {}; self.reports = {}; self.evaluations = []
    def persist_eval(self, result):
        path = Path(__file__).parents[2] / "evaluations/results/latest.json"
        path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(result, indent=2))

store = Store()
