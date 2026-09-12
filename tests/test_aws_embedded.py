"""Embedded AWS workflow: same agent path for local mirror and live AWS APIs."""
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from aws.adapter import AWSAdapter, aws_config_from_env, embed_run_in_aws
from backend.agents import generate


def test_aws_event_boundary_still_enforced():
    class Session:
        def client(self, name): return object()
    a = AWSAdapter('raw-bucket', 'optimized', 'job', 'workgroup', Session())
    e = {'detail': {'bucket': {'name': 'raw-bucket'}, 'object': {'key': 'raw/logs.json', 'version-id': 'v1'}}}
    assert a.plan_event(e) == a.plan_event(e)
    e['detail']['bucket']['name'] = 'other'
    with pytest.raises(ValueError):
        a.plan_event(e)
    with pytest.raises(NotImplementedError):
        a.archive()


def test_local_mirror_stages_s3_contract(tmp_path):
    rows = generate(count=20)
    raw = json.dumps(rows).encode()
    parquet = tmp_path / 'logs.parquet'
    parquet.write_bytes(b'PAR1')
    report = dict(analysis=dict(asset_classes={'equity': 20}), query=dict(sql='SELECT 1'))
    aws = embed_run_in_aws('abc123', raw, 'logs.json', parquet, report, tmp_path, environ={})
    assert aws['embedded'] and aws['cloud'] == 'aws' and aws['live'] is False
    assert aws['mode'] == 'embedded_local'
    raw_bucket = aws['raw_uri'].split('/')[2]
    opt_bucket = aws['optimized_uri'].split('/')[2]
    assert (tmp_path / 'aws-mirror' / 's3' / raw_bucket / 'raw' / 'abc123' / 'logs.json').exists()
    assert (tmp_path / 'aws-mirror' / 's3' / opt_bucket / 'optimized' / 'abc123' / 'logs.parquet').exists()
    assert list((tmp_path / 'aws-mirror' / 'events').glob('*.json'))
    assert aws['athena_query_execution_id']


def test_live_flag_requires_buckets():
    cfg = aws_config_from_env({'TRADEOPS_AWS_LIVE': '1'})
    assert cfg['live'] is False  # buckets missing
    cfg = aws_config_from_env({
        'TRADEOPS_AWS_LIVE': '1',
        'TRADEOPS_AWS_RAW_BUCKET': 'r',
        'TRADEOPS_AWS_OPTIMIZED_BUCKET': 'o',
        'TRADEOPS_AWS_GLUE_JOB': 'g',
        'AWS_REGION': 'eu-west-1',
    })
    assert cfg['live'] is True and cfg['region'] == 'eu-west-1'


def test_demo_run_includes_aws_block(tmp_path, monkeypatch):
    from backend import app as module
    from backend import store
    monkeypatch.setattr(module, 'DATA', tmp_path)
    store._ready.clear()
    with TestClient(module.app) as client:
        health = client.get('/api/health').json()
        assert health['cloud'] == 'aws' and health['mode'] == 'aws_embedded_local'
        status = client.get('/api/aws/status').json()
        assert status['embedded'] is True and 's3' in status['services']
        run = client.post('/api/demo', json={'scenario': 'normal', 'format': 'json'}).json()
        assert run['aws']['embedded'] is True
        assert run['aws']['raw_uri'].startswith('s3://')
        assert any('AWS workflow embedded' in e['message'] for e in run['events'])
        planned = client.post('/api/aws/events', json={
            'detail': {
                'bucket': {'name': run['aws']['plan']['input_bucket']},
                'object': {'key': run['aws']['plan']['input_key'], 'version-id': run['aws']['plan']['input_version']},
            }
        }).json()
        assert planned['status'] == 'planned' and planned['plan']['idempotency_key']
