"""Local planning and incident aggregation. No cloud calls or notifications."""
from collections import Counter
from pydantic import BaseModel, Field
from typing import Literal

class NetworkPlan(BaseModel):
    company: Literal['boutique_trading','fintech_saas','specialist_broker']='boutique_trading'
    monthly_budget: float = Field(default=50,ge=1,le=100000,allow_inf_nan=False)
    availability_zones: int = Field(default=2,ge=1,le=3)
    interface_endpoints: int = Field(default=2,ge=0,le=20)
    endpoint_hourly: float = Field(default=.01,ge=0,le=10,allow_inf_nan=False)
    endpoint_gb: float = Field(default=10,ge=0,le=1000000,allow_inf_nan=False)
    endpoint_per_gb: float = Field(default=.01,ge=0,le=10,allow_inf_nan=False)
    service_allowance: float = Field(default=20,ge=0,le=100000,allow_inf_nan=False)

def network_plan(p):
    fixed=730*p.availability_zones*p.interface_endpoints*p.endpoint_hourly
    usage=p.endpoint_gb*p.endpoint_per_gb
    total=fixed+usage+p.service_allowance
    return dict(**p.model_dump(),endpoint_fixed=round(fixed,2),endpoint_usage=round(usage,2),estimated_total=round(total,2),budget_remaining=round(p.monthly_budget-total,2),within_budget=total<=p.monthly_budget,
        gateway_endpoint_charge=0,nat_gateways=0,bedrock_enabled=False,
        availability_note='One AZ reduces fixed cost but loses multi-AZ endpoint resilience.' if p.availability_zones==1 else 'Multi-AZ endpoint placement improves availability; validate routes and service support in each AZ.',
        recommendation='Keep AI optional, group alerts, and use S3 gateway access for bulk logs.' if total<=p.monthly_budget else 'Plan exceeds budget. Review required endpoint services and ingestion volume; do not remove isolation controls just to fit the budget.',
        scope='Planning estimate only. 730 hours/month. Service allowance is your input, not a calculated AWS bill. Excludes VPN/private dashboard access, tax, cross-region traffic and unlisted services. Verify region-specific rates.')

def incidents(rows,threshold):
    counts=Counter()
    for r in rows:
        status=r['status'].upper()
        if status in {'ERROR','REJECTED'}:counts['execution_errors']+=1
        elif r['latency_ms']>threshold:counts['latency_spike']+=1
    descriptions={'execution_errors':('Execution failures','Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.'),'latency_spike':('Elevated execution latency','Compare upstream latency and deployment timing. This signal does not establish a root cause.')}
    return [dict(kind=k,title=descriptions[k][0],count=n,severity='high' if n>=10 else 'review',recommendation=descriptions[k][1],notification='local_only',evidence='Aggregate counts only; no raw lines, account IDs, symbols or event IDs in this incident summary.') for k,n in sorted(counts.items())]
