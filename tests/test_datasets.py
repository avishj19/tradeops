import gzip, io, json, zipfile
from pathlib import Path
import pyarrow.parquet as pq
import pytest
from backend.datasets import parse_market, optimize_market, unpack
from backend import app as module
from fastapi.testclient import TestClient

# Invented schema fixtures, not vendor market observations.
ALGO=b'Date,Timestamp,EventType,Ticker,Price,Quantity,Exchange,Conditions\n20260701,09:30:00.123456789,TRADE,TEST,1.2345,2,NASDAQ,00000000\n'
HYPER=json.dumps([{'coin':'TEST','px':'1.123456789012345678','sz':'2','time':1704067200000,'tid':123}]).encode()
BINANCE=b'1,1.23000000,2,2.46,1735689600010866,true,true\n'

@pytest.mark.parametrize('source,data,symbol',[('algoseek',ALGO,''),('hyperliquid',HYPER,''),('binance',BINANCE,'BTCUSDT')])
def test_all_adapters_roundtrip(tmp_path,source,data,symbol):
    r=optimize_market(data,'file',source,tmp_path,symbol)
    assert r['rows']==1 and r['removed_rows']==0 and r['kind']=='market_data'
    table=pq.read_table(tmp_path/'logs.parquet')
    assert 'latency_ms' not in table.column_names
    assert r['incidents']==[]

def test_algoseek_nanoseconds_and_timezone():
    a=parse_market(ALGO,'file','algoseek')[0]
    b=parse_market(ALGO,'file','algoseek',timezone_name='America/New_York')[0]
    assert a['timestamp']=='2026-07-01T14:30:00.123456789+00:00'
    assert b['timestamp']=='2026-07-01T13:30:00.123456789+00:00'

def test_binance_microseconds_and_milliseconds():
    a=parse_market(BINANCE,'x','binance','BTCUSDT')[0]
    b=parse_market(BINANCE.replace(b'1735689600010866',b'1735689600010'),'x','binance','BTCUSDT')[0]
    assert a['timestamp']=='2025-01-01T00:00:00.010866+00:00'
    assert b['timestamp']=='2025-01-01T00:00:00.010000+00:00'

def test_market_repeats_preserved(tmp_path):
    r=optimize_market(BINANCE*2,'x','binance',tmp_path,'BTCUSDT')
    assert r['rows']==2 and r['repeated_rows']==1 and r['removed_rows']==0

def test_precision_preserved():
    r=parse_market(HYPER,'x','hyperliquid')[0]
    assert r['price']=='1.123456789012345678'

def test_gzip_and_zip():
    assert parse_market(gzip.compress(ALGO),'x.csv.gz','algoseek')==parse_market(ALGO,'x','algoseek')
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w') as z:z.writestr('x.csv',BINANCE)
    assert parse_market(b.getvalue(),'x.zip','binance','BTCUSDT')[0]['symbol']=='BTCUSDT'

@pytest.mark.parametrize('source,data,symbol',[('binance',BINANCE,''),('binance',b'1,2,3\n','BTC'),('hyperliquid',b'{"block":1}',''),('algoseek',b'Date,Price\n20260101,2\n','')])
def test_unsupported_schema_rejected(source,data,symbol):
    with pytest.raises(ValueError):parse_market(data,'x',source,symbol)

def test_archive_expansion_limit(monkeypatch):
    from backend import datasets
    monkeypatch.setattr(datasets,'LIMIT',100)
    with pytest.raises(ValueError):unpack(gzip.compress(b'A'*1000),'x.gz')

def test_real_binance_sample(tmp_path):
    root=Path(__file__).resolve().parents[1]/'samples'
    data=(root/'BTCUSDT-trades-2017-08-17.csv').read_bytes()
    r=optimize_market(data,'sample.csv','binance',tmp_path,'BTCUSDT')
    provenance=json.loads((root/'binance-provenance.json').read_text())
    assert r['rows']==3427 and r['sha256']==provenance['raw_sha256']
    assert r['after_bytes']>0

def test_dataset_api(tmp_path,monkeypatch):
    monkeypatch.setattr(module,'DATA',tmp_path)
    with TestClient(module.app) as c:
        r=c.post('/api/datasets/upload',data={'source':'hyperliquid'},files={'file':('fills.json',HYPER)})
        assert r.status_code==200
        id=r.json()['id']
        assert c.get(f'/api/runs/{id}/download').content[:4]==b'PAR1'
        assert c.get('/api/runs').json()[0]['kind']=='market_data'

def test_real_bitmex_sample(tmp_path):
    data=(Path(__file__).resolve().parents[1]/'samples/bitmex-20141122.csv.gz').read_bytes()
    r=optimize_market(data,'20141122.csv.gz','bitmex',tmp_path)
    assert r['rows']==2 and r['first_timestamp']=='2014-11-22T17:51:38.948471000+00:00'

def test_real_futures_sample(tmp_path):
    root=Path(__file__).resolve().parents[1]/'samples'
    data=(root/'binance-futures-2019-09-08.zip').read_bytes()
    r=optimize_market(data,'BTCUSDT-trades-2019-09-08.zip','binance_um',tmp_path,'BTCUSDT')
    assert r['rows']==3754 and r['removed_rows']==0
