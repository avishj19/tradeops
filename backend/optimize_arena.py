"""Live before/after optimization arena for HackCMU pitch demos.

Measures three concrete wins on the same machine, same synthetic workload:
1) hot-path dedupe/profile (naive Python vs Polars when available)
2) run-list payload shape (full JSON hydrate vs lean summaries)
3) SQLite writer contention (naive connects vs hardened store)

Returns numbers suitable for a 3-minute optimization-track pitch.
"""
from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

# ThreadPoolExecutor / as_completed used by contention probes.

from .agents import generate
from .fastpath import _python_dedupe_and_profile
from . import store

ARENA_ROWS = int(os.getenv('TRADEOPS_ARENA_ROWS', '8000'))
ARENA_LIST_RUNS = int(os.getenv('TRADEOPS_ARENA_LIST_RUNS', '120'))
ARENA_WORKERS = int(os.getenv('TRADEOPS_ARENA_WORKERS', '32'))
ARENA_WRITES_PER_WORKER = int(os.getenv('TRADEOPS_ARENA_WRITES_PER_WORKER', '25'))


def _ms(t0: float) -> float:
    return round((time.perf_counter() - t0) * 1000, 2)


def _speedup(before_ms: float, after_ms: float) -> float | None:
    if after_ms <= 0:
        return None
    return round(before_ms / after_ms, 2)


def _canonical_from_generate(n: int) -> list[dict]:
    """Match LogAnalysisAgent scalar normalization without CSV/JSON round-trip cost."""
    rows = generate('duplicates', n)
    out = []
    for r in rows:
        item = {str(k): (str(v) if k != 'latency_ms' else v) for k, v in r.items()}
        item['latency_ms'] = float(r['latency_ms'])
        item['timestamp'] = datetime.fromisoformat(str(r['timestamp']).replace('Z', '+00:00')).astimezone(timezone.utc).isoformat()
        out.append(item)
    return out


def _heavy_run(i: int) -> dict:
    return dict(
        id=f'arena{i:08d}',
        name=f'arena-{i}.json',
        scenario='optimize_arena',
        created='2026-09-01T00:00:00Z',
        approval='pending',
        events=[dict(agent='Supervisor', message='x' * 80, time='2026-09-01T00:00:00Z') for _ in range(40)],
        analysis=dict(
            rows=10000,
            unique_rows=9900,
            duplicates=100,
            anomalies=12,
            p95_ms=18.0,
            threshold_ms=50,
            sample=[{'latency_ms': 1.0, 'symbol': 'AAPL', 'status': 'FILLED'} for _ in range(80)],
            engine='python',
        ),
        gateway=dict(latency_ms=[1.25] * 800),
        aws=dict(embedded=True, live=False, mode='local-mirror', region='us-east-1', keys=['k' * 48] * 20),
        before_bytes=2_000_000,
        after_bytes=400_000,
        reduction_pct=80.0,
        storage=dict(eligible=True, age_days=120, recommendation='Archive cold raw'),
        cost=dict(before_monthly=2.0, after_monthly=0.5, savings_monthly=1.5),
        query=dict(recommendation='Partition by date', sql='SELECT 1'),
    )


def _naive_json_dedupe_and_profile(canonical):
    """Pre-optimization baseline: JSON fingerprint keys (the slow path we replaced)."""
    import math
    import statistics
    from collections import Counter

    unique = {json.dumps(r, sort_keys=True, separators=(',', ':')): r for r in canonical}
    clean = list(unique.values())
    values = []
    symbols = set()
    asset_classes = Counter()
    oldest = newest = None
    for r in clean:
        values.append(r['latency_ms'])
        symbols.add(r['symbol'])
        asset_classes[r.get('asset_class', 'unknown')] += 1
        ts = r['timestamp']
        if oldest is None or ts < oldest:
            oldest = ts
        if newest is None or ts > newest:
            newest = ts
    median = statistics.median(values)
    mad = statistics.median(abs(v - median) for v in values)
    threshold = max(100, median + 6 * max(mad, 1))
    abnormal = [r for r in clean if r['latency_ms'] > threshold or r['status'].upper() in ['ERROR', 'REJECTED']]
    ranked = sorted(values)
    return clean, dict(
        unique_rows=len(clean),
        anomalies=len(abnormal),
        threshold_ms=round(threshold, 2),
        p95_ms=ranked[min(len(ranked) - 1, math.ceil(len(ranked) * .95) - 1)],
        symbols=sorted(symbols),
        asset_classes=dict(sorted(asset_classes.items())),
        oldest=oldest,
        newest=newest,
        sample=abnormal[:8],
        engine='python-json-fingerprint',
    )


def measure_hotpath(rows: int = ARENA_ROWS) -> dict:
    canonical = _canonical_from_generate(rows)
    t0 = time.perf_counter()
    clean_b, profile_b = _naive_json_dedupe_and_profile(canonical)
    before_ms = _ms(t0)

    t1 = time.perf_counter()
    clean_a, profile_a = _python_dedupe_and_profile(canonical)
    after_ms = _ms(t1)

    # Optional Polars timing (informational). Not used as the headline "after"
    # when it loses to tuple fingerprints on this machine/workload.
    polars = None
    try:
        from .fastpath import _polars_dedupe_and_profile
        t2 = time.perf_counter()
        _, profile_p = _polars_dedupe_and_profile(canonical)
        polars = dict(ms=_ms(t2), engine=profile_p.get('engine', 'polars'))
    except Exception as e:
        polars = dict(ms=None, engine=None, error=type(e).__name__)

    return dict(
        name='hotpath_dedupe_profile',
        rows_in=len(canonical),
        unique_before=profile_b['unique_rows'],
        unique_after=profile_a['unique_rows'],
        engine_before=profile_b.get('engine', 'python-json-fingerprint'),
        engine_after=profile_a.get('engine', 'python'),
        before_ms=before_ms,
        after_ms=after_ms,
        speedup_x=_speedup(before_ms, after_ms),
        equal_unique=profile_b['unique_rows'] == profile_a['unique_rows'] == len(clean_b) == len(clean_a),
        polars=polars,
        pitch='Same synthetic fills: json.dumps fingerprints vs tuple fingerprints (the measured hot-path win).',
    )


def measure_list_shape(n_runs: int = ARENA_LIST_RUNS) -> dict:
    root = Path(tempfile.mkdtemp(prefix='tradeops-arena-list-'))
    desk = 'arena-list'
    store._ready.clear()
    for i in range(n_runs):
        store.save_run(root, _heavy_run(i), desk)
    path = store.db_path(root, desk)

    t0 = time.perf_counter()
    with store.connect(path) as conn:
        full = [json.loads(p) for (p,) in conn.execute('SELECT payload FROM runs ORDER BY rowid DESC')]
    full_ms = _ms(t0)
    full_bytes = len(json.dumps(full, separators=(',', ':')))

    t1 = time.perf_counter()
    summaries = store.list_run_summaries(root, desk)
    summary_ms = _ms(t1)
    summary_bytes = len(json.dumps(summaries, separators=(',', ':')))

    return dict(
        name='run_list_shape',
        runs=n_runs,
        before_ms=full_ms,
        after_ms=summary_ms,
        before_bytes=full_bytes,
        after_bytes=summary_bytes,
        bytes_reduction_pct=round(100 * (1 - summary_bytes / max(full_bytes, 1)), 1),
        speedup_x=_speedup(full_ms, summary_ms),
        pitch='Listing history without shipping every sample array / gateway vector / AWS key blob.',
    )


def _naive_write_errors(path: Path, workers: int, writes: int) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    boot = sqlite3.connect(str(path), timeout=0.05)
    boot.execute('CREATE TABLE runs (id TEXT PRIMARY KEY, payload TEXT NOT NULL)')
    boot.commit()
    boot.close()
    errs: list[str] = []
    ok = 0

    def worker(wid: int):
        local_ok = 0
        local_err = []
        for i in range(writes):
            try:
                # Intentionally weak: tiny timeout, no busy_timeout pragma, no process lock.
                c = sqlite3.connect(str(path), timeout=0.05)
                c.execute(
                    'INSERT OR REPLACE INTO runs(id, payload) VALUES (?,?)',
                    (f'{wid}-{i}', json.dumps(_heavy_run(wid * 1000 + i))),
                )
                c.commit()
                c.close()
                local_ok += 1
            except Exception as e:
                local_err.append(f'{type(e).__name__}: {e}')
        return local_ok, local_err

    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(worker, w) for w in range(workers)]
        for f in as_completed(futs):
            o, e = f.result()
            ok += o
            errs.extend(e)
    return dict(ms=_ms(t0), ok=ok, errors=len(errs), sample=errs[:3])


def _hardened_write_errors(root: Path, desk: str, workers: int, writes: int) -> dict:
    store._ready.clear()
    store.connect(store.db_path(root, desk)).close()
    errs: list[str] = []
    ok = 0
    lock = threading.Lock()

    def worker(wid: int):
        local_ok = 0
        local_err = []
        for i in range(writes):
            try:
                store.save_run(root, _heavy_run(wid * 1000 + i), desk)
                local_ok += 1
            except Exception as e:
                local_err.append(f'{type(e).__name__}: {e}')
        return local_ok, local_err

    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(worker, w) for w in range(workers)]
        for f in as_completed(futs):
            o, e = f.result()
            with lock:
                ok += o
                errs.extend(e)
    return dict(ms=_ms(t0), ok=ok, errors=len(errs), sample=errs[:3])


def measure_contention(workers: int = ARENA_WORKERS, writes: int = ARENA_WRITES_PER_WORKER) -> dict:
    tmp = Path(tempfile.mkdtemp(prefix='tradeops-arena-busy-'))
    naive = _naive_write_errors(tmp / 'naive.db', workers, writes)
    hardened = _hardened_write_errors(tmp / 'hardened', 'arena-busy', workers, writes)
    return dict(
        name='sqlite_contention',
        workers=workers,
        writes_per_worker=writes,
        before_errors=naive['errors'],
        after_errors=hardened['errors'],
        before_ok=naive['ok'],
        after_ok=hardened['ok'],
        before_ms=naive['ms'],
        after_ms=hardened['ms'],
        before_sample=naive['sample'],
        after_sample=hardened['sample'],
        error_reduction=max(0, naive['errors'] - hardened['errors']),
        pitch='Concurrent desk writers: naive SQLite fails open; hardened WAL + busy_timeout + write lock absorbs the same load.',
    )


def headline(hot: dict, listing: dict, busy: dict) -> dict:
    parts = []
    if hot.get('speedup_x') and hot['speedup_x'] >= 1.05:
        parts.append(f"{hot['speedup_x']}× faster log dedupe/profile")
    if listing.get('bytes_reduction_pct', 0) >= 5:
        parts.append(f"{listing['bytes_reduction_pct']}% smaller run-list payloads")
    if busy.get('before_errors', 0) > 0 and busy.get('after_errors', 0) == 0:
        parts.append(f"{busy['before_errors']}→0 lock errors under {busy['workers']} writers")
    elif busy.get('error_reduction', 0) > 0:
        parts.append(f"{busy['error_reduction']} fewer lock errors under contention")
    if not parts:
        parts.append('Measured local optimizations (hot path, list shape, SQLite contention)')
    return dict(
        line=' · '.join(parts),
        track_fit='Optimization: find bottleneck → measure → fix → re-measure on the same machine.',
    )


def run_arena(
    rows: int = ARENA_ROWS,
    list_runs: int = ARENA_LIST_RUNS,
    workers: int = ARENA_WORKERS,
    writes_per_worker: int = ARENA_WRITES_PER_WORKER,
) -> dict:
    t0 = time.perf_counter()
    hot = measure_hotpath(rows)
    listing = measure_list_shape(list_runs)
    busy = measure_contention(workers, writes_per_worker)
    return dict(
        kind='optimize_arena',
        created=datetime.now(timezone.utc).isoformat(),
        elapsed_ms=_ms(t0),
        headline=headline(hot, listing, busy),
        measurements=dict(hotpath=hot, list_shape=listing, contention=busy),
        honesty=[
            'Numbers are from this host, this process, synthetic logs — not exchange NIC timestamps.',
            'Hot-path before uses json.dumps fingerprints; after uses tuple fingerprints (production Python path).',
            'Polars timing is reported when importable, but is not the headline if it loses on this workload.',
            'Contention uses an intentionally weak naive baseline to show the failure class we fixed.',
        ],
        pitch_script=[
            '1. Show before: Python hot path + full JSON list + lock errors under concurrent writers.',
            '2. Click Run live measurement once — three metrics re-measure on this machine.',
            '3. Close on the headline string: faster kernel, leaner list, zero lock errors.',
        ],
    )


def persist_latest(data_root: Path, result: dict) -> Path:
    path = Path(data_root) / 'optimize-arena-latest.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2))
    return path


def load_latest(data_root: Path) -> dict | None:
    path = Path(data_root) / 'optimize-arena-latest.json'
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None
