"""Conservative, auditable selection. Timing ranges are empirical, not confidence intervals."""
import math
import statistics


def nonnegative(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(f'{name} must be finite and nonnegative')
    return value


def recommend(candidates, weights, query_count, storage_budget, baseline='csv_gzip',
              minimum_savings_fraction=.10, search_overhead_s=0):
    if isinstance(query_count, bool) or not isinstance(query_count, int) or query_count < 0:
        raise ValueError('query_count must be a nonnegative integer')
    nonnegative(storage_budget, 'storage_budget')
    nonnegative(search_overhead_s, 'search_overhead_s')
    nonnegative(minimum_savings_fraction, 'minimum_savings_fraction')
    if minimum_savings_fraction >= 1:
        raise ValueError('minimum_savings_fraction must be less than one')
    if not weights or any(nonnegative(w, 'weight') == 0 for w in weights.values()):
        raise ValueError('Provide positive workload weights')
    total = sum(weights.values())
    weights = {q: w / total for q, w in weights.items()}
    names = [c['layout'] for c in candidates]
    if len(names) != len(set(names)) or baseline not in names:
        raise ValueError('Unique layouts and an explicit baseline are required')
    scored, rejected = [], []
    for c in candidates:
        name = c['layout']
        if c.get('verified') is not True:
            rejected.append(dict(layout=name, reason='record_verification_failed'))
            continue
        for key in ('extra_bytes', 'conversion_s'):
            nonnegative(c[key], key)
        if c['extra_bytes'] > storage_budget:
            rejected.append(dict(layout=name, reason='storage_budget_exceeded'))
            continue
        samples = c.get('samples', {})
        if any(q not in samples or len(samples[q]) < 3 for q in weights):
            rejected.append(dict(layout=name, reason='insufficient_workload_measurements'))
            continue
        for q in weights:
            for value in samples[q]:
                nonnegative(value, 'query timing')
        setup = c['conversion_s'] + (search_overhead_s if name != baseline else 0)
        timing = {stat: sum(fn(samples[q]) * w for q, w in weights.items())
                  for stat, fn in [('low', min), ('median', statistics.median), ('high', max)]}
        scored.append(dict(layout=name, setup_s=setup, query_s=timing,
                           total_s={k: setup + query_count * v for k, v in timing.items()}))
    base = next((c for c in scored if c['layout'] == baseline), None)
    if base is None:
        raise ValueError('Baseline must be verified, measured and within budget')
    eligible = []
    for c in scored:
        if c['layout'] == baseline:
            continue
        gain = base['total_s']['low'] - c['total_s']['high']
        c['conservative_savings_s'] = gain
        per_query = base['query_s']['low'] - c['query_s']['high']
        c['break_even_queries'] = max(0, math.ceil((c['setup_s']-base['setup_s']) / per_query)) if per_query > 0 else None
        if gain > 0 and gain >= minimum_savings_fraction * base['total_s']['low']:
            eligible.append(c)
        else:
            rejected.append(dict(layout=c['layout'], reason='insufficient_conservative_savings'))
    winner = min(eligible, key=lambda c: (c['total_s']['high'], c['layout'])) if eligible else base
    return dict(selected=winner['layout'], baseline=baseline, weights=weights, query_count=query_count,
                minimum_savings_fraction=minimum_savings_fraction, search_overhead_s=search_overhead_s,
                scores=scored, rejected=rejected,
                reason='measured_savings_clear_threshold' if eligible else 'retain_baseline',
                limitations=['Observed min/max timing envelope is not a statistical confidence interval.',
                             'Prediction applies to measured data and workload; changes require remeasurement.',
                             'Search overhead is an explicit planning allowance for alternatives; already incurred costs are sunk.',
                             'Seconds saved are not automatically dollars saved.'])


def verify_relations(connection, baseline, candidate):
    """Compare multisets, including duplicate multiplicity and schema. Internal SQL relation names only."""
    import re
    if any(not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*', name) for name in (baseline, candidate)):
        raise ValueError('Invalid relation identifier')
    schema_equal = connection.execute(f'DESCRIBE {baseline}').fetchall() == connection.execute(f'DESCRIBE {candidate}').fetchall()
    if not schema_equal:
        return dict(verified=False, reason='schema_mismatch', differing_rows=None)
    count = connection.execute(f'SELECT count(*) FROM ((SELECT * FROM {baseline} EXCEPT ALL SELECT * FROM {candidate}) UNION ALL (SELECT * FROM {candidate} EXCEPT ALL SELECT * FROM {baseline}))').fetchone()[0]
    return dict(verified=count == 0, reason='equal' if count == 0 else 'record_mismatch', differing_rows=count)


def check_measurement_scope(measured_rows, target_rows, tolerance=.20):
    """Prevent silent transfer of local timings to materially different dataset sizes."""
    for name, value in [('measured_rows', measured_rows), ('target_rows', target_rows)]:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f'{name} must be a positive integer')
    nonnegative(tolerance, 'tolerance')
    change = abs(target_rows - measured_rows) / measured_rows
    return dict(remeasurement_required=change > tolerance, relative_row_change=change,
                tolerance=tolerance, measured_rows=measured_rows, target_rows=target_rows,
                limitation='Row count is only a drift indicator; schema, value distribution, hardware and query changes also require review.')
