import pytest
from pydantic import ValidationError
from backend.experiment_costs import CostScenario, estimate_costs


def report():
    return dict(rows=100,created='test',sources=[dict(archive_bytes=1024)],elapsed_s=100,
        candidates=[dict(layout='csv_gzip',bytes=2048,conversion_s=0,verified=True),dict(layout='parquet',bytes=1024,conversion_s=10,verified=True)],
        measurements={'calibration':{'csv_gzip':{'selective':[1]},'parquet':{'selective':[.1]}}})


def test_charges_overhead_once_and_retains_originals():
    r=estimate_costs(report(),CostScenario(compute_per_hour=360,queries_per_month=1000))
    b,p=r['candidates']
    assert p['setup_usd']==10
    assert b['retained_bytes']==3072 and p['retained_bytes']==4096
    assert p['monthly_query_compute_usd']==10
    assert r['recommended']=='parquet' and p['savings_usd']>0


def test_rare_queries_do_not_repay_search():
    r=estimate_costs(report(),CostScenario(queries_per_month=1))
    assert r['recommended']=='csv_gzip' and r['candidates'][1]['savings_usd']<0


def test_sunk_overhead_keeps_conversion_cost():
    p=estimate_costs(report(),CostScenario(compute_per_hour=360,include_experiment_overhead=False))['candidates'][1]
    assert p['setup_usd']==1


def test_zero_rates_no_division_by_zero():
    r=estimate_costs(report(),CostScenario(compute_per_hour=0,storage_per_gib_month=0))
    assert all(c['savings_pct'] is None and c['break_even_months'] is None for c in r['candidates'])


@pytest.mark.parametrize('kw',[{'months':0},{'queries_per_month':-1},{'compute_per_hour':float('nan')},{'storage_per_gib_month':float('inf')},{'workload':'invalid'}])
def test_reject_invalid_inputs(kw):
    with pytest.raises(ValidationError):CostScenario(**kw)
