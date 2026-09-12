"""Regression tests against the fixed efficiency execution-log fixtures."""
import gzip, json
from pathlib import Path
import pytest
from backend.agents import SupervisorAgent, LogAnalysisAgent

ROOT = Path(__file__).resolve().parents[1] / 'samples' / 'efficiency'
MANIFEST = json.loads((ROOT / 'manifest.json').read_text())


def load_json(name: str) -> bytes:
    path = ROOT / f'{name}.json.gz'
    return gzip.open(path, 'rb').read()


def test_manifest_hashes_match_files():
    for name, meta in MANIFEST['files'].items():
        raw = load_json(name)
        import hashlib
        assert hashlib.sha256(raw).hexdigest() == meta['sha256_json']
        assert hashlib.sha256((ROOT / f'{name}.json.gz').read_bytes()).hexdigest() == meta['sha256_json_gz']
        assert len(json.loads(raw)) == meta['rows']


def test_latency_spike_log_analysis_metrics():
    expected = MANIFEST['expected_latency_spike_10k']
    data = load_json('latency-spike-10k')
    _, analysis = LogAnalysisAgent().run(data, 'latency-spike-10k.json')
    assert analysis['rows'] == expected['rows']
    assert analysis['unique_rows'] == expected['unique_rows']
    assert analysis['duplicates'] == expected['duplicates']
    assert analysis['anomalies'] == expected['anomalies']
    assert analysis['threshold_ms'] == expected['threshold_ms']
    assert analysis['p95_ms'] == expected['p95_ms']
    assert analysis['symbols'] == ['AAPL', 'MSFT', 'NVDA', 'SPY']


def test_latency_spike_supervisor_pipeline(tmp_path):
    expected = MANIFEST['expected_latency_spike_10k']
    data = load_json('latency-spike-10k')
    result = SupervisorAgent().run(data, 'latency-spike-10k.json', tmp_path)
    assert result['analysis']['duplicates'] == expected['duplicates']
    assert result['analysis']['anomalies'] == expected['anomalies']
    assert result['sequence_evidence']['candidate_count'] == expected['sequence_candidates']
    assert result['sequence_evidence']['tested_cohorts'] == expected['tested_cohorts']
    kinds = {i['kind']: i['count'] for i in result['incidents']}
    assert kinds == expected['incident_kinds']
    assert (tmp_path / 'logs.parquet').exists()
    assert result['after_bytes'] > 0


@pytest.mark.parametrize('name', ['duplicates-1500', 'normal-1000'])
def test_companion_fixtures_parse(name, tmp_path):
    meta = MANIFEST['files'][name]
    data = load_json(name)
    result = SupervisorAgent().run(data, f'{name}.json', tmp_path)
    assert result['analysis']['rows'] == meta['rows']
    assert result['analysis']['duplicates'] == meta['expected_duplicates']
