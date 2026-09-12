import io,json
from backend.connectors import Runner

class Session:
    def __init__(self,client):self.value=client
    def client(self,*args,**kwargs):return self.value

class S3:
    def __init__(self):self.gets=[];self.tag='v1'
    def get_paginator(self,name):assert name=='list_objects_v2';return self
    def paginate(self,**kwargs):yield {'Contents':[{'Key':'logs/a.jsonl','Size':8,'ETag':self.tag}]}
    def get_object(self,**kwargs):
        self.gets.append(kwargs)
        assert kwargs['IfMatch']==self.tag and 'RequestPayer' not in kwargs
        return {'Body':io.BytesIO(b'{"a":1}\n')}

def test_folder_checkpoint_and_source_preserved(tmp_path):
    folder=tmp_path/'input';folder.mkdir();p=folder/'a.jsonl';p.write_text('{"a":1}\n')
    config={'type':'folder','path':str(folder),'format':'jsonl','settle_seconds':0}
    r=Runner(config,tmp_path/'output');assert r.run()==1;assert r.run()==0;r.close()
    r=Runner(config,tmp_path/'output');assert r.run()==0
    assert p.read_text()=='{"a":1}\n';r.close()

def test_s3_conditional_get_and_resume(tmp_path):
    fake=S3();r=Runner({'type':'s3','bucket':'example','prefix':'logs/','format':'jsonl'},tmp_path,Session(fake))
    assert r.run()==1 and r.run()==0 and len(fake.gets)==1
    fake.tag='v2';assert r.run()==1;r.close()

def test_cloudwatch_empty_page_and_replay(tmp_path):
    class Logs:
        def filter_log_events(self,**args):
            if 'nextToken' not in args:return {'events':[],'nextToken':'next'}
            return {'events':[{'eventId':'id','timestamp':1,'message':'hello','logStreamName':'test'}]}
    r=Runner({'type':'cloudwatch','log_group':'test','start_ms':0,'format':'json'},tmp_path,Session(Logs()))
    assert r.run()==1 and r.run()==0 and r.state('watermark')>0;r.close()

def test_failed_mapping_does_not_checkpoint(tmp_path):
    import pytest
    r=Runner({'type':'folder','format':'json','mapping':{'timestamp':'missing'}},tmp_path)
    with pytest.raises(ValueError):r.ingest(b'[{"a":1}]','source','test')
    assert r.db.execute('SELECT count(*) FROM runs').fetchone()[0]==0;r.close()

def test_blocked_source_does_not_list(tmp_path):
    import pytest
    r=Runner({'type':'s3','bucket':'hl-mainnet-node-data','prefix':'node_fills_by_block/','blocked_reason':'Authorization required'},tmp_path)
    with pytest.raises(ValueError,match='Authorization'):list(r.discover())
    r.close()

def test_market_connector_preserves_rows(tmp_path):
    r=Runner({'type':'folder','dataset':'binance_um'},tmp_path)
    assert r.ingest(b'1,2,3,6,1567900800000,true\n','id','BTCUSDT-trades-test.csv')
    run=json.loads(r.db.execute('SELECT payload FROM runs').fetchone()[0])
    assert run['kind']=='market_data' and run['rows']==1 and run['removed_rows']==0
    r.close()

def test_selected_key_cannot_escape_prefix(tmp_path):
    import pytest
    r=Runner({'type':'s3','bucket':'test','prefix':'allowed/','keys':['private/key']},tmp_path,Session(S3()))
    with pytest.raises(ValueError,match='outside'):list(r.discover())
    r.close()
