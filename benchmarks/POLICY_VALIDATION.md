# Policy validation findings

The executable source is `scripts/validate_layout_policy.py`; machine-readable observations are in `policy-validation.json`. Calibration uses 269,898 records dated 2020-01-01; held-out evaluation uses 682,164 dated 2020-01-03. Both symbols and both dates originate in the previously downloaded Binance corpus. Publisher SHA-256 checksums are checked again before reconstructing canonical data.

Four candidates, three query types, one warmup plus three timed repeats per split, DuckDB threads=1 and memory_limit=1GB. Recommendations were written to disk before the holdout was measured. Every candidate passed schema and full multiset equality; every timed query matched the baseline. An intentionally removed record produced `record_mismatch`, differing_rows=1. Separate unit tests cover duplicate loss and value/type corruption.

| Workload | Projected queries | Frozen choice | Holdout best | Choice / result |
|---|---:|---|---|---|
| Selective | 1 | Keep gzip | Keep gzip | Correctly avoids setup |
| Selective | 100 | Keep gzip | Partitioned Parquet | Missed 15.65 seconds of modeled savings |
| Selective | 10,000 | Partitioned Parquet | Partitioned Parquet | 10.31× vs gzip; 1.07× vs single Parquet |
| Full scan | 1 | Keep gzip | Keep gzip | Correctly avoids setup |
| Full scan | 100 | Keep gzip | Single Parquet | Missed 34.82 seconds of modeled savings |
| Full scan | 10,000 | Single Parquet | Single Parquet | 2.29× vs gzip; same as single Parquet baseline |
| Mixed | 1 | Keep gzip | Keep gzip | Correctly avoids setup |
| Mixed | 100 | Keep gzip | Single Parquet | Missed 22.45 seconds of modeled savings |
| Mixed | 10,000 | Single Parquet | Single Parquet | 3.64× vs gzip; same as single Parquet baseline |

These results are one run, not significance claims. Alternatives are charged calibration/search elapsed time plus held-out conversion, whereas keeping the baseline avoids that planned work. Realized experiment costs have already been incurred; they are sunk and cannot be recovered by subsequently selecting baseline. Holdout validation overhead is excluded from projected totals. Repeating 10,000 full queries was not part of this experiment.

## What changed because of the failures

The later date has roughly 2.53× as many rows. Raw latency calibration did not transfer reliably at medium query volumes. The API now rejects transfer when an explicitly supplied target row count differs by over 20%, requiring fresh measurements. This is a guardrail, not evidence that recommendations within 20% are guaranteed. The frozen experiment above deliberately remains unchanged: it documents the failure that motivated the guardrail rather than rewriting the test to look successful.

Stronger evidence still requires multiple date splits, other providers, representative user queries, repeated conversion timings, cold caches, and concurrent load. No validated customer demand or actual AWS billing measurements were obtained by this work. The policy is a conservative measured search, not a trained model or a novel mathematical result.
