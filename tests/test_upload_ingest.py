"""Upload path: gzip + schema aliases must still run full analysis."""
import gzip, json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend import app as module
from backend import store
from backend.agents import generate


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(module, 'DATA', tmp_path)
    store._ready.clear()
    with TestClient(module.app) as c:
        yield c


def test_upload_json_gz_runs_calculations(client):
    rows = generate('duplicates', 100)
    raw = gzip.compress(json.dumps(rows).encode())
    r = client.post('/api/upload', files={'file': ('logs.json.gz', raw, 'application/gzip')})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body['analysis']['rows'] == 115
    assert body['analysis']['duplicates'] == 15
    assert body['analysis']['unique_rows'] == 100
    assert body['before_bytes'] > body['after_bytes']
    assert body['reduction_pct'] > 0
    assert 'cost' in body and 'storage' in body and 'query' in body


def test_upload_wrapped_and_aliased_json(client):
    # Deep-copy: generate() appends duplicate rows by reference.
    rows = [dict(r) for r in generate(count=25)]
    for row in rows:
        row['latency'] = row.pop('latency_ms')
        row['id'] = row.pop('event_id')
        row['time'] = row.pop('timestamp')
        row['ticker'] = row.pop('symbol')
    payload = json.dumps({'records': rows}).encode()
    r = client.post('/api/upload', files={'file': ('wrap.json', payload, 'application/json')})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body['analysis']['unique_rows'] == 25
    assert body['analysis']['rows'] == 26
    assert body['reduction_pct'] is not None
    assert 'cost' in body


def test_upload_efficiency_fixture_gz(client):
    path = Path('samples/efficiency/normal-1000.json.gz')
    if not path.exists():
        pytest.skip('efficiency fixture missing')
    r = client.post('/api/upload', files={'file': (path.name, path.read_bytes(), 'application/gzip')})
    assert r.status_code == 200, r.text
    a = r.json()['analysis']
    assert a['rows'] == 1040 and a['unique_rows'] == 1000 and a['duplicates'] == 40
