"""Optional Polars (Rust) kernels for log dedupe/profile, with a pure-Python fallback."""
import math
import os
import statistics
from collections import Counter


def _python_dedupe_and_profile(canonical):
    # First-seen key order, last-seen values — matches the historical dict comprehension.
    unique = {tuple(sorted(r.items())): r for r in canonical}
    clean = list(unique.values())
    values = []; symbols = set(); asset_classes = Counter(); oldest = newest = None
    for r in clean:
        values.append(r['latency_ms']); symbols.add(r['symbol'])
        asset_classes[r.get('asset_class', 'unknown')] += 1
        ts = r['timestamp']
        if oldest is None or ts < oldest: oldest = ts
        if newest is None or ts > newest: newest = ts
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
        engine='python',
    )


def _polars_dedupe_and_profile(canonical):
    import polars as pl
    df = pl.from_dicts(canonical)
    # keep='last' + maintain_order=True mirrors dict-comprehension semantics.
    clean_df = df.unique(maintain_order=True, keep='last')
    values = clean_df['latency_ms'].to_list()
    median = statistics.median(values)
    mad = statistics.median(abs(v - median) for v in values)
    threshold = max(100, median + 6 * max(mad, 1))
    status = clean_df['status'].str.to_uppercase()
    mask = (clean_df['latency_ms'] > threshold) | status.is_in(['ERROR', 'REJECTED'])
    abnormal_df = clean_df.filter(mask)
    ranked = sorted(values)
    if 'asset_class' in clean_df.columns:
        asset_classes = dict(sorted(Counter(clean_df['asset_class'].to_list()).items()))
    else:
        asset_classes = {}
    clean = clean_df.to_dicts()
    abnormal = abnormal_df.to_dicts()
    return clean, dict(
        unique_rows=len(clean),
        anomalies=len(abnormal),
        threshold_ms=round(threshold, 2),
        p95_ms=ranked[min(len(ranked) - 1, math.ceil(len(ranked) * .95) - 1)],
        symbols=sorted(clean_df['symbol'].unique().to_list()),
        asset_classes=asset_classes,
        oldest=clean_df['timestamp'].min(),
        newest=clean_df['timestamp'].max(),
        sample=abnormal[:8],
        engine='polars',
    )


def dedupe_and_profile(canonical):
    """Exact-row dedupe plus latency profile. Prefer Polars when available."""
    if not canonical:
        raise ValueError('Provide 1–200,000 log records.')
    force_python = os.environ.get('TRADEOPS_FORCE_PYTHON_FASTPATH', '').strip() in {'1', 'true', 'yes'}
    if not force_python:
        try:
            return _polars_dedupe_and_profile(canonical)
        except Exception:
            pass
    return _python_dedupe_and_profile(canonical)
