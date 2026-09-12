"""Bounded market-data adapters. Preserve every row and exact source payload."""
import csv, gzip, io, json, re, zipfile, hashlib
from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from .agents import CompressionAgent, CostAgent
LIMIT=20*1024*1024

def unpack(data,name):
    if len(data)>LIMIT:raise ValueError('Maximum input is 20 MiB.')
    if name.lower().endswith('.gz'):
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

def parse_market(data,name,source,symbol='',timezone_name='Etc/GMT+5'):
    text=unpack(data,name).decode('utf-8-sig')
    if source in ('binance','binance_um'):
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,30}',symbol):raise ValueError('Enter the Binance symbol, e.g. BTCUSDT.')
        raw=list(csv.reader(io.StringIO(text)))
        if raw and raw[0][0] in ('id','trade_id'):raw=raw[1:]
        rows=[]
        for r in raw:
            if len(r)!=(7 if source=='binance' else 6):raise ValueError('Expected Binance spot 7-column or USD-M futures 6-column trades CSV.')
            if not r[0].isdigit() or r[5].lower() not in ('true','false') or (source=='binance' and r[6].lower() not in ('true','false')):raise ValueError('Invalid Binance trade ID or boolean.')
            rows.append(dict(timestamp=epoch(r[4]),symbol=symbol.upper(),price=positive(r[1]),quantity=positive(r[2]),source_record=json.dumps(r,separators=(',',':'))))
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
        if not isinstance(raw,list):raise ValueError('Upload an API-format fill array or JSONL records. Block envelopes and L2 books are not supported.')
        rows=[]
        for r in raw:
            if not isinstance(r,dict) or not {'coin','px','sz','time','tid'}.issubset(r):raise ValueError('Expected Hyperliquid API fills: coin, px, sz, time, tid.')
            if int(r['time'])>=100000000000000:raise ValueError('Hyperliquid fill timestamps must be milliseconds.')
            rows.append(dict(timestamp=epoch(r['time']),symbol=str(r['coin']),price=positive(r['px']),quantity=positive(r['sz']),source_record=json.dumps(r,sort_keys=True,separators=(',',':'))))
    else:raise ValueError('Unknown dataset source.')
    if not rows or len(rows)>200000:raise ValueError('Provide 1–200,000 records.')
    if any(not r['symbol'].strip() for r in rows):raise ValueError('Symbol is missing.')
    return rows

def optimize_market(data,name,source,destination,symbol='',timezone_name='Etc/GMT+5'):
    try:rows=parse_market(data,name,source,symbol,timezone_name)
    except (UnicodeError,KeyError,TypeError,OverflowError,zipfile.BadZipFile,EOFError,OSError) as e:raise ValueError('Invalid or unsupported dataset: '+str(e)) from e
    size=CompressionAgent().run(rows,destination)
    repeats=len(rows)-len(set(r['source_record'] for r in rows))
    return dict(kind='market_data',source=source,before_bytes=len(data),after_bytes=size,reduction_pct=round((1-size/len(data))*100,1),rows=len(rows),repeated_rows=repeats,removed_rows=0,symbols=sorted(set(r['symbol'] for r in rows)),first_timestamp=min(r['timestamp'] for r in rows),last_timestamp=max(r['timestamp'] for r in rows),cost=CostAgent().run(len(data),size),sha256=hashlib.sha256(data).hexdigest(),timezone_assumption=timezone_name if source=='algoseek' else 'UTC epoch',sample=[{k:v for k,v in r.items() if k!='source_record'} for r in rows[:8]],incidents=[],events=[dict(agent='Supervisor',time=datetime.now(timezone.utc).isoformat(),message='Market data validated and preserved in verified Parquet. Repeated rows reported, not removed. Operational latency and security incidents cannot be inferred from these fields.')],approval='not_required')
