import io, csv, json, os, threading, uuid, zipfile, hashlib
from pathlib import Path
from datetime import datetime, timezone
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal
from .agents import SupervisorAgent, generate, NAMES
from .planning import NetworkPlan, network_plan
from .datasets import optimize_market
from .hardware_latency import summarize_hardware_samples
from . import store
from . import optimize_arena
from aws.adapter import embed_run_in_aws, aws_config_from_env
ROOT=Path(__file__).resolve().parents[1]
DATA=Path(os.getenv('TRADEOPS_DATA',str(ROOT/'data')))
DATA.mkdir(parents=True,exist_ok=True)
lock=threading.RLock()
app=FastAPI(title='TradeOps Agent API',version='1.0.0')
app.add_middleware(TrustedHostMiddleware, allowed_hosts=['127.0.0.1','localhost','testserver'])

def attach_aws(run, data, name, folder):
    """Embed the AWS S3→EventBridge→Glue→Athena contract into every agent run."""
    parquet=folder/'optimized'/'logs.parquet'
    report={k:run[k] for k in run if k not in {'events'}}
    try:
        aws=embed_run_in_aws(run['id'], data, name, parquet if parquet.exists() else None, report, DATA)
    except Exception as e:
        aws=dict(embedded=False, cloud='aws', live=False, error=str(e), note='AWS embedding failed; local agent results are still valid.')
    run['aws']=aws
    mode=aws.get('mode','unavailable')
    run.setdefault('events',[]).append(dict(
        agent='Supervisor',
        message=f"AWS workflow embedded ({mode}): staged raw+Parquet on the S3 contract and emitted EventBridge/Athena handles." if aws.get('embedded') else f"AWS embedding skipped: {aws.get('error','unknown error')}",
        time=datetime.now(timezone.utc).isoformat(),
    ))
    return run

def save(run):
    store.save_run(DATA, run)

def get(id):
    run=store.get_run(DATA, id)
    if not run:raise HTTPException(404,'Run not found')
    return run

@app.middleware('http')
async def local_guard(request:Request,call_next):
    origin=request.headers.get('origin')
    if request.method not in ['GET','HEAD','OPTIONS'] and origin and origin not in ['http://127.0.0.1:8000','http://localhost:8000']:
        return Response('Cross-origin writes forbidden',status_code=403)
    desk=request.headers.get('x-tradeops-desk') or request.query_params.get('desk')
    try:
        store.set_desk(desk)
    except ValueError as e:
        return Response(str(e),status_code=400)
    response=await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['X-TradeOps-Desk']=store.get_desk()
    return response

class Demo(BaseModel):
    scenario:Literal['normal','duplicates','latency_spike']='latency_spike'
    format:Literal['csv','json']='json'

class Decision(BaseModel):
    action:Literal['approve','reject']
    confirm:bool=False

class HardwareLatencyBatch(BaseModel):
    samples:list[dict]
    run_id:str|None=None
    execution_latency_ms:list[float]|None=None
    workstation:str|None=None

def process(data,name,scenario='uploaded'):
    id=uuid.uuid4().hex
    folder=DATA/id;folder.mkdir()
    try:result=SupervisorAgent().run(data,name,folder/'optimized')
    except ValueError as e:
        import shutil;shutil.rmtree(folder,ignore_errors=True);raise HTTPException(422,str(e))
    (folder/('raw'+Path(name).suffix.lower())).write_bytes(data)
    run=dict(id=id,name=Path(name).name,scenario=scenario,created=datetime.now(timezone.utc).isoformat(),approval='pending' if result['storage']['eligible'] else 'not_required',**result)
    attach_aws(run, data, name, folder)
    save(run);return run

def process_market(data,name,source,symbol='',timezone_name='Etc/GMT+5'):
    id=uuid.uuid4().hex
    folder=DATA/id;folder.mkdir()
    try:result=optimize_market(data,name,source,folder/'optimized',symbol,timezone_name)
    except ValueError as e:
        import shutil;shutil.rmtree(folder,ignore_errors=True);raise HTTPException(422,str(e))
    (folder/'raw.source').write_bytes(data)
    run=dict(id=id,name=Path(name).name,scenario=source,created=datetime.now(timezone.utc).isoformat(),**result)
    attach_aws(run, data, name, folder)
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
def health():
    cfg=aws_config_from_env()
    desks=store.list_desks(DATA)
    return dict(
        status='ok',
        mode='aws_live' if cfg['live'] else 'aws_embedded_local',
        cloud='aws',
        desk=store.get_desk(),
        desks=len(desks),
        agents=NAMES,
        aws=dict(live=cfg['live'], region=cfg['region'], raw_bucket=cfg['raw_bucket'], optimized_bucket=cfg['optimized_bucket'], glue_job=cfg['glue_job'], athena_workgroup=cfg['athena_workgroup'], event_bus=cfg['event_bus']),
    )

@app.get('/api/desks')
def desks():
    """List local desk databases (one SQLite file per desk)."""
    items=[]
    for d in store.list_desks(DATA):
        path=Path(d['path'])
        count=0
        if path.exists():
            with store.connect(path) as conn:
                count=conn.execute('SELECT count(*) FROM runs').fetchone()[0]
        items.append(dict(id=d['id'], path=d['path'], legacy=d['legacy'], runs=count, active=d['id']==store.get_desk()))
    return dict(desk=store.get_desk(), desks=items)

class DeskCreate(BaseModel):
    id:str=Field(min_length=1,max_length=64)

@app.post('/api/desks')
def create_desk(body:DeskCreate):
    try:
        desk=store.normalize_desk(body.id)
    except ValueError as e:
        raise HTTPException(400,str(e))
    if desk=='default':
        path=store.db_path(DATA,'default')
    else:
        path=store.db_path(DATA,desk)
    store.connect(path).close()
    return dict(id=desk, path=str(path), created=True)

@app.get('/api/aws/status')
def aws_status():
    cfg=aws_config_from_env()
    mirror=DATA/'aws-mirror'
    return dict(
        cloud='aws',
        live=cfg['live'],
        embedded=True,
        region=cfg['region'],
        buckets=dict(raw=cfg['raw_bucket'], optimized=cfg['optimized_bucket']),
        glue_job=cfg['glue_job'],
        athena_workgroup=cfg['athena_workgroup'],
        event_bus=cfg['event_bus'],
        local_mirror=str(mirror) if mirror.exists() else None,
        activation='Set TRADEOPS_AWS_LIVE=1 with TRADEOPS_AWS_RAW_BUCKET, TRADEOPS_AWS_OPTIMIZED_BUCKET, TRADEOPS_AWS_GLUE_JOB to switch the same agent workflow onto live AWS APIs.',
        services=['s3','events','glue','athena'],
    )

@app.post('/api/aws/events')
def aws_ingest_event(event: dict):
    """Plan an EventBridge S3 Object Created event through the same AWS adapter contract."""
    from aws.adapter import get_aws_backend
    backend, cfg = get_aws_backend(DATA)
    try:
        plan=backend.plan_event(event)
    except (KeyError, ValueError) as e:
        raise HTTPException(422, str(e))
    return dict(status='planned', live=cfg['live'], plan=plan, next_step='Persist and claim the idempotency key, then submit the Glue transform. Agent analysis remains unchanged.')

@app.get('/api/runs')
def runs():
    """Lean summaries for the workspace list/history. Full payloads via /api/runs/{id}/report."""
    return store.list_run_summaries(DATA)

@app.get('/api/optimize/arena')
def optimize_arena_latest():
    """Last measured before/after optimization arena result (HackCMU pitch view)."""
    latest = optimize_arena.load_latest(DATA)
    if not latest:
        raise HTTPException(404, 'No arena measurement yet. POST /api/optimize/arena to run one.')
    return latest

@app.post('/api/optimize/arena')
def optimize_arena_run():
    """Re-measure hot path, list shape, and SQLite contention on this machine."""
    result = optimize_arena.run_arena()
    optimize_arena.persist_latest(DATA, result)
    return result

@app.post('/api/hardware-latency/ack')
def hardware_ack():
    """Tiny ack endpoint used by the desk probe to measure click→platform RTT."""
    return dict(ok=True, server_time=datetime.now(timezone.utc).isoformat())

@app.post('/api/hardware-latency')
def hardware_latency(body:HardwareLatencyBatch):
    """Opt-in workstation probe: refresh rate + input→frame / click→ack timing (no keylogging)."""
    execution=body.execution_latency_ms
    linked=None
    if body.run_id:
        linked=get(body.run_id)
        if execution is None:
            sample=(linked.get('analysis') or {}).get('sample') or []
            execution=[float(s['latency_ms']) for s in sample if isinstance(s,dict) and 'latency_ms' in s]
            if not execution:
                p95=(linked.get('analysis') or {}).get('p95_ms')
                if p95 is not None:
                    execution=[float(p95)]
                else:
                    thr=(linked.get('analysis') or {}).get('threshold_ms')
                    if thr is not None:
                        execution=[float(thr)]
    try:
        summary=summarize_hardware_samples(body.samples, execution)
    except ValueError as e:
        raise HTTPException(422,str(e))
    if body.workstation:
        summary['workstation']=str(body.workstation)[:80]
    probe_id=uuid.uuid4().hex
    probe=dict(
        id=probe_id,
        kind='hardware_latency',
        name='desk-probe',
        scenario='hardware_latency',
        created=datetime.now(timezone.utc).isoformat(),
        approval='not_required',
        hardware=summary,
        linked_run_id=body.run_id,
        events=[dict(agent='Supervisor', message='Hardware desk probe ingested (refresh rate + input timing; no key characters stored).', time=datetime.now(timezone.utc).isoformat())],
        before_bytes=0,
        after_bytes=0,
        reduction_pct=0,
    )
    save(probe)
    if linked is not None:
        linked['hardware_latency']=summary
        linked.setdefault('events',[]).append(dict(
            agent='Supervisor',
            message=f"Linked desk hardware probe {probe_id}: refresh≈{summary.get('refresh_hz')} Hz; key→frame p50={((summary.get('key_to_frame_ms') or {}).get('p50'))} ms.",
            time=datetime.now(timezone.utc).isoformat(),
        ))
        save(linked)
    return dict(probe_id=probe_id, linked_run_id=body.run_id, hardware=summary)

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
