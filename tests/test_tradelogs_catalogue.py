"""Formats from the vdnttiwari08-boop/tradelogs catalogue (schema fixtures; no network)."""
import io, json, zipfile, pytest, lz4.frame, pyarrow as pa, pyarrow.parquet as pq
from backend.datasets import parse_market
from backend.connectors import Runner, records
T=1757548800000
def z(member,text):
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w') as f:f.writestr(member,text)
    return b.getvalue()
def test_coin_m_trades():
    rows=parse_market(z('BTCUSD_PERP-trades-2026-09-11.csv','id,price,qty,base_qty,time,is_buyer_maker\n1,60000.5,10,0.000166,%d,true\n'%T),'x.zip','binance_cm','BTCUSD_PERP')
    assert rows[0]['quantity']=='10' and rows[0]['symbol']=='BTCUSD_PERP'
def test_spot_aggtrades_microseconds():
    rows=parse_market(('1,60000.1,0.5,10,11,%d,True,True\n'%(T*1000+7)).encode(),'x.csv','binance_agg','BTCUSDT')
    assert rows[0]['timestamp'].startswith('2025-09-11T00:00:00.000007')
def test_futures_aggtrades_header_and_both_margins():
    text='agg_trade_id,price,quantity,first_trade_id,last_trade_id,transact_time,is_buyer_maker\n5,60000,1.5,9,9,%d,false\n'%T
    for src,sym in (('binance_um_agg','BTCUSDT'),('binance_cm_agg','BTCUSD_PERP')):
        assert parse_market(text.encode(),'x.csv',src,sym)[0]['quantity']=='1.5'
def test_wrong_binance_source_names_correct_one():
    with pytest.raises(ValueError,match='binance_agg'):parse_market(b'1,1,1,1,1,%d,True,True\n'%T,'x.csv','binance','BTCUSDT')
def test_hyperliquid_node_fills_lz4_envelope_and_node_trades():
    fills=lz4.frame.compress(json.dumps(['0xab',dict(coin='BTC',px='60000',sz='0.1',time=T,tid=1)]).encode())
    assert parse_market(fills,'f.lz4','hyperliquid')[0]['price']=='60000'
    trades=json.dumps(dict(coin='ETH',side='B',time=T,px_str='3000.1',sz_str='2',hash='0x0',side_info=[])).encode()
    assert parse_market(trades,'t.jsonl','hyperliquid')[0]['quantity']=='2'
def test_hydromancer_parquet():
    b=io.BytesIO();pq.write_table(pa.table({'timestamp':pa.array([T],pa.int64()),'coin':['BTC'],'price':[60000.5],'size':[0.25],'wallet':['0x1'],'direction':['Open Long'],'fee':[0.1],'realized_pnl':[0.0]}),b)
    r=parse_market(b.getvalue(),'fills.parquet','hydromancer')[0]
    assert r['symbol']=='BTC' and r['quantity']=='0.25' and r['timestamp'].startswith('2025-09-11')
    with pytest.raises(ValueError,match='Parquet'):parse_market(b.getvalue(),'fills.parquet','hyperliquid')
def test_singlestore_tab_separated():
    r=parse_market(b'id\tstock_symbol\tshares\tshare_price\ttrade_time\n1\tAAPL\t10\t150.25\t2026-09-11 13:00:00\n','trade.csv','singlestore')[0]
    assert r['symbol']=='AAPL' and r['price']=='150.25' and r['timestamp']=='2026-09-11T13:00:00+00:00'
def test_raw_csv_mode_rejects_single_mangled_column():
    assert records(b'a\tb\n1\t2\n','csv')==[{'a':'1','b':'2'}]   # sniffed
    assert records(b'a\tb\n1\t2\n','tsv')==[{'a':'1','b':'2'}]
    assert records(b'a;b\n1;2\n','csv',';')==[{'a':'1','b':'2'}]
def test_scan_isolates_bad_file_and_reports(tmp_path):
    (tmp_path/'BTCUSD_PERP-trades-2026-09-11.zip').write_bytes(z('a.csv','1,60000,10,0.0001,%d,true\n'%T))
    (tmp_path/'BTCUSDT-aggTrades-2026-09-11.zip').write_bytes(z('b.csv','1,1,1,1,1,%d,True,True\n'%T))
    r=Runner({'type':'folder','path':str(tmp_path),'pattern':'*.zip','dataset':'binance_cm','settle_seconds':0},tmp_path/'data')
    assert r.folder()==1 and len(r.failures)==1 and 'binance_agg' in r.failures[0]['error']
    assert not [d for d in (tmp_path/'data').iterdir() if d.is_dir() and not any(d.iterdir())]
def test_namespace_ignores_operational_knobs(tmp_path):
    a=Runner({'type':'folder','path':'/x','pattern':'*','format':'csv','settle_seconds':0},tmp_path)
    b=Runner({'type':'folder','path':'/x','pattern':'*','format':'csv','settle_seconds':99,'max_objects':7},tmp_path)
    assert a.namespace==b.namespace
def test_requester_pays_needs_explicit_acceptance(tmp_path):
    with pytest.raises(ValueError,match='accept_requester_pays_charges'):Runner({'type':'s3','bucket':'b','prefix':'p/','dataset':'hydromancer','request_payer':True},tmp_path).s3args()
    assert Runner({'type':'s3','bucket':'b','prefix':'p/','dataset':'hydromancer','request_payer':True,'accept_requester_pays_charges':True},tmp_path).s3args()=={'RequestPayer':'requester'}
def test_symbol_derived_from_aggtrades_filename(tmp_path):
    r=Runner({'type':'folder','path':str(tmp_path),'pattern':'*.zip','dataset':'binance_agg','settle_seconds':0},tmp_path/'d')
    (tmp_path/'ETHUSDT-aggTrades-2026-09-11.zip').write_bytes(z('a.csv','1,3000,1,1,1,%d,True,True\n'%T))
    assert r.folder()==1 and r.failures==[]

def test_singlestore_real_file_has_no_header():
    rows=parse_market(b'5296438\tARGS\t400.0000\t96.6275\t2022-08-12 02:20:46.000000\n5296439\tXYZ\t10\t1.5\t2022-08-12 02:20:47.000000\n','trade.csv','singlestore')
    assert len(rows)==2 and rows[0]['symbol']=='ARGS' and rows[0]['quantity']=='400.0000' and rows[0]['timestamp']=='2022-08-12T02:20:46+00:00'
