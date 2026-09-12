import pytest
from backend.experiments import choose_layout


def choices():
    return [dict(layout='csv',verified=True,conversion_s=0,query_s=.1,extra_bytes=0),
            dict(layout='parquet',verified=True,conversion_s=2,query_s=.01,extra_bytes=100)]


def test_conversion_amortization_changes_choice():
    assert choose_layout(choices(),1,100)['selected']=='csv'
    assert choose_layout(choices(),100,100)['selected']=='parquet'


def test_storage_limit_and_verification_override_speed():
    assert choose_layout(choices(),100,0)['selected']=='csv'
    c=choices();c[1]['verified']=False
    assert choose_layout(c,100,100)['selected']=='csv'


def test_no_eligible_choice():
    c=choices()
    for row in c:row['verified']=False
    with pytest.raises(ValueError):choose_layout(c,1,100)


@pytest.mark.parametrize('queries,budget',[(True,1),(-1,100),(1,-1),(1,float('nan'))])
def test_invalid_profile(queries,budget):
    with pytest.raises(ValueError):choose_layout(choices(),queries,budget)
