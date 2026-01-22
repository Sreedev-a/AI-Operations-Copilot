from app.evaluation import run_evaluation
from app.store import store
r=run_evaluation(list(store.incidents.values()))
store.persist_eval(r)
print(r["metrics"])
