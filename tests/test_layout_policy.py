import duckdb
import pytest
from fastapi.testclient import TestClient
from backend.app import app
from backend.layout_policy import recommend, verify_relations


def candidates():
    return [dict(layout='csv_gzip', verified=True, extra_bytes=0, conversion_s=0,
                 samples={'point':[1, 1, 1], 'scan':[1,1,1]}),
            dict(layout='parquet', verified=True, extra_bytes=10, conversion_s=2,
                 samples={'point':[.1,.1,.1], 'scan':[2,2,2]})]


def test_workload_and_amortization():
    assert recommend(candidates(), {'point':1}, 1, 10)['selected']=='csv_gzip'
    assert recommend(candidates(), {'point':1}, 100, 10)['selected']=='parquet'
    assert recommend(candidates(), {'scan':1}, 100, 10)['selected']=='csv_gzip'
    assert recommend(candidates(), {'point':1}, 100, 10, search_overhead_s=100)['selected']=='csv_gzip'


def test_uncertainty_and_rejection_explanations():
    c=candidates();c[1]['samples']['point']=[.1,.1,1.1]
    assert recommend(c, {'point':1}, 100, 10)['reason']=='retain_baseline'
    c[1]['verified']=False
    assert recommend(c, {'point':1},100,10)['rejected'][0]['reason']=='record_verification_failed'
    c=candidates()
    assert recommend(c, {'point':1},100,0)['rejected'][0]['reason']=='storage_budget_exceeded'


@pytest.mark.parametrize('weights', [{}, {'point':-1}, {'point':float('nan')}, {'unknown':1}])
def test_invalid_or_unmeasured_workload(weights):
    with pytest.raises(ValueError):recommend(candidates(),weights,100,10)


def test_duplicate_loss_and_corruption_are_rejected():
    con=duckdb.connect()
    con.execute("CREATE TABLE original AS SELECT * FROM (VALUES ('trade1','1.00'),('trade1','1.00'),('trade2','2.00')) t(id,price)")
    con.execute('CREATE TABLE exact AS SELECT * FROM original ORDER BY id DESC')
    con.execute('CREATE TABLE missing_duplicate AS SELECT DISTINCT * FROM original')
    con.execute("CREATE TABLE changed AS SELECT id, '9.00' AS price FROM original")
    assert verify_relations(con,'original','exact')['verified']
    assert verify_relations(con,'original','missing_duplicate')['differing_rows']==1
    assert not verify_relations(con,'original','changed')['verified']
    con.close()


def test_recommendation_api():
    client=TestClient(app)
    response=client.post('/api/experiments/recommend',json={'query_count':100})
    assert response.status_code==200
    assert response.json()['selected'] in ['csv_gzip','parquet','partitioned','partitioned_csv']
    assert client.post('/api/experiments/recommend',json={'workload_weights':{'missing':1}}).status_code==422
    assert client.post('/api/experiments/recommend',json={'query_count':True}).status_code==422


def test_scope_guard_refuses_large_data_change():
    from backend.layout_policy import check_measurement_scope
    assert not check_measurement_scope(100,120)['remeasurement_required']
    assert check_measurement_scope(100,121)['remeasurement_required']
    client=TestClient(app)
    response=client.post('/api/experiments/recommend',json={'target_rows':1000000000})
    assert response.status_code==409
    assert response.json()['detail']['reason']=='remeasurement_required'


def test_schema_change_is_rejected():
    con=duckdb.connect()
    con.execute('CREATE TABLE source (id VARCHAR)')
    con.execute('CREATE TABLE target (id INTEGER)')
    assert verify_relations(con,'source','target')['reason']=='schema_mismatch'
    con.close()
