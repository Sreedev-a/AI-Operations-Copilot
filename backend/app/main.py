from __future__ import annotations
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from .agent import investigate
from .evaluation import run_evaluation
from .store import store
from .tools import retrieve

app=FastAPI(title="AI Operations Copilot", version="1.0.0", description="Safe agentic incident investigation API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class IncidentCreate(BaseModel):
    title:str=Field(min_length=5,max_length=160); description:str=Field(min_length=10,max_length=4000); service:str; environment:str="production"; severity:str="SEV-2"
class Approval(BaseModel): decision:str; actor:str="Demo operator"
class DocumentCreate(BaseModel): title:str=Field(min_length=3,max_length=160); content:str=Field(min_length=20,max_length=50000)

@app.get("/health")
def health(): return {"status":"ok","mode":"demo","version":"1.0.0"}
@app.get("/api/dashboard")
def dashboard():
    rows=list(store.incidents.values()); resolved=sum(x["status"]=="Resolved" for x in rows)
    return {"active":len(rows)-resolved,"critical":sum(x["severity"]=="SEV-1" for x in rows),"resolved":resolved,"average_investigation_minutes":4.2,"ai_success":1.0,"recent":rows[:6],"services":sorted({x["service"] for x in rows}),"severity_distribution":{s:sum(x["severity"]==s for x in rows) for s in ["SEV-1","SEV-2","SEV-3","SEV-4"]}}
@app.get("/api/incidents")
def list_incidents(q:str="",severity:str="",status:str=""):
    rows=list(store.incidents.values())
    if q: rows=[x for x in rows if q.lower() in (x["title"]+x["service"]+x["id"]).lower()]
    if severity: rows=[x for x in rows if x["severity"]==severity]
    if status: rows=[x for x in rows if x["status"]==status]
    return rows
@app.post("/api/incidents",status_code=201)
def create_incident(body:IncidentCreate):
    ident=f"INC-{2026000+len(store.incidents)+1}"; root="Unclassified operational failure"
    row={"id":ident,**body.model_dump(),"status":"New","created_at":datetime.now(timezone.utc).isoformat(),"investigator":"AI Copilot","ai_state":"Queued","root_cause":root,"recommended_action":"restart service","expected_tools":["logs","health","knowledge"]}
    store.incidents[ident]=row; return row
def get_incident(ident):
    if ident not in store.incidents: raise HTTPException(404,"Incident not found")
    return store.incidents[ident]
@app.get("/api/incidents/{ident}")
def incident_detail(ident:str):
    row=get_incident(ident); return {**row,"investigation":store.investigations.get(ident),"approval":store.approvals.get(ident)}
@app.post("/api/incidents/{ident}/investigate")
def start_investigation(ident:str):
    row=get_incident(ident); result=investigate(row); store.investigations[ident]=result; store.reports[ident]=result["report"]; row["status"]="Awaiting Approval"; row["ai_state"]="Diagnosis complete"; return result
@app.get("/api/incidents/{ident}/trace")
def trace(ident:str): return store.investigations.get(ident,{}).get("trace",[])
@app.post("/api/incidents/{ident}/approval")
def approval(ident:str,body:Approval):
    row=get_incident(ident)
    if body.decision not in {"approve","reject"}: raise HTTPException(422,"Decision must be approve or reject")
    record={"decision":body.decision,"actor":body.actor,"decided_at":datetime.now(timezone.utc).isoformat(),"simulated":True,"verification":"Service health returned to nominal" if body.decision=="approve" else "Action was not executed"}
    store.approvals[ident]=record; row["status"]="Resolved" if body.decision=="approve" else "Investigating"; return record
@app.get("/api/incidents/{ident}/report",response_class=PlainTextResponse)
def report(ident:str):
    get_incident(ident)
    if ident not in store.reports: raise HTTPException(404,"Run an investigation first")
    return store.reports[ident]
@app.get("/api/knowledge")
def knowledge(q:str=""): return retrieve(q) if q else store.knowledge
@app.post("/api/knowledge",status_code=201)
def add_document(body:DocumentCreate):
    doc={"id":len(store.knowledge)+1,"title":body.title,"content":body.content,"chunks":max(1,len(body.content)//800)}; store.knowledge.append(doc); return doc
@app.get("/api/evaluations")
def evaluations(): return store.evaluations
@app.post("/api/evaluations/run")
def evaluate():
    result=run_evaluation(list(store.incidents.values())[:20]); store.evaluations.insert(0,result); store.persist_eval(result); return result
@app.post("/api/demo/reset")
def reset(): store.reset(); return {"status":"reset","incidents":len(store.incidents)}

