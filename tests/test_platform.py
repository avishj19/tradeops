import csv, io, json
import pytest
import pyarrow.parquet as pq
from fastapi.testclient import TestClient
from backend.agents import LogAnalysisAgent, SupervisorAgent, CostAgent, generate
from backend import app as module

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(module,'DATA',tmp_path)
    with TestClient(module.app) as c:yield c

@pytest.mark.parametrize('fmt',['json','csv'])
def test_formats_and_roundtrip(tmp_path,fmt):
    rows=generate('duplicates',100)
    if fmt=='json': data=json.dumps(rows).encode()
    else:
        s=io.StringIO();w=csv.DictWriter(s,fieldnames=rows[0]);w.writeheader();w.writerows(rows);data=s.getvalue().encode()
    r=SupervisorAgent().run(data,'logs.'+fmt,tmp_path)
    assert r['analysis']['duplicates']==15
    assert pq.read_table(tmp_path/'logs.parquet').num_rows==100
    assert len(r['events'])==7

@pytest.mark.parametrize('rows',[[],{},[{'foo':1}],[{'timestamp':'bad','event_id':'1','symbol':'X','latency_ms':1,'status':'OK'}]])
def test_invalid_input(rows):
    with pytest.raises(ValueError):LogAnalysisAgent().run(json.dumps(rows).encode(),'x.json')

@pytest.mark.parametrize('latency',['NaN','inf',-1])
def test_bad_latency(latency):
    rows=generate(count=1);rows[0]['latency_ms']=latency
    with pytest.raises(ValueError):LogAnalysisAgent().run(json.dumps(rows).encode(),'x.json')

def test_same_id_different_payload_is_preserved():
    a=generate(count=1)[0];b={**a,'price':999}
    rows,report=LogAnalysisAgent().run(json.dumps([a,b,a]).encode(),'x.json')
    assert report['duplicates']==1 and len(rows)==2

def test_synthetic_incident_detected():
    _,r=LogAnalysisAgent().run(json.dumps(generate('latency_spike',1000)).encode(),'x.json')
    assert r['anomalies']==199

def test_cost_minimum_and_retained_raw():
    r=CostAgent().run(1_000_000,100_000)
    assert r['savings_monthly']<0 and r['before_monthly']>=.05

def test_end_to_end_approval_and_download(client):
    r=client.post('/api/demo',json={'scenario':'duplicates','format':'csv'})
    assert r.status_code==200
    run=r.json();id=run['id'];folder=module.DATA/id
    assert run['approval']=='pending' and list(folder.glob('raw.*'))
    assert client.post(f'/api/runs/{id}/decision',json={'action':'approve'}).status_code==422
    assert list(folder.glob('raw.*'))
    assert client.post(f'/api/runs/{id}/decision',json={'action':'approve','confirm':True}).json()['approval']=='archived_locally'
    assert list((folder/'archive').glob('raw.*'))
    assert client.post(f'/api/runs/{id}/decision',json={'action':'approve','confirm':True}).status_code==409
    assert client.get(f'/api/runs/{id}/download').content[:4]==b'PAR1'
    assert client.get('/api/runs').json()[0]['approval']=='archived_locally'

def test_reject_preserves_original(client):
    run=client.post('/api/demo',json={}).json();id=run['id']
    assert client.post(f'/api/runs/{id}/decision',json={'action':'reject'}).json()['approval']=='rejected'
    assert list((module.DATA/id).glob('raw.*'))

def test_upload_validation_and_origins(client):
    assert client.post('/api/upload',files={'file':('bad.txt',b'hello')}).status_code==422
    assert client.post('/api/upload',files={'file':('bad.json',b'no')}).status_code==422
    assert client.post('/api/demo',headers={'Origin':'https://evil.example'},json={}).status_code==403
    assert client.get('/api/runs/missing/download').status_code==404

def test_upload_good_file(client):
    data=json.dumps(generate(count=10)).encode()
    r=client.post('/api/upload',files={'file':('upload.json',data)})
    assert r.status_code==200 and r.json()['analysis']['unique_rows']==10

def test_aws_event_boundary():
    from aws.adapter import AWSAdapter
    class Session:
        def client(self,name):return object()
    a=AWSAdapter('raw-bucket','optimized','job','workgroup',Session())
    e={'detail':{'bucket':{'name':'raw-bucket'},'object':{'key':'raw/logs.json','version-id':'v1'}}}
    assert a.plan_event(e)==a.plan_event(e)
    e['detail']['bucket']['name']='other'
    with pytest.raises(ValueError):a.plan_event(e)
    with pytest.raises(NotImplementedError):a.archive()

@pytest.mark.parametrize('change',[{'extra':'late column'},{'symbol':None},{'symbol':{'nested':1}},{'event_id':''}])
def test_malformed_schema_not_silently_lost(change):
    a=generate(count=1)[0]
    with pytest.raises(ValueError):LogAnalysisAgent().run(json.dumps([a,{**a,**change}]).encode(),'x.json')

def test_host_validation(client):
    assert client.get('/api/health',headers={'Host':'attacker.example'}).status_code==400

def test_network_budget_and_validation(client):
    p=client.post('/api/network-plan',json={}).json()
    assert p['endpoint_fixed']==29.2 and p['estimated_total']==49.3
    assert p['within_budget'] and not p['bedrock_enabled']
    p=client.post('/api/network-plan',json={'monthly_budget':10}).json()
    assert not p['within_budget']
    assert client.post('/api/network-plan',json={'availability_zones':0}).status_code==422

def test_incident_summaries_exclude_sensitive_records():
    from backend.planning import incidents
    r=generate('latency_spike',100)
    r[99]['password']='SECRET';r[99]['account_id']='PRIVATE'
    result=incidents(r,100)
    assert sum(i['count'] for i in result)==19
    assert 'SECRET' not in json.dumps(result) and 'PRIVATE' not in json.dumps(result)
    assert all(i['notification']=='local_only' for i in result)
