#!/usr/bin/env python3
"""Progressive multi-desk SQLite stress for TradeOps MVP.

Raises the number of desk databases and concurrent writers until contention
shows up, then reports whether the hardened store absorbs it.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend import store  # noqa: E402


def fake_run(i: int, heavy: bool = False) -> dict:
    lat_n = 2000 if heavy else 50
    events_n = 80 if heavy else 10
    return dict(
        id=f'run{i:08d}',
        name=f'log-{i}.json',
        scenario='stress',
        created='2026-09-01T00:00:00Z',
        approval='pending',
        events=[dict(agent='Supervisor', message='x' * 40, time='2026-09-01T00:00:00Z') for _ in range(events_n)],
        analysis=dict(rows=10000, unique_rows=9990, duplicates=10, anomalies=5, p95_ms=12.0, threshold_ms=50, sample=[{'latency_ms': 1}] * (200 if heavy else 5)),
        gateway=dict(latency_ms=[1.2] * lat_n),
        aws=dict(embedded=True, live=False, mode='local-mirror', region='us-east-1', keys=['k' * 40] * (30 if heavy else 3)),
        before_bytes=1_000_000,
        after_bytes=250_000,
        reduction_pct=75.0,
        storage=dict(eligible=True, age_days=3, recommendation='Archive cold raw'),
        cost=dict(before_monthly=1.0, after_monthly=0.4, savings_monthly=0.6),
        query=dict(recommendation='Partition by date', sql='SELECT 1'),
    )


def phase_scale_desks(root: Path, counts: list[int]) -> list[dict]:
    results = []
    for n in counts:
        store._ready.clear()
        t0 = time.perf_counter()
        try:
            for d in range(n):
                desk = f'desk{d:04d}'
                path = store.db_path(root, desk)
                store.save_run(root, fake_run(d), desk)
                # a few more writes
                for j in range(4):
                    store.save_run(root, fake_run(d * 10 + j + 1), desk)
            listed = 0
            for d in range(n):
                listed += len(store.list_run_summaries(root, f'desk{d:04d}'))
            dt = time.perf_counter() - t0
            row = dict(phase='scale_desks', n_dbs=n, listed=listed, sec=round(dt, 3), ok=True)
            print(json.dumps(row))
            results.append(row)
        except Exception as e:
            row = dict(phase='scale_desks', n_dbs=n, ok=False, error=f'{type(e).__name__}: {e}', sec=round(time.perf_counter() - t0, 3))
            print(json.dumps(row))
            results.append(row)
            break
    return results


def phase_contention(root: Path, workers_list: list[int]) -> list[dict]:
    results = []
    for workers in workers_list:
        store._ready.clear()
        desk = f'busy{workers}'
        path = store.db_path(root, desk)
        store.connect(path).close()
        errs: list[str] = []

        def writer(wid: int):
            local = []
            for i in range(40):
                try:
                    store.save_run(root, fake_run(wid * 1000 + i, heavy=True), desk)
                except Exception as e:
                    local.append(f'{type(e).__name__}: {e}')
            return local

        def reader(_rid: int):
            local = []
            for _ in range(20):
                try:
                    store.list_run_summaries(root, desk)
                except Exception as e:
                    local.append(f'{type(e).__name__}: {e}')
            return local

        t0 = time.perf_counter()
        with ThreadPoolExecutor(max_workers=workers * 2) as ex:
            futs = [ex.submit(writer, w) for w in range(workers)]
            futs += [ex.submit(reader, r) for r in range(workers)]
            for f in as_completed(futs):
                errs.extend(f.result())
        n = len(store.list_run_summaries(root, desk))
        row = dict(
            phase='contention',
            workers=workers,
            runs=n,
            errs=len(errs),
            sample=errs[:2],
            sec=round(time.perf_counter() - t0, 3),
            ok=len(errs) == 0,
        )
        print(json.dumps(row))
        results.append(row)
        if len(errs) > workers // 2:
            break
    return results


def phase_list_shape(root: Path, n_runs: int = 500) -> dict:
    store._ready.clear()
    desk = 'listshape'
    for i in range(n_runs):
        store.save_run(root, fake_run(i, heavy=True), desk)
    t0 = time.perf_counter()
    summaries = store.list_run_summaries(root, desk)
    summary_s = time.perf_counter() - t0
    path = store.db_path(root, desk)
    t1 = time.perf_counter()
    with store.connect(path) as conn:
        full = [json.loads(r[0]) for r in conn.execute('SELECT payload FROM runs')]
    full_s = time.perf_counter() - t1
    s_bytes = sum(len(json.dumps(x)) for x in summaries)
    f_bytes = sum(len(json.dumps(x)) for x in full)
    row = dict(
        phase='list_shape',
        n=n_runs,
        summary_s=round(summary_s, 3),
        full_s=round(full_s, 3),
        summary_bytes=s_bytes,
        full_bytes=f_bytes,
        reduction_pct=round(100 * (1 - s_bytes / max(f_bytes, 1)), 1),
        ok=summary_s <= full_s and s_bytes < f_bytes * 0.5,
    )
    print(json.dumps(row))
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='')
    args = ap.parse_args()
    root = Path(args.root) if args.root else Path(tempfile.mkdtemp(prefix='tradeops-mvp-db-'))
    root.mkdir(parents=True, exist_ok=True)
    print(json.dumps(dict(root=str(root))))
    out = []
    out += phase_scale_desks(root, [1, 8, 32, 128, 512, 1024])
    out += phase_contention(root, [8, 16, 32, 64])
    out.append(phase_list_shape(root, 400))
    failed = [r for r in out if not r.get('ok', True)]
    print(json.dumps(dict(failed=len(failed), total=len(out), mvp_ok=len(failed) == 0)))
    return 0 if not failed else 1


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc()
        raise SystemExit(2)
