import io, csv, json, os, sqlite3, threading, uuid, zipfile, hashlib
from pathlib import Path
from datetime import datetime, timezone
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel
from typing import Literal
from .agents import SupervisorAgent, generate, NAMES
from .planning import NetworkPlan, network_plan
from .datasets import optimize_market
ROOT=Path(__file__).resolve().parents[1]
DATA=Path(os.getenv('TRADEOPS_DATA',str(ROOT/'data')))
DATA.mkdir(parents=True,exist_ok=True)
lock=threading.RLock()
app=FastAPI(title='TradeOps Agent API',version='1.0.0')
app.add_middleware(TrustedHostMiddleware, allowed_hosts=['127.0.0.1','localhost','testserver'])
_db_ready=set()

def db():
    path=DATA/'tradeops.db'
    c=sqlite3.connect(path)
    key=str(path)
    # Schema/PRAGMA once per DB path so tests with patched DATA stay correct.
    if key not in _db_ready:
        c.execute('CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, payload TEXT NOT NULL)')
        c.execute('PRAGMA journal_mode=WAL')
        c.execute('PRAGMA synchronous=NORMAL')
        _db_ready.add(key)
    return c

def save(run):
    with db() as c:c.execute('INSERT OR REPLACE INTO runs VALUES (?,?)',(run['id'],json.dumps(run)))

def get(id):
    with db() as c:r=c.execute('SELECT payload FROM runs WHERE id=?',(id,)).fetchone()
    if not r:raise HTTPException(404,'Run not found')
    return json.loads(r[0])

@app.middleware('http')
async def local_guard(request:Request,call_next):
    origin=request.headers.get('origin')
    if request.method not in ['GET','HEAD','OPTIONS'] and origin and origin not in ['http://127.0.0.1:8000','http://localhost:8000']:
        return Response('Cross-origin writes forbidden',status_code=403)
    response=await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    return response

class Demo(BaseModel):
    scenario:Literal['normal','duplicates','latency_spike']='latency_spike'
    format:Literal['csv','json']='json'

class Decision(BaseModel):
    action:Literal['approve','reject']
    confirm:bool=False

def process(data,name,scenario='uploaded'):
    id=uuid.uuid4().hex
    folder=DATA/id;folder.mkdir()
    try:result=SupervisorAgent().run(data,name,folder/'optimized')
    except ValueError as e:
        import shutil;shutil.rmtree(folder,ignore_errors=True);raise HTTPException(422,str(e))
    (folder/('raw'+Path(name).suffix.lower())).write_bytes(data)
    run=dict(id=id,name=Path(name).name,scenario=scenario,created=datetime.now(timezone.utc).isoformat(),approval='pending' if result['storage']['eligible'] else 'not_required',**result)
    save(run);return run

def process_market(data,name,source,symbol='',timezone_name='Etc/GMT+5'):
    id=uuid.uuid4().hex
    folder=DATA/id;folder.mkdir()
    try:result=optimize_market(data,name,source,folder/'optimized',symbol,timezone_name)
    except ValueError as e:
        import shutil;shutil.rmtree(folder,ignore_errors=True);raise HTTPException(422,str(e))
    (folder/'raw.source').write_bytes(data)
    run=dict(id=id,name=Path(name).name,scenario=source,created=datetime.now(timezone.utc).isoformat(),**result)
    save(run);return run

@app.post('/api/datasets/upload')
async def market_upload(file:UploadFile=File(...),source:str=Form(...),symbol:str=Form(''),timezone_name:str=Form('Etc/GMT+5')):
    data=await file.read(20*1024*1024+1)
    if len(data)>20*1024*1024:raise HTTPException(413,'Maximum upload is 20 MiB.')
    return process_market(data,file.filename or 'dataset',source,symbol,timezone_name)

@app.post('/api/datasets/binance-sample')
def binance_sample():
    path=ROOT/'samples/BTCUSDT-trades-2017-08-17.csv'
    if not path.exists():raise HTTPException(404,'Run scripts/fetch_binance_sample.py to fetch the verified sample first.')
    data=path.read_bytes()
    provenance=json.loads((ROOT/'samples/binance-provenance.json').read_text())
    if hashlib.sha256(data).hexdigest()!=provenance['raw_sha256']:
        raise HTTPException(409,'Cached sample integrity check failed; download it again.')
    return process_market(data,path.name,'binance','BTCUSDT')

@app.post('/api/network-plan')
def plan(body:NetworkPlan):return network_plan(body)

@app.get('/api/health')
def health():return dict(status='ok',mode='local',agents=NAMES)

@app.get('/api/runs')
def runs():
    with db() as c:return [json.loads(r[0]) for r in c.execute('SELECT payload FROM runs ORDER BY rowid DESC')]

@app.post('/api/demo')
def demo(body:Demo):
    rows=generate(body.scenario)
    if body.format=='json':data=json.dumps(rows).encode()
    else:
        s=io.StringIO();w=csv.DictWriter(s,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows);data=s.getvalue().encode()
    return process(data,'execution-logs.'+body.format,body.scenario)

@app.post('/api/upload')
async def upload(file:UploadFile=File(...)):
    name=file.filename or ''
    if Path(name).suffix.lower() not in ['.csv','.json']:raise HTTPException(422,'Choose a CSV or JSON file.')
    data=await file.read(20*1024*1024+1)
    if len(data)>20*1024*1024:raise HTTPException(413,'Maximum file size is 20 MiB.')
    return process(data,name)

@app.post('/api/runs/{id}/decision')
def decision(id:str,body:Decision):
    with lock:
        run=get(id)
        if run['approval']!='pending':raise HTTPException(409,'This run has no pending approval.')
        if body.action=='approve' and not body.confirm:raise HTTPException(422,'Explicit confirmation is required.')
        if body.action=='approve':
            # Demo archive is reversible relocation, never S3 lifecycle or permanent deletion.
            folder=DATA/id;archive=folder/'archive';archive.mkdir(exist_ok=True)
            for p in folder.glob('raw.*'):p.rename(archive/p.name)
        run['approval']='archived_locally' if body.action=='approve' else 'rejected'
        run['events'].append(dict(agent='Supervisor',message='Human decision: '+run['approval'],time=datetime.now(timezone.utc).isoformat()))
        save(run);return run

@app.get('/api/runs/{id}/download')
def download(id:str):
    get(id);return FileResponse(DATA/id/'optimized/logs.parquet',filename='optimized-logs.parquet')

@app.get('/api/runs/{id}/report')
def report(id:str):return get(id)

@app.get('/')
def home():return FileResponse(ROOT/'frontend/index.html')
app.mount('/static',StaticFiles(directory=ROOT/'frontend'),name='static')


@app.get('/api/experiments/latest')
def latest_experiment():
    path=ROOT/'benchmarks'/'latest.json'
    if not path.exists():raise HTTPException(404,'Run python -m scripts.benchmark_lab to create measurements.')
    return FileResponse(path,media_type='application/json')

from .experiment_costs import CostScenario, estimate_costs

@app.post('/api/experiments/cost')
def experiment_cost(body: CostScenario):
    path=ROOT/'benchmarks'/'latest.json'
    if not path.exists():raise HTTPException(404,'Run the benchmark first.')
    return estimate_costs(json.loads(path.read_text()),body)

from .layout_policy import recommend, check_measurement_scope
from pydantic import Field, ConfigDict

class LayoutRecommendation(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False, extra='forbid')
    query_count: int = Field(default=100, ge=0, le=100000000, strict=True)
    storage_budget_bytes: int = Field(default=200*1024*1024, ge=0, strict=True)
    workload_weights: dict[str, float] = Field(default_factory=lambda: {'selective': 1.0})
    minimum_savings_fraction: float = Field(default=.1, ge=0, lt=1)
    search_overhead_s: float = Field(default=0, ge=0)
    target_rows: int | None = Field(default=None, gt=0, strict=True)

@app.post('/api/experiments/recommend')
def layout_recommendation(body: LayoutRecommendation):
    path=ROOT/'benchmarks'/'latest.json'
    if not path.exists():raise HTTPException(404,'Run the benchmark first.')
    report=json.loads(path.read_text())
    scope_check=check_measurement_scope(report['rows'],body.target_rows) if body.target_rows is not None else None
    if scope_check and scope_check['remeasurement_required']:
        raise HTTPException(409,dict(reason='remeasurement_required',**scope_check))
    candidates=[dict(c, samples=report['measurements']['calibration'][c['layout']]) for c in report['candidates']]
    try:
        result=recommend(candidates, body.workload_weights, body.query_count, body.storage_budget_bytes,
                         minimum_savings_fraction=body.minimum_savings_fraction, search_overhead_s=body.search_overhead_s)
    except ValueError as exc:
        raise HTTPException(422,str(exc)) from exc
    return dict(**result, measured_at=report['created'], data_rows=report['rows'], scope_check=scope_check,
                scope='Existing benchmark dataset only. No cloud changes or automatic execution.')
