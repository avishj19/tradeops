"""Run: python -m scripts.benchmark_lab. Bounded public-data experiment."""
import csv, gzip, hashlib, io, json, platform, random, ssl, statistics, time, urllib.request, zipfile
from datetime import datetime, timezone
from pathlib import Path
import certifi
import duckdb
from backend.experiments import choose_layout

ROOT=Path(__file__).resolve().parents[1]
MAX_ARCHIVE=20*1024*1024
MAX_EXPANDED=150*1024*1024

def download(url, limit):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url,context=ssl.create_default_context(cafile=certifi.where()),timeout=30) as r:
                data=r.read(limit+1)
            if len(data)>limit:raise ValueError('Download exceeds configured limit')
            return data
        except (OSError, TimeoutError):
            if attempt==2:raise
            time.sleep(1)

def literal(s):return "'"+str(s).replace("'","''")+"'"

def run():
    started=time.perf_counter()
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    work=ROOT/'data'/'benchmarks'/stamp;work.mkdir(parents=True)
    provenance=[];rows=0
    columns=['trade_id','price','quantity','quote_quantity','timestamp_ms','buyer_maker','best_match','symbol','date']
    baseline=work/'trades.csv.gz'
    with gzip.open(baseline,'wt',newline='') as output:
        writer=csv.writer(output);writer.writerow(columns)
        for symbol in ['BTCUSDT','ETHUSDT']:
            for day in ['2020-01-01','2020-01-02','2020-01-03']:
                name=f'{symbol}-trades-{day}.zip'
                url=f'https://data.binance.vision/data/spot/daily/trades/{symbol}/{name}'
                checksum=download(url+'.CHECKSUM',4096).decode().split()[0]
                cached=next((ROOT/'data'/'benchmarks').glob('*/'+name),None)
                data=cached.read_bytes() if cached else download(url,MAX_ARCHIVE)
                if hashlib.sha256(data).hexdigest()!=checksum:raise ValueError('Publisher checksum mismatch')
                (work/name).write_bytes(data)
                count=0
                with zipfile.ZipFile(io.BytesIO(data)) as archive:
                    infos=archive.infolist()
                    if len(infos)!=1 or infos[0].file_size>MAX_EXPANDED:raise ValueError('Unexpected archive')
                    with archive.open(infos[0]) as source:
                        for row in csv.reader(io.TextIOWrapper(source)):
                            if len(row)!=7:raise ValueError('Unexpected trade schema')
                            if datetime.fromtimestamp(int(row[4])/1000,timezone.utc).date().isoformat()!=day:
                                raise ValueError('Date does not match archive')
                            writer.writerow(row+[symbol,day]);count+=1
                rows+=count
                provenance.append(dict(url=url,checksum_url=url+'.CHECKSUM',sha256=checksum,archive_bytes=len(data),expanded_bytes=infos[0].file_size,rows=count))
                print(f'Downloaded and verified {name}: {count:,} rows',flush=True)
    con=duckdb.connect(config={'threads':1,'memory_limit':'1GB'})
    # Explicit VARCHAR schema preserves original numeric text and flags. Cast only in queries.
    schema='{'+','.join(literal(c)+": 'VARCHAR'" for c in columns)+'}'
    con.execute(f"CREATE VIEW csv_gzip AS SELECT * FROM read_csv({literal(baseline)}, header=true, columns={schema}, auto_detect=false)")
    conversions={'csv_gzip':0.0}
    paths={'csv_gzip':baseline,'parquet':work/'trades.parquet','partitioned':work/'partitioned'}
    for name, options in [('parquet',''),('partitioned',', PARTITION_BY (date, symbol)')]:
        t=time.perf_counter()
        con.execute(f"COPY csv_gzip TO {literal(paths[name])} (FORMAT PARQUET, COMPRESSION ZSTD{options})")
        conversions[name]=time.perf_counter()-t
        target=str(paths[name]) if name=='parquet' else str(paths[name]/'**/*.parquet')
        hive_options=", hive_partitioning=true, hive_types={'date':VARCHAR,'symbol':VARCHAR}" if name=='partitioned' else ', hive_partitioning=false'
        con.execute(f"CREATE VIEW {name} AS SELECT {','.join(columns)} FROM read_parquet({literal(target)}{hive_options})")
    # A stronger control separates partition pruning from Parquet encoding.
    paths['partitioned_csv']=work/'partitioned_csv'
    t=time.perf_counter()
    con.execute(f"COPY csv_gzip TO {literal(paths['partitioned_csv'])} (FORMAT CSV, HEADER true, COMPRESSION GZIP, PARTITION_BY (date, symbol))")
    conversions['partitioned_csv']=time.perf_counter()-t
    partial_schema='{'+','.join(literal(c)+": 'VARCHAR'" for c in columns[:-2])+'}'
    csv_glob=paths['partitioned_csv']/'**/*.csv.gz'
    con.execute(f"CREATE VIEW partitioned_csv AS SELECT {','.join(columns)} FROM read_csv({literal(csv_glob)},header=true,columns={partial_schema},auto_detect=false,hive_partitioning=true,hive_types={{'date':VARCHAR,'symbol':VARCHAR}})")
    verified={}
    for name in paths:
        mismatch=con.execute(f'SELECT count(*) FROM ((SELECT * FROM csv_gzip EXCEPT ALL SELECT * FROM {name}) UNION ALL (SELECT * FROM {name} EXCEPT ALL SELECT * FROM csv_gzip))').fetchone()[0]
        verified[name]=mismatch==0
        if mismatch:raise ValueError(f'Record preservation failed: {name}')
    queries={
        'selective':"SELECT count(*), sum(CAST(quantity AS DECIMAL(28,8))) FROM {table} WHERE symbol='BTCUSDT' AND date='2020-01-02' AND CAST(timestamp_ms AS BIGINT) BETWEEN 1577923200000 AND 1577926800000",
        'daily_volume':"SELECT date,symbol,count(*),sum(CAST(quantity AS DECIMAL(28,8))) FROM {table} GROUP BY date,symbol ORDER BY date,symbol",
        'vwap_components':"SELECT symbol,sum(CAST(quote_quantity AS DECIMAL(28,8))),sum(CAST(quantity AS DECIMAL(28,8))) FROM {table} GROUP BY symbol ORDER BY symbol",
    }
    expected={q:con.execute(sql.format(table='csv_gzip')).fetchall() for q,sql in queries.items()}
    measurements={phase:{n:{q:[] for q in queries} for n in paths} for phase in ['calibration','evaluation']}
    rng=random.Random(42)
    # Explicit warmup; fresh query execution, warm OS cache, no cache flush claim.
    for name in paths:
        for q,sql in queries.items():
            if con.execute(sql.format(table=name)).fetchall()!=expected[q]:raise ValueError('Query mismatch')
    for phase in measurements:
        for repeat in range(5):
            jobs=[(n,q) for n in paths for q in queries];rng.shuffle(jobs)
            for name,q in jobs:
                t=time.perf_counter();result=con.execute(queries[q].format(table=name)).fetchall();elapsed=time.perf_counter()-t
                if result!=expected[q]:raise ValueError('Repeated query mismatch')
                measurements[phase][name][q].append(elapsed)
        print(f'{phase} timings complete',flush=True)
    sizes={n:p.stat().st_size if p.is_file() else sum(f.stat().st_size for f in p.rglob('*') if f.is_file()) for n,p in paths.items()}
    candidates=[]
    for name in paths:
        candidates.append(dict(layout=name,verified=verified[name],conversion_s=conversions[name],bytes=sizes[name],extra_bytes=0 if name=='csv_gzip' else sizes[name],
            query_s=statistics.median(measurements['calibration'][name]['selective'])))
    decisions=[]
    for profile,weights in [('selective',{'selective':1}),('mixed',dict.fromkeys(queries,1/3))]:
        for count in [1,100,10000]:
            inputs=[dict(c,query_s=sum(statistics.median(measurements['calibration'][c['layout']][q])*w for q,w in weights.items())) for c in candidates]
            decision=choose_layout(inputs,count,200*1024*1024)
            eval_totals={c['layout']:c['conversion_s']+count*sum(statistics.median(measurements['evaluation'][c['layout']][q])*w for q,w in weights.items()) for c in candidates}
            chosen=decision['selected']
            decisions.append(dict(profile=profile,query_count=count,**decision,evaluation_total_s=eval_totals,
                evaluation_speedup_vs_csv=eval_totals['csv_gzip']/eval_totals[chosen],
                evaluation_speedup_vs_always_parquet=eval_totals['parquet']/eval_totals[chosen],
                evaluation_speedup_vs_partitioned_csv=eval_totals['partitioned_csv']/eval_totals[chosen]))
    report=dict(created=datetime.now(timezone.utc).isoformat(),rows=rows,sources=provenance,candidates=candidates,queries=queries,measurements=measurements,decisions=decisions,
        environment=dict(python=platform.python_version(),duckdb=duckdb.__version__,platform=platform.platform(),threads=1,memory_limit='1GB'),
        elapsed_s=time.perf_counter()-started,
        limitations=['Local DuckDB warm-cache benchmarks, not AWS/Athena timing or billing.',
        'Six historical daily spot trade files from one provider; no synthetic duplication and no application logs.',
        'Calibration and evaluation use separate timing rounds on the same data/queries, not unseen datasets.',
        'Conversion measured once; totals extrapolate median query time to hypothetical query counts.',
        'Download and normalization are common preparation costs excluded from the layout decision. Original ZIPs and canonical gzip are retained.',
        'Full bidirectional EXCEPT ALL checks preserve duplicate multiplicity and every canonical string field; every timed query is checked.',
        'VWAP query returns exact numerator/denominator; no floating-point division is benchmarked.',
        'Search and verification overhead is reported in elapsed_s but excluded from projected layout totals. No net optimizer speedup claim.',
        'Baseline is a normalized combined gzip, not the publisher ZIP layout. Partitioned gzip is a stronger control for pruning benefits.',
        'No measured peak memory, physical bytes scanned, concurrency, cold cache, significance tests, or dollar savings.',
        'Bounded exhaustive four-candidate search with deterministic selection; no LLM or autonomous cloud changes.'])
    out=ROOT/'benchmarks';out.mkdir(exist_ok=True)
    (out/f'{stamp}.json').write_text(json.dumps(report,indent=2))
    (out/'latest.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(dict(rows=rows,candidates=candidates,decisions=decisions,elapsed_s=report['elapsed_s']),indent=2),flush=True)
    con.close()

if __name__=='__main__':run()
