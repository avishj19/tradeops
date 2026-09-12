# Public-data layout experiment

Measured 1,350,922 real BTC/ETH trades from six Binance daily archives (January 1–3, 2020). Publisher checksums verified. No synthetic scaling.

| Layout | Size MB | Conversion s | Selective ms | Daily volume ms | VWAP components ms |
|---|---:|---:|---:|---:|---:|
| csv_gzip | 23.82 | 0.000 | 528.85 | 651.49 | 1309.05 |
| parquet | 20.10 | 1.312 | 31.34 | 175.18 | 909.00 |
| partitioned | 20.12 | 1.439 | 22.76 | 155.79 | 879.62 |
| partitioned_csv | 23.75 | 4.965 | 101.50 | 535.23 | 1206.26 |

## Interpretation

1. Selective reads benefit most: partitioned Parquet takes about 23 ms versus 529 ms for combined gzip. Partitioned gzip takes 102 ms, so partitioning alone explains part of the improvement. This is an observed layout comparison, not a measured attribution of each internal engine operation.
2. Workload matters: the daily aggregation improves more than the full-dataset VWAP-component query. A single compression ratio cannot predict every query speedup.
3. Conversion must be repaid: partitioned Parquet costs 1.439 seconds to build in this run. For one query the selector keeps gzip; for 100 or 10,000 modeled queries it chooses partitioned Parquet.
4. Compare against a strong baseline: for 100 modeled selective queries, the chosen layout is about 1.20× faster than always converting to a single Parquet file, including conversion. For 100 mixed queries that ratio is only 1.05×; this small difference is not established as statistically significant.
5. No net agent-speed claim: the whole experiment took 131.2 seconds including preparation, search and verification. Projected layout totals exclude that overhead. Those costs must be amortized before claiming the optimizer itself saves time.
6. The Parquet copies are about 20.1 MB versus 23.8 MB of canonical gzip. Since originals and baseline remain retained, total retained storage grows. No AWS cost savings were measured.

## Reproduction and evidence

Run `python -m scripts.benchmark_lab` after installing `.[benchmark]`. See [latest.json](latest.json) for source URLs, SHA-256 values, all individual timings, SQL, calibration decisions and environment. The timestamped JSON is an immutable snapshot; latest.json changes on rerun.

Full row multiset equality (EXCEPT ALL in both directions) passed for every candidate, and all 120 timed query results matched. Five calibration and five separate evaluation rounds use the same data and queries; evaluation is not an unseen-dataset test. OS caches were warm, one DuckDB thread was used, and conversion was measured once.

Sources: [Binance public-data documentation](https://github.com/binance/binance-public-data), [DuckDB Parquet support](https://duckdb.org/docs/current/data/parquet/overview), [DuckDB CSV support](https://duckdb.org/docs/current/data/csv/overview).

This is a deterministic, four-candidate experiment/verification/selection workflow. It is not an LLM research system, a formal proof, or a test of the Sequence Evidence Agent.
