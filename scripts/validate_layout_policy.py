"""Offline temporal holdout on cached, checksum-verified Binance benchmark data.
Run python -m scripts.validate_layout_policy. Does not replace benchmarks/latest.json.
"""
import hashlib
import json
import random
import statistics
import time
from datetime import datetime, timezone
import duckdb
from backend.layout_policy import recommend, verify_relations
from scripts.benchmark_lab import ROOT, literal


def run():
    source_report=json.loads((ROOT/'benchmarks/latest.json').read_text())
    source_dir=next((p.parent for p in sorted((ROOT/'data/benchmarks').glob('*/trades.csv.gz'),reverse=True)
                     if all((p.parent / s['url'].split('/')[-1]).exists() for s in source_report['sources'])),None)
    if source_dir is None:raise ValueError('Run the original benchmark to populate local data first')
    for s in source_report['sources']:
        if hashlib.sha256((source_dir/s['url'].split('/')[-1]).read_bytes()).hexdigest()!=s['sha256']:
            raise ValueError('Cached publisher archive checksum mismatch')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out=ROOT/'data/validation'/stamp;out.mkdir(parents=True)
    con=duckdb.connect(config={'threads':1,'memory_limit':'1GB'})
    # Reconstruct canonical strings from verified archives rather than trusting cached CSV.
    import csv, gzip, io, zipfile
    canonical=out/'canonical.csv.gz'
    columns=['trade_id','price','quantity','quote_quantity','timestamp_ms','buyer_maker','best_match','symbol','date']
    with gzip.open(canonical,'wt',newline='') as dest:
        writer=csv.writer(dest);writer.writerow(columns)
        for s in source_report['sources']:
            name=s['url'].split('/')[-1];symbol=name.split('-trades-')[0];day=name.split('-trades-')[1][:-4]
            with zipfile.ZipFile(source_dir/name) as archive:
                with archive.open(archive.namelist()[0]) as raw:
                    for row in csv.reader(io.TextIOWrapper(raw)):writer.writerow(row+[symbol,day])
    con.execute(f'CREATE VIEW all_data AS SELECT * FROM read_csv({literal(canonical)},all_varchar=true)')
    records={};frozen=None
    for phase,day in [('calibration','2020-01-01'),('holdout','2020-01-03')]:
        phase_start=time.perf_counter();folder=out/phase;folder.mkdir()
        base=folder/'trades.csv.gz'
        con.execute(f"COPY (SELECT * FROM all_data WHERE date={literal(day)}) TO {literal(base)} (FORMAT CSV,HEADER true,COMPRESSION GZIP)")
        con.execute(f'CREATE OR REPLACE VIEW csv_gzip AS SELECT * FROM read_csv({literal(base)},all_varchar=true)')
        paths={'csv_gzip':base};conversion={'csv_gzip':0}
        for name,options,extension in [('parquet','FORMAT PARQUET, COMPRESSION ZSTD','parquet'),
                                       ('partitioned','FORMAT PARQUET, COMPRESSION ZSTD, PARTITION_BY (symbol)','parquet'),
                                       ('partitioned_csv','FORMAT CSV, HEADER true, COMPRESSION GZIP, PARTITION_BY (symbol)','csv.gz')]:
            paths[name]=folder/(f'trades.{extension}' if name=='parquet' else name)
            t=time.perf_counter();con.execute(f'COPY csv_gzip TO {literal(paths[name])} ({options})');conversion[name]=time.perf_counter()-t
            target=paths[name] if name=='parquet' else paths[name]/f'**/*.{extension}'
            reader=f'read_csv({literal(target)}, all_varchar=true, hive_partitioning=true)' if name=='partitioned_csv' else f'read_parquet({literal(target)},hive_partitioning=true)'
            con.execute(f'CREATE OR REPLACE VIEW {name} AS SELECT {",".join(columns)} FROM {reader}')
        checks={name:verify_relations(con,'csv_gzip',name) for name in paths}
        queries={
            'point':f"SELECT count(*),sum(CAST(quantity AS DECIMAL(28,8))) FROM {{table}} WHERE symbol='BTCUSDT' AND CAST(timestamp_ms AS BIGINT) < {int(datetime.fromisoformat(day).replace(tzinfo=timezone.utc).timestamp()*1000)+3600000}",
            'scan':"SELECT symbol,sum(CAST(quote_quantity AS DECIMAL(28,8))),sum(CAST(quantity AS DECIMAL(28,8))) FROM {table} GROUP BY symbol ORDER BY symbol",
            'id_lookup':"SELECT * FROM {table} WHERE trade_id IN ('210000000','49000000') ORDER BY ALL",
        }
        expected={q:con.execute(sql.format(table='csv_gzip')).fetchall() for q,sql in queries.items()}
        samples={n:{q:[] for q in queries} for n in paths}
        rng=random.Random(173)
        for repeat in range(4):
            jobs=[(n,q) for n in paths for q in queries];rng.shuffle(jobs)
            for n,q in jobs:
                t=time.perf_counter();result=con.execute(queries[q].format(table=n)).fetchall();elapsed=time.perf_counter()-t
                if result!=expected[q]:checks[n]=dict(verified=False,reason='query_result_mismatch')
                if repeat:samples[n][q].append(elapsed)
        candidates=[dict(layout=n,verified=checks[n]['verified'],conversion_s=conversion[n],
                         extra_bytes=0 if n=='csv_gzip' else (p.stat().st_size if p.is_file() else sum(f.stat().st_size for f in p.rglob('*') if f.is_file())),samples=samples[n]) for n,p in paths.items()]
        records[phase]=dict(date=day,rows=con.execute('SELECT count(*) FROM csv_gzip').fetchone()[0],checks=checks,candidates=candidates,queries=queries,elapsed_s=time.perf_counter()-phase_start)
        if phase=='calibration':
            # Freeze decisions BEFORE timing or inspecting holdout candidates.
            frozen=[dict(profile=profile,**recommend(candidates,weights,count,200*1024*1024,search_overhead_s=records[phase]['elapsed_s']))
                    for profile,weights in [('point',{'point':1}),('scan',{'scan':1}),('mixed',dict.fromkeys(queries,1))] for count in [1,100,10000]]
            (out/'frozen-decisions.json').write_text(json.dumps(frozen,indent=2))
        print(f'{phase}: {records[phase]["rows"]:,} rows verified and measured',flush=True)
    evaluations=[]
    for decision in frozen:
        totals={c['layout']:(0 if c['layout']=='csv_gzip' else c['conversion_s']+records['calibration']['elapsed_s']) + decision['query_count']*sum(statistics.median(c['samples'][q])*w for q,w in decision['weights'].items()) for c in records['holdout']['candidates']}
        chosen=decision['selected'];best=min(totals,key=totals.get)
        evaluations.append(dict(profile=decision['profile'],query_count=decision['query_count'],selected=chosen,
                                holdout_total_s=totals,holdout_best=best,regret_s=totals[chosen]-totals[best],
                                speedup_vs_keep_csv=totals['csv_gzip']/totals[chosen],speedup_vs_always_parquet=totals['parquet']/totals[chosen]))
    # Deliberately remove one row: deterministic negative control, never used for timings.
    con.execute('CREATE TABLE corrupted AS SELECT * FROM csv_gzip LIMIT 0')
    con.execute('INSERT INTO corrupted SELECT * FROM csv_gzip OFFSET 1')
    corruption=verify_relations(con,'csv_gzip','corrupted')
    if corruption['verified']:raise AssertionError('Corruption escaped verifier')
    report=dict(created=datetime.now(timezone.utc).isoformat(),sources=source_report['sources'],records=records,decisions=frozen,evaluations=evaluations,
                corruption_control=corruption,environment=dict(duckdb=duckdb.__version__,threads=1,memory_limit='1GB'),
                limitations=['Temporal holdout within the same previously downloaded six-file corpus, not a new provider or prospective production data.',
                             'Three timed repeats after warmup; empirical timing ranges are not confidence intervals.',
                             'Point workload keeps its template but changes date; ID lookup is a negative lookup workload.',
                             'Calibration search cost charged to each alternative, separate from deployment conversion. Holdout validation cost excluded.',
                             'Conversion measured once; query-count totals are projections, not full workload executions.',
                             'Local DuckDB with warm caches; no AWS billing, cold-cache, concurrent-load or large-scale claims.'])
    (ROOT/'benchmarks/policy-validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(dict(evaluations=evaluations,corruption_control=corruption),indent=2),flush=True)
    con.close()

if __name__=='__main__':run()
