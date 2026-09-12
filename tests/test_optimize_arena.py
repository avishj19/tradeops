"""Optimization arena: live before/after measurements for the HackCMU pitch."""
import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend import app as module
from backend import optimize_arena
from backend import store


def test_run_arena_reports_measurements():
    result = optimize_arena.run_arena(rows=3000, list_runs=40, workers=16, writes_per_worker=12)
    assert result['kind'] == 'optimize_arena'
    hot = result['measurements']['hotpath']
    listing = result['measurements']['list_shape']
    busy = result['measurements']['contention']
    assert hot['equal_unique'] is True
    # A benchmark can legitimately lose on this host; verify its arithmetic.
    assert hot['before_ms'] >= 0 and hot['after_ms'] >= 0
    assert hot['speedup_x'] == optimize_arena._speedup(hot['before_ms'], hot['after_ms'])
    assert listing['bytes_reduction_pct'] >= 30
    assert busy['before_errors'] > 0
    assert busy['after_errors'] == 0
    assert 'faster' in result['headline']['line'] or 'smaller' in result['headline']['line'] or 'lock' in result['headline']['line']


def test_arena_endpoints(tmp_path, monkeypatch):
    monkeypatch.setattr(module, 'DATA', tmp_path)
    store._ready.clear()
    with TestClient(module.app) as client:
        assert client.get('/api/optimize/arena').status_code == 404
        measured = client.post('/api/optimize/arena').json()
        assert measured['measurements']['contention']['after_errors'] == 0
        latest = client.get('/api/optimize/arena').json()
        assert latest['created'] == measured['created']
        assert (tmp_path / 'optimize-arena-latest.json').exists()
