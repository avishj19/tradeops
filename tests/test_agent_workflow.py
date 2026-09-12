import json
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from backend.agent_workflow import run_workflow

@pytest.fixture
def source(tmp_path):
    path = tmp_path/'input.parquet'
    pq.write_table(pa.table({'symbol':['A','A','B',None]*100, 'value':[1,1,2,None]*100}), path, compression=None)
    return path

def test_local_preserves_source_and_persists(source,tmp_path):
    before=source.read_bytes()
    result=run_workflow(source,tmp_path/'history','run')
    assert result['status']=='completed'
    assert len(result['candidates'])==3
    assert all(c['verified'] for c in result['candidates'])
    assert source.read_bytes()==before
    assert result['recommendation']['deployed'] is False
    assert json.loads((tmp_path/'history'/f"{result['id']}.json").read_text())==result

def test_adaptive_model_reads_tool_results(source,tmp_path):
    steps=[]
    def model(items):
        outputs=[i for i in items if i.get('type')=='function_call_output']
        steps.append(len(outputs))
        if not outputs: name,args='inspect_dataset',{}
        elif len(outputs)==1:
            assert json.loads(outputs[-1]['output'])['rows']==400
            name,args='test_compression',{'codec':'zstd'}
        else:
            assert json.loads(outputs[-1]['output'])['verified']
            return {'output':[{'type':'message','content':[{'type':'output_text','text':'Measured one candidate; stopping.'}]}]}
        return {'output':[{'type':'function_call','name':name,'arguments':json.dumps(args),'call_id':str(len(outputs))}]}
    result=run_workflow(source,tmp_path/'history','run','live',call_model=model)
    assert result['status']=='completed'
    assert steps==[0,1,2]
    assert [c['codec'] for c in result['candidates']]==['existing','zstd']

def test_unknown_tool_cannot_execute_and_budget_stops(source,tmp_path):
    def model(items):
        return {'output':[{'type':'function_call','name':'delete_file','arguments':'{}','call_id':str(len(items))}]}
    result=run_workflow(source,tmp_path/'history','run','live',call_model=model)
    assert result['status']=='failed'
    assert source.exists()
    assert len(result['candidates'])==1
    assert any(t['evidence'].get('error') for t in result['trace'] if isinstance(t['evidence'],dict))

def test_early_model_exit_is_not_success(source,tmp_path):
    result=run_workflow(source,tmp_path/'history','run','live',call_model=lambda _: {'output':[]})
    assert result['status']=='failed'
    assert result['recommendation'] is None

def test_missing_credentials_does_not_fall_back(source,tmp_path,monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    with pytest.raises(ValueError,match='OPENAI_API_KEY'):
        run_workflow(source,tmp_path/'history','run','live')

def test_corrupted_candidate_never_recommended(source,tmp_path,monkeypatch):
    original=pq.write_table
    def corrupt(table,path,**kwargs):
        original(table.slice(1),path,**kwargs)
    monkeypatch.setattr(pq,'write_table',corrupt)
    result=run_workflow(source,tmp_path/'history','run')
    assert result['status']=='completed'
    assert all(not c['verified'] for c in result['candidates'][1:])
    assert result['recommendation']['codec']=='existing'

def test_api_consent_and_history(source,tmp_path,monkeypatch):
    from backend import app as module
    from fastapi.testclient import TestClient
    ident='a'*32
    target=tmp_path/ident/'optimized'
    target.mkdir(parents=True)
    (target/'logs.parquet').write_bytes(source.read_bytes())
    monkeypatch.setattr(module,'DATA',tmp_path)
    monkeypatch.setattr(module,'get',lambda _: {'id':ident})
    client=TestClient(module.app)
    assert client.post('/api/ai-workflows',json={'run_id':ident,'mode':'live'}).status_code==422
    response=client.post('/api/ai-workflows',json={'run_id':ident})
    assert response.status_code==200
    assert response.json()['status']=='completed'
    assert client.get('/api/ai-workflows').json()[0]['id']==response.json()['id']
    assert client.get('/api/ai-workflows',headers={'x-tradeops-desk':'other'}).json()==[]
