"""Hardware desk-probe: refresh/input timing linked to platform latency."""
import pytest
from backend.hardware_latency import summarize_hardware_samples


def test_summarize_refresh_and_key_path():
    samples = [
        {'kind': 'frame', 'frame_delta_ms': 8.34, 'refresh_hz': 120},
        {'kind': 'frame', 'frame_delta_ms': 8.32, 'refresh_hz': 120},
        {'kind': 'keydown', 'key_to_frame_ms': 7.5},
        {'kind': 'keydown', 'key_to_frame_ms': 9.0},
        {'kind': 'ack', 'click_to_ack_ms': 11.0},
        {'kind': 'ack', 'click_to_ack_ms': 13.0},
    ]
    s = summarize_hardware_samples(samples, [40.0, 42.0, 41.0])
    assert s['refresh_hz'] == 120
    assert s['key_to_frame_ms']['count'] == 2
    assert s['click_to_ack_ms']['p50'] == 11.0 or s['click_to_ack_ms']['p50'] == 13.0
    assert s['linked_execution']['desk_share_pct'] > 0
    assert 'key' not in s['privacy'].lower() or 'No key' in s['privacy']


def test_rejects_keylogging_fields():
    with pytest.raises(ValueError, match='must not include key'):
        summarize_hardware_samples([{'kind': 'keydown', 'key': 'A', 'key_to_frame_ms': 8}])


def test_hardware_latency_endpoint_links_run(tmp_path, monkeypatch):
    from backend import app as module
    from backend import store
    from fastapi.testclient import TestClient
    monkeypatch.setattr(module, 'DATA', tmp_path)
    store._ready.clear()
    with TestClient(module.app) as client:
        run = client.post('/api/demo', json={'scenario': 'normal', 'format': 'json'}).json()
        body = {
            'run_id': run['id'],
            'workstation': 'test-desk',
            'samples': [
                {'kind': 'frame', 'frame_delta_ms': 16.67, 'refresh_hz': 60},
                {'kind': 'keydown', 'key_to_frame_ms': 10.5},
                {'kind': 'ack', 'click_to_ack_ms': 14.2},
            ],
        }
        assert client.post('/api/hardware-latency/ack').json()['ok'] is True
        res = client.post('/api/hardware-latency', json=body).json()
        assert res['hardware']['refresh_hz'] == 60
        assert res['linked_run_id'] == run['id']
        linked = client.get('/api/runs').json()
        match = next(r for r in linked if r['id'] == run['id'])
        assert match['hardware_latency']['workstation'] == 'test-desk'
        assert match['hardware_latency']['linked_execution']
