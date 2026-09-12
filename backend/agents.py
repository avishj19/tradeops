"""Deterministic, evidence-driven agents. No LLM or AWS credentials required."""
import csv, io, json, math, random, statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path
from .planning import incidents
from .sequences import SequenceEvidenceAgent
from .instruments import INSTRUMENTS, infer_asset_class, normalize_asset_class
from .fastpath import dedupe_and_profile
from .ingest import parse_log_records
import pyarrow as pa
import pyarrow.parquet as pq

NAMES = ['Supervisor', 'Log Analysis', 'Storage Optimization', 'Compression', 'Query Optimization', 'Cost', 'Sequence Evidence']
REQUIRED = {'timestamp', 'event_id', 'symbol', 'latency_ms', 'status'}

def generate(scenario='normal', count=10000):
    """Synthetic multi-asset execution logs: equities, commodities, options, crypto."""
    rng = random.Random(42)
    base = datetime.now(timezone.utc).replace(hour=9, minute=30, second=0, microsecond=0)-timedelta(days=95)
    rows=[]
    for i in range(count):
        incident = scenario=='latency_spike' and i > count*.8
        asset_class, symbol, lo, hi = INSTRUMENTS[i % len(INSTRUMENTS)]
        # Rotate strategies slightly by asset class so sequence cohorts stay meaningful.
        strategy = {'equity':'momentum','commodity':'roll-carry','option':'vol-surface','crypto':'market-making'}[asset_class]
        if rng.random() < .25:
            strategy = rng.choice(['momentum','market-making','roll-carry','vol-surface'])
        qty = rng.randint(1, 20) if asset_class == 'option' else rng.randint(1, 500)
        rows.append(dict(
            timestamp=(base+timedelta(seconds=i*10)).isoformat(),
            event_id=f'EX-{i:08}',
            asset_class=asset_class,
            symbol=symbol,
            latency_ms=round(rng.uniform(400,1200) if incident else rng.uniform(3,45),2),
            status='ERROR' if incident and i%3==0 else 'FILLED',
            quantity=qty,
            price=round(rng.uniform(float(lo), float(hi)), 6 if asset_class == 'crypto' else 2),
            source='execution-gateway',
            strategy=strategy,
        ))
    rows += rows[:int(count*(.15 if scenario=='duplicates' else .04))]
    return rows

class LogAnalysisAgent:
    def run(self, data, filename):
        try:
            rows=parse_log_records(data, filename)
            canonical=[]
            columns=set(rows[0])
            has_asset_class='asset_class' in columns or 'assetClass' in columns
            for r in rows:
                if set(r)!=columns:
                    raise ValueError('Records must have consistent columns.')
                if not REQUIRED.issubset(r): raise ValueError('Required columns: '+', '.join(sorted(REQUIRED))+' (aliases like latency, id, time, ticker are accepted).')
                # Reject nested/null required values.
                if any(r.get(k) is None or isinstance(r.get(k),(list,dict)) for k in REQUIRED):
                    raise ValueError('Required fields must be non-null scalars.')
                if any(not str(r[k]).strip() for k in REQUIRED):
                    raise ValueError('Required fields cannot be empty.')
                ts=r['timestamp']
                if isinstance(ts,(int,float)) or (isinstance(ts,str) and str(ts).isdigit()):
                    n=int(ts);unit=1000000 if n>=100000000000000 else (1000 if n>=100000000000 else 1)
                    t=datetime.fromtimestamp(n/unit,tz=timezone.utc)
                else:
                    try:t=datetime.fromisoformat(str(ts).replace('Z','+00:00'))
                    except ValueError:raise ValueError('Timestamps must be ISO-8601 with timezone or an epoch in s/ms/us; got '+repr(ts)[:40])
                if t.tzinfo is None: raise ValueError('Timestamps must include a timezone.')
                latency=float(r['latency_ms'])
                if not math.isfinite(latency) or latency<0: raise ValueError('Latency must be finite and non-negative.')
                item={str(k):str(v) for k,v in r.items() if v is not None and not isinstance(v,(list,dict))}
                item.update(timestamp=t.astimezone(timezone.utc).isoformat(),latency_ms=latency)
                # Embed or infer asset class so equities/commodities/options/crypto stay labeled.
                if has_asset_class and (r.get('asset_class') is not None or r.get('assetClass') is not None):
                    item['asset_class']=normalize_asset_class(r.get('asset_class', r.get('assetClass')))
                else:
                    item['asset_class']=infer_asset_class(item['symbol'])
                canonical.append(item)
        except (UnicodeError, TypeError, OverflowError) as e:
            raise ValueError('Invalid CSV/JSON log data.') from e
        except ValueError:
            raise
        # Exact normalized row duplicates only: repeated event IDs with different data survive.
        # Polars (Rust) fast path when available; pure-Python fallback otherwise.
        clean, profile = dedupe_and_profile(canonical)
        # Always include sample list so the UI can render anomaly tables safely.
        profile.setdefault('sample', [])
        return clean, dict(rows=len(rows), duplicates=len(rows)-profile['unique_rows'], **profile)

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
        return dict(partitions=['date','asset_class'], recommendation='Partition production datasets by UTC date and asset_class (equity, commodity, option, crypto). Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.', sql="SELECT asset_class, symbol, count(*) AS executions, avg(latency_ms) AS latency_ms\nFROM trading_logs\nWHERE date = '2026-09-01'\nGROUP BY asset_class, symbol\nORDER BY asset_class, executions DESC;", demo_partitioned=False)

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
