"""Deterministic, evidence-driven agents. No LLM or AWS credentials required."""
import csv, io, json, math, random, statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path
from .planning import incidents
from .sequences import SequenceEvidenceAgent
import pyarrow as pa
import pyarrow.parquet as pq

NAMES = ['Supervisor', 'Log Analysis', 'Storage Optimization', 'Compression', 'Query Optimization', 'Cost', 'Sequence Evidence']
REQUIRED = {'timestamp', 'event_id', 'symbol', 'latency_ms', 'status'}

def generate(scenario='normal', count=10000):
    rng = random.Random(42)
    base = datetime.now(timezone.utc).replace(hour=9, minute=30, second=0, microsecond=0)-timedelta(days=95)
    rows=[]
    for i in range(count):
        incident = scenario=='latency_spike' and i > count*.8
        rows.append(dict(timestamp=(base+timedelta(seconds=i*10)).isoformat(), event_id=f'EX-{i:08}', symbol=rng.choice(['AAPL','MSFT','NVDA','SPY']), latency_ms=round(rng.uniform(400,1200) if incident else rng.uniform(3,45),2), status='ERROR' if incident and i%3==0 else 'FILLED', quantity=rng.randint(1,500), price=round(rng.uniform(100,800),2), source='execution-gateway', strategy=rng.choice(['momentum','market-making'])))
    rows += rows[:int(count*(.15 if scenario=='duplicates' else .04))]
    return rows

class LogAnalysisAgent:
    def run(self, data, filename):
        try:
            text=data.decode('utf-8-sig')
            rows=list(csv.DictReader(io.StringIO(text))) if filename.lower().endswith('.csv') else json.loads(text)
            if not isinstance(rows,list) or not rows or len(rows)>200000: raise ValueError('Provide 1–200,000 log records.')
            canonical=[]
            columns=set(rows[0]) if isinstance(rows[0],dict) else set()
            for r in rows:
                if not isinstance(r,dict) or not REQUIRED.issubset(r): raise ValueError('Required columns: '+', '.join(sorted(REQUIRED)))
                if set(r)!=columns or any(k is None or v is None or isinstance(v,(list,dict)) for k,v in r.items()):
                    raise ValueError('Records must have consistent columns and non-null scalar values.')
                if any(not str(r[k]).strip() for k in REQUIRED):
                    raise ValueError('Required fields cannot be empty.')
                ts=r['timestamp']
                if isinstance(ts,(int,float)) or (isinstance(ts,str) and ts.isdigit()):
                    n=int(ts);unit=1000000 if n>=100000000000000 else (1000 if n>=100000000000 else 1)
                    t=datetime.fromtimestamp(n/unit,tz=timezone.utc)
                else:
                    try:t=datetime.fromisoformat(str(ts).replace('Z','+00:00'))
                    except ValueError:raise ValueError('Timestamps must be ISO-8601 with timezone or an epoch in s/ms/us; got '+repr(ts)[:40])
                if t.tzinfo is None: raise ValueError('Timestamps must include a timezone.')
                latency=float(r['latency_ms'])
                if not math.isfinite(latency) or latency<0: raise ValueError('Latency must be finite and non-negative.')
                item={str(k):str(v) for k,v in r.items()}
                item.update(timestamp=t.astimezone(timezone.utc).isoformat(),latency_ms=latency)
                canonical.append(item)
        except (UnicodeError, json.JSONDecodeError, TypeError, OverflowError) as e:
            raise ValueError('Invalid CSV/JSON log data.') from e
        # Exact normalized row duplicates only: repeated event IDs with different data survive.
        # Tuple fingerprints avoid json.dumps on every row while preserving exact-match semantics.
        unique={tuple(sorted(r.items())):r for r in canonical}
        clean=list(unique.values())
        values=[]; symbols=set(); oldest=newest=None
        for r in clean:
            values.append(r['latency_ms']); symbols.add(r['symbol']); ts=r['timestamp']
            if oldest is None or ts<oldest: oldest=ts
            if newest is None or ts>newest: newest=ts
        median=statistics.median(values); mad=statistics.median(abs(v-median) for v in values)
        threshold=max(100,median+6*max(mad,1))
        abnormal=[r for r in clean if r['latency_ms']>threshold or r['status'].upper() in ['ERROR','REJECTED']]
        ranked=sorted(values)
        return clean,dict(rows=len(rows),unique_rows=len(clean),duplicates=len(rows)-len(clean),anomalies=len(abnormal),threshold_ms=round(threshold,2),p95_ms=ranked[min(len(ranked)-1,math.ceil(len(ranked)*.95)-1)],symbols=sorted(symbols),oldest=oldest,newest=newest,sample=abnormal[:8])

class CompressionAgent:
    def run(self,rows,destination):
        destination.mkdir(parents=True,exist_ok=True)
        path=destination/'logs.parquet'
        table=pa.Table.from_pylist(rows)
        pq.write_table(table,path,compression='zstd')
        # Arrow equality avoids materializing the full table as Python dicts.
        if not pq.read_table(path).equals(table): raise ValueError('Parquet round-trip verification failed.')
        return path.stat().st_size

class QueryOptimizationAgent:
    def run(self,analysis,size):
        return dict(partitions=['date'], recommendation='Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.', sql="SELECT symbol, count(*) AS executions, avg(latency_ms) AS latency_ms\nFROM trading_logs\nWHERE date = '2026-09-01'\nGROUP BY symbol;", demo_partitioned=False)

class StorageOptimizationAgent:
    def run(self,analysis,size):
        age=(datetime.now(timezone.utc)-datetime.fromisoformat(analysis['newest'])).days
        eligible=age>=90 and size>=128*1024
        return dict(eligible=eligible,age_days=age,recommendation='Review cold raw logs for archival after 90 days; confirm retention and access requirements.' if eligible else 'Keep raw logs in hot storage. Age or minimum object size does not meet the demo archive policy.',minimum_object_bytes=131072)

class CostAgent:
    def run(self,before,after,queries=1000):
        rate=.023
        scan=lambda b:max(10,math.ceil(b/1_000_000))*1_000_000/1e12*5*queries
        # Raw retained: total storage grows. Query savings may be zero at minimum billing.
        old=before/1e9*rate+scan(before)
        new=(before+after)/1e9*rate+scan(after)
        return dict(before_monthly=old,after_monthly=new,savings_monthly=old-new,queries=queries,raw_retained=True,storage_rate=rate,athena_per_tb=5,assumptions='Illustrative USD rates: $0.023/GB-month, $5/TB scanned, 1,000 full-dataset queries/month, 10 MB/query minimum. Raw originals retained. Excludes requests, ETL, retrieval, tax and archive charges. No partition pruning assumed.', projected_1tb_before=1000*rate+1000*5,projected_1tb_after=(1000+1000*after/before)*rate+1000*5*after/before)

class SupervisorAgent:
    def run(self,data,filename,destination):
        events=[]
        def record(agent,message): events.append(dict(agent=agent,message=message,time=datetime.now(timezone.utc).isoformat()))
        record('Supervisor','Started analysis. Raw evidence will be preserved.')
        rows,analysis=LogAnalysisAgent().run(data,filename)
        record('Log Analysis',f"Validated {analysis['rows']:,} rows; detected {analysis['duplicates']:,} exact duplicates and {analysis['anomalies']:,} anomalous records.")
        sequence=SequenceEvidenceAgent().run(rows)
        record('Sequence Evidence',f"Compared {sequence['tested_cohorts']} cohorts; found {sequence['candidate_count']} candidate sequence changes. Review only; no causal conclusion.")
        after=CompressionAgent().run(rows,destination)
        record('Compression',f'Wrote and round-trip verified Zstandard Parquet: {after:,} bytes.')
        query=QueryOptimizationAgent().run(analysis,after)
        record('Query Optimization',query['recommendation'])
        storage=StorageOptimizationAgent().run(analysis,len(data))
        record('Storage Optimization',storage['recommendation'])
        cost=CostAgent().run(len(data),after)
        record('Cost','Calculated workload estimates including retained raw storage and Athena minimum billing.')
        record('Supervisor','Optimization complete. Archive requires separate approval.' if storage['eligible'] else 'Optimization complete. Archive is not eligible.')
        return dict(sequence_evidence=sequence,incidents=incidents(rows,analysis['threshold_ms']),analysis=analysis,before_bytes=len(data),after_bytes=after,reduction_pct=round((1-after/len(data))*100,1),query=query,storage=storage,cost=cost,events=events)
