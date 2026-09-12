# Efficiency test datasets

Fixed execution-log fixtures for benchmarking and regression-testing the SupervisorAgent pipeline (the ~10k-row latency-spike workload used for TradeOps hot-path timing).

These are **invented demo rows**, not real market or brokerage activity. Timestamps use a frozen base date (`2026-06-09T09:30:00+00:00`) so hashes and anomaly counts do not drift day to day.

## Files

| File | Scenario | Rows | Notes |
|---|---|---:|---|
| `latency-spike-10k.json.gz` | latency_spike | 10,400 | Primary efficiency workload (10k unique + 400 repeats) |
| `latency-spike-10k.csv.gz` | same | 10,400 | CSV form of the same rows |
| `duplicates-1500.json[.gz]` | duplicates | 1,725 | Heavier duplicate burst |
| `normal-1000.json[.gz]` | normal | 1,040 | Baseline day |
| `manifest.json` | — | — | SHA-256 hashes and expected analysis metrics |

## How to use

Decompress before uploading to the dashboard (the log upload path expects JSON/CSV, not gzip):

```sh
gunzip -k samples/efficiency/latency-spike-10k.json.gz
# Dashboard → upload execution logs, or:
curl -F file=@samples/efficiency/latency-spike-10k.json http://127.0.0.1:8000/api/upload
```

Regenerate (must match committed hashes):

```sh
python3 scripts/make_efficiency_dataset.py
```

Run the fixture tests:

```sh
python3 -m pytest -q tests/test_efficiency_dataset.py
```

## Expected latency-spike metrics

From `manifest.json` → `expected_latency_spike_10k`:

- 10,400 rows → 10,000 unique, **400** exact duplicates
- **1,999** anomalies (threshold 108.72 ms, p95 1002.95 ms)
- Sequence Evidence: **22** candidates across **8** cohorts
- Incidents: 667 execution errors, 1,332 latency spikes
