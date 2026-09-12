"""Scenario costs derived from measured local performance; not an AWS invoice."""
import statistics
from pydantic import BaseModel, Field, ConfigDict


class CostScenario(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    queries_per_month: int = Field(default=10000, ge=0, le=100000000)
    months: int = Field(default=1, ge=1, le=120)
    compute_per_hour: float = Field(default=.10, ge=0, le=1000)
    storage_per_gib_month: float = Field(default=.023, ge=0, le=100)
    workload: str = Field(default='selective', pattern='^(selective|mixed)$')
    include_experiment_overhead: bool = True
    additional_setup_usd: float = Field(default=0, ge=0, le=1000000)


def estimate_costs(report, scenario):
    candidates=report['candidates']
    baseline=next(c for c in candidates if c['layout']=='csv_gzip')
    raw_bytes=sum(s['archive_bytes'] for s in report['sources'])
    baseline_bytes=raw_bytes+baseline['bytes']
    rate=scenario.compute_per_hour/3600
    rows=[]
    for c in candidates:
        if not c['verified']:continue
        measurements=report['measurements']['calibration'][c['layout']]
        names=['selective'] if scenario.workload=='selective' else list(measurements)
        seconds=statistics.mean(statistics.median(measurements[n]) for n in names)
        existing=c['layout']=='csv_gzip'
        extra_bytes=0 if existing else c['bytes']
        storage=(baseline_bytes+extra_bytes)/2**30*scenario.storage_per_gib_month
        queries=scenario.queries_per_month*seconds*rate
        # Full experiment already includes candidate conversion; never add it twice.
        setup_s=0 if existing else max(c['conversion_s'],report['elapsed_s']) if scenario.include_experiment_overhead else c['conversion_s']
        setup=0 if existing else setup_s*rate+scenario.additional_setup_usd
        rows.append(dict(layout=c['layout'],query_seconds=seconds,retained_bytes=baseline_bytes+extra_bytes,
                         monthly_storage_usd=storage,monthly_query_compute_usd=queries,
                         setup_usd=setup,total_usd=(storage+queries)*scenario.months+setup))
    base=next(r for r in rows if r['layout']=='csv_gzip')
    for r in rows:
        savings=base['total_usd']-r['total_usd']
        recurring=(base['monthly_storage_usd']+base['monthly_query_compute_usd'])-(r['monthly_storage_usd']+r['monthly_query_compute_usd'])
        r.update(savings_usd=savings,savings_pct=100*savings/base['total_usd'] if base['total_usd'] else None,
                 break_even_months=r['setup_usd']/recurring if recurring>0 else None)
    return dict(scenario=scenario.model_dump(),data_rows=report['rows'],measured_at=report['created'],
                recommended=min(rows,key=lambda r:r['total_usd'])['layout'],candidates=rows,
                assumptions=[
                    'USD scenario estimate using local DuckDB calibration medians; not measured AWS performance or a bill.',
                    'Compute rate is user-assumed, not an AWS instance quote. Savings require avoiding metered compute; an always-on fixed-size server may save no cash.',
                    'Storage rate is editable and illustrative. GiB = 2^30 bytes. Regional tiers, discounts and taxes are not modeled.',
                    'Every choice retains original ZIP archives and canonical gzip; conversions add storage. No deletion or archive assumed.',
                    'One-time experiment overhead includes preparation and conversions; it is conservatively charged once to each alternative, never twice. Disable only if it is already a sunk cost.',
                    'No extrapolation to larger datasets: query frequency changes, measured dataset size stays fixed.',
                    'Athena charges by scanned bytes, not local query seconds. Athena savings are not calculated without scan measurements.',
                    'Requests, transfer, Glue, catalog, network endpoints, billing minimums, idle capacity and operations labor are excluded unless covered by the additional setup allowance.',
                ])
