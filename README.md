# TradeOps

Local trading-log operations dashboard for specialist finance teams. Deterministic agents turn messy fills into verified Parquet, flag anomalies, and estimate storage/query cost — without an LLM and without writing back to your sources.

**Status:** local demo. Not a deployed AWS service, trading engine, or compliance product.

## Quick start

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000 · API docs http://127.0.0.1:8000/docs · tests: `python -m pytest -q`

Python 3.11+ (macOS/Linux). No Node build step.

```sh
export TRADEOPS_DATA=/absolute/path/to/private/data   # optional; default ./data
```

## Layout

```text
backend/       FastAPI app, agents, store, Polars fast path, optimize arena
frontend/      Static dashboard (plain JS/CSS)
aws/           S3 → EventBridge → Glue → Athena adapter (local mirror by default)
connectors/    Read-only folder / S3 / CloudWatch presets
samples/       Verified public market-data fixtures
scripts/       Benchmark + stress helpers
tests/         pytest suite
benchmarks/    Measured layout/cost JSON (latest.json)
```

Runtime data (gitignored): `tradeops.db`, optional `desks/<id>/`, run folders, `optimize-arena-latest.json`.

## Demo

1. **Optimization arena** — one-click before/after (hot-path dedupe, lean run list, SQLite contention).
2. **Run agents** — Latency incident / Duplicate burst / Normal day on synthetic multi-asset fills.
3. **Market datasets** — “Analyze verified sample” uses the bundled Binance file (checksum-verified).
4. **Archive** — approval only moves the *local* raw copy; never mutates S3 lifecycle.

## Connectors (read-only)

```sh
python -m backend.connectors --config connectors/binance-spot.json --list
python -m backend.connectors --config connectors/folder.example.json
```

Presets under `connectors/` cover Binance spot/futures, BitMEX, Hyperliquid (blocked until requester-pays is accepted), plus `folder.example.json`, `s3.example.json`, `cloudwatch.example.json`, and `mapping.example.json`. Sources are never deleted or rewritten. Scans are bounded (list/download caps); this is not a full-archive sync.

## AWS

Default: isomorphic local mirror under `$TRADEOPS_DATA/aws-mirror/`.  
Live: `TRADEOPS_AWS_LIVE=1` with raw/optimized bucket + Glue job env vars (see `.env.example`). Short private-VPC notes: [aws/README.md](aws/README.md).

## Benchmarks

```sh
python -m scripts.benchmark_lab          # writes benchmarks/latest.json
python -m scripts.validate_layout_policy # writes benchmarks/policy-validation.json
python -m scripts.stress_databases       # multi-desk SQLite stress
```

Numbers are local DuckDB timings on verified public samples — not Athena invoices.

## Environment

| Variable | Purpose |
|---|---|
| `TRADEOPS_DATA` | Data root (DB + run artifacts) |
| `TRADEOPS_DESK` / `X-TradeOps-Desk` | Multi-desk SQLite isolation |
| `TRADEOPS_AWS_LIVE` + bucket/job vars | Live AWS backend |
| `TRADEOPS_FORCE_PYTHON_FASTPATH=1` | Disable Polars hot path |

## License / scope

Deterministic agents only. Human approval for local archive. No secret scanning of your books — keep private data under `TRADEOPS_DATA`, not in git.

## First-time visitor experience

The website opens on **Start here**, explaining trading logs, the problem TradeOps addresses, and a three-step workflow. **Try an example analysis** runs generated data without an upload or cloud account. Operational results start with a plain-English summary, a checked-copy download, and expandable evidence. Advanced tools remain available under **Explore more tools**. A glossary explains logs, Parquet, agents, and AWS, with clear distinctions between measured file sizes, modeled costs, and actual savings.

The merged application and this interface update were checked with 122 passing tests (two upstream deprecation warnings). The sample-to-results flow was also exercised in the browser. The performance test checks reported timing arithmetic rather than assuming every run must be faster.
