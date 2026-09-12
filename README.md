# TradeOps

TradeOps is a local operations dashboard for small, specialized financial businesses that want to understand their logs and market-data files, reduce analytical storage costs, and review changes before taking action. It combines a Python API, a browser dashboard, seven deterministic analysis agents, source-specific market-data readers, and read-only folder/S3/CloudWatch connectors.

**Current status:** working local demo with real Parquet conversion and tested public S3 imports. It is not a deployed AWS service, autonomous LLM system, trading engine, or production compliance product. No AWS credentials are needed for the generated scenarios or bundled samples.

## Start here

1. Follow **Installation** to run the dashboard.
2. Read **How a run works** to understand the data flow.
3. Try the **Demo walkthrough**.
4. Use **Debugging guide** when something fails.
5. Consult [CONNECTORS.md](CONNECTORS.md), [DATASETS.md](DATASETS.md), and [the private AWS blueprint](aws/PRIVATE_DEPLOYMENT.md) for integration details.

## Installation

Use Python 3.11+ on macOS/Linux. The full suite was tested with Python 3.14. The connector CLI uses Unix file locking and is not Windows-native. The frontend uses plain JavaScript and CSS; no Node installation or frontend build is needed to run it.

```sh
git clone https://github.com/avishj19/tradeops.git
cd tradeops
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Open [the dashboard](http://127.0.0.1:8000) or [interactive API documentation](http://127.0.0.1:8000/docs). Keep the terminal running. Stop with Ctrl+C. Run one application process for this local demo.

```sh
python -m pytest -q
```

`requirements.txt` contains the tested dependency versions. `pyproject.toml` describes the project and test configuration. There is no Docker installer or automated AWS deployment yet.

### Configuration and local data

`.env.example` documents environment variables; the app does **not** automatically load a `.env` file. Set variables in your shell before starting the app/connector:

```sh
export TRADEOPS_DATA=/absolute/path/to/private/tradeops-data
```

Otherwise, the application stores results in the repository's `data/` directory:

```text
data/
  tradeops.db                    Saved run JSON and connector checkpoints
  <run-id>/
    raw.*                        Original bytes / source evidence
    optimized/logs.parquet       Verified analytical output
    archive/raw.*                Original moved here after local approval
  connector.lock                 Single connector process lock
```

Use the same `TRADEOPS_DATA` value for server and connectors. Back up the **whole data directory**, not just SQLite: database records reference files. For a consistent simple backup, stop both processes first. `data/`, `.env`, `.venv/`, caches and credentials are excluded from Git. A fresh clone starts with empty history; public samples are included, private run history is not.

## What the dashboard provides

| View | What you can do |
|---|---|
| Overview | Inspect sizes, duplicates, anomalies, recommendations and cost assumptions; review archival |
| Agent activity | Read saved agent evidence and decisions for the selected run |
| History | Search recorded runs/events, filter human decisions, reopen results, access reports and Parquet |
| Market datasets | Import supported source formats or run the bundled Binance sample |
| Incident inbox | Inspect grouped latency/error signals without raw identifiers in the summary |
| Private AWS plan | Estimate endpoint costs, service allowance and budget headroom |
| Architecture | See the integration boundaries and source articles |

History uses stored runs and their events; it is not a complete audit log of every HTTP request. Earlier failed/unrecorded requests, skipped connector scans and planner interactions are not reconstructed. Refresh History to see newly completed connector imports.

## Demo walkthrough

1. Choose **Latency incident**, then **Run agents**. This generates 10,000 unique executions plus 400 repeated records; the example produces 1,999 anomaly signals.
2. Inspect measured original/Parquet sizes. Download the Parquet analytical copy.
3. Try **Duplicate burst** to create 1,500 repeated rows, or **Normal trading day** for a baseline.
4. Open **Agent activity** for the evidence behind each decision.
5. Use **Review archive** to approve, reject or cancel. Approval moves only the local original into that run's archive folder. It never archives an external S3 object.
6. Open **Market datasets → Analyze verified sample** for real Binance data.
7. Open **History**, search `binance` or `archived`, and expand a record for its source, run ID, metrics and downloads.

Generated scenarios use a fixed random seed, with dates relative to the current day. They are simulations, not real financial transactions. To manually restore a locally archived original, stop the application and move the archived file back to the run directory; the existing decision history remains a record of the prior action.

## How a run works

```text
Browser/API upload or read-only connector
  → validate source format
  → normalize supported fields / retain source evidence
  → analyze operational logs OR preserve market-data records
  → write Zstandard Parquet
  → read Parquet back and compare records
  → save run + evidence to local SQLite
  → dashboard, history, recommendations and downloads
```

### The seven agents

| Agent | Implementation and responsibility |
|---|---|
| Supervisor | `backend/agents.py`: coordinates validation, transformation, recommendations and approval gating |
| Log Analysis | Validates log fields, normalizes UTC timestamps, detects exact normalized duplicates, computes latency/error signals |
| Compression | Writes Zstandard Parquet with PyArrow and verifies complete record round-trip equality |
| Query Optimization | Recommends UTC date partitions and compaction; supplies example Athena SQL |
| Storage Optimization | Suggests review when newest event is at least 90 days old and input is at least 128 KiB |
| Cost | Estimates storage/query costs, retaining the original in the model |

The agents use deterministic policies and statistics, **not LLM inference, online learning or root-cause diagnosis**. The latency threshold is `max(100 ms, median + 6 × max(MAD, 1))`; ERROR/REJECTED statuses are also signals. These signals are not confirmed incidents. Small datasets remain one Parquet file; partitions/128–512 MiB compaction are recommendations, not completed distributed transformations.

Incident summaries group errors and latency signals **within a run**. They include fixed descriptions and counts rather than raw source identifiers. No SNS messages are sent. Raw inputs and analytical files may still contain sensitive data; local files are not encrypted by the app.

### Three different input paths

**Operational log upload:** UTF-8 CSV or a JSON array of flat objects. Required fields are `timestamp`, `event_id`, `symbol`, `latency_ms`, `status`. Timestamps need explicit timezones, latency must be finite/non-negative, and columns must be consistent. Exact normalized duplicates are removed from the analytical copy; original bytes are preserved. Same event ID with different content survives.

```json
[{"timestamp":"2026-09-11T13:30:00Z","event_id":"EX-1","symbol":"AAPL","latency_ms":12.5,"status":"FILLED"}]
```

**Market data:** `backend/datasets.py` keeps all rows, including repeated prints, because identical market records may be legitimate. Price/quantity strings and source payloads are retained. Market data does not create synthetic latency/error fields or security alerts. Timestamp conversion is source-specific.

**Existing logs without canonical fields:** `backend/connectors.py` can preserve text/CSV/JSON/JSONL as source records in Parquet. Optional dotted-path field mappings enable operational analysis when the real fields exist. It does not infer missing units or invent timestamps.

Input/expanded archive limits are 20 MiB and 200,000 accepted records. Large archives require a streaming/distributed worker; this demo does not claim full historical archive ingestion.

## Dataset integration and actual verification

| Source | Supported format | Verification performed |
|---|---|---|
| Binance spot | Seven-column trades CSV / single CSV ZIP; millisecond and microsecond epochs | Real 3,427-record BTCUSDT sample; publisher checksum and Parquet verified |
| Binance USD-M futures | Six-column trades CSV / ZIP | Real 3,754-record BTCUSDT sample; publisher checksum and Parquet verified |
| BitMEX | Trade CSV.GZ | Real two-record early historical sample; Parquet verified, local SHA-256 recorded |
| Algoseek | Trade Only CSV/CSV.GZ with documented headers | Invented schema fixtures only; no licensed/sandbox export downloaded |
| Hyperliquid API fills | Fill arrays / JSONL with coin, px, sz, time, tid | Invented schema fixtures only |
| Hyperliquid block fills | `node_fills_by_block/` | Blocked: anonymous access returned Requester Pays AccessDenied; block/LZ4 parser not validated |

Read [DATASETS.md](DATASETS.md) for precise schemas, unsupported variants and timezone assumptions. Algoseek defaults to fixed EST per its guide wording; explicitly select America/New_York only when appropriate for your export. Nanosecond source text is preserved. No trade corrections are reconciled and no strategy backtests are performed.

Provenance lives in `samples/binance-provenance.json` and `samples/s3-verification.json`. `scripts/fetch_binance_sample.py` downloads one bounded public sample with TLS and publisher SHA-256 verification. Public samples are supplied for reproducible tests; inclusion does not grant additional vendor redistribution rights.

### Read-only S3 presets

```text
connectors/binance-spot.json     s3://data.binance.vision/data/spot/daily/trades/
connectors/binance-futures.json  s3://data.binance.vision/data/futures/um/daily/trades/
connectors/bitmex.json           s3://public.bitmex.com/data/trade/
connectors/hyperliquid.json      s3://hl-mainnet-node-data/node_fills_by_block/
```

```sh
python -m backend.connectors --config connectors/binance-spot.json --list
python -m backend.connectors --config connectors/binance-spot.json
```

Public presets use anonymous requests. Defaults bound discovery to 100 objects and one supported download. Narrow the prefix or configure exact `keys`; this is not an unrestricted bulk sync. Oversized objects are skipped. Hyperliquid refuses execution before billable opt-in; do not remove the block and assume its archive matches API fills.

The three tested S3 sources imported successfully; second scans imported zero records. Source objects were unchanged. The connector uses conditional S3 reads, content-based run IDs and persistent checkpoints. Config changes create a new checkpoint namespace and can deliberately re-import data.

Folder and CloudWatch examples, mapping configuration, repeat polling, IAM and retry limitations are documented in [CONNECTORS.md](CONNECTORS.md). Folder/CloudWatch behavior has local fake-client tests; no company's private AWS account or CloudWatch group has been connected. CloudWatch currently creates one local run per event, so high-volume production needs batching. Late events beyond the overlap require backfill.

## Affordability and security design

Measured sizes are distinct from cost projections. Illustrative rates are $0.023/GB-month for storage and $5/TB scanned with 1,000 full scans/month and a 10 MB/query minimum. Originals remain in the estimate. Requests, ETL, taxes, retrieval, licenses and archive transfer fees are excluded. The 1 TB panel extrapolates a measured ratio, not a measured AWS bill.

The real spot CSV was 231,002 bytes; Parquet was 109,463 bytes (52.6% smaller). Its ZIP source was only 63,039 bytes: **Parquet was larger than ZIP**. Futures and tiny BitMEX compressed samples also grew. Analytical format benefits do not guarantee physical-storage savings.

The private-AWS calculator uses editable endpoint count, AZ count, hourly/traffic rates and a user-entered service allowance. It does not query AWS billing or enforce spending caps. Private S3 gateway access and optional interface endpoints can avoid NAT for suitable isolated workers; service reachability, VPN/dashboard access and regional costs still require planning.

Current protections: localhost binding, Host validation, cross-origin write checks, escaped UI content, bounded imports, raw preservation, explicit local archive approval and no source write/delete connector permissions. These do not replace production authentication, tenancy isolation, encrypted storage or immutable auditing.

## AWS architecture: implemented vs planned

```text
Existing S3 / folders / CloudWatch → read-only CLI → local TradeOps

Planned cloud deployment:
Versioned S3 → EventBridge → Lambda planner → durable queue/idempotency
 → Glue transformation → S3 Parquet / Glue Catalog → Athena

Optional incident path:
CloudWatch subscription → Lambda grouping → optional Bedrock → optional SNS
```

`aws/adapter.py` supplies versioned event planning, Glue submission and Athena statistics methods. `aws/lambda_handler.py` returns a plan; it does not auto-submit jobs. `aws/glue_job.py` is a bounded worker example, not a deployed job. Archival in the AWS adapter fails closed. Live **public S3 reads** were tested; Lambda, Glue, Athena, Bedrock, SNS, VPCs and private-account integrations were not deployed or verified end-to-end.

Before production: authentication/RBAC, durable distributed orchestration, audit trail, batching, retries/DLQ, retention/legal-hold policies, scoped IAM, encryption, monitoring, tenant isolation and validated deployment infrastructure. See [PRIVATE_DEPLOYMENT.md](aws/PRIVATE_DEPLOYMENT.md).

## Articles and how they informed the implementation

| Reference | Influence | Boundary |
|---|---|---|
| [IBM — What is log analysis with AI?](https://www.ibm.com/think/topics/ai-for-log-analysis) | Collection → normalization → analysis → visualization; synthetic incident scenarios | No predictive/online ML or conversational agent implemented |
| [Splunk — Log monitoring](https://www.splunk.com/en_us/blog/learn/log-monitoring.html) | Standardized signals, private-network planning, privacy-conscious summaries | No Splunk integration or adaptive threat-prevention claims |
| [Divyam Sharma — AWS log analysis and incident alerting](https://medium.com/@divyam.sharma3/how-i-built-an-ai-driven-log-analysis-and-incident-alerting-system-on-aws-7cea7ec29e5d) | CloudWatch subscription/Lambda/optional Bedrock/SNS blueprint, filtering and human control | Blueprint only; local inbox sends no notifications |

Primary technical references used to check implementation choices:

- [Binance formats, timestamp changes and checksums](https://github.com/binance/binance-public-data)
- [Algoseek dataset](https://algoseek.com/dataset/us-equities-trade-only/) and [schema guide](https://algoseek.com/data-docs/equity-market-data/algoseek.US.Equity.Trades.Only.pdf)
- [Hyperliquid historical data](https://hyperliquid.gitbook.io/hyperliquid-docs/historical-data) and [API fills](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
- [BitMEX archive](https://public.bitmex.com/?prefix=data/trade/)
- [S3 conditional reads](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObject.html)
- [CloudWatch pagination](https://docs.aws.amazon.com/botocore/latest/reference/services/logs/client/filter_log_events.html)
- [Athena pricing](https://aws.amazon.com/athena/pricing/), [S3 lifecycle constraints](https://docs.aws.amazon.com/AmazonS3/latest/userguide/lifecycle-transition-general-considerations.html)
- [S3 gateway endpoints](https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints-s3.html), [PrivateLink pricing](https://aws.amazon.com/privatelink/pricing/), [Lambda VPC connectivity](https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc-internet.html)

Articles supplied design guidance, not instructions to deploy paid services or evidence that production capabilities are complete.

## Implementation record so far

1. Built FastAPI/static frontend, generated scenarios, six agents, SQLite persistence, verified Parquet conversion and local approvals.
2. Added incident grouping and the private-network cost planner for specialist financial firms; removed external font requests.
3. Separated market-data ingestion from operational logs; added source adapters, precise timestamps and actual Binance sample validation.
4. Added folder/S3/CloudWatch CLI connectors with saved progress and mappings. Added the four requested S3 presets; tested three live sources and documented the Hyperliquid block.
5. Expanded History into searchable recorded activity with details, source references, reports and downloads.
6. Consolidated this README, specialized guides, provenance and tests for maintainers.

See [VALIDATION.md](VALIDATION.md) for recorded checks. The current suite has **85 passing tests**. Known upstream test-client deprecation warnings do not represent failed tests. UI verification covered populated results, archive cancellation, network calculation, real sample import, history search and detail expansion. No claim is made of exhaustive accessibility, browser or production load testing.

## Code map for debugging

| File | Start here when… |
|---|---|
| `backend/app.py` | A route, upload, SQLite record, approval or download fails |
| `backend/agents.py` | Operational parsing, duplicate counts, anomaly thresholds or costs look wrong |
| `backend/datasets.py` | Vendor formats, archive expansion, decimal/timestamp preservation fail |
| `backend/planning.py` | Incident grouping or private-network estimates look wrong |
| `backend/connectors.py` | Discovery, source reads, mappings, checkpoints or polling fail |
| `frontend/app.js` | Navigation, history filtering, rendering or UI actions fail |
| `frontend/index.html`, `frontend/style.css` | Layout, forms or responsive appearance need changes |
| `aws/` | Cloud integration examples and design assumptions need review |
| `tests/` | Reproduce expected parser/API/connector behavior |
| `samples/` | Verify the exact public test inputs and hashes |

## Debugging guide

| Symptom | What to check |
|---|---|
| Dashboard cannot connect | Confirm the server terminal is running and `/api/health` responds. Port 8000 must be available. Do not stop unrelated processes blindly. |
| UI looks stale after edits | Reload the page. Static JS/CSS require reload; backend changes require restarting Uvicorn unless you intentionally use development reload. |
| HTTP 422 on upload | Inspect the response in browser network tools or `/docs`. Select the correct operational vs market-data form and provider. Verify headers, timezone, units and row limits. |
| CSV works but ZIP/GZIP fails | Compressed import is source-specific. Check one-file ZIP constraints and expanded-size limits. LZ4 is not supported. |
| S3 scan imports zero files | Check suffix, selected keys, prefix, object sizes, discovery bound and existing checkpoints. Zero after a successful repeat is expected. |
| S3 conditional request fails | Source changed after listing; rescan. Do not disable the condition to force a stale import. |
| Hyperliquid AccessDenied | Requester-pays is intentionally blocked; paid access and a block-format adapter remain pending. |
| Private AWS AccessDenied | Verify role/profile, region, bucket prefix/log-group IAM and KMS decrypt permissions where applicable. Never paste credentials into logs or bug reports. |
| Connector succeeds but History is empty | Server/CLI must share the same `TRADEOPS_DATA`; refresh History. Check whether an import was skipped rather than created. |
| Connector lock is held | Another connector process may be running. Stop it normally before retrying; the lock file's presence alone does not prove a process owns the lock. |
| CloudWatch events are missing | Check start time, filter and ingestion lag. Empty pages can still have continuation tokens. Events beyond the overlap need explicit backfill. |
| Unexpected repeated data | Operational dedupe is per run; market rows are preserved. Changed folder snapshots or changed connector config can generate new runs. |
| Parquet is larger | Small files and already-compressed sources can grow. Check the comparison denominator before claiming savings. |
| Archive/download file missing | Check the run's data directory and restore a consistent directory backup. A SQLite-only backup does not restore payload files. |

For a useful bug report, include the failing route/command, sanitized configuration, source format, run ID, exact error and a minimal non-sensitive reproducer. Run the focused test module, e.g. `python -m pytest tests/test_connectors.py -q`, then the full suite after the fix. Do not attach full proprietary trading logs or AWS secrets.

## Main API routes

- `GET /api/health`, `GET /api/runs`
- `POST /api/demo`, `POST /api/upload`
- `POST /api/datasets/upload`, `POST /api/datasets/binance-sample`
- `POST /api/network-plan`
- `POST /api/runs/{id}/decision`
- `GET /api/runs/{id}/report`, `GET /api/runs/{id}/download`

Use `/docs` for request schemas. GitHub stores the source, not the running localhost service or your private workspace history.


## Sequencing-inspired evidence agent

The user-supplied educational DNA substitution-counter example inspired a software
analysis method, not a cancer detector or biological model. Its useful principles
are reference comparison, evidence depth, ambiguity handling and independent validation.

`backend/sequences.py` implements the Sequence Evidence Agent. After operational
log validation, it groups events by source, strategy and symbol, orders them by
UTC timestamp, and uses the earliest 70% as reference and the later 30% as observation.
The reference alone determines the robust latency threshold. Status/latency pairs
form a fixed token vocabulary; adjacent token pairs are the sequence motifs.

Candidates require at least 30 eligible transitions per period, 5 supporting later
transitions and a 15-percentage-point increase. Reports include both counts and
denominators, time boundaries, example event IDs, thresholds, skipped cohorts and
validation recommendations. These are heuristic filters, not significance tests.
The reference is not certified healthy. Changes may reflect traffic, deployment,
seasonality or faults. Overlapping transitions are dependent, and cohort adjacency
does not establish that events belong to the same order or request.

Exact duplicate rows are excluded from this analysis. Unknown statuses and gaps
over five minutes break sequences; tied timestamps cause cohort abstention. Reports
retain at most 50 strongest candidates and disclose truncation. Sorting is O(N log N)
in the worst case, with O(N) working memory under the existing 200,000-record cap;
this is not an out-of-core or distributed sequence pipeline.

Run **Latency incident** to see the new evidence panel on Overview and Agent activity.
New operational runs persist the evidence in their JSON reports and history; old
reports are not retroactively recomputed. Market datasets and generic unmapped logs
are not analyzed by this agent. No archive, suppression or deletion is authorized
by its findings. The existing optimization cost model is not changed by this agent.

`build_ai_messages(result)` produces optional provider-neutral explanatory context
with instructions to treat identifiers as untrusted data and separate observations
from hypotheses. It does not invoke a model or transmit any data. A future LLM
integration must enforce permissions outside the model; prompt text is not a security boundary.

Validation: eight added tests cover stable streams, known changes and exact counts,
reference-only thresholds, duplicate inflation, ordering, cohort isolation, ambiguous
timestamps, sparse/unknown data, long gaps and provider-neutral context. Synthetic
controls validate implementation behavior; real-world detection accuracy remains unmeasured.

## Measured layout experiments

Open **Experiment lab** for the latest recorded experiment. To reproduce:

```bash
python -m pip install -e '.[benchmark,test]'
python -m scripts.benchmark_lab
```

This downloads six public Binance spot trade archives (BTCUSDT and ETHUSDT,
January 1–3, 2020), verifies publisher SHA-256 checksums and retains provenance.
Downloads are capped at 20 MiB/archive, expanded files at 150 MiB/archive.
Raw downloads and generated candidates stay under ignored `data/benchmarks/`.
Machine-readable reports, SQL and all individual query timings are in `benchmarks/`.
Public source documentation: https://github.com/binance/binance-public-data
Engine documentation: https://duckdb.org/docs/current/data/parquet/overview
and https://duckdb.org/docs/current/data/csv/overview

The bounded search compares combined gzip CSV, Zstd Parquet, date/symbol-partitioned
Parquet and date/symbol-partitioned gzip CSV. The latter is a stronger control for
partition pruning, so we do not attribute every speedup to the file format.
Each candidate preserves the nine canonical string columns and all repeated records.
Full bidirectional `EXCEPT ALL` checks and matching results for every timed query
verify preservation. Numeric quantities are explicitly cast to decimal in queries;
VWAP returns exact numerator/denominator components, not approximate division.

Five calibration and five evaluation rounds run in seeded randomized order after
warmup, on a single DuckDB thread with a 1 GB engine memory limit. The Supervisor's
pure selection function (`backend/experiments.py`) minimizes measured conversion
seconds plus hypothetical query count times calibration median query time, subject
to verification and a 200 MiB additional-storage budget. It can choose no conversion.
Results evaluate the selected choice on separate timing rounds of the same data;
this is not validation on unseen workloads. Counts of 1, 100 and 10,000 are modeled
usage scenarios, not claims that all those queries were executed.

This implements a small proposal → experiment → verification → selection workflow.
It does not use the internal OpenAI research model, parallel LLM agents, formal
proofs or autonomous AWS operations. Ordinary correctness checks are not a Lean proof.
The comparison is local and warm-cache: no AWS billing, cold-cache performance,
physical bytes scanned, measured peak memory or statistical significance is claimed.
Conversion is timed once. Download/normalization and the search/verification costs
are excluded from projected candidate totals; total experiment elapsed time is
reported separately. Do not claim net optimizer savings without amortizing those
costs over actual future use. Original ZIPs and baseline gzip remain retained.


## Cost scenarios from measured data

Experiment lab now has an editable cost calculator (`POST /api/experiments/cost`).
It uses the recorded dataset sizes and local calibration query medians, with inputs
for monthly query count, months, assumed metered compute USD/hour, storage USD/GiB-month,
workload mix and additional one-time costs. `backend/experiment_costs.py` calculates
before/after component costs, net savings and break-even months. It selects the
lowest modeled cost, including keeping the baseline.

Original ZIPs and the canonical gzip remain stored in every scenario. Converted
copies add storage. By default the complete measured experiment duration is charged
once as setup for each alternative; this already includes conversion and is not
added twice. Turning off that overhead excludes search/preparation but still charges
conversion. This is a prospective scenario; no cloud spending or actions occur.

The example in `benchmarks/cost-example.json` uses 10,000 selective queries/month,
one month, assumed $0.10/hour compute and illustrative $0.023/GiB-month storage:
$0.148246 baseline vs $0.011603 partitioned Parquet, approximately $0.136642 saved.
The percentage is large but absolute savings are tiny on this dataset. Actual cash
savings require reducing billable compute rather than leaving the same server idle.
No claim is made that local execution matches the performance of a particular AWS instance.

Athena uses scanned-data pricing, so local runtime is not used to claim Athena
savings. See https://aws.amazon.com/athena/pricing/ and https://aws.amazon.com/s3/pricing/
for current region/service pricing. Request charges, transfers, billing minimums,
network services, labor, and other services are not calculated. Measured Athena scan
bytes and actual infrastructure charges are needed for a defensible AWS total.
