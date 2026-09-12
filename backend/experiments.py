"""Budgeted layout selection from measured experiments, not LLM assertions."""
import math


def choose_layout(candidates, query_count, extra_storage_budget):
    if isinstance(query_count, bool) or not isinstance(query_count, int) or query_count < 0:
        raise ValueError('query_count must be a nonnegative integer')
    if not math.isfinite(extra_storage_budget) or extra_storage_budget < 0:
        raise ValueError('extra_storage_budget must be finite and nonnegative')
    scored = []
    for c in candidates:
        if not c['verified'] or c['extra_bytes'] > extra_storage_budget:
            continue
        if any(not math.isfinite(c[k]) or c[k] < 0 for k in ('conversion_s','query_s','extra_bytes')):
            raise ValueError('Invalid measurement')
        score = c['conversion_s'] + query_count*c['query_s']
        scored.append(dict(layout=c['layout'], predicted_total_s=score))
    if not scored:
        raise ValueError('No verified candidate meets the storage budget')
    scored.sort(key=lambda x:(x['predicted_total_s'],x['layout']))
    return dict(selected=scored[0]['layout'], scores=scored,
                objective='Minimize conversion seconds + query count × calibration query seconds; retained baseline storage is common to all choices.')
