import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest
from fastapi.testclient import TestClient

from backend import app as module
from backend import store


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(module, 'DATA', tmp_path)
    store._ready.clear()
    with TestClient(module.app) as c:
        yield c


def test_runs_list_is_summary_not_full_sample(client):
    run = client.post('/api/demo', json={'scenario': 'duplicates', 'format': 'json'}).json()
    assert 'analysis' in run and 'sample' in run['analysis']
    listed = client.get('/api/runs').json()
    assert listed and listed[0]['id'] == run['id']
    assert listed[0].get('_summary') is True
    assert 'sample' not in (listed[0].get('analysis') or {})
    full = client.get(f"/api/runs/{run['id']}/report").json()
    assert 'sample' in full['analysis']


def test_multi_desk_isolation(client):
    a = client.post('/api/demo', json={}, headers={'X-TradeOps-Desk': 'alpha'}).json()
    b = client.post('/api/demo', json={}, headers={'X-TradeOps-Desk': 'beta'}).json()
    assert a['id'] != b['id']
    alpha = client.get('/api/runs', headers={'X-TradeOps-Desk': 'alpha'}).json()
    beta = client.get('/api/runs', headers={'X-TradeOps-Desk': 'beta'}).json()
    assert [r['id'] for r in alpha] == [a['id']]
    assert [r['id'] for r in beta] == [b['id']]
    desks = client.get('/api/desks').json()
    ids = {d['id'] for d in desks['desks']}
    assert 'default' in ids and 'alpha' in ids and 'beta' in ids


def test_invalid_desk_rejected(client):
    r = client.get('/api/runs', headers={'X-TradeOps-Desk': '../evil'})
    assert r.status_code == 400


def test_create_desk(client):
    r = client.post('/api/desks', json={'id': 'floor-1'})
    assert r.status_code == 200 and r.json()['id'] == 'floor-1'
    assert (module.DATA / 'desks' / 'floor-1' / 'tradeops.db').exists()


def test_concurrent_saves_same_desk(tmp_path, monkeypatch):
    monkeypatch.setattr(module, 'DATA', tmp_path)
    store._ready.clear()
    errs = []

    def write(i):
        try:
            store.save_run(
                tmp_path,
                dict(
                    id=f'id{i}',
                    name='n',
                    created='2026-09-01T00:00:00Z',
                    approval='pending',
                    events=[],
                    analysis=dict(rows=1, sample=[{'x': 1}] * 20),
                ),
                'default',
            )
        except Exception as e:
            errs.append(e)

    with ThreadPoolExecutor(max_workers=32) as ex:
        list(ex.map(write, range(200)))
    assert not errs
    assert len(store.list_run_summaries(tmp_path, 'default')) == 200


def test_legacy_payload_migration(tmp_path):
    import sqlite3

    path = tmp_path / 'tradeops.db'
    conn = sqlite3.connect(path)
    conn.execute('CREATE TABLE runs (id TEXT PRIMARY KEY, payload TEXT NOT NULL)')
    payload = json.dumps(dict(id='legacy1', name='old.json', created='2026-01-01T00:00:00Z', approval='pending', events=[], analysis=dict(rows=3, sample=[1, 2, 3])))
    conn.execute('INSERT INTO runs VALUES (?,?)', ('legacy1', payload))
    conn.commit()
    conn.close()
    store._ready.clear()
    items = store.list_run_summaries(tmp_path, 'default')
    assert items[0]['id'] == 'legacy1'
    assert items[0].get('_summary') is True
    assert 'sample' not in (items[0].get('analysis') or {})
    full = store.get_run(tmp_path, 'legacy1')
    assert full['analysis']['sample'] == [1, 2, 3]
