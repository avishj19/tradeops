"""Build fixed execution-log fixtures for efficiency / SupervisorAgent testing.

Matches backend.agents.generate row semantics with a frozen base timestamp so
hashes and anomaly counts stay stable across calendar days.

  python3 scripts/make_efficiency_dataset.py
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'samples' / 'efficiency'
AS_OF = datetime(2026, 9, 12, tzinfo=timezone.utc)
BASE = AS_OF.replace(hour=9, minute=30, second=0, microsecond=0) - timedelta(days=95)
SEED = 42
DATASETS = {
    'latency-spike-10k': ('latency_spike', 10000),
    'duplicates-1500': ('duplicates', 1500),
    'normal-1000': ('normal', 1000),
}


def generate(scenario: str = 'latency_spike', count: int = 10000) -> list[dict]:
    rng = random.Random(SEED)
    rows = []
    for i in range(count):
        incident = scenario == 'latency_spike' and i > count * 0.8
        rows.append(dict(
            timestamp=(BASE + timedelta(seconds=i * 10)).isoformat(),
            event_id=f'EX-{i:08}',
            symbol=rng.choice(['AAPL', 'MSFT', 'NVDA', 'SPY']),
            latency_ms=round(rng.uniform(400, 1200) if incident else rng.uniform(3, 45), 2),
            status='ERROR' if incident and i % 3 == 0 else 'FILLED',
            quantity=rng.randint(1, 500),
            price=round(rng.uniform(100, 800), 2),
            source='execution-gateway',
            strategy=rng.choice(['momentum', 'market-making']),
        ))
    rows += rows[: int(count * (0.15 if scenario == 'duplicates' else 0.04))]
    return rows


def write() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {
        'purpose': 'Fixed execution-log fixtures for TradeOps efficiency / SupervisorAgent regression testing.',
        'schema_required': sorted(['timestamp', 'event_id', 'symbol', 'latency_ms', 'status']),
        'generator': 'scripts/make_efficiency_dataset.py',
        'as_of_utc': AS_OF.isoformat(),
        'base_timestamp_utc': BASE.isoformat(),
        'seed': SEED,
        'note': 'Invented demo executions, not real market or brokerage activity. Matches backend.agents.generate semantics with a frozen base date.',
        'expected_latency_spike_10k': {
            'rows': 10400,
            'unique_rows': 10000,
            'duplicates': 400,
            'anomalies': 1999,
            'threshold_ms': 108.72,
            'p95_ms': 1002.95,
            'sequence_candidates': 22,
            'tested_cohorts': 8,
            'incident_kinds': {'execution_errors': 667, 'latency_spike': 1332},
        },
        'files': {},
    }
    for name, (scenario, count) in DATASETS.items():
        rows = generate(scenario, count)
        raw = json.dumps(rows, separators=(',', ':')).encode()
        gz_path = OUT / f'{name}.json.gz'
        gz_path.write_bytes(gzip.compress(raw, compresslevel=9))
        if len(raw) < 400_000:
            (OUT / f'{name}.json').write_bytes(raw)
        entry = {
            'scenario': scenario,
            'unique_generated': count,
            'rows': len(rows),
            'expected_duplicates': len(rows) - count,
            'bytes_json': len(raw),
            'bytes_json_gz': gz_path.stat().st_size,
            'sha256_json': hashlib.sha256(raw).hexdigest(),
            'sha256_json_gz': hashlib.sha256(gz_path.read_bytes()).hexdigest(),
            'first_timestamp': rows[0]['timestamp'],
            'last_unique_timestamp': rows[count - 1]['timestamp'],
            'symbols': sorted({r['symbol'] for r in rows}),
        }
        if name == 'latency-spike-10k':
            buf = io.StringIO()
            fields = list(rows[0].keys())
            writer = csv.DictWriter(buf, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
            csv_bytes = buf.getvalue().encode()
            csv_gz = OUT / f'{name}.csv.gz'
            csv_gz.write_bytes(gzip.compress(csv_bytes, compresslevel=9))
            entry.update(
                sha256_csv=hashlib.sha256(csv_bytes).hexdigest(),
                sha256_csv_gz=hashlib.sha256(csv_gz.read_bytes()).hexdigest(),
                bytes_csv=len(csv_bytes),
                bytes_csv_gz=csv_gz.stat().st_size,
            )
        manifest['files'][name] = entry
        print(f'{name}: {entry["rows"]} rows, {entry["bytes_json_gz"]} byte gz')
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


if __name__ == '__main__':
    write()
