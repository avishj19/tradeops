"""Bounded market-data adapters. Preserve every row and exact source payload."""
import csv, gzip, io, json, re, zipfile, hashlib
from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from .agents import CompressionAgent, CostAgent
LIMIT=20*1024*1024

PARQUET_MAGIC=b'PAR1';LZ4_MAGIC=b'\x04\x22\x4d\x18'
def is_parquet(data):return data[:4]==PARQUET_MAGIC and data[-4:]==PARQUET_MAGIC
def unpack(data,name):
    if len(data)>LIMIT:raise ValueError('Maximum input is 20 MiB.')
    if name.lower().endswith('.lz4') or data[:4]==LZ4_MAGIC:
        try:import lz4.frame
        except ImportError:raise ValueError('LZ4 input requires the lz4 package (pip install lz4).')
        d=lz4.frame.LZ4FrameDecompressor();data=d.decompress(data,max_length=LIMIT+1)
        if not d.eof and len(data)>LIMIT:raise ValueError('Expanded LZ4 input exceeds 20 MiB.')
    elif name.lower().endswith('.gz'):
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as f: data=f.read(LIMIT+1)
    elif name.lower().endswith('.zip'):
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            entries=z.infolist()
            if len(entries)!=1 or entries[0].is_dir() or entries[0].file_size>LIMIT:raise ValueError('ZIP must contain one CSV file up to 20 MiB.')
            if not entries[0].filename.lower().endswith('.csv'):raise ValueError('ZIP member must be CSV.')
            with z.open(entries[0]) as f:data=f.read(LIMIT+1)
    if len(data)>LIMIT:raise ValueError('Expanded input exceeds 20 MiB.')
    return data

def epoch(value):
    n=int(value)
    # Binance spot changed milliseconds to microseconds in 2025.
    unit=1000000 if n>=100000000000000 else 1000
    t=datetime(1970,1,1,tzinfo=timezone.utc)+timedelta(seconds=n//unit,microseconds=(n%unit)*(1000000//unit))
    if not 2000<=t.year<=2100:raise ValueError('Timestamp outside supported 2000–2100 range.')
    return t.isoformat()

def positive(value,zero=False):
    try:d=Decimal(str(value))
    except InvalidOperation:raise ValueError('Invalid price or quantity.')
    if not d.is_finite() or d<0 or (not zero and d==0):raise ValueError('Price/quantity must be finite and positive (zero quantity allowed for Algoseek).')
    return str(value)

# source: (columns, timestamp column index, boolean column indexes, label)
BINANCE={
 'binance':(7,4,(5,6),'Binance spot trades'),
 'binance_um':(6,4,(5,),'Binance USD-M futures trades'),
 'binance_cm':(6,4,(5,),'Binance COIN-M futures trades'),
 'binance_agg':(8,5,(6,7),'Binance spot aggTrades'),
 'binance_um_agg':(7,5,(6,),'Binance USD-M futures aggTrades'),
 'binance_cm_agg':(7,5,(6,),'Binance COIN-M futures aggTrades'),
}
def sniff_reader(text):
    sample=text[:4096]
    try:dialect=csv.Sniffer().sniff(sample,delimiters=',\t;|')
    except csv.Error:dialect=csv.excel
    return csv.DictReader(io.StringIO(text),dialect=dialect),dialect.delimiter

def parse_market(data,name,source,symbol='',timezone_name='Etc/GMT+5'):
    data=unpack(data,name)
    if is_parquet(data) and source!='hydromancer':raise ValueError('This file is Parquet; choose source=hydromancer or a Parquet-capable source.')
    text='' if is_parquet(data) else data.decode('utf-8-sig')
    if source in BINANCE:
        cols,tcol,bools,label=BINANCE[source]
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,30}',symbol):raise ValueError('Enter the Binance symbol, e.g. BTCUSDT or BTCUSD_PERP.')
        raw=list(csv.reader(io.StringIO(text)))
        if raw and not raw[0][0].isdigit():raw=raw[1:]  # header row (id / trade_id / agg_trade_id)
        rows=[]
        for r in raw:
            if len(r)!=cols:
                hint={8:'spot aggTrades (binance_agg)',7:'spot trades (binance) or futures aggTrades (binance_um_agg / binance_cm_agg)',6:'USD-M trades (binance_um) or COIN-M trades (binance_cm)'}.get(len(r),'an unsupported layout')
                raise ValueError(f'{label} expects {cols} columns; this file has {len(r)}, which looks like {hint}.')
            if not r[0].isdigit() or any(r[i].lower() not in ('true','false') for i in bools):raise ValueError(f'Invalid {label} trade ID or boolean flag.')
            rows.append(dict(timestamp=epoch(r[tcol]),symbol=symbol.upper(),price=positive(r[1]),quantity=positive(r[2]),source_record=json.dumps(r,separators=(',',':'))))
    elif source=='algoseek':
        if timezone_name not in ('Etc/GMT+5','America/New_York'):raise ValueError('Choose fixed EST or America/New_York explicitly.')
        reader=csv.DictReader(io.StringIO(text));required={'Date','Timestamp','EventType','Ticker','Price','Quantity','Exchange','Conditions'}
        if not reader.fieldnames or len(set(reader.fieldnames))!=len(reader.fieldnames) or not required.issubset(reader.fieldnames):raise ValueError('Expected Algoseek Date, Timestamp, EventType, Ticker, Price, Quantity, Exchange, Conditions headers.')
        raw=list(reader);rows=[]
        for r in raw:
            if None in r or any(v is None for v in r.values()):raise ValueError('Malformed CSV row.')
            if not re.fullmatch(r'\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?',r['Timestamp']):raise ValueError('Invalid Algoseek timestamp.')
            # UTC ISO text retains all fractional digits; do not round nanoseconds.
            whole,_,fraction=r['Timestamp'].partition('.')
            local=datetime.strptime(r['Date']+whole,'%Y%m%d%H:%M:%S').replace(tzinfo=ZoneInfo(timezone_name))
            utc=local.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')+('.'+fraction.ljust(9,'0') if fraction else '')+'+00:00'
            rows.append(dict(timestamp=utc,symbol=r['Ticker'],price=positive(r['Price']),quantity=positive(r['Quantity'],True),source_record=json.dumps(r,sort_keys=True,separators=(',',':'))))
    elif source=='bitmex':
        raw=list(csv.DictReader(io.StringIO(text)));rows=[]
        for r in raw:
            if not {'timestamp','symbol','price','size','trdMatchID'}.issubset(r) or None in r or any(v is None for v in r.values()):raise ValueError('Expected BitMEX trade CSV headers.')
            value=r['timestamp'].replace('D','T')
            if not value.endswith(('Z','+00:00')):value+='Z'
            dt=datetime.fromisoformat(value.replace('Z','+00:00'))
            rows.append(dict(timestamp=value.replace('Z','+00:00'),symbol=r['symbol'],price=positive(r['price']),quantity=positive(r['size']),source_record=json.dumps(r,sort_keys=True,separators=(',',':'))))
    elif source=='hyperliquid':
        try:raw=json.loads(text)
        except json.JSONDecodeError:raw=[json.loads(line) for line in text.splitlines() if line.strip()]
        if isinstance(raw,dict):raw=[raw]  # single-line JSONL
        if not isinstance(raw,list):raise ValueError('Upload an API-format fill array, node_fills or node_trades JSONL. L2 books are not supported.')
        if len(raw)==2 and isinstance(raw[0],str) and isinstance(raw[1],dict):raw=[raw]  # single node_fills line
        rows=[]
        for r in raw:
            # node_fills archive lines are [address, fill]; unwrap to the fill.
            if isinstance(r,list) and len(r)==2 and isinstance(r[1],dict):r=r[1]
            if not isinstance(r,dict):raise ValueError('Expected Hyperliquid fill/trade objects.')
            if {'coin','px','sz','time','tid'}.issubset(r):px,sz=r['px'],r['sz']
            elif {'coin','px_str','sz_str','time'}.issubset(r):px,sz=r['px_str'],r['sz_str']   # node_trades format
            else:raise ValueError('Expected Hyperliquid API fills (coin, px, sz, time, tid) or node_trades (coin, px_str, sz_str, time).')
            if int(r['time'])>=100000000000000:raise ValueError('Hyperliquid timestamps must be milliseconds.')
            rows.append(dict(timestamp=epoch(r['time']),symbol=str(r['coin']),price=positive(px),quantity=positive(sz),source_record=json.dumps(r,sort_keys=True,separators=(',',':'))))
    elif source=='hydromancer':
        import pyarrow.parquet as pq
        if not is_parquet(data):raise ValueError('Hydromancer Reservoir fills must be a Parquet file (date=YYYY-MM-DD/fills.parquet).')
        table=pq.read_table(io.BytesIO(data));cols=set(table.column_names)
        ts=next((c for c in ('timestamp','time','ts') if c in cols),None);coin=next((c for c in ('coin','symbol','asset') if c in cols),None)
        px=next((c for c in ('price','px') if c in cols),None);sz=next((c for c in ('size','sz','quantity') if c in cols),None)
        if not all((ts,coin,px,sz)):raise ValueError('Hydromancer fills need timestamp, coin, price and size columns; found: '+', '.join(sorted(cols)))
        rows=[]
        for r in table.to_pylist():
            t=r[ts]
            tv=epoch(int(t.timestamp()*1000)) if hasattr(t,'timestamp') else (epoch(t) if isinstance(t,(int,float)) else datetime.fromisoformat(str(t).replace('Z','+00:00')).astimezone(timezone.utc).isoformat())
            rows.append(dict(timestamp=tv,symbol=str(r[coin]),price=positive(r[px]),quantity=positive(r[sz]),source_record=json.dumps(r,sort_keys=True,separators=(',',':'),default=str)))
    elif source=='singlestore':
        reader,delim=sniff_reader(text)
        required={'stock_symbol','shares','share_price','trade_time'}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):raise ValueError(f'Expected SingleStore trade columns stock_symbol, shares, share_price, trade_time (detected delimiter {delim!r}); found: '+', '.join(reader.fieldnames or []))
        rows=[]
        for r in reader:
            if None in r or any(v is None for v in r.values()):raise ValueError('Malformed delimited row.')
            t=datetime.fromisoformat(r['trade_time'].replace('Z','+00:00'))
            if t.tzinfo is None:t=t.replace(tzinfo=timezone.utc)  # tutorial data carries no zone; assume UTC and record it
            rows.append(dict(timestamp=t.astimezone(timezone.utc).isoformat(),symbol=r['stock_symbol'],price=positive(r['share_price']),quantity=positive(r['shares']),source_record=json.dumps(r,sort_keys=True,separators=(',',':'))))
    else:raise ValueError('Unknown dataset source. Supported: '+', '.join(sorted(list(BINANCE)+['algoseek','bitmex','hyperliquid','hydromancer','singlestore'])))
    if not rows or len(rows)>200000:raise ValueError('Provide 1–200,000 records.')
    if any(not r['symbol'].strip() for r in rows):raise ValueError('Symbol is missing.')
    return rows

def optimize_market(data,name,source,destination,symbol='',timezone_name='Etc/GMT+5'):
    try:rows=parse_market(data,name,source,symbol,timezone_name)
    except (UnicodeError,KeyError,TypeError,OverflowError,zipfile.BadZipFile,EOFError,OSError) as e:raise ValueError('Invalid or unsupported dataset: '+str(e)) from e
    size=CompressionAgent().run(rows,destination)
    repeats=len(rows)-len(set(r['source_record'] for r in rows))
    return dict(kind='market_data',source=source,before_bytes=len(data),after_bytes=size,reduction_pct=round((1-size/len(data))*100,1),rows=len(rows),repeated_rows=repeats,removed_rows=0,symbols=sorted(set(r['symbol'] for r in rows)),first_timestamp=min(r['timestamp'] for r in rows),last_timestamp=max(r['timestamp'] for r in rows),cost=CostAgent().run(len(data),size),sha256=hashlib.sha256(data).hexdigest(),timezone_assumption=timezone_name if source=='algoseek' else ('UTC assumed (source has no zone)' if source=='singlestore' else 'UTC epoch'),sample=[{k:v for k,v in r.items() if k!='source_record'} for r in rows[:8]],incidents=[],events=[dict(agent='Supervisor',time=datetime.now(timezone.utc).isoformat(),message='Market data validated and preserved in verified Parquet. Repeated rows reported, not removed. Operational latency and security incidents cannot be inferred from these fields.')],approval='not_required')
