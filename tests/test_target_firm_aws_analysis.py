"""Regression coverage for AWS-primary target-firm analysis corpus."""
import json
from pathlib import Path

from scripts.target_firm_aws_analysis import (
    aws_ingest_plan,
    build_catalogue,
    generate_firm_logs,
    help_score,
    rows_to_bytes,
)
from backend.agents import SupervisorAgent
from backend.planning import NetworkPlan, network_plan
import tempfile


def test_catalogue_covers_target_niches_only():
    firms = build_catalogue(120)
    assert len(firms) == 120
    niches = {f['niche'] for f in firms}
    assert niches == {'boutique_trading', 'fintech_saas', 'specialist_broker'}
    assert all(f['aws_primary'] for f in firms)
    assert all(f['s3_bucket'].startswith('to-') for f in firms)
    assert all(f['cloudwatch_group'].startswith('/tradeops/') for f in firms)
    # Customer firms are niche specialists — not modeled as public megacap issuers.
    joined = ' '.join(f['name'].lower() for f in firms)
    for banned in ('apple', 'microsoft', 'amazon', 'nvidia', 'google', 'meta platforms'):
        assert banned not in joined


def test_supervisor_and_aws_plan_on_one_firm():
    firm = build_catalogue(100)[0]
    rows = generate_firm_logs(firm, seed=1)
    data = rows_to_bytes(rows)
    with tempfile.TemporaryDirectory() as tmp:
        result = SupervisorAgent().run(data, 'logs.json', Path(tmp) / 'optimized')
    assert result['analysis']['rows'] == len(rows)
    plan = network_plan(NetworkPlan(company=firm['niche'], monthly_budget=firm['monthly_budget']))
    ingest = aws_ingest_plan(firm)
    assert 'idempotency_key' in ingest
    assert ingest['live_submit'] is False
    metrics = help_score(result, plan)
    assert 0 <= metrics['help_score'] <= 100


def test_benchmark_artifact_if_present():
    path = Path('benchmarks/target-firm-aws-analysis.json')
    if not path.exists():
        return
    payload = json.loads(path.read_text())
    assert payload['summary']['dataset_count'] >= 100
    assert payload['summary']['aws_primary_firms'] == payload['summary']['dataset_count']
    assert set(payload['summary']['niches']) == {'boutique_trading', 'fintech_saas', 'specialist_broker'}
