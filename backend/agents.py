"""Deterministic, evidence-driven agents. No LLM or AWS credentials required."""
import csv, io, json, math, random, statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path
from .planning import incidents
import pyarrow as pa
import pyarrow.parquet as pq

NAMES = ['Supervisor', 'Log Analysis', 'Storage Optimization', 'Compression', 'Query Optimization', 'Cost']
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
                t=datetime.fromisoformat(str(r['timestamp']).replace('Z','+00:00'))
                if t.tzinfo is None: raise ValueError('Timestamps must include a timezone.')
                latency=float(r['latency_ms'])
                if not math.isfinite(latency) or latency<0: raise ValueError('Latency must be finite and non-negative.')
                item={str(k):str(v) for k,v in r.items()}
                item.update(timestamp=t.astimezone(timezone.utc).isoformat(),latency_ms=latency)
                canonical.append(item)
        except (UnicodeError, json.JSONDecodeError, TypeError, OverflowError) as e:
            raise ValueError('Invalid CSV/JSON log data.') from e
        # Exact normalized row duplicates only: repeated event IDs with different data survive.
        unique={json.dumps(r,sort_keys=True):r for r in canonical}
        clean=list(unique.values()); values=[r['latency_ms'] for r in clean]
        median=statistics.median(values); mad=statistics.median(abs(v-median) for v in values)
        threshold=max(100,median+6*max(mad,1))
        abnormal=[r for r in clean if r['latency_ms']>threshold or r['status'].upper() in ['ERROR','REJECTED']]
        return clean,dict(rows=len(rows),unique_rows=len(clean),duplicates=len(rows)-len(clean),anomalies=len(abnormal),threshold_ms=round(threshold,2),p95_ms=sorted(values)[min(len(values)-1,math.ceil(len(values)*.95)-1)],symbols=sorted(set(r['symbol'] for r in clean)),oldest=min(r['timestamp'] for r in clean),newest=max(r['timestamp'] for r in clean),sample=abnormal[:8])

class CompressionAgent:
    def run(self,rows,destination):
        destination.mkdir(parents=True,exist_ok=True)
        table=pa.Table.from_pylist(rows)
        pq.write_table(table,destination/'logs.parquet',compression='zstd')
        restored=pq.read_table(destination/'logs.parquet')
        if restored.to_pylist()!=rows: raise ValueError('Parquet round-trip verification failed.')
        return (destination/'logs.parquet').stat().st_size

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
        after=CompressionAgent().run(rows,destination)
        record('Compression',f'Wrote and round-trip verified Zstandard Parquet: {after:,} bytes.')
        query=QueryOptimizationAgent().run(analysis,after)
        record('Query Optimization',query['recommendation'])
        storage=StorageOptimizationAgent().run(analysis,len(data))
        record('Storage Optimization',storage['recommendation'])
        cost=CostAgent().run(len(data),after)
        record('Cost','Calculated workload estimates including retained raw storage and Athena minimum billing.')
        record('Supervisor','Optimization complete. Archive requires separate approval.' if storage['eligible'] else 'Optimization complete. Archive is not eligible.')
        return dict(incidents=incidents(rows,analysis['threshold_ms']),analysis=analysis,before_bytes=len(data),after_bytes=after,reduction_pct=round((1-after/len(data))*100,1),query=query,storage=storage,cost=cost,events=events)
