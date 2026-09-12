"""Multi-asset trade logs and Polars/Python fast-path equivalence."""
import json
import os
from backend.agents import generate, LogAnalysisAgent
from backend.instruments import infer_asset_class, normalize_asset_class, INSTRUMENTS
from backend.fastpath import dedupe_and_profile


def test_generate_covers_all_asset_classes():
    rows = generate('normal', 72)
    classes = {r['asset_class'] for r in rows}
    assert classes == {'equity', 'commodity', 'option', 'crypto'}
    assert all('asset_class' in r and r['symbol'] for r in rows)
    assert {c for c, *_ in INSTRUMENTS} == classes


def test_infer_asset_class_for_uploads_without_field():
    assert infer_asset_class('AAPL') == 'equity'
    assert infer_asset_class('GC') == 'commodity'
    assert infer_asset_class('CLZ5') == 'commodity'
    assert infer_asset_class('AAPL250919C00200000') == 'option'
    assert infer_asset_class('BTCUSDT') == 'crypto'
    assert normalize_asset_class('Equities') == 'equity'
    assert normalize_asset_class('futures') == 'commodity'


def test_log_analysis_infers_asset_class_when_omitted():
    rows = generate('normal', 12)
    for r in rows:
        r.pop('asset_class')
    clean, analysis = LogAnalysisAgent().run(json.dumps(rows).encode(), 'x.json')
    assert all(r['asset_class'] in {'equity', 'commodity', 'option', 'crypto'} for r in clean)
    assert sum(analysis['asset_classes'].values()) == analysis['unique_rows']


def test_polars_and_python_fastpath_match():
    rows = generate('duplicates', 400)
    clean, analysis = LogAnalysisAgent().run(json.dumps(rows).encode(), 'x.json')
    # Re-run profile engines directly on the canonicalized clean+dup mix.
    # Use agent canonicalization first to match production dtypes.
    canonical = clean + clean[:20]
    os.environ['TRADEOPS_FORCE_PYTHON_FASTPATH'] = '1'
    py_clean, py_profile = dedupe_and_profile(canonical)
    os.environ['TRADEOPS_FORCE_PYTHON_FASTPATH'] = '0'
    pl_clean, pl_profile = dedupe_and_profile(canonical)
    assert py_profile['engine'] == 'python'
    assert pl_profile['engine'] == 'polars'
    assert {tuple(sorted(r.items())) for r in py_clean} == {tuple(sorted(r.items())) for r in pl_clean}
    for key in ('unique_rows', 'anomalies', 'threshold_ms', 'p95_ms', 'asset_classes', 'symbols'):
        assert py_profile[key] == pl_profile[key]
    assert analysis['engine'] in {'polars', 'python'}
