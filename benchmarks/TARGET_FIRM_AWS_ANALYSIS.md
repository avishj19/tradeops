# TradeOps help analysis: AWS-primary target firms

Generated: `2026-09-12T03:22:40.051540+00:00`

## Scope

- **120 datasets** — one operational execution-log batch per firm.
- **Target niches only:** boutique trading firms, specialist fintech SaaS, specialist brokers.
- **Cloud posture:** every firm is modeled as **AWS-primary** (S3 raw evidence + CloudWatch gateway logs + private-VPC worker plan).
- Not a survey of public equity issuers; symbols inside logs (AAPL, SPY, …) are traded instruments, not the customer firm.

## How much TradeOps helped (corpus)

| Metric | Value |
|---|---:|
| Firms / datasets | 120 |
| Total log rows ingested | 442,088 |
| Exact duplicates removed from analytical copy | 24,008 |
| Anomaly signals (latency / ERROR / REJECTED) | 25,790 |
| Raw bytes → Parquet bytes | 160,722,438 → 7,511,996 |
| Mean analytical size reduction | 95.26% |
| Mean / median help score (0–100) | 62.17 / 61.25 |
| Help score p10 / p90 | 49.6 / 76.6 |
| Archive-eligible firms (policy gate) | 120 |
| Private AWS plans within stated budget | 120 / 120 |
| Mean Supervisor runtime | 84.69 ms |
| Sum of illustrative monthly cost deltas (raw retained) | $-0.0002 |

## By target niche

| Niche | Firms | Mean help | Dupes removed | Anomalies | Mean size ↓ | Archive OK | AWS in budget | Mean AWS $/mo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Boutique trading | 40 | 62.1 | 4,880 | 5,169 | 94.97% | 40 | 40 | 41.36 |
| Specialist fintech SaaS | 40 | 62.2 | 8,070 | 8,688 | 95.36% | 40 | 40 | 68.92 |
| Specialist broker | 40 | 62.21 | 11,058 | 11,933 | 95.44% | 40 | 40 | 49.28 |

## AWS deployment boundary (what was exercised)

1. **Private AWS plan** (`POST /api/network-plan` / `network_plan`) per firm — S3 gateway, interface endpoints, budget headroom.
2. **Ingest planner** (`AWSAdapter.plan_event`) — versioned `raw/` object → idempotent optimized prefix (no live Glue submit).
3. **Local Supervisor pipeline** on each firm’s execution logs — the same agents the dashboard runs.

Live AWS account provisioning was **not** performed in this run (no credentials / no destructive cloud writes).

## Top helped firms

- **Harbor Brokerage (SPE-001)** (`specialist_broker`) — help 76.6: Log Analysis validated 4,717 gateway rows, removed 137 exact redelivery duplicates (2.9%), and flagged 1,007 latency/error signals (21.99% of unique rows).
- **Opsfolio Labs (FIN-004)** (`fintech_saas`) — help 76.6: Log Analysis validated 3,708 gateway rows, removed 108 exact redelivery duplicates (2.91%), and flagged 791 latency/error signals (21.97% of unique rows).
- **Midwest Brokerage (SPE-005)** (`specialist_broker`) — help 76.6: Log Analysis validated 5,211 gateway rows, removed 151 exact redelivery duplicates (2.9%), and flagged 1,113 latency/error signals (22.0% of unique rows).
- **Flowkit Labs (FIN-008)** (`fintech_saas`) — help 76.6: Log Analysis validated 3,502 gateway rows, removed 102 exact redelivery duplicates (2.91%), and flagged 747 latency/error signals (21.97% of unique rows).
- **Private Brokerage (SPE-009)** (`specialist_broker`) — help 76.6: Log Analysis validated 5,005 gateway rows, removed 145 exact redelivery duplicates (2.9%), and flagged 1,069 latency/error signals (22.0% of unique rows).
- **Fillbook Labs (FIN-012)** (`fintech_saas`) — help 76.6: Log Analysis validated 3,296 gateway rows, removed 96 exact redelivery duplicates (2.91%), and flagged 703 latency/error signals (21.97% of unique rows).
- **Clearing Brokerage (SPE-013)** (`specialist_broker`) — help 76.6: Log Analysis validated 4,799 gateway rows, removed 139 exact redelivery duplicates (2.9%), and flagged 1,025 latency/error signals (22.0% of unique rows).
- **Bookstack Labs (FIN-016)** (`fintech_saas`) — help 76.6: Log Analysis validated 3,790 gateway rows, removed 110 exact redelivery duplicates (2.9%), and flagged 809 latency/error signals (21.98% of unique rows).
- **Market Brokerage (SPE-017)** (`specialist_broker`) — help 76.6: Log Analysis validated 5,294 gateway rows, removed 154 exact redelivery duplicates (2.91%), and flagged 1,130 latency/error signals (21.98% of unique rows).
- **SettleOS Labs (FIN-020)** (`fintech_saas`) — help 76.6: Log Analysis validated 3,584 gateway rows, removed 104 exact redelivery duplicates (2.9%), and flagged 765 latency/error signals (21.98% of unique rows).

## Least helped firms

- **Echo Capital (BOU-025)** (`boutique_trading`) — help 49.4: Log Analysis validated 2,018 gateway rows, removed 58 exact redelivery duplicates (2.87%), and flagged 0 latency/error signals (0.0% of unique rows).
- **Apex Capital (BOU-001)** (`boutique_trading`) — help 49.5: Log Analysis validated 1,854 gateway rows, removed 54 exact redelivery duplicates (2.91%), and flagged 0 latency/error signals (0.0% of unique rows).
- **Meridian Capital (BOU-005)** (`boutique_trading`) — help 49.5: Log Analysis validated 2,348 gateway rows, removed 68 exact redelivery duplicates (2.9%), and flagged 0 latency/error signals (0.0% of unique rows).
- **Signal Capital (BOU-009)** (`boutique_trading`) — help 49.5: Log Analysis validated 2,142 gateway rows, removed 62 exact redelivery duplicates (2.89%), and flagged 0 latency/error signals (0.0% of unique rows).
- **Prairie Capital (BOU-013)** (`boutique_trading`) — help 49.5: Log Analysis validated 1,936 gateway rows, removed 56 exact redelivery duplicates (2.89%), and flagged 0 latency/error signals (0.0% of unique rows).
- **Horizon Capital (BOU-017)** (`boutique_trading`) — help 49.5: Log Analysis validated 2,430 gateway rows, removed 70 exact redelivery duplicates (2.88%), and flagged 0 latency/error signals (0.0% of unique rows).
- **Atlas Capital (BOU-021)** (`boutique_trading`) — help 49.5: Log Analysis validated 2,224 gateway rows, removed 64 exact redelivery duplicates (2.88%), and flagged 0 latency/error signals (0.0% of unique rows).
- **Monad Capital (BOU-033)** (`boutique_trading`) — help 49.5: Log Analysis validated 2,307 gateway rows, removed 67 exact redelivery duplicates (2.9%), and flagged 0 latency/error signals (0.0% of unique rows).
- **Northbridge Trading (BOU-037)** (`boutique_trading`) — help 49.5: Log Analysis validated 2,101 gateway rows, removed 61 exact redelivery duplicates (2.9%), and flagged 0 latency/error signals (0.0% of unique rows).
- **Clearpath Labs (FIN-002)** (`fintech_saas`) — help 49.6: Log Analysis validated 3,460 gateway rows, removed 100 exact redelivery duplicates (2.89%), and flagged 0 latency/error signals (0.0% of unique rows).

## Detailed per-firm feedback

Each firm below includes agent outcomes and AWS plan notes.

### Apex Capital (BOU-001)

- Niche: `boutique_trading` · Region: `us-east-1` · Scenario: `normal` · Help score: **49.5** · Runtime: 80.97 ms
- S3: `s3://to-bou-001-raw-logs/raw/execution/` · CW: `/tradeops/bou-001/execution-gateway`
- Rows 1,854 (unique 1,800); dupes 54; anomalies 0; size 667,710→34,982 (94.8%)
- AWS plan $29.68/mo; ingest idempotency `54b4afe41e52f86f…`
  - Apex Capital (BOU-001) (boutique_trading) ingests primarily from AWS us-east-1 via s3://to-bou-001-raw-logs/raw/execution/ and /tradeops/bou-001/execution-gateway.
  - Log Analysis validated 1,854 gateway rows, removed 54 exact redelivery duplicates (2.91%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (667,710 → 34,982 bytes, 94.8% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $29.68/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.5/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Ledger Labs (FIN-001)

- Niche: `fintech_saas` · Region: `us-east-2` · Scenario: `duplicates` · Help score: **63.9** · Runtime: 76.7 ms
- S3: `s3://to-fin-001-raw-logs/raw/execution/` · CW: `/tradeops/fin-001/execution-gateway`
- Rows 3,628 (unique 3,240); dupes 388; anomalies 0; size 1,326,983→58,315 (95.6%)
- AWS plan $68.92/mo; ingest idempotency `27244ec9989656a3…`
  - Ledger Labs (FIN-001) (fintech_saas) ingests primarily from AWS us-east-2 via s3://to-fin-001-raw-logs/raw/execution/ and /tradeops/fin-001/execution-gateway.
  - Log Analysis validated 3,628 gateway rows, removed 388 exact redelivery duplicates (10.69%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,326,983 → 58,315 bytes, 95.6% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.9/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Harbor Brokerage (SPE-001)

- Niche: `specialist_broker` · Region: `us-west-2` · Scenario: `latency_spike` · Help score: **76.6** · Runtime: 101.54 ms
- S3: `s3://to-spe-001-raw-logs/raw/execution/` · CW: `/tradeops/spe-001/execution-gateway`
- Rows 4,717 (unique 4,580); dupes 137; anomalies 1,007; size 1,704,549→81,988 (95.2%)
- AWS plan $49.28/mo; ingest idempotency `9e922fd1b52ab03b…`
  - Harbor Brokerage (SPE-001) (specialist_broker) ingests primarily from AWS us-west-2 via s3://to-spe-001-raw-logs/raw/execution/ and /tradeops/spe-001/execution-gateway.
  - Log Analysis validated 4,717 gateway rows, removed 137 exact redelivery duplicates (2.9%), and flagged 1,007 latency/error signals (21.99% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,704,549 → 81,988 bytes, 95.2% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×320 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×687 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Northbridge Capital (BOU-002)

- Niche: `boutique_trading` · Region: `eu-west-1` · Scenario: `mixed_errors` · Help score: **58.6** · Runtime: 46.0 ms
- S3: `s3://to-bou-002-raw-logs/raw/execution/` · CW: `/tradeops/bou-002/execution-gateway`
- Rows 2,016 (unique 1,920); dupes 96; anomalies 52; size 725,714→37,029 (94.9%)
- AWS plan $44.28/mo; ingest idempotency `c0de5f8a8b1ae422…`
  - Northbridge Capital (BOU-002) (boutique_trading) ingests primarily from AWS eu-west-1 via s3://to-bou-002-raw-logs/raw/execution/ and /tradeops/bou-002/execution-gateway.
  - Log Analysis validated 2,016 gateway rows, removed 96 exact redelivery duplicates (4.76%), and flagged 52 latency/error signals (2.71% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (725,714 → 37,029 bytes, 94.9% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×52 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Clearpath Labs (FIN-002)

- Niche: `fintech_saas` · Region: `ap-northeast-1` · Scenario: `normal` · Help score: **49.6** · Runtime: 70.49 ms
- S3: `s3://to-fin-002-raw-logs/raw/execution/` · CW: `/tradeops/fin-002/execution-gateway`
- Rows 3,460 (unique 3,360); dupes 100; anomalies 0; size 1,282,606→60,359 (95.3%)
- AWS plan $68.92/mo; ingest idempotency `0b8274ca1f6ccb44…`
  - Clearpath Labs (FIN-002) (fintech_saas) ingests primarily from AWS ap-northeast-1 via s3://to-fin-002-raw-logs/raw/execution/ and /tradeops/fin-002/execution-gateway.
  - Log Analysis validated 3,460 gateway rows, removed 100 exact redelivery duplicates (2.89%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,282,606 → 60,359 bytes, 95.3% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Seaboard Brokerage (SPE-002)

- Niche: `specialist_broker` · Region: `us-east-1` · Scenario: `duplicates` · Help score: **63.9** · Runtime: 109.4 ms
- S3: `s3://to-spe-002-raw-logs/raw/execution/` · CW: `/tradeops/spe-002/execution-gateway`
- Rows 5,264 (unique 4,700); dupes 564; anomalies 0; size 1,900,699→81,906 (95.7%)
- AWS plan $49.28/mo; ingest idempotency `254ede9bcfddac07…`
  - Seaboard Brokerage (SPE-002) (specialist_broker) ingests primarily from AWS us-east-1 via s3://to-spe-002-raw-logs/raw/execution/ and /tradeops/spe-002/execution-gateway.
  - Log Analysis validated 5,264 gateway rows, removed 564 exact redelivery duplicates (10.71%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,900,699 → 81,906 bytes, 95.7% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.9/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Harbor Capital (BOU-003)

- Niche: `boutique_trading` · Region: `us-east-2` · Scenario: `latency_spike` · Help score: **76.5** · Runtime: 44.25 ms
- S3: `s3://to-bou-003-raw-logs/raw/execution/` · CW: `/tradeops/bou-003/execution-gateway`
- Rows 2,101 (unique 2,040); dupes 61; anomalies 448; size 757,320→39,459 (94.8%)
- AWS plan $44.28/mo; ingest idempotency `2054fe798e429dd0…`
  - Harbor Capital (BOU-003) (boutique_trading) ingests primarily from AWS us-east-2 via s3://to-bou-003-raw-logs/raw/execution/ and /tradeops/bou-003/execution-gateway.
  - Log Analysis validated 2,101 gateway rows, removed 61 exact redelivery duplicates (2.9%), and flagged 448 latency/error signals (21.96% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (757,320 → 39,459 bytes, 94.8% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×143 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×305 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.5/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Routeline Labs (FIN-003)

- Niche: `fintech_saas` · Region: `us-west-2` · Scenario: `mixed_errors` · Help score: **58.7** · Runtime: 71.23 ms
- S3: `s3://to-fin-003-raw-logs/raw/execution/` · CW: `/tradeops/fin-003/execution-gateway`
- Rows 3,654 (unique 3,480); dupes 174; anomalies 95; size 1,336,430→62,158 (95.3%)
- AWS plan $68.92/mo; ingest idempotency `65f5d6b15d6749e3…`
  - Routeline Labs (FIN-003) (fintech_saas) ingests primarily from AWS us-west-2 via s3://to-fin-003-raw-logs/raw/execution/ and /tradeops/fin-003/execution-gateway.
  - Log Analysis validated 3,654 gateway rows, removed 174 exact redelivery duplicates (4.76%), and flagged 95 latency/error signals (2.73% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,336,430 → 62,158 bytes, 95.3% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×95 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Continental Brokerage (SPE-003)

- Niche: `specialist_broker` · Region: `eu-west-1` · Scenario: `normal` · Help score: **49.6** · Runtime: 101.33 ms
- S3: `s3://to-spe-003-raw-logs/raw/execution/` · CW: `/tradeops/spe-003/execution-gateway`
- Rows 4,964 (unique 4,820); dupes 144; anomalies 0; size 1,793,470→83,408 (95.3%)
- AWS plan $49.28/mo; ingest idempotency `735c22cf4b8796af…`
  - Continental Brokerage (SPE-003) (specialist_broker) ingests primarily from AWS eu-west-1 via s3://to-spe-003-raw-logs/raw/execution/ and /tradeops/spe-003/execution-gateway.
  - Log Analysis validated 4,964 gateway rows, removed 144 exact redelivery duplicates (2.9%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,793,470 → 83,408 bytes, 95.3% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Lattice Capital (BOU-004)

- Niche: `boutique_trading` · Region: `ap-northeast-1` · Scenario: `duplicates` · Help score: **63.8** · Runtime: 47.63 ms
- S3: `s3://to-bou-004-raw-logs/raw/execution/` · CW: `/tradeops/bou-004/execution-gateway`
- Rows 2,419 (unique 2,160); dupes 259; anomalies 0; size 883,268→41,463 (95.3%)
- AWS plan $44.28/mo; ingest idempotency `d821ce36b5902b19…`
  - Lattice Capital (BOU-004) (boutique_trading) ingests primarily from AWS ap-northeast-1 via s3://to-bou-004-raw-logs/raw/execution/ and /tradeops/bou-004/execution-gateway.
  - Log Analysis validated 2,419 gateway rows, removed 259 exact redelivery duplicates (10.71%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (883,268 → 41,463 bytes, 95.3% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.8/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Opsfolio Labs (FIN-004)

- Niche: `fintech_saas` · Region: `us-east-1` · Scenario: `latency_spike` · Help score: **76.6** · Runtime: 79.13 ms
- S3: `s3://to-fin-004-raw-logs/raw/execution/` · CW: `/tradeops/fin-004/execution-gateway`
- Rows 3,708 (unique 3,600); dupes 108; anomalies 791; size 1,357,446→65,252 (95.2%)
- AWS plan $68.92/mo; ingest idempotency `b1583ede1a52bb5b…`
  - Opsfolio Labs (FIN-004) (fintech_saas) ingests primarily from AWS us-east-1 via s3://to-fin-004-raw-logs/raw/execution/ and /tradeops/fin-004/execution-gateway.
  - Log Analysis validated 3,708 gateway rows, removed 108 exact redelivery duplicates (2.91%), and flagged 791 latency/error signals (21.97% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,357,446 → 65,252 bytes, 95.2% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×251 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×540 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Pacific Brokerage (SPE-004)

- Niche: `specialist_broker` · Region: `us-east-2` · Scenario: `mixed_errors` · Help score: **58.7** · Runtime: 110.54 ms
- S3: `s3://to-spe-004-raw-logs/raw/execution/` · CW: `/tradeops/spe-004/execution-gateway`
- Rows 5,187 (unique 4,940); dupes 247; anomalies 134; size 1,872,986→85,657 (95.4%)
- AWS plan $49.28/mo; ingest idempotency `d29bb791ed79245d…`
  - Pacific Brokerage (SPE-004) (specialist_broker) ingests primarily from AWS us-east-2 via s3://to-spe-004-raw-logs/raw/execution/ and /tradeops/spe-004/execution-gateway.
  - Log Analysis validated 5,187 gateway rows, removed 247 exact redelivery duplicates (4.76%), and flagged 134 latency/error signals (2.71% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,872,986 → 85,657 bytes, 95.4% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×134 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Meridian Capital (BOU-005)

- Niche: `boutique_trading` · Region: `us-west-2` · Scenario: `normal` · Help score: **49.5** · Runtime: 48.63 ms
- S3: `s3://to-bou-005-raw-logs/raw/execution/` · CW: `/tradeops/bou-005/execution-gateway`
- Rows 2,348 (unique 2,280); dupes 68; anomalies 0; size 845,583→43,324 (94.9%)
- AWS plan $44.28/mo; ingest idempotency `12fb913af7d08c2c…`
  - Meridian Capital (BOU-005) (boutique_trading) ingests primarily from AWS us-west-2 via s3://to-bou-005-raw-logs/raw/execution/ and /tradeops/bou-005/execution-gateway.
  - Log Analysis validated 2,348 gateway rows, removed 68 exact redelivery duplicates (2.9%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (845,583 → 43,324 bytes, 94.9% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.5/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### TradeNest Labs (FIN-005)

- Niche: `fintech_saas` · Region: `eu-west-1` · Scenario: `duplicates` · Help score: **63.9** · Runtime: 81.48 ms
- S3: `s3://to-fin-005-raw-logs/raw/execution/` · CW: `/tradeops/fin-005/execution-gateway`
- Rows 4,166 (unique 3,720); dupes 446; anomalies 0; size 1,523,830→65,665 (95.7%)
- AWS plan $68.92/mo; ingest idempotency `4f29600f29864fea…`
  - TradeNest Labs (FIN-005) (fintech_saas) ingests primarily from AWS eu-west-1 via s3://to-fin-005-raw-logs/raw/execution/ and /tradeops/fin-005/execution-gateway.
  - Log Analysis validated 4,166 gateway rows, removed 446 exact redelivery duplicates (10.71%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,523,830 → 65,665 bytes, 95.7% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.9/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Midwest Brokerage (SPE-005)

- Niche: `specialist_broker` · Region: `ap-northeast-1` · Scenario: `latency_spike` · Help score: **76.6** · Runtime: 107.41 ms
- S3: `s3://to-spe-005-raw-logs/raw/execution/` · CW: `/tradeops/spe-005/execution-gateway`
- Rows 5,211 (unique 5,060); dupes 151; anomalies 1,113; size 1,909,571→89,872 (95.3%)
- AWS plan $49.28/mo; ingest idempotency `45f16a7b6de86f67…`
  - Midwest Brokerage (SPE-005) (specialist_broker) ingests primarily from AWS ap-northeast-1 via s3://to-spe-005-raw-logs/raw/execution/ and /tradeops/spe-005/execution-gateway.
  - Log Analysis validated 5,211 gateway rows, removed 151 exact redelivery duplicates (2.9%), and flagged 1,113 latency/error signals (22.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,909,571 → 89,872 bytes, 95.3% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×354 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×759 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Vector Capital (BOU-006)

- Niche: `boutique_trading` · Region: `us-east-1` · Scenario: `mixed_errors` · Help score: **58.6** · Runtime: 58.16 ms
- S3: `s3://to-bou-006-raw-logs/raw/execution/` · CW: `/tradeops/bou-006/execution-gateway`
- Rows 2,520 (unique 2,400); dupes 120; anomalies 65; size 907,319→45,195 (95.0%)
- AWS plan $29.68/mo; ingest idempotency `7b525d8e1a1888dd…`
  - Vector Capital (BOU-006) (boutique_trading) ingests primarily from AWS us-east-1 via s3://to-bou-006-raw-logs/raw/execution/ and /tradeops/bou-006/execution-gateway.
  - Log Analysis validated 2,520 gateway rows, removed 120 exact redelivery duplicates (4.76%), and flagged 65 latency/error signals (2.71% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (907,319 → 45,195 bytes, 95.0% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $29.68/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×65 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Auditly Labs (FIN-006)

- Niche: `fintech_saas` · Region: `us-east-2` · Scenario: `normal` · Help score: **49.6** · Runtime: 84.46 ms
- S3: `s3://to-fin-006-raw-logs/raw/execution/` · CW: `/tradeops/fin-006/execution-gateway`
- Rows 3,955 (unique 3,840); dupes 115; anomalies 0; size 1,446,634→67,684 (95.3%)
- AWS plan $68.92/mo; ingest idempotency `2f035e51988c634f…`
  - Auditly Labs (FIN-006) (fintech_saas) ingests primarily from AWS us-east-2 via s3://to-fin-006-raw-logs/raw/execution/ and /tradeops/fin-006/execution-gateway.
  - Log Analysis validated 3,955 gateway rows, removed 115 exact redelivery duplicates (2.91%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,446,634 → 67,684 bytes, 95.3% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Atlantic Brokerage (SPE-006)

- Niche: `specialist_broker` · Region: `us-west-2` · Scenario: `duplicates` · Help score: **63.9** · Runtime: 102.52 ms
- S3: `s3://to-spe-006-raw-logs/raw/execution/` · CW: `/tradeops/spe-006/execution-gateway`
- Rows 5,040 (unique 4,500); dupes 540; anomalies 0; size 1,820,879→78,991 (95.7%)
- AWS plan $49.28/mo; ingest idempotency `6b3aa48ef3d9bf56…`
  - Atlantic Brokerage (SPE-006) (specialist_broker) ingests primarily from AWS us-west-2 via s3://to-spe-006-raw-logs/raw/execution/ and /tradeops/spe-006/execution-gateway.
  - Log Analysis validated 5,040 gateway rows, removed 540 exact redelivery duplicates (10.71%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,820,879 → 78,991 bytes, 95.7% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.9/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Cascade Capital (BOU-007)

- Niche: `boutique_trading` · Region: `eu-west-1` · Scenario: `latency_spike` · Help score: **76.5** · Runtime: 42.31 ms
- S3: `s3://to-bou-007-raw-logs/raw/execution/` · CW: `/tradeops/bou-007/execution-gateway`
- Rows 1,895 (unique 1,840); dupes 55; anomalies 404; size 682,979→36,141 (94.7%)
- AWS plan $44.28/mo; ingest idempotency `edda57005e46c80e…`
  - Cascade Capital (BOU-007) (boutique_trading) ingests primarily from AWS eu-west-1 via s3://to-bou-007-raw-logs/raw/execution/ and /tradeops/bou-007/execution-gateway.
  - Log Analysis validated 1,895 gateway rows, removed 55 exact redelivery duplicates (2.9%), and flagged 404 latency/error signals (21.96% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (682,979 → 36,141 bytes, 94.7% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×129 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×275 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.5/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Reconcile Labs (FIN-007)

- Niche: `fintech_saas` · Region: `ap-northeast-1` · Scenario: `mixed_errors` · Help score: **58.7** · Runtime: 74.45 ms
- S3: `s3://to-fin-007-raw-logs/raw/execution/` · CW: `/tradeops/fin-007/execution-gateway`
- Rows 3,444 (unique 3,280); dupes 164; anomalies 89; size 1,276,826→59,152 (95.4%)
- AWS plan $68.92/mo; ingest idempotency `798940c16931271a…`
  - Reconcile Labs (FIN-007) (fintech_saas) ingests primarily from AWS ap-northeast-1 via s3://to-fin-007-raw-logs/raw/execution/ and /tradeops/fin-007/execution-gateway.
  - Log Analysis validated 3,444 gateway rows, removed 164 exact redelivery duplicates (4.76%), and flagged 89 latency/error signals (2.71% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,276,826 → 59,152 bytes, 95.4% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×89 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Crossborder Brokerage (SPE-007)

- Niche: `specialist_broker` · Region: `us-east-1` · Scenario: `normal` · Help score: **49.6** · Runtime: 104.15 ms
- S3: `s3://to-spe-007-raw-logs/raw/execution/` · CW: `/tradeops/spe-007/execution-gateway`
- Rows 4,758 (unique 4,620); dupes 138; anomalies 0; size 1,718,584→80,564 (95.3%)
- AWS plan $49.28/mo; ingest idempotency `0b8206459f0bd2c0…`
  - Crossborder Brokerage (SPE-007) (specialist_broker) ingests primarily from AWS us-east-1 via s3://to-spe-007-raw-logs/raw/execution/ and /tradeops/spe-007/execution-gateway.
  - Log Analysis validated 4,758 gateway rows, removed 138 exact redelivery duplicates (2.9%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,718,584 → 80,564 bytes, 95.3% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Quorum Capital (BOU-008)

- Niche: `boutique_trading` · Region: `us-east-2` · Scenario: `duplicates` · Help score: **63.8** · Runtime: 65.4 ms
- S3: `s3://to-bou-008-raw-logs/raw/execution/` · CW: `/tradeops/bou-008/execution-gateway`
- Rows 2,195 (unique 1,960); dupes 235; anomalies 0; size 790,616→37,768 (95.2%)
- AWS plan $44.28/mo; ingest idempotency `4471f5e6571edb9b…`
  - Quorum Capital (BOU-008) (boutique_trading) ingests primarily from AWS us-east-2 via s3://to-bou-008-raw-logs/raw/execution/ and /tradeops/bou-008/execution-gateway.
  - Log Analysis validated 2,195 gateway rows, removed 235 exact redelivery duplicates (10.71%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (790,616 → 37,768 bytes, 95.2% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.8/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Flowkit Labs (FIN-008)

- Niche: `fintech_saas` · Region: `us-west-2` · Scenario: `latency_spike` · Help score: **76.6** · Runtime: 108.92 ms
- S3: `s3://to-fin-008-raw-logs/raw/execution/` · CW: `/tradeops/fin-008/execution-gateway`
- Rows 3,502 (unique 3,400); dupes 102; anomalies 747; size 1,282,518→62,209 (95.1%)
- AWS plan $68.92/mo; ingest idempotency `64616a6fb9346ab7…`
  - Flowkit Labs (FIN-008) (fintech_saas) ingests primarily from AWS us-west-2 via s3://to-fin-008-raw-logs/raw/execution/ and /tradeops/fin-008/execution-gateway.
  - Log Analysis validated 3,502 gateway rows, removed 102 exact redelivery duplicates (2.91%), and flagged 747 latency/error signals (21.97% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,282,518 → 62,209 bytes, 95.1% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×237 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×510 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Institutional Brokerage (SPE-008)

- Niche: `specialist_broker` · Region: `eu-west-1` · Scenario: `mixed_errors` · Help score: **58.7** · Runtime: 109.53 ms
- S3: `s3://to-spe-008-raw-logs/raw/execution/` · CW: `/tradeops/spe-008/execution-gateway`
- Rows 4,977 (unique 4,740); dupes 237; anomalies 129; size 1,796,581→82,448 (95.4%)
- AWS plan $49.28/mo; ingest idempotency `cbfcd599dcd8e5e7…`
  - Institutional Brokerage (SPE-008) (specialist_broker) ingests primarily from AWS eu-west-1 via s3://to-spe-008-raw-logs/raw/execution/ and /tradeops/spe-008/execution-gateway.
  - Log Analysis validated 4,977 gateway rows, removed 237 exact redelivery duplicates (4.76%), and flagged 129 latency/error signals (2.72% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,796,581 → 82,448 bytes, 95.4% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×129 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Signal Capital (BOU-009)

- Niche: `boutique_trading` · Region: `ap-northeast-1` · Scenario: `normal` · Help score: **49.5** · Runtime: 49.71 ms
- S3: `s3://to-bou-009-raw-logs/raw/execution/` · CW: `/tradeops/bou-009/execution-gateway`
- Rows 2,142 (unique 2,080); dupes 62; anomalies 0; size 782,039→40,158 (94.9%)
- AWS plan $44.28/mo; ingest idempotency `74af27c5ed919d98…`
  - Signal Capital (BOU-009) (boutique_trading) ingests primarily from AWS ap-northeast-1 via s3://to-bou-009-raw-logs/raw/execution/ and /tradeops/bou-009/execution-gateway.
  - Log Analysis validated 2,142 gateway rows, removed 62 exact redelivery duplicates (2.89%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (782,039 → 40,158 bytes, 94.9% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.5/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### PostTrade Labs (FIN-009)

- Niche: `fintech_saas` · Region: `us-east-1` · Scenario: `duplicates` · Help score: **63.9** · Runtime: 113.67 ms
- S3: `s3://to-fin-009-raw-logs/raw/execution/` · CW: `/tradeops/fin-009/execution-gateway`
- Rows 3,942 (unique 3,520); dupes 422; anomalies 0; size 1,442,201→62,863 (95.6%)
- AWS plan $68.92/mo; ingest idempotency `793ca93103f8f0a5…`
  - PostTrade Labs (FIN-009) (fintech_saas) ingests primarily from AWS us-east-1 via s3://to-fin-009-raw-logs/raw/execution/ and /tradeops/fin-009/execution-gateway.
  - Log Analysis validated 3,942 gateway rows, removed 422 exact redelivery duplicates (10.71%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,442,201 → 62,863 bytes, 95.6% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.9/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Private Brokerage (SPE-009)

- Niche: `specialist_broker` · Region: `us-east-2` · Scenario: `latency_spike` · Help score: **76.6** · Runtime: 152.63 ms
- S3: `s3://to-spe-009-raw-logs/raw/execution/` · CW: `/tradeops/spe-009/execution-gateway`
- Rows 5,005 (unique 4,860); dupes 145; anomalies 1,069; size 1,808,831→86,461 (95.2%)
- AWS plan $49.28/mo; ingest idempotency `9a3b511b8ce1cfac…`
  - Private Brokerage (SPE-009) (specialist_broker) ingests primarily from AWS us-east-2 via s3://to-spe-009-raw-logs/raw/execution/ and /tradeops/spe-009/execution-gateway.
  - Log Analysis validated 5,005 gateway rows, removed 145 exact redelivery duplicates (2.9%), and flagged 1,069 latency/error signals (22.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,808,831 → 86,461 bytes, 95.2% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×340 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×729 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Ridge Capital (BOU-010)

- Niche: `boutique_trading` · Region: `us-west-2` · Scenario: `mixed_errors` · Help score: **58.6** · Runtime: 73.13 ms
- S3: `s3://to-bou-010-raw-logs/raw/execution/` · CW: `/tradeops/bou-010/execution-gateway`
- Rows 2,310 (unique 2,200); dupes 110; anomalies 60; size 831,944→41,978 (95.0%)
- AWS plan $44.28/mo; ingest idempotency `95fe0b4db1506f83…`
  - Ridge Capital (BOU-010) (boutique_trading) ingests primarily from AWS us-west-2 via s3://to-bou-010-raw-logs/raw/execution/ and /tradeops/bou-010/execution-gateway.
  - Log Analysis validated 2,310 gateway rows, removed 110 exact redelivery duplicates (4.76%), and flagged 60 latency/error signals (2.73% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (831,944 → 41,978 bytes, 95.0% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×60 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Risklane Labs (FIN-010)

- Niche: `fintech_saas` · Region: `eu-west-1` · Scenario: `normal` · Help score: **49.6** · Runtime: 82.49 ms
- S3: `s3://to-fin-010-raw-logs/raw/execution/` · CW: `/tradeops/fin-010/execution-gateway`
- Rows 3,749 (unique 3,640); dupes 109; anomalies 0; size 1,371,161→64,556 (95.3%)
- AWS plan $68.92/mo; ingest idempotency `ebf5ed741bd234dd…`
  - Risklane Labs (FIN-010) (fintech_saas) ingests primarily from AWS eu-west-1 via s3://to-fin-010-raw-logs/raw/execution/ and /tradeops/fin-010/execution-gateway.
  - Log Analysis validated 3,749 gateway rows, removed 109 exact redelivery duplicates (2.91%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,371,161 → 64,556 bytes, 95.3% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Prime Brokerage (SPE-010)

- Niche: `specialist_broker` · Region: `ap-northeast-1` · Scenario: `duplicates` · Help score: **63.9** · Runtime: 118.16 ms
- S3: `s3://to-spe-010-raw-logs/raw/execution/` · CW: `/tradeops/spe-010/execution-gateway`
- Rows 5,577 (unique 4,980); dupes 597; anomalies 0; size 2,041,840→85,807 (95.8%)
- AWS plan $49.28/mo; ingest idempotency `afbf3650902896b8…`
  - Prime Brokerage (SPE-010) (specialist_broker) ingests primarily from AWS ap-northeast-1 via s3://to-spe-010-raw-logs/raw/execution/ and /tradeops/spe-010/execution-gateway.
  - Log Analysis validated 5,577 gateway rows, removed 597 exact redelivery duplicates (10.7%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (2,041,840 → 85,807 bytes, 95.8% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.9/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Cobalt Capital (BOU-011)

- Niche: `boutique_trading` · Region: `us-east-1` · Scenario: `latency_spike` · Help score: **76.5** · Runtime: 65.0 ms
- S3: `s3://to-bou-011-raw-logs/raw/execution/` · CW: `/tradeops/bou-011/execution-gateway`
- Rows 2,389 (unique 2,320); dupes 69; anomalies 510; size 861,181→44,599 (94.8%)
- AWS plan $29.68/mo; ingest idempotency `dd54a44023819e85…`
  - Cobalt Capital (BOU-011) (boutique_trading) ingests primarily from AWS us-east-1 via s3://to-bou-011-raw-logs/raw/execution/ and /tradeops/bou-011/execution-gateway.
  - Log Analysis validated 2,389 gateway rows, removed 69 exact redelivery duplicates (2.89%), and flagged 510 latency/error signals (21.98% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (861,181 → 44,599 bytes, 94.8% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $29.68/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×162 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×348 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.5/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### OrderMesh Labs (FIN-011)

- Niche: `fintech_saas` · Region: `us-east-2` · Scenario: `mixed_errors` · Help score: **58.7** · Runtime: 101.67 ms
- S3: `s3://to-fin-011-raw-logs/raw/execution/` · CW: `/tradeops/fin-011/execution-gateway`
- Rows 3,948 (unique 3,760); dupes 188; anomalies 102; size 1,444,166→66,395 (95.4%)
- AWS plan $68.92/mo; ingest idempotency `88acbfd52379de65…`
  - OrderMesh Labs (FIN-011) (fintech_saas) ingests primarily from AWS us-east-2 via s3://to-fin-011-raw-logs/raw/execution/ and /tradeops/fin-011/execution-gateway.
  - Log Analysis validated 3,948 gateway rows, removed 188 exact redelivery duplicates (4.76%), and flagged 102 latency/error signals (2.71% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,444,166 → 66,395 bytes, 95.4% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×102 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Agency Brokerage (SPE-011)

- Niche: `specialist_broker` · Region: `us-west-2` · Scenario: `normal` · Help score: **49.7** · Runtime: 116.31 ms
- S3: `s3://to-spe-011-raw-logs/raw/execution/` · CW: `/tradeops/spe-011/execution-gateway`
- Rows 5,253 (unique 5,100); dupes 153; anomalies 0; size 1,897,245→88,076 (95.4%)
- AWS plan $49.28/mo; ingest idempotency `15b25dda79dfad43…`
  - Agency Brokerage (SPE-011) (specialist_broker) ingests primarily from AWS us-west-2 via s3://to-spe-011-raw-logs/raw/execution/ and /tradeops/spe-011/execution-gateway.
  - Log Analysis validated 5,253 gateway rows, removed 153 exact redelivery duplicates (2.91%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,897,245 → 88,076 bytes, 95.4% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Summit Capital (BOU-012)

- Niche: `boutique_trading` · Region: `eu-west-1` · Scenario: `duplicates` · Help score: **63.8** · Runtime: 57.79 ms
- S3: `s3://to-bou-012-raw-logs/raw/execution/` · CW: `/tradeops/bou-012/execution-gateway`
- Rows 2,732 (unique 2,440); dupes 292; anomalies 0; size 983,959→45,651 (95.4%)
- AWS plan $44.28/mo; ingest idempotency `80d917457593fd83…`
  - Summit Capital (BOU-012) (boutique_trading) ingests primarily from AWS eu-west-1 via s3://to-bou-012-raw-logs/raw/execution/ and /tradeops/bou-012/execution-gateway.
  - Log Analysis validated 2,732 gateway rows, removed 292 exact redelivery duplicates (10.69%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (983,959 → 45,651 bytes, 95.4% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.8/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Fillbook Labs (FIN-012)

- Niche: `fintech_saas` · Region: `ap-northeast-1` · Scenario: `latency_spike` · Help score: **76.6** · Runtime: 73.04 ms
- S3: `s3://to-fin-012-raw-logs/raw/execution/` · CW: `/tradeops/fin-012/execution-gateway`
- Rows 3,296 (unique 3,200); dupes 96; anomalies 703; size 1,222,996→59,100 (95.2%)
- AWS plan $68.92/mo; ingest idempotency `c9e7737938099050…`
  - Fillbook Labs (FIN-012) (fintech_saas) ingests primarily from AWS ap-northeast-1 via s3://to-fin-012-raw-logs/raw/execution/ and /tradeops/fin-012/execution-gateway.
  - Log Analysis validated 3,296 gateway rows, removed 96 exact redelivery duplicates (2.91%), and flagged 703 latency/error signals (21.97% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,222,996 → 59,100 bytes, 95.2% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×223 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×480 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Desk Brokerage (SPE-012)

- Niche: `specialist_broker` · Region: `us-east-1` · Scenario: `mixed_errors` · Help score: **58.7** · Runtime: 100.4 ms
- S3: `s3://to-spe-012-raw-logs/raw/execution/` · CW: `/tradeops/spe-012/execution-gateway`
- Rows 4,767 (unique 4,540); dupes 227; anomalies 123; size 1,721,281→79,475 (95.4%)
- AWS plan $49.28/mo; ingest idempotency `384f49c852bae720…`
  - Desk Brokerage (SPE-012) (specialist_broker) ingests primarily from AWS us-east-1 via s3://to-spe-012-raw-logs/raw/execution/ and /tradeops/spe-012/execution-gateway.
  - Log Analysis validated 4,767 gateway rows, removed 227 exact redelivery duplicates (4.76%), and flagged 123 latency/error signals (2.71% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,721,281 → 79,475 bytes, 95.4% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×123 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Prairie Capital (BOU-013)

- Niche: `boutique_trading` · Region: `us-east-2` · Scenario: `normal` · Help score: **49.5** · Runtime: 44.84 ms
- S3: `s3://to-bou-013-raw-logs/raw/execution/` · CW: `/tradeops/bou-013/execution-gateway`
- Rows 1,936 (unique 1,880); dupes 56; anomalies 0; size 697,389→36,328 (94.8%)
- AWS plan $44.28/mo; ingest idempotency `48ba0e2205a16337…`
  - Prairie Capital (BOU-013) (boutique_trading) ingests primarily from AWS us-east-2 via s3://to-bou-013-raw-logs/raw/execution/ and /tradeops/bou-013/execution-gateway.
  - Log Analysis validated 1,936 gateway rows, removed 56 exact redelivery duplicates (2.89%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (697,389 → 36,328 bytes, 94.8% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.5/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### CustodyIQ Labs (FIN-013)

- Niche: `fintech_saas` · Region: `us-west-2` · Scenario: `duplicates` · Help score: **63.9** · Runtime: 79.38 ms
- S3: `s3://to-fin-013-raw-logs/raw/execution/` · CW: `/tradeops/fin-013/execution-gateway`
- Rows 3,718 (unique 3,320); dupes 398; anomalies 0; size 1,359,791→59,839 (95.6%)
- AWS plan $68.92/mo; ingest idempotency `8634eacfe0911cfd…`
  - CustodyIQ Labs (FIN-013) (fintech_saas) ingests primarily from AWS us-west-2 via s3://to-fin-013-raw-logs/raw/execution/ and /tradeops/fin-013/execution-gateway.
  - Log Analysis validated 3,718 gateway rows, removed 398 exact redelivery duplicates (10.7%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,359,791 → 59,839 bytes, 95.6% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.9/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Clearing Brokerage (SPE-013)

- Niche: `specialist_broker` · Region: `eu-west-1` · Scenario: `latency_spike` · Help score: **76.6** · Runtime: 110.67 ms
- S3: `s3://to-spe-013-raw-logs/raw/execution/` · CW: `/tradeops/spe-013/execution-gateway`
- Rows 4,799 (unique 4,660); dupes 139; anomalies 1,025; size 1,734,225→83,345 (95.2%)
- AWS plan $49.28/mo; ingest idempotency `64bc22e5d2065428…`
  - Clearing Brokerage (SPE-013) (specialist_broker) ingests primarily from AWS eu-west-1 via s3://to-spe-013-raw-logs/raw/execution/ and /tradeops/spe-013/execution-gateway.
  - Log Analysis validated 4,799 gateway rows, removed 139 exact redelivery duplicates (2.9%), and flagged 1,025 latency/error signals (22.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,734,225 → 83,345 bytes, 95.2% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×326 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×699 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Kinetic Capital (BOU-014)

- Niche: `boutique_trading` · Region: `ap-northeast-1` · Scenario: `mixed_errors` · Help score: **58.7** · Runtime: 44.21 ms
- S3: `s3://to-bou-014-raw-logs/raw/execution/` · CW: `/tradeops/bou-014/execution-gateway`
- Rows 2,100 (unique 2,000); dupes 100; anomalies 55; size 766,560→38,296 (95.0%)
- AWS plan $44.28/mo; ingest idempotency `75ba9ab6f90e2a91…`
  - Kinetic Capital (BOU-014) (boutique_trading) ingests primarily from AWS ap-northeast-1 via s3://to-bou-014-raw-logs/raw/execution/ and /tradeops/bou-014/execution-gateway.
  - Log Analysis validated 2,100 gateway rows, removed 100 exact redelivery duplicates (4.76%), and flagged 55 latency/error signals (2.75% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (766,560 → 38,296 bytes, 95.0% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×55 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### MarginHub Labs (FIN-014)

- Niche: `fintech_saas` · Region: `us-east-1` · Scenario: `normal` · Help score: **49.6** · Runtime: 77.7 ms
- S3: `s3://to-fin-014-raw-logs/raw/execution/` · CW: `/tradeops/fin-014/execution-gateway`
- Rows 3,543 (unique 3,440); dupes 103; anomalies 0; size 1,295,640→61,671 (95.2%)
- AWS plan $68.92/mo; ingest idempotency `e3b58b0687c9c471…`
  - MarginHub Labs (FIN-014) (fintech_saas) ingests primarily from AWS us-east-1 via s3://to-fin-014-raw-logs/raw/execution/ and /tradeops/fin-014/execution-gateway.
  - Log Analysis validated 3,543 gateway rows, removed 103 exact redelivery duplicates (2.91%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,295,640 → 61,671 bytes, 95.2% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Execution Brokerage (SPE-014)

- Niche: `specialist_broker` · Region: `us-east-2` · Scenario: `duplicates` · Help score: **63.9** · Runtime: 105.0 ms
- S3: `s3://to-spe-014-raw-logs/raw/execution/` · CW: `/tradeops/spe-014/execution-gateway`
- Rows 5,353 (unique 4,780); dupes 573; anomalies 0; size 1,933,596→82,652 (95.7%)
- AWS plan $49.28/mo; ingest idempotency `d357e3d91aa94bc3…`
  - Execution Brokerage (SPE-014) (specialist_broker) ingests primarily from AWS us-east-2 via s3://to-spe-014-raw-logs/raw/execution/ and /tradeops/spe-014/execution-gateway.
  - Log Analysis validated 5,353 gateway rows, removed 573 exact redelivery duplicates (10.7%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,933,596 → 82,652 bytes, 95.7% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.9/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Aurora Capital (BOU-015)

- Niche: `boutique_trading` · Region: `us-west-2` · Scenario: `latency_spike` · Help score: **76.4** · Runtime: 45.74 ms
- S3: `s3://to-bou-015-raw-logs/raw/execution/` · CW: `/tradeops/bou-015/execution-gateway`
- Rows 2,183 (unique 2,120); dupes 63; anomalies 466; size 786,673→41,391 (94.7%)
- AWS plan $44.28/mo; ingest idempotency `9f3d9c76b986bfcf…`
  - Aurora Capital (BOU-015) (boutique_trading) ingests primarily from AWS us-west-2 via s3://to-bou-015-raw-logs/raw/execution/ and /tradeops/bou-015/execution-gateway.
  - Log Analysis validated 2,183 gateway rows, removed 63 exact redelivery duplicates (2.89%), and flagged 466 latency/error signals (21.98% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (786,673 → 41,391 bytes, 94.7% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×147 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×319 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.4/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### TickForge Labs (FIN-015)

- Niche: `fintech_saas` · Region: `eu-west-1` · Scenario: `mixed_errors` · Help score: **58.7** · Runtime: 76.98 ms
- S3: `s3://to-fin-015-raw-logs/raw/execution/` · CW: `/tradeops/fin-015/execution-gateway`
- Rows 3,738 (unique 3,560); dupes 178; anomalies 97; size 1,367,361→63,346 (95.4%)
- AWS plan $68.92/mo; ingest idempotency `f592ad7d52720513…`
  - TickForge Labs (FIN-015) (fintech_saas) ingests primarily from AWS eu-west-1 via s3://to-fin-015-raw-logs/raw/execution/ and /tradeops/fin-015/execution-gateway.
  - Log Analysis validated 3,738 gateway rows, removed 178 exact redelivery duplicates (4.76%), and flagged 97 latency/error signals (2.72% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,367,361 → 63,346 bytes, 95.4% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×97 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Access Brokerage (SPE-015)

- Niche: `specialist_broker` · Region: `ap-northeast-1` · Scenario: `normal` · Help score: **49.7** · Runtime: 102.97 ms
- S3: `s3://to-spe-015-raw-logs/raw/execution/` · CW: `/tradeops/spe-015/execution-gateway`
- Rows 5,047 (unique 4,900); dupes 147; anomalies 0; size 1,848,205→84,884 (95.4%)
- AWS plan $49.28/mo; ingest idempotency `49ab08b21390be1e…`
  - Access Brokerage (SPE-015) (specialist_broker) ingests primarily from AWS ap-northeast-1 via s3://to-spe-015-raw-logs/raw/execution/ and /tradeops/spe-015/execution-gateway.
  - Log Analysis validated 5,047 gateway rows, removed 147 exact redelivery duplicates (2.91%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,848,205 → 84,884 bytes, 95.4% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Falcon Capital (BOU-016)

- Niche: `boutique_trading` · Region: `us-east-1` · Scenario: `duplicates` · Help score: **63.8** · Runtime: 48.93 ms
- S3: `s3://to-bou-016-raw-logs/raw/execution/` · CW: `/tradeops/bou-016/execution-gateway`
- Rows 2,508 (unique 2,240); dupes 268; anomalies 0; size 903,427→42,669 (95.3%)
- AWS plan $29.68/mo; ingest idempotency `bae3124a52b3f1cd…`
  - Falcon Capital (BOU-016) (boutique_trading) ingests primarily from AWS us-east-1 via s3://to-bou-016-raw-logs/raw/execution/ and /tradeops/bou-016/execution-gateway.
  - Log Analysis validated 2,508 gateway rows, removed 268 exact redelivery duplicates (10.69%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (903,427 → 42,669 bytes, 95.3% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $29.68/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.8/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Bookstack Labs (FIN-016)

- Niche: `fintech_saas` · Region: `us-east-2` · Scenario: `latency_spike` · Help score: **76.6** · Runtime: 78.63 ms
- S3: `s3://to-fin-016-raw-logs/raw/execution/` · CW: `/tradeops/fin-016/execution-gateway`
- Rows 3,790 (unique 3,680); dupes 110; anomalies 809; size 1,387,660→66,615 (95.2%)
- AWS plan $68.92/mo; ingest idempotency `798350fcdf6ae868…`
  - Bookstack Labs (FIN-016) (fintech_saas) ingests primarily from AWS us-east-2 via s3://to-fin-016-raw-logs/raw/execution/ and /tradeops/fin-016/execution-gateway.
  - Log Analysis validated 3,790 gateway rows, removed 110 exact redelivery duplicates (2.9%), and flagged 809 latency/error signals (21.98% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,387,660 → 66,615 bytes, 95.2% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×258 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×551 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Gateway Brokerage (SPE-016)

- Niche: `specialist_broker` · Region: `us-west-2` · Scenario: `mixed_errors` · Help score: **58.7** · Runtime: 113.01 ms
- S3: `s3://to-spe-016-raw-logs/raw/execution/` · CW: `/tradeops/spe-016/execution-gateway`
- Rows 5,271 (unique 5,020); dupes 251; anomalies 136; size 1,902,815→86,381 (95.5%)
- AWS plan $49.28/mo; ingest idempotency `db9b359174106dba…`
  - Gateway Brokerage (SPE-016) (specialist_broker) ingests primarily from AWS us-west-2 via s3://to-spe-016-raw-logs/raw/execution/ and /tradeops/spe-016/execution-gateway.
  - Log Analysis validated 5,271 gateway rows, removed 251 exact redelivery duplicates (4.76%), and flagged 136 latency/error signals (2.71% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,902,815 → 86,381 bytes, 95.5% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×136 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Horizon Capital (BOU-017)

- Niche: `boutique_trading` · Region: `eu-west-1` · Scenario: `normal` · Help score: **49.5** · Runtime: 50.49 ms
- S3: `s3://to-bou-017-raw-logs/raw/execution/` · CW: `/tradeops/bou-017/execution-gateway`
- Rows 2,430 (unique 2,360); dupes 70; anomalies 0; size 875,045→44,354 (94.9%)
- AWS plan $44.28/mo; ingest idempotency `1bdf829f990de316…`
  - Horizon Capital (BOU-017) (boutique_trading) ingests primarily from AWS eu-west-1 via s3://to-bou-017-raw-logs/raw/execution/ and /tradeops/bou-017/execution-gateway.
  - Log Analysis validated 2,430 gateway rows, removed 70 exact redelivery duplicates (2.88%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (875,045 → 44,354 bytes, 94.9% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.5/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Wireframe Labs (FIN-017)

- Niche: `fintech_saas` · Region: `ap-northeast-1` · Scenario: `duplicates` · Help score: **63.9** · Runtime: 90.71 ms
- S3: `s3://to-fin-017-raw-logs/raw/execution/` · CW: `/tradeops/fin-017/execution-gateway`
- Rows 4,256 (unique 3,800); dupes 456; anomalies 0; size 1,577,786→67,109 (95.7%)
- AWS plan $68.92/mo; ingest idempotency `7aa3ee1b732cac19…`
  - Wireframe Labs (FIN-017) (fintech_saas) ingests primarily from AWS ap-northeast-1 via s3://to-fin-017-raw-logs/raw/execution/ and /tradeops/fin-017/execution-gateway.
  - Log Analysis validated 4,256 gateway rows, removed 456 exact redelivery duplicates (10.71%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,577,786 → 67,109 bytes, 95.7% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.9/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Market Brokerage (SPE-017)

- Niche: `specialist_broker` · Region: `us-east-1` · Scenario: `latency_spike` · Help score: **76.6** · Runtime: 154.58 ms
- S3: `s3://to-spe-017-raw-logs/raw/execution/` · CW: `/tradeops/spe-017/execution-gateway`
- Rows 5,294 (unique 5,140); dupes 154; anomalies 1,130; size 1,913,998→90,843 (95.3%)
- AWS plan $49.28/mo; ingest idempotency `bfd8421dd4eb2696…`
  - Market Brokerage (SPE-017) (specialist_broker) ingests primarily from AWS us-east-1 via s3://to-spe-017-raw-logs/raw/execution/ and /tradeops/spe-017/execution-gateway.
  - Log Analysis validated 5,294 gateway rows, removed 154 exact redelivery duplicates (2.91%), and flagged 1,130 latency/error signals (21.98% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,913,998 → 90,843 bytes, 95.3% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×360 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×770 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Nexus Capital (BOU-018)

- Niche: `boutique_trading` · Region: `us-east-2` · Scenario: `mixed_errors` · Help score: **58.6** · Runtime: 65.55 ms
- S3: `s3://to-bou-018-raw-logs/raw/execution/` · CW: `/tradeops/bou-018/execution-gateway`
- Rows 1,890 (unique 1,800); dupes 90; anomalies 49; size 680,333→35,019 (94.9%)
- AWS plan $44.28/mo; ingest idempotency `ea8db361e9e2b53f…`
  - Nexus Capital (BOU-018) (boutique_trading) ingests primarily from AWS us-east-2 via s3://to-bou-018-raw-logs/raw/execution/ and /tradeops/bou-018/execution-gateway.
  - Log Analysis validated 1,890 gateway rows, removed 90 exact redelivery duplicates (4.76%), and flagged 49 latency/error signals (2.72% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (680,333 → 35,019 bytes, 94.9% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×49 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Clipstream Labs (FIN-018)

- Niche: `fintech_saas` · Region: `us-west-2` · Scenario: `normal` · Help score: **49.6** · Runtime: 122.38 ms
- S3: `s3://to-fin-018-raw-logs/raw/execution/` · CW: `/tradeops/fin-018/execution-gateway`
- Rows 3,337 (unique 3,240); dupes 97; anomalies 0; size 1,220,670→58,365 (95.2%)
- AWS plan $68.92/mo; ingest idempotency `d79df79f442963c2…`
  - Clipstream Labs (FIN-018) (fintech_saas) ingests primarily from AWS us-west-2 via s3://to-fin-018-raw-logs/raw/execution/ and /tradeops/fin-018/execution-gateway.
  - Log Analysis validated 3,337 gateway rows, removed 97 exact redelivery duplicates (2.91%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,220,670 → 58,365 bytes, 95.2% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Order Brokerage (SPE-018)

- Niche: `specialist_broker` · Region: `eu-west-1` · Scenario: `duplicates` · Help score: **63.9** · Runtime: 125.78 ms
- S3: `s3://to-spe-018-raw-logs/raw/execution/` · CW: `/tradeops/spe-018/execution-gateway`
- Rows 5,129 (unique 4,580); dupes 549; anomalies 0; size 1,851,534→80,051 (95.7%)
- AWS plan $49.28/mo; ingest idempotency `848e16efad3406a1…`
  - Order Brokerage (SPE-018) (specialist_broker) ingests primarily from AWS eu-west-1 via s3://to-spe-018-raw-logs/raw/execution/ and /tradeops/spe-018/execution-gateway.
  - Log Analysis validated 5,129 gateway rows, removed 549 exact redelivery duplicates (10.7%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,851,534 → 80,051 bytes, 95.7% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.9/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Pulse Capital (BOU-019)

- Niche: `boutique_trading` · Region: `ap-northeast-1` · Scenario: `latency_spike` · Help score: **76.5** · Runtime: 43.05 ms
- S3: `s3://to-bou-019-raw-logs/raw/execution/` · CW: `/tradeops/bou-019/execution-gateway`
- Rows 1,977 (unique 1,920); dupes 57; anomalies 422; size 722,483→37,582 (94.8%)
- AWS plan $44.28/mo; ingest idempotency `2fc4faf370c8ee5b…`
  - Pulse Capital (BOU-019) (boutique_trading) ingests primarily from AWS ap-northeast-1 via s3://to-bou-019-raw-logs/raw/execution/ and /tradeops/bou-019/execution-gateway.
  - Log Analysis validated 1,977 gateway rows, removed 57 exact redelivery duplicates (2.88%), and flagged 422 latency/error signals (21.98% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (722,483 → 37,582 bytes, 94.8% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×134 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×288 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.5/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Matchbox Labs (FIN-019)

- Niche: `fintech_saas` · Region: `us-east-1` · Scenario: `mixed_errors` · Help score: **58.7** · Runtime: 78.52 ms
- S3: `s3://to-fin-019-raw-logs/raw/execution/` · CW: `/tradeops/fin-019/execution-gateway`
- Rows 3,528 (unique 3,360); dupes 168; anomalies 91; size 1,290,145→60,267 (95.3%)
- AWS plan $68.92/mo; ingest idempotency `18316d3c4b11420a…`
  - Matchbox Labs (FIN-019) (fintech_saas) ingests primarily from AWS us-east-1 via s3://to-fin-019-raw-logs/raw/execution/ and /tradeops/fin-019/execution-gateway.
  - Log Analysis validated 3,528 gateway rows, removed 168 exact redelivery duplicates (4.76%), and flagged 91 latency/error signals (2.71% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,290,145 → 60,267 bytes, 95.3% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×91 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Client Brokerage (SPE-019)

- Niche: `specialist_broker` · Region: `us-east-2` · Scenario: `normal` · Help score: **49.7** · Runtime: 106.5 ms
- S3: `s3://to-spe-019-raw-logs/raw/execution/` · CW: `/tradeops/spe-019/execution-gateway`
- Rows 4,841 (unique 4,700); dupes 141; anomalies 0; size 1,747,987→81,973 (95.3%)
- AWS plan $49.28/mo; ingest idempotency `f778680fdf8b8200…`
  - Client Brokerage (SPE-019) (specialist_broker) ingests primarily from AWS us-east-2 via s3://to-spe-019-raw-logs/raw/execution/ and /tradeops/spe-019/execution-gateway.
  - Log Analysis validated 4,841 gateway rows, removed 141 exact redelivery duplicates (2.91%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,747,987 → 81,973 bytes, 95.3% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Sterling Capital (BOU-020)

- Niche: `boutique_trading` · Region: `us-west-2` · Scenario: `duplicates` · Help score: **63.8** · Runtime: 50.56 ms
- S3: `s3://to-bou-020-raw-logs/raw/execution/` · CW: `/tradeops/bou-020/execution-gateway`
- Rows 2,284 (unique 2,040); dupes 244; anomalies 0; size 822,782→38,800 (95.3%)
- AWS plan $44.28/mo; ingest idempotency `e95f09be77a2b735…`
  - Sterling Capital (BOU-020) (boutique_trading) ingests primarily from AWS us-west-2 via s3://to-bou-020-raw-logs/raw/execution/ and /tradeops/bou-020/execution-gateway.
  - Log Analysis validated 2,284 gateway rows, removed 244 exact redelivery duplicates (10.68%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (822,782 → 38,800 bytes, 95.3% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.8/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### SettleOS Labs (FIN-020)

- Niche: `fintech_saas` · Region: `eu-west-1` · Scenario: `latency_spike` · Help score: **76.6** · Runtime: 81.04 ms
- S3: `s3://to-fin-020-raw-logs/raw/execution/` · CW: `/tradeops/fin-020/execution-gateway`
- Rows 3,584 (unique 3,480); dupes 104; anomalies 765; size 1,311,877→63,433 (95.2%)
- AWS plan $68.92/mo; ingest idempotency `c029993926c970a8…`
  - SettleOS Labs (FIN-020) (fintech_saas) ingests primarily from AWS eu-west-1 via s3://to-fin-020-raw-logs/raw/execution/ and /tradeops/fin-020/execution-gateway.
  - Log Analysis validated 3,584 gateway rows, removed 104 exact redelivery duplicates (2.9%), and flagged 765 latency/error signals (21.98% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,311,877 → 63,433 bytes, 95.2% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×243 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×522 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Wealth Brokerage (SPE-020)

- Niche: `specialist_broker` · Region: `ap-northeast-1` · Scenario: `mixed_errors` · Help score: **58.7** · Runtime: 114.64 ms
- S3: `s3://to-spe-020-raw-logs/raw/execution/` · CW: `/tradeops/spe-020/execution-gateway`
- Rows 5,061 (unique 4,820); dupes 241; anomalies 131; size 1,852,824→83,516 (95.5%)
- AWS plan $49.28/mo; ingest idempotency `55b2ba5c938b4d29…`
  - Wealth Brokerage (SPE-020) (specialist_broker) ingests primarily from AWS ap-northeast-1 via s3://to-spe-020-raw-logs/raw/execution/ and /tradeops/spe-020/execution-gateway.
  - Log Analysis validated 5,061 gateway rows, removed 241 exact redelivery duplicates (4.76%), and flagged 131 latency/error signals (2.72% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,852,824 → 83,516 bytes, 95.5% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×131 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Atlas Capital (BOU-021)

- Niche: `boutique_trading` · Region: `us-east-1` · Scenario: `normal` · Help score: **49.5** · Runtime: 55.17 ms
- S3: `s3://to-bou-021-raw-logs/raw/execution/` · CW: `/tradeops/bou-021/execution-gateway`
- Rows 2,224 (unique 2,160); dupes 64; anomalies 0; size 800,631→41,270 (94.8%)
- AWS plan $29.68/mo; ingest idempotency `91df2f364a0c96db…`
  - Atlas Capital (BOU-021) (boutique_trading) ingests primarily from AWS us-east-1 via s3://to-bou-021-raw-logs/raw/execution/ and /tradeops/bou-021/execution-gateway.
  - Log Analysis validated 2,224 gateway rows, removed 64 exact redelivery duplicates (2.88%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (800,631 → 41,270 bytes, 94.8% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $29.68/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.5/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Logyard Labs (FIN-021)

- Niche: `fintech_saas` · Region: `us-east-2` · Scenario: `duplicates` · Help score: **63.9** · Runtime: 88.83 ms
- S3: `s3://to-fin-021-raw-logs/raw/execution/` · CW: `/tradeops/fin-021/execution-gateway`
- Rows 4,032 (unique 3,600); dupes 432; anomalies 0; size 1,474,894→64,105 (95.7%)
- AWS plan $68.92/mo; ingest idempotency `947f112b0cf38e43…`
  - Logyard Labs (FIN-021) (fintech_saas) ingests primarily from AWS us-east-2 via s3://to-fin-021-raw-logs/raw/execution/ and /tradeops/fin-021/execution-gateway.
  - Log Analysis validated 4,032 gateway rows, removed 432 exact redelivery duplicates (10.71%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,474,894 → 64,105 bytes, 95.7% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.9/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Family Brokerage (SPE-021)

- Niche: `specialist_broker` · Region: `us-west-2` · Scenario: `latency_spike` · Help score: **76.6** · Runtime: 110.5 ms
- S3: `s3://to-spe-021-raw-logs/raw/execution/` · CW: `/tradeops/spe-021/execution-gateway`
- Rows 5,088 (unique 4,940); dupes 148; anomalies 1,086; size 1,839,241→87,330 (95.3%)
- AWS plan $49.28/mo; ingest idempotency `cc484ad3b2582d64…`
  - Family Brokerage (SPE-021) (specialist_broker) ingests primarily from AWS us-west-2 via s3://to-spe-021-raw-logs/raw/execution/ and /tradeops/spe-021/execution-gateway.
  - Log Analysis validated 5,088 gateway rows, removed 148 exact redelivery duplicates (2.91%), and flagged 1,086 latency/error signals (21.98% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,839,241 → 87,330 bytes, 95.3% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×345 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×741 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Beacon Capital (BOU-022)

- Niche: `boutique_trading` · Region: `eu-west-1` · Scenario: `mixed_errors` · Help score: **58.6** · Runtime: 50.61 ms
- S3: `s3://to-bou-022-raw-logs/raw/execution/` · CW: `/tradeops/bou-022/execution-gateway`
- Rows 2,394 (unique 2,280); dupes 114; anomalies 62; size 862,177→43,271 (95.0%)
- AWS plan $44.28/mo; ingest idempotency `1cc5683d34156f57…`
  - Beacon Capital (BOU-022) (boutique_trading) ingests primarily from AWS eu-west-1 via s3://to-bou-022-raw-logs/raw/execution/ and /tradeops/bou-022/execution-gateway.
  - Log Analysis validated 2,394 gateway rows, removed 114 exact redelivery duplicates (4.76%), and flagged 62 latency/error signals (2.72% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (862,177 → 43,271 bytes, 95.0% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×62 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Vaultline Labs (FIN-022)

- Niche: `fintech_saas` · Region: `ap-northeast-1` · Scenario: `normal` · Help score: **49.6** · Runtime: 80.91 ms
- S3: `s3://to-fin-022-raw-logs/raw/execution/` · CW: `/tradeops/fin-022/execution-gateway`
- Rows 3,831 (unique 3,720); dupes 111; anomalies 0; size 1,420,241→65,950 (95.4%)
- AWS plan $68.92/mo; ingest idempotency `4991105247c46525…`
  - Vaultline Labs (FIN-022) (fintech_saas) ingests primarily from AWS ap-northeast-1 via s3://to-fin-022-raw-logs/raw/execution/ and /tradeops/fin-022/execution-gateway.
  - Log Analysis validated 3,831 gateway rows, removed 111 exact redelivery duplicates (2.9%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,420,241 → 65,950 bytes, 95.4% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Boutique Brokerage (SPE-022)

- Niche: `specialist_broker` · Region: `us-east-1` · Scenario: `duplicates` · Help score: **63.9** · Runtime: 114.96 ms
- S3: `s3://to-spe-022-raw-logs/raw/execution/` · CW: `/tradeops/spe-022/execution-gateway`
- Rows 5,667 (unique 5,060); dupes 607; anomalies 0; size 2,046,734→87,317 (95.7%)
- AWS plan $49.28/mo; ingest idempotency `5fe0af4ed7327a1b…`
  - Boutique Brokerage (SPE-022) (specialist_broker) ingests primarily from AWS us-east-1 via s3://to-spe-022-raw-logs/raw/execution/ and /tradeops/spe-022/execution-gateway.
  - Log Analysis validated 5,667 gateway rows, removed 607 exact redelivery duplicates (10.71%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (2,046,734 → 87,317 bytes, 95.7% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.9/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Cipher Capital (BOU-023)

- Niche: `boutique_trading` · Region: `us-east-2` · Scenario: `latency_spike` · Help score: **76.5** · Runtime: 55.04 ms
- S3: `s3://to-bou-023-raw-logs/raw/execution/` · CW: `/tradeops/bou-023/execution-gateway`
- Rows 2,472 (unique 2,400); dupes 72; anomalies 527; size 891,275→46,179 (94.8%)
- AWS plan $44.28/mo; ingest idempotency `ceeae0b8452f5700…`
  - Cipher Capital (BOU-023) (boutique_trading) ingests primarily from AWS us-east-2 via s3://to-bou-023-raw-logs/raw/execution/ and /tradeops/bou-023/execution-gateway.
  - Log Analysis validated 2,472 gateway rows, removed 72 exact redelivery duplicates (2.91%), and flagged 527 latency/error signals (21.96% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (891,275 → 46,179 bytes, 94.8% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×167 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×360 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.5/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### PrimeOps Labs (FIN-023)

- Niche: `fintech_saas` · Region: `us-west-2` · Scenario: `mixed_errors` · Help score: **58.7** · Runtime: 86.39 ms
- S3: `s3://to-fin-023-raw-logs/raw/execution/` · CW: `/tradeops/fin-023/execution-gateway`
- Rows 4,032 (unique 3,840); dupes 192; anomalies 104; size 1,474,530→67,711 (95.4%)
- AWS plan $68.92/mo; ingest idempotency `1fc56fa7425b85c1…`
  - PrimeOps Labs (FIN-023) (fintech_saas) ingests primarily from AWS us-west-2 via s3://to-fin-023-raw-logs/raw/execution/ and /tradeops/fin-023/execution-gateway.
  - Log Analysis validated 4,032 gateway rows, removed 192 exact redelivery duplicates (4.76%), and flagged 104 latency/error signals (2.71% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,474,530 → 67,711 bytes, 95.4% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×104 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Regional Brokerage (SPE-023)

- Niche: `specialist_broker` · Region: `eu-west-1` · Scenario: `normal` · Help score: **49.7** · Runtime: 106.04 ms
- S3: `s3://to-spe-023-raw-logs/raw/execution/` · CW: `/tradeops/spe-023/execution-gateway`
- Rows 4,635 (unique 4,500); dupes 135; anomalies 0; size 1,673,027→78,940 (95.3%)
- AWS plan $49.28/mo; ingest idempotency `16342ba9c9ffb5e1…`
  - Regional Brokerage (SPE-023) (specialist_broker) ingests primarily from AWS eu-west-1 via s3://to-spe-023-raw-logs/raw/execution/ and /tradeops/spe-023/execution-gateway.
  - Log Analysis validated 4,635 gateway rows, removed 135 exact redelivery duplicates (2.91%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,673,027 → 78,940 bytes, 95.3% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Delta Capital (BOU-024)

- Niche: `boutique_trading` · Region: `ap-northeast-1` · Scenario: `duplicates` · Help score: **63.8** · Runtime: 45.11 ms
- S3: `s3://to-bou-024-raw-logs/raw/execution/` · CW: `/tradeops/bou-024/execution-gateway`
- Rows 2,060 (unique 1,840); dupes 220; anomalies 0; size 752,103→35,768 (95.2%)
- AWS plan $44.28/mo; ingest idempotency `34aba07881f1bcf8…`
  - Delta Capital (BOU-024) (boutique_trading) ingests primarily from AWS ap-northeast-1 via s3://to-bou-024-raw-logs/raw/execution/ and /tradeops/bou-024/execution-gateway.
  - Log Analysis validated 2,060 gateway rows, removed 220 exact redelivery duplicates (10.68%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (752,103 → 35,768 bytes, 95.2% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.8/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Quota Labs (FIN-024)

- Niche: `fintech_saas` · Region: `us-east-1` · Scenario: `latency_spike` · Help score: **76.6** · Runtime: 78.53 ms
- S3: `s3://to-fin-024-raw-logs/raw/execution/` · CW: `/tradeops/fin-024/execution-gateway`
- Rows 3,378 (unique 3,280); dupes 98; anomalies 721; size 1,236,523→60,576 (95.1%)
- AWS plan $68.92/mo; ingest idempotency `e44400f654442572…`
  - Quota Labs (FIN-024) (fintech_saas) ingests primarily from AWS us-east-1 via s3://to-fin-024-raw-logs/raw/execution/ and /tradeops/fin-024/execution-gateway.
  - Log Analysis validated 3,378 gateway rows, removed 98 exact redelivery duplicates (2.9%), and flagged 721 latency/error signals (21.98% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,236,523 → 60,576 bytes, 95.1% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×230 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×491 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Specialty Brokerage (SPE-024)

- Niche: `specialist_broker` · Region: `us-east-2` · Scenario: `mixed_errors` · Help score: **58.7** · Runtime: 103.99 ms
- S3: `s3://to-spe-024-raw-logs/raw/execution/` · CW: `/tradeops/spe-024/execution-gateway`
- Rows 4,851 (unique 4,620); dupes 231; anomalies 125; size 1,752,172→80,461 (95.4%)
- AWS plan $49.28/mo; ingest idempotency `834b04fca0b369bb…`
  - Specialty Brokerage (SPE-024) (specialist_broker) ingests primarily from AWS us-east-2 via s3://to-spe-024-raw-logs/raw/execution/ and /tradeops/spe-024/execution-gateway.
  - Log Analysis validated 4,851 gateway rows, removed 231 exact redelivery duplicates (4.76%), and flagged 125 latency/error signals (2.71% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,752,172 → 80,461 bytes, 95.4% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×125 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Echo Capital (BOU-025)

- Niche: `boutique_trading` · Region: `us-west-2` · Scenario: `normal` · Help score: **49.4** · Runtime: 43.93 ms
- S3: `s3://to-bou-025-raw-logs/raw/execution/` · CW: `/tradeops/bou-025/execution-gateway`
- Rows 2,018 (unique 1,960); dupes 58; anomalies 0; size 727,068→37,678 (94.8%)
- AWS plan $44.28/mo; ingest idempotency `8145927eef511cff…`
  - Echo Capital (BOU-025) (boutique_trading) ingests primarily from AWS us-west-2 via s3://to-bou-025-raw-logs/raw/execution/ and /tradeops/bou-025/execution-gateway.
  - Log Analysis validated 2,018 gateway rows, removed 58 exact redelivery duplicates (2.87%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (727,068 → 37,678 bytes, 94.8% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.4/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Stackfill Labs (FIN-025)

- Niche: `fintech_saas` · Region: `eu-west-1` · Scenario: `duplicates` · Help score: **63.9** · Runtime: 78.59 ms
- S3: `s3://to-fin-025-raw-logs/raw/execution/` · CW: `/tradeops/fin-025/execution-gateway`
- Rows 3,808 (unique 3,400); dupes 408; anomalies 0; size 1,393,085→61,076 (95.6%)
- AWS plan $68.92/mo; ingest idempotency `2030c09f65952ce1…`
  - Stackfill Labs (FIN-025) (fintech_saas) ingests primarily from AWS eu-west-1 via s3://to-fin-025-raw-logs/raw/execution/ and /tradeops/fin-025/execution-gateway.
  - Log Analysis validated 3,808 gateway rows, removed 408 exact redelivery duplicates (10.71%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,393,085 → 61,076 bytes, 95.6% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.9/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Direct Brokerage (SPE-025)

- Niche: `specialist_broker` · Region: `ap-northeast-1` · Scenario: `latency_spike` · Help score: **76.6** · Runtime: 108.48 ms
- S3: `s3://to-spe-025-raw-logs/raw/execution/` · CW: `/tradeops/spe-025/execution-gateway`
- Rows 4,882 (unique 4,740); dupes 142; anomalies 1,042; size 1,789,026→84,574 (95.3%)
- AWS plan $49.28/mo; ingest idempotency `cbed90442b4814d2…`
  - Direct Brokerage (SPE-025) (specialist_broker) ingests primarily from AWS ap-northeast-1 via s3://to-spe-025-raw-logs/raw/execution/ and /tradeops/spe-025/execution-gateway.
  - Log Analysis validated 4,882 gateway rows, removed 142 exact redelivery duplicates (2.91%), and flagged 1,042 latency/error signals (21.98% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,789,026 → 84,574 bytes, 95.3% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×331 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×711 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Forge Capital (BOU-026)

- Niche: `boutique_trading` · Region: `us-east-1` · Scenario: `mixed_errors` · Help score: **58.6** · Runtime: 73.37 ms
- S3: `s3://to-bou-026-raw-logs/raw/execution/` · CW: `/tradeops/bou-026/execution-gateway`
- Rows 2,184 (unique 2,080); dupes 104; anomalies 57; size 786,349→40,137 (94.9%)
- AWS plan $29.68/mo; ingest idempotency `d919301647159ee5…`
  - Forge Capital (BOU-026) (boutique_trading) ingests primarily from AWS us-east-1 via s3://to-bou-026-raw-logs/raw/execution/ and /tradeops/bou-026/execution-gateway.
  - Log Analysis validated 2,184 gateway rows, removed 104 exact redelivery duplicates (4.76%), and flagged 57 latency/error signals (2.74% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (786,349 → 40,137 bytes, 94.9% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $29.68/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×57 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Relaybook Labs (FIN-026)

- Niche: `fintech_saas` · Region: `us-east-2` · Scenario: `normal` · Help score: **49.6** · Runtime: 126.84 ms
- S3: `s3://to-fin-026-raw-logs/raw/execution/` · CW: `/tradeops/fin-026/execution-gateway`
- Rows 3,625 (unique 3,520); dupes 105; anomalies 0; size 1,325,764→62,986 (95.2%)
- AWS plan $68.92/mo; ingest idempotency `1ec8ec0526d46326…`
  - Relaybook Labs (FIN-026) (fintech_saas) ingests primarily from AWS us-east-2 via s3://to-fin-026-raw-logs/raw/execution/ and /tradeops/fin-026/execution-gateway.
  - Log Analysis validated 3,625 gateway rows, removed 105 exact redelivery duplicates (2.9%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,325,764 → 62,986 bytes, 95.2% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Electron Brokerage (SPE-026)

- Niche: `specialist_broker` · Region: `us-west-2` · Scenario: `duplicates` · Help score: **63.9** · Runtime: 116.5 ms
- S3: `s3://to-spe-026-raw-logs/raw/execution/` · CW: `/tradeops/spe-026/execution-gateway`
- Rows 5,443 (unique 4,860); dupes 583; anomalies 0; size 1,966,203→84,048 (95.7%)
- AWS plan $49.28/mo; ingest idempotency `438ca606fc7100ea…`
  - Electron Brokerage (SPE-026) (specialist_broker) ingests primarily from AWS us-west-2 via s3://to-spe-026-raw-logs/raw/execution/ and /tradeops/spe-026/execution-gateway.
  - Log Analysis validated 5,443 gateway rows, removed 583 exact redelivery duplicates (10.71%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,966,203 → 84,048 bytes, 95.7% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.9/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Granite Capital (BOU-027)

- Niche: `boutique_trading` · Region: `eu-west-1` · Scenario: `latency_spike` · Help score: **76.5** · Runtime: 51.3 ms
- S3: `s3://to-bou-027-raw-logs/raw/execution/` · CW: `/tradeops/bou-027/execution-gateway`
- Rows 2,266 (unique 2,200); dupes 66; anomalies 483; size 816,601→42,583 (94.8%)
- AWS plan $44.28/mo; ingest idempotency `8605cc44fabcab88…`
  - Granite Capital (BOU-027) (boutique_trading) ingests primarily from AWS eu-west-1 via s3://to-bou-027-raw-logs/raw/execution/ and /tradeops/bou-027/execution-gateway.
  - Log Analysis validated 2,266 gateway rows, removed 66 exact redelivery duplicates (2.91%), and flagged 483 latency/error signals (21.95% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (816,601 → 42,583 bytes, 94.8% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×153 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×330 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.5/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Nightwatch Labs (FIN-027)

- Niche: `fintech_saas` · Region: `ap-northeast-1` · Scenario: `mixed_errors` · Help score: **58.7** · Runtime: 82.51 ms
- S3: `s3://to-fin-027-raw-logs/raw/execution/` · CW: `/tradeops/fin-027/execution-gateway`
- Rows 3,822 (unique 3,640); dupes 182; anomalies 99; size 1,416,902→64,576 (95.4%)
- AWS plan $68.92/mo; ingest idempotency `60b7ad01f8fc68e9…`
  - Nightwatch Labs (FIN-027) (fintech_saas) ingests primarily from AWS ap-northeast-1 via s3://to-fin-027-raw-logs/raw/execution/ and /tradeops/fin-027/execution-gateway.
  - Log Analysis validated 3,822 gateway rows, removed 182 exact redelivery duplicates (4.76%), and flagged 99 latency/error signals (2.72% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,416,902 → 64,576 bytes, 95.4% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×99 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Floor Brokerage (SPE-027)

- Niche: `specialist_broker` · Region: `us-east-1` · Scenario: `normal` · Help score: **49.7** · Runtime: 118.75 ms
- S3: `s3://to-spe-027-raw-logs/raw/execution/` · CW: `/tradeops/spe-027/execution-gateway`
- Rows 5,129 (unique 4,980); dupes 149; anomalies 0; size 1,852,936→85,711 (95.4%)
- AWS plan $49.28/mo; ingest idempotency `275e9a2e012445fa…`
  - Floor Brokerage (SPE-027) (specialist_broker) ingests primarily from AWS us-east-1 via s3://to-spe-027-raw-logs/raw/execution/ and /tradeops/spe-027/execution-gateway.
  - Log Analysis validated 5,129 gateway rows, removed 149 exact redelivery duplicates (2.91%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,852,936 → 85,711 bytes, 95.4% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Helix Capital (BOU-028)

- Niche: `boutique_trading` · Region: `us-east-2` · Scenario: `duplicates` · Help score: **63.8** · Runtime: 96.44 ms
- S3: `s3://to-bou-028-raw-logs/raw/execution/` · CW: `/tradeops/bou-028/execution-gateway`
- Rows 2,598 (unique 2,320); dupes 278; anomalies 0; size 935,564→44,044 (95.3%)
- AWS plan $44.28/mo; ingest idempotency `eaf929eed8956ad2…`
  - Helix Capital (BOU-028) (boutique_trading) ingests primarily from AWS us-east-2 via s3://to-bou-028-raw-logs/raw/execution/ and /tradeops/bou-028/execution-gateway.
  - Log Analysis validated 2,598 gateway rows, removed 278 exact redelivery duplicates (10.7%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (935,564 → 44,044 bytes, 95.3% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.8/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Controlbay Labs (FIN-028)

- Niche: `fintech_saas` · Region: `us-west-2` · Scenario: `latency_spike` · Help score: **76.6** · Runtime: 122.41 ms
- S3: `s3://to-fin-028-raw-logs/raw/execution/` · CW: `/tradeops/fin-028/execution-gateway`
- Rows 3,872 (unique 3,760); dupes 112; anomalies 827; size 1,417,522→68,026 (95.2%)
- AWS plan $68.92/mo; ingest idempotency `80afc9a5a2583cc4…`
  - Controlbay Labs (FIN-028) (fintech_saas) ingests primarily from AWS us-west-2 via s3://to-fin-028-raw-logs/raw/execution/ and /tradeops/fin-028/execution-gateway.
  - Log Analysis validated 3,872 gateway rows, removed 112 exact redelivery duplicates (2.89%), and flagged 827 latency/error signals (21.99% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,417,522 → 68,026 bytes, 95.2% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×262 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×565 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Block Brokerage (SPE-028)

- Niche: `specialist_broker` · Region: `eu-west-1` · Scenario: `mixed_errors` · Help score: **58.7** · Runtime: 122.68 ms
- S3: `s3://to-spe-028-raw-logs/raw/execution/` · CW: `/tradeops/spe-028/execution-gateway`
- Rows 5,355 (unique 5,100); dupes 255; anomalies 138; size 1,934,128→87,748 (95.5%)
- AWS plan $49.28/mo; ingest idempotency `cb73ba46c115c047…`
  - Block Brokerage (SPE-028) (specialist_broker) ingests primarily from AWS eu-west-1 via s3://to-spe-028-raw-logs/raw/execution/ and /tradeops/spe-028/execution-gateway.
  - Log Analysis validated 5,355 gateway rows, removed 255 exact redelivery duplicates (4.76%), and flagged 138 latency/error signals (2.71% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,934,128 → 87,748 bytes, 95.5% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×138 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Ion Capital (BOU-029)

- Niche: `boutique_trading` · Region: `ap-northeast-1` · Scenario: `normal` · Help score: **49.6** · Runtime: 55.28 ms
- S3: `s3://to-bou-029-raw-logs/raw/execution/` · CW: `/tradeops/bou-029/execution-gateway`
- Rows 2,513 (unique 2,440); dupes 73; anomalies 0; size 917,512→45,677 (95.0%)
- AWS plan $44.28/mo; ingest idempotency `c2274e5332291268…`
  - Ion Capital (BOU-029) (boutique_trading) ingests primarily from AWS ap-northeast-1 via s3://to-bou-029-raw-logs/raw/execution/ and /tradeops/bou-029/execution-gateway.
  - Log Analysis validated 2,513 gateway rows, removed 73 exact redelivery duplicates (2.9%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (917,512 → 45,677 bytes, 95.0% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Datapath Labs (FIN-029)

- Niche: `fintech_saas` · Region: `us-east-1` · Scenario: `duplicates` · Help score: **63.9** · Runtime: 76.55 ms
- S3: `s3://to-fin-029-raw-logs/raw/execution/` · CW: `/tradeops/fin-029/execution-gateway`
- Rows 3,584 (unique 3,200); dupes 384; anomalies 0; size 1,311,088→57,888 (95.6%)
- AWS plan $68.92/mo; ingest idempotency `2878e0589e4b1226…`
  - Datapath Labs (FIN-029) (fintech_saas) ingests primarily from AWS us-east-1 via s3://to-fin-029-raw-logs/raw/execution/ and /tradeops/fin-029/execution-gateway.
  - Log Analysis validated 3,584 gateway rows, removed 384 exact redelivery duplicates (10.71%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,311,088 → 57,888 bytes, 95.6% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.9/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Dark Brokerage (SPE-029)

- Niche: `specialist_broker` · Region: `us-east-2` · Scenario: `latency_spike` · Help score: **76.6** · Runtime: 102.86 ms
- S3: `s3://to-spe-029-raw-logs/raw/execution/` · CW: `/tradeops/spe-029/execution-gateway`
- Rows 4,676 (unique 4,540); dupes 136; anomalies 998; size 1,689,542→81,250 (95.2%)
- AWS plan $49.28/mo; ingest idempotency `1fb9c30f7007e3d1…`
  - Dark Brokerage (SPE-029) (specialist_broker) ingests primarily from AWS us-east-2 via s3://to-spe-029-raw-logs/raw/execution/ and /tradeops/spe-029/execution-gateway.
  - Log Analysis validated 4,676 gateway rows, removed 136 exact redelivery duplicates (2.91%), and flagged 998 latency/error signals (21.98% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,689,542 → 81,250 bytes, 95.2% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×317 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×681 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Jade Capital (BOU-030)

- Niche: `boutique_trading` · Region: `us-west-2` · Scenario: `mixed_errors` · Help score: **58.6** · Runtime: 50.0 ms
- S3: `s3://to-bou-030-raw-logs/raw/execution/` · CW: `/tradeops/bou-030/execution-gateway`
- Rows 1,974 (unique 1,880); dupes 94; anomalies 51; size 710,715→36,273 (94.9%)
- AWS plan $44.28/mo; ingest idempotency `c9937d4598202c27…`
  - Jade Capital (BOU-030) (boutique_trading) ingests primarily from AWS us-west-2 via s3://to-bou-030-raw-logs/raw/execution/ and /tradeops/bou-030/execution-gateway.
  - Log Analysis validated 1,974 gateway rows, removed 94 exact redelivery duplicates (4.76%), and flagged 51 latency/error signals (2.71% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (710,715 → 36,273 bytes, 94.9% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×51 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Fleetlog Labs (FIN-030)

- Niche: `fintech_saas` · Region: `eu-west-1` · Scenario: `normal` · Help score: **49.6** · Runtime: 94.82 ms
- S3: `s3://to-fin-030-raw-logs/raw/execution/` · CW: `/tradeops/fin-030/execution-gateway`
- Rows 3,419 (unique 3,320); dupes 99; anomalies 0; size 1,250,546→59,981 (95.2%)
- AWS plan $68.92/mo; ingest idempotency `7bc7825a867f267e…`
  - Fleetlog Labs (FIN-030) (fintech_saas) ingests primarily from AWS eu-west-1 via s3://to-fin-030-raw-logs/raw/execution/ and /tradeops/fin-030/execution-gateway.
  - Log Analysis validated 3,419 gateway rows, removed 99 exact redelivery duplicates (2.9%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,250,546 → 59,981 bytes, 95.2% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Lit Brokerage (SPE-030)

- Niche: `specialist_broker` · Region: `ap-northeast-1` · Scenario: `duplicates` · Help score: **63.9** · Runtime: 145.13 ms
- S3: `s3://to-spe-030-raw-logs/raw/execution/` · CW: `/tradeops/spe-030/execution-gateway`
- Rows 5,219 (unique 4,660); dupes 559; anomalies 0; size 1,910,553→81,385 (95.7%)
- AWS plan $49.28/mo; ingest idempotency `083bed4d956651c4…`
  - Lit Brokerage (SPE-030) (specialist_broker) ingests primarily from AWS ap-northeast-1 via s3://to-spe-030-raw-logs/raw/execution/ and /tradeops/spe-030/execution-gateway.
  - Log Analysis validated 5,219 gateway rows, removed 559 exact redelivery duplicates (10.71%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,910,553 → 81,385 bytes, 95.7% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.9/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Keystone Capital (BOU-031)

- Niche: `boutique_trading` · Region: `us-east-1` · Scenario: `latency_spike` · Help score: **76.5** · Runtime: 53.51 ms
- S3: `s3://to-bou-031-raw-logs/raw/execution/` · CW: `/tradeops/bou-031/execution-gateway`
- Rows 2,060 (unique 2,000); dupes 60; anomalies 439; size 742,460→38,854 (94.8%)
- AWS plan $29.68/mo; ingest idempotency `4cf2c5bbb1808152…`
  - Keystone Capital (BOU-031) (boutique_trading) ingests primarily from AWS us-east-1 via s3://to-bou-031-raw-logs/raw/execution/ and /tradeops/bou-031/execution-gateway.
  - Log Analysis validated 2,060 gateway rows, removed 60 exact redelivery duplicates (2.91%), and flagged 439 latency/error signals (21.95% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (742,460 → 38,854 bytes, 94.8% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $29.68/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×139 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×300 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.5/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Portside Labs (FIN-031)

- Niche: `fintech_saas` · Region: `us-east-2` · Scenario: `mixed_errors` · Help score: **58.6** · Runtime: 98.69 ms
- S3: `s3://to-fin-031-raw-logs/raw/execution/` · CW: `/tradeops/fin-031/execution-gateway`
- Rows 3,612 (unique 3,440); dupes 172; anomalies 93; size 1,321,360→61,857 (95.3%)
- AWS plan $68.92/mo; ingest idempotency `da9515ec71bdfc86…`
  - Portside Labs (FIN-031) (fintech_saas) ingests primarily from AWS us-east-2 via s3://to-fin-031-raw-logs/raw/execution/ and /tradeops/fin-031/execution-gateway.
  - Log Analysis validated 3,612 gateway rows, removed 172 exact redelivery duplicates (4.76%), and flagged 93 latency/error signals (2.7% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,321,360 → 61,857 bytes, 95.3% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×93 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Smart Brokerage (SPE-031)

- Niche: `specialist_broker` · Region: `us-west-2` · Scenario: `normal` · Help score: **49.6** · Runtime: 109.28 ms
- S3: `s3://to-spe-031-raw-logs/raw/execution/` · CW: `/tradeops/spe-031/execution-gateway`
- Rows 4,923 (unique 4,780); dupes 143; anomalies 0; size 1,777,922→82,942 (95.3%)
- AWS plan $49.28/mo; ingest idempotency `db51341c066827be…`
  - Smart Brokerage (SPE-031) (specialist_broker) ingests primarily from AWS us-west-2 via s3://to-spe-031-raw-logs/raw/execution/ and /tradeops/spe-031/execution-gateway.
  - Log Analysis validated 4,923 gateway rows, removed 143 exact redelivery duplicates (2.9%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,777,922 → 82,942 bytes, 95.3% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Lumen Capital (BOU-032)

- Niche: `boutique_trading` · Region: `eu-west-1` · Scenario: `duplicates` · Help score: **63.8** · Runtime: 54.04 ms
- S3: `s3://to-bou-032-raw-logs/raw/execution/` · CW: `/tradeops/bou-032/execution-gateway`
- Rows 2,374 (unique 2,120); dupes 254; anomalies 0; size 854,778→40,747 (95.2%)
- AWS plan $44.28/mo; ingest idempotency `55133b4247d2091c…`
  - Lumen Capital (BOU-032) (boutique_trading) ingests primarily from AWS eu-west-1 via s3://to-bou-032-raw-logs/raw/execution/ and /tradeops/bou-032/execution-gateway.
  - Log Analysis validated 2,374 gateway rows, removed 254 exact redelivery duplicates (10.7%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (854,778 → 40,747 bytes, 95.2% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.8/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Shipshape Labs (FIN-032)

- Niche: `fintech_saas` · Region: `ap-northeast-1` · Scenario: `latency_spike` · Help score: **76.6** · Runtime: 82.65 ms
- S3: `s3://to-fin-032-raw-logs/raw/execution/` · CW: `/tradeops/fin-032/execution-gateway`
- Rows 3,666 (unique 3,560); dupes 106; anomalies 783; size 1,360,474→64,991 (95.2%)
- AWS plan $68.92/mo; ingest idempotency `47eb54019e7c1c4b…`
  - Shipshape Labs (FIN-032) (fintech_saas) ingests primarily from AWS ap-northeast-1 via s3://to-fin-032-raw-logs/raw/execution/ and /tradeops/fin-032/execution-gateway.
  - Log Analysis validated 3,666 gateway rows, removed 106 exact redelivery duplicates (2.89%), and flagged 783 latency/error signals (21.99% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,360,474 → 64,991 bytes, 95.2% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×249 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×534 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Trusted Brokerage (SPE-032)

- Niche: `specialist_broker` · Region: `us-east-1` · Scenario: `mixed_errors` · Help score: **58.7** · Runtime: 114.62 ms
- S3: `s3://to-spe-032-raw-logs/raw/execution/` · CW: `/tradeops/spe-032/execution-gateway`
- Rows 5,145 (unique 4,900); dupes 245; anomalies 133; size 1,858,152→84,363 (95.5%)
- AWS plan $49.28/mo; ingest idempotency `f27abac17ec8f22f…`
  - Trusted Brokerage (SPE-032) (specialist_broker) ingests primarily from AWS us-east-1 via s3://to-spe-032-raw-logs/raw/execution/ and /tradeops/spe-032/execution-gateway.
  - Log Analysis validated 5,145 gateway rows, removed 245 exact redelivery duplicates (4.76%), and flagged 133 latency/error signals (2.71% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,858,152 → 84,363 bytes, 95.5% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×133 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Monad Capital (BOU-033)

- Niche: `boutique_trading` · Region: `us-east-2` · Scenario: `normal` · Help score: **49.5** · Runtime: 51.42 ms
- S3: `s3://to-bou-033-raw-logs/raw/execution/` · CW: `/tradeops/bou-033/execution-gateway`
- Rows 2,307 (unique 2,240); dupes 67; anomalies 0; size 830,906→42,534 (94.9%)
- AWS plan $44.28/mo; ingest idempotency `d6fed7e80c0cd80c…`
  - Monad Capital (BOU-033) (boutique_trading) ingests primarily from AWS us-east-2 via s3://to-bou-033-raw-logs/raw/execution/ and /tradeops/bou-033/execution-gateway.
  - Log Analysis validated 2,307 gateway rows, removed 67 exact redelivery duplicates (2.9%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (830,906 → 42,534 bytes, 94.9% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.5/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Tracebay Labs (FIN-033)

- Niche: `fintech_saas` · Region: `us-west-2` · Scenario: `duplicates` · Help score: **63.9** · Runtime: 87.61 ms
- S3: `s3://to-fin-033-raw-logs/raw/execution/` · CW: `/tradeops/fin-033/execution-gateway`
- Rows 4,121 (unique 3,680); dupes 441; anomalies 0; size 1,507,176→65,200 (95.7%)
- AWS plan $68.92/mo; ingest idempotency `619053efea8f0170…`
  - Tracebay Labs (FIN-033) (fintech_saas) ingests primarily from AWS us-west-2 via s3://to-fin-033-raw-logs/raw/execution/ and /tradeops/fin-033/execution-gateway.
  - Log Analysis validated 4,121 gateway rows, removed 441 exact redelivery duplicates (10.7%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,507,176 → 65,200 bytes, 95.7% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.9/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### United Brokerage (SPE-033)

- Niche: `specialist_broker` · Region: `eu-west-1` · Scenario: `latency_spike` · Help score: **76.6** · Runtime: 116.13 ms
- S3: `s3://to-spe-033-raw-logs/raw/execution/` · CW: `/tradeops/spe-033/execution-gateway`
- Rows 5,170 (unique 5,020); dupes 150; anomalies 1,104; size 1,868,283→89,034 (95.2%)
- AWS plan $49.28/mo; ingest idempotency `642070466286976d…`
  - United Brokerage (SPE-033) (specialist_broker) ingests primarily from AWS eu-west-1 via s3://to-spe-033-raw-logs/raw/execution/ and /tradeops/spe-033/execution-gateway.
  - Log Analysis validated 5,170 gateway rows, removed 150 exact redelivery duplicates (2.9%), and flagged 1,104 latency/error signals (21.99% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,868,283 → 89,034 bytes, 95.2% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×351 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×753 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Noble Capital (BOU-034)

- Niche: `boutique_trading` · Region: `ap-northeast-1` · Scenario: `mixed_errors` · Help score: **58.6** · Runtime: 55.98 ms
- S3: `s3://to-bou-034-raw-logs/raw/execution/` · CW: `/tradeops/bou-034/execution-gateway`
- Rows 2,478 (unique 2,360); dupes 118; anomalies 64; size 905,024→44,480 (95.1%)
- AWS plan $44.28/mo; ingest idempotency `0a0d1b76b8cf65e0…`
  - Noble Capital (BOU-034) (boutique_trading) ingests primarily from AWS ap-northeast-1 via s3://to-bou-034-raw-logs/raw/execution/ and /tradeops/bou-034/execution-gateway.
  - Log Analysis validated 2,478 gateway rows, removed 118 exact redelivery duplicates (4.76%), and flagged 64 latency/error signals (2.71% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (905,024 → 44,480 bytes, 95.1% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×64 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Unitops Labs (FIN-034)

- Niche: `fintech_saas` · Region: `us-east-1` · Scenario: `normal` · Help score: **49.7** · Runtime: 86.62 ms
- S3: `s3://to-fin-034-raw-logs/raw/execution/` · CW: `/tradeops/fin-034/execution-gateway`
- Rows 3,914 (unique 3,800); dupes 114; anomalies 0; size 1,431,617→67,088 (95.3%)
- AWS plan $68.92/mo; ingest idempotency `a6f33b562d6d9e1c…`
  - Unitops Labs (FIN-034) (fintech_saas) ingests primarily from AWS us-east-1 via s3://to-fin-034-raw-logs/raw/execution/ and /tradeops/fin-034/execution-gateway.
  - Log Analysis validated 3,914 gateway rows, removed 114 exact redelivery duplicates (2.91%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,431,617 → 67,088 bytes, 95.3% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Vista Brokerage (SPE-034)

- Niche: `specialist_broker` · Region: `us-east-2` · Scenario: `duplicates` · Help score: **63.9** · Runtime: 120.34 ms
- S3: `s3://to-spe-034-raw-logs/raw/execution/` · CW: `/tradeops/spe-034/execution-gateway`
- Rows 5,756 (unique 5,140); dupes 616; anomalies 0; size 2,078,252→88,135 (95.8%)
- AWS plan $49.28/mo; ingest idempotency `adb39b98255fbbf4…`
  - Vista Brokerage (SPE-034) (specialist_broker) ingests primarily from AWS us-east-2 via s3://to-spe-034-raw-logs/raw/execution/ and /tradeops/spe-034/execution-gateway.
  - Log Analysis validated 5,756 gateway rows, removed 616 exact redelivery duplicates (10.7%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (2,078,252 → 88,135 bytes, 95.8% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.9/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Orbit Capital (BOU-035)

- Niche: `boutique_trading` · Region: `us-west-2` · Scenario: `latency_spike` · Help score: **76.5** · Runtime: 40.94 ms
- S3: `s3://to-bou-035-raw-logs/raw/execution/` · CW: `/tradeops/bou-035/execution-gateway`
- Rows 1,854 (unique 1,800); dupes 54; anomalies 395; size 668,140→35,423 (94.7%)
- AWS plan $44.28/mo; ingest idempotency `b78815fca6dac329…`
  - Orbit Capital (BOU-035) (boutique_trading) ingests primarily from AWS us-west-2 via s3://to-bou-035-raw-logs/raw/execution/ and /tradeops/bou-035/execution-gateway.
  - Log Analysis validated 1,854 gateway rows, removed 54 exact redelivery duplicates (2.91%), and flagged 395 latency/error signals (21.94% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (668,140 → 35,423 bytes, 94.7% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×125 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×270 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.5/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Workbench Labs (FIN-035)

- Niche: `fintech_saas` · Region: `eu-west-1` · Scenario: `mixed_errors` · Help score: **58.7** · Runtime: 72.45 ms
- S3: `s3://to-fin-035-raw-logs/raw/execution/` · CW: `/tradeops/fin-035/execution-gateway`
- Rows 3,402 (unique 3,240); dupes 162; anomalies 88; size 1,243,830→58,618 (95.3%)
- AWS plan $68.92/mo; ingest idempotency `9f1556335edca599…`
  - Workbench Labs (FIN-035) (fintech_saas) ingests primarily from AWS eu-west-1 via s3://to-fin-035-raw-logs/raw/execution/ and /tradeops/fin-035/execution-gateway.
  - Log Analysis validated 3,402 gateway rows, removed 162 exact redelivery duplicates (4.76%), and flagged 88 latency/error signals (2.72% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,243,830 → 58,618 bytes, 95.3% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×88 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### West Brokerage (SPE-035)

- Niche: `specialist_broker` · Region: `ap-northeast-1` · Scenario: `normal` · Help score: **49.7** · Runtime: 100.57 ms
- S3: `s3://to-spe-035-raw-logs/raw/execution/` · CW: `/tradeops/spe-035/execution-gateway`
- Rows 4,717 (unique 4,580); dupes 137; anomalies 0; size 1,726,825→79,850 (95.4%)
- AWS plan $49.28/mo; ingest idempotency `da35da605714f467…`
  - West Brokerage (SPE-035) (specialist_broker) ingests primarily from AWS ap-northeast-1 via s3://to-spe-035-raw-logs/raw/execution/ and /tradeops/spe-035/execution-gateway.
  - Log Analysis validated 4,717 gateway rows, removed 137 exact redelivery duplicates (2.9%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,726,825 → 79,850 bytes, 95.4% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Apex Trading (BOU-036)

- Niche: `boutique_trading` · Region: `us-east-1` · Scenario: `duplicates` · Help score: **63.8** · Runtime: 45.9 ms
- S3: `s3://to-bou-036-raw-logs/raw/execution/` · CW: `/tradeops/bou-036/execution-gateway`
- Rows 2,150 (unique 1,920); dupes 230; anomalies 0; size 774,313→37,026 (95.2%)
- AWS plan $29.68/mo; ingest idempotency `ea84e364af2ad0ff…`
  - Apex Trading (BOU-036) (boutique_trading) ingests primarily from AWS us-east-1 via s3://to-bou-036-raw-logs/raw/execution/ and /tradeops/bou-036/execution-gateway.
  - Log Analysis validated 2,150 gateway rows, removed 230 exact redelivery duplicates (10.7%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (774,313 → 37,026 bytes, 95.2% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $29.68/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.8/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Ledger Systems (FIN-036)

- Niche: `fintech_saas` · Region: `us-east-2` · Scenario: `latency_spike` · Help score: **76.6** · Runtime: 78.39 ms
- S3: `s3://to-fin-036-raw-logs/raw/execution/` · CW: `/tradeops/fin-036/execution-gateway`
- Rows 3,460 (unique 3,360); dupes 100; anomalies 739; size 1,266,757→61,607 (95.1%)
- AWS plan $68.92/mo; ingest idempotency `62e7770b75eaf42b…`
  - Ledger Systems (FIN-036) (fintech_saas) ingests primarily from AWS us-east-2 via s3://to-fin-036-raw-logs/raw/execution/ and /tradeops/fin-036/execution-gateway.
  - Log Analysis validated 3,460 gateway rows, removed 100 exact redelivery duplicates (2.89%), and flagged 739 latency/error signals (21.99% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,266,757 → 61,607 bytes, 95.1% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×234 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×505 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Harbor Securities (SPE-036)

- Niche: `specialist_broker` · Region: `us-west-2` · Scenario: `mixed_errors` · Help score: **58.7** · Runtime: 112.92 ms
- S3: `s3://to-spe-036-raw-logs/raw/execution/` · CW: `/tradeops/spe-036/execution-gateway`
- Rows 4,935 (unique 4,700); dupes 235; anomalies 128; size 1,781,708→81,848 (95.4%)
- AWS plan $49.28/mo; ingest idempotency `154f7a05772db0ff…`
  - Harbor Securities (SPE-036) (specialist_broker) ingests primarily from AWS us-west-2 via s3://to-spe-036-raw-logs/raw/execution/ and /tradeops/spe-036/execution-gateway.
  - Log Analysis validated 4,935 gateway rows, removed 235 exact redelivery duplicates (4.76%), and flagged 128 latency/error signals (2.72% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,781,708 → 81,848 bytes, 95.4% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×128 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Northbridge Trading (BOU-037)

- Niche: `boutique_trading` · Region: `eu-west-1` · Scenario: `normal` · Help score: **49.5** · Runtime: 46.55 ms
- S3: `s3://to-bou-037-raw-logs/raw/execution/` · CW: `/tradeops/bou-037/execution-gateway`
- Rows 2,101 (unique 2,040); dupes 61; anomalies 0; size 756,566→38,947 (94.9%)
- AWS plan $44.28/mo; ingest idempotency `fe5538cfd1db65bb…`
  - Northbridge Trading (BOU-037) (boutique_trading) ingests primarily from AWS eu-west-1 via s3://to-bou-037-raw-logs/raw/execution/ and /tradeops/bou-037/execution-gateway.
  - Log Analysis validated 2,101 gateway rows, removed 61 exact redelivery duplicates (2.9%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (756,566 → 38,947 bytes, 94.9% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.5/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Clearpath Systems (FIN-037)

- Niche: `fintech_saas` · Region: `ap-northeast-1` · Scenario: `duplicates` · Help score: **63.9** · Runtime: 81.94 ms
- S3: `s3://to-fin-037-raw-logs/raw/execution/` · CW: `/tradeops/fin-037/execution-gateway`
- Rows 3,897 (unique 3,480); dupes 417; anomalies 0; size 1,445,037→62,245 (95.7%)
- AWS plan $68.92/mo; ingest idempotency `01edf802d289ea7f…`
  - Clearpath Systems (FIN-037) (fintech_saas) ingests primarily from AWS ap-northeast-1 via s3://to-fin-037-raw-logs/raw/execution/ and /tradeops/fin-037/execution-gateway.
  - Log Analysis validated 3,897 gateway rows, removed 417 exact redelivery duplicates (10.7%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,445,037 → 62,245 bytes, 95.7% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.9/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Seaboard Securities (SPE-037)

- Niche: `specialist_broker` · Region: `us-east-1` · Scenario: `latency_spike` · Help score: **76.6** · Runtime: 109.45 ms
- S3: `s3://to-spe-037-raw-logs/raw/execution/` · CW: `/tradeops/spe-037/execution-gateway`
- Rows 4,964 (unique 4,820); dupes 144; anomalies 1,060; size 1,793,630→85,459 (95.2%)
- AWS plan $49.28/mo; ingest idempotency `45c4a16ce21e4223…`
  - Seaboard Securities (SPE-037) (specialist_broker) ingests primarily from AWS us-east-1 via s3://to-spe-037-raw-logs/raw/execution/ and /tradeops/spe-037/execution-gateway.
  - Log Analysis validated 4,964 gateway rows, removed 144 exact redelivery duplicates (2.9%), and flagged 1,060 latency/error signals (21.99% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,793,630 → 85,459 bytes, 95.2% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×338 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×722 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Harbor Trading (BOU-038)

- Niche: `boutique_trading` · Region: `us-east-2` · Scenario: `mixed_errors` · Help score: **58.6** · Runtime: 50.0 ms
- S3: `s3://to-bou-038-raw-logs/raw/execution/` · CW: `/tradeops/bou-038/execution-gateway`
- Rows 2,268 (unique 2,160); dupes 108; anomalies 59; size 816,623→41,438 (94.9%)
- AWS plan $44.28/mo; ingest idempotency `6abcf60ee45ba645…`
  - Harbor Trading (BOU-038) (boutique_trading) ingests primarily from AWS us-east-2 via s3://to-bou-038-raw-logs/raw/execution/ and /tradeops/bou-038/execution-gateway.
  - Log Analysis validated 2,268 gateway rows, removed 108 exact redelivery duplicates (4.76%), and flagged 59 latency/error signals (2.73% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (816,623 → 41,438 bytes, 94.9% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×59 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Routeline Systems (FIN-038)

- Niche: `fintech_saas` · Region: `us-west-2` · Scenario: `normal` · Help score: **49.7** · Runtime: 79.95 ms
- S3: `s3://to-fin-038-raw-logs/raw/execution/` · CW: `/tradeops/fin-038/execution-gateway`
- Rows 3,708 (unique 3,600); dupes 108; anomalies 0; size 1,356,228→64,075 (95.3%)
- AWS plan $68.92/mo; ingest idempotency `b23c7982068445bc…`
  - Routeline Systems (FIN-038) (fintech_saas) ingests primarily from AWS us-west-2 via s3://to-fin-038-raw-logs/raw/execution/ and /tradeops/fin-038/execution-gateway.
  - Log Analysis validated 3,708 gateway rows, removed 108 exact redelivery duplicates (2.91%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,356,228 → 64,075 bytes, 95.3% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Continental Securities (SPE-038)

- Niche: `specialist_broker` · Region: `eu-west-1` · Scenario: `duplicates` · Help score: **63.9** · Runtime: 116.51 ms
- S3: `s3://to-spe-038-raw-logs/raw/execution/` · CW: `/tradeops/spe-038/execution-gateway`
- Rows 5,532 (unique 4,940); dupes 592; anomalies 0; size 1,998,524→85,591 (95.7%)
- AWS plan $49.28/mo; ingest idempotency `f2ff51089ed3534c…`
  - Continental Securities (SPE-038) (specialist_broker) ingests primarily from AWS eu-west-1 via s3://to-spe-038-raw-logs/raw/execution/ and /tradeops/spe-038/execution-gateway.
  - Log Analysis validated 5,532 gateway rows, removed 592 exact redelivery duplicates (10.7%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,998,524 → 85,591 bytes, 95.7% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.9/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Lattice Trading (BOU-039)

- Niche: `boutique_trading` · Region: `ap-northeast-1` · Scenario: `latency_spike` · Help score: **76.5** · Runtime: 53.58 ms
- S3: `s3://to-bou-039-raw-logs/raw/execution/` · CW: `/tradeops/bou-039/execution-gateway`
- Rows 2,348 (unique 2,280); dupes 68; anomalies 501; size 857,910→43,937 (94.9%)
- AWS plan $44.28/mo; ingest idempotency `a7b19b6b7a51aa14…`
  - Lattice Trading (BOU-039) (boutique_trading) ingests primarily from AWS ap-northeast-1 via s3://to-bou-039-raw-logs/raw/execution/ and /tradeops/bou-039/execution-gateway.
  - Log Analysis validated 2,348 gateway rows, removed 68 exact redelivery duplicates (2.9%), and flagged 501 latency/error signals (21.97% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (857,910 → 43,937 bytes, 94.9% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×160 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×341 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.5/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Opsfolio Systems (FIN-039)

- Niche: `fintech_saas` · Region: `us-east-1` · Scenario: `mixed_errors` · Help score: **58.7** · Runtime: 84.83 ms
- S3: `s3://to-fin-039-raw-logs/raw/execution/` · CW: `/tradeops/fin-039/execution-gateway`
- Rows 3,906 (unique 3,720); dupes 186; anomalies 101; size 1,428,496→66,009 (95.4%)
- AWS plan $68.92/mo; ingest idempotency `39fb521546cdecd7…`
  - Opsfolio Systems (FIN-039) (fintech_saas) ingests primarily from AWS us-east-1 via s3://to-fin-039-raw-logs/raw/execution/ and /tradeops/fin-039/execution-gateway.
  - Log Analysis validated 3,906 gateway rows, removed 186 exact redelivery duplicates (4.76%), and flagged 101 latency/error signals (2.72% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,428,496 → 66,009 bytes, 95.4% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×101 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Pacific Securities (SPE-039)

- Niche: `specialist_broker` · Region: `us-east-2` · Scenario: `normal` · Help score: **49.6** · Runtime: 111.18 ms
- S3: `s3://to-spe-039-raw-logs/raw/execution/` · CW: `/tradeops/spe-039/execution-gateway`
- Rows 5,211 (unique 5,060); dupes 151; anomalies 0; size 1,881,398→87,094 (95.4%)
- AWS plan $49.28/mo; ingest idempotency `0ad231d8face7d4f…`
  - Pacific Securities (SPE-039) (specialist_broker) ingests primarily from AWS us-east-2 via s3://to-spe-039-raw-logs/raw/execution/ and /tradeops/spe-039/execution-gateway.
  - Log Analysis validated 5,211 gateway rows, removed 151 exact redelivery duplicates (2.9%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,881,398 → 87,094 bytes, 95.4% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 49.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Meridian Trading (BOU-040)

- Niche: `boutique_trading` · Region: `us-west-2` · Scenario: `duplicates` · Help score: **63.8** · Runtime: 57.19 ms
- S3: `s3://to-bou-040-raw-logs/raw/execution/` · CW: `/tradeops/bou-040/execution-gateway`
- Rows 2,688 (unique 2,400); dupes 288; anomalies 0; size 967,932→44,979 (95.4%)
- AWS plan $44.28/mo; ingest idempotency `9af268489c3b66a4…`
  - Meridian Trading (BOU-040) (boutique_trading) ingests primarily from AWS us-west-2 via s3://to-bou-040-raw-logs/raw/execution/ and /tradeops/bou-040/execution-gateway.
  - Log Analysis validated 2,688 gateway rows, removed 288 exact redelivery duplicates (10.71%), and flagged 0 latency/error signals (0.0% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (967,932 → 44,979 bytes, 95.4% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $44.28/mo (within $50 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 63.8/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### TradeNest Systems (FIN-040)

- Niche: `fintech_saas` · Region: `eu-west-1` · Scenario: `latency_spike` · Help score: **76.6** · Runtime: 97.96 ms
- S3: `s3://to-fin-040-raw-logs/raw/execution/` · CW: `/tradeops/fin-040/execution-gateway`
- Rows 3,955 (unique 3,840); dupes 115; anomalies 844; size 1,447,767→69,259 (95.2%)
- AWS plan $68.92/mo; ingest idempotency `9dac47703379dc07…`
  - TradeNest Systems (FIN-040) (fintech_saas) ingests primarily from AWS eu-west-1 via s3://to-fin-040-raw-logs/raw/execution/ and /tradeops/fin-040/execution-gateway.
  - Log Analysis validated 3,955 gateway rows, removed 115 exact redelivery duplicates (2.91%), and flagged 844 latency/error signals (21.98% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,447,767 → 69,259 bytes, 95.2% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $68.92/mo (within $75 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×269 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Incident inbox: Elevated execution latency ×575 — Compare upstream latency and deployment timing. This signal does not establish a root cause.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 76.6/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

### Midwest Securities (SPE-040)

- Niche: `specialist_broker` · Region: `ap-northeast-1` · Scenario: `mixed_errors` · Help score: **58.7** · Runtime: 106.18 ms
- S3: `s3://to-spe-040-raw-logs/raw/execution/` · CW: `/tradeops/spe-040/execution-gateway`
- Rows 4,725 (unique 4,500); dupes 225; anomalies 122; size 1,728,947→79,010 (95.4%)
- AWS plan $49.28/mo; ingest idempotency `f5559355faf39545…`
  - Midwest Securities (SPE-040) (specialist_broker) ingests primarily from AWS ap-northeast-1 via s3://to-spe-040-raw-logs/raw/execution/ and /tradeops/spe-040/execution-gateway.
  - Log Analysis validated 4,725 gateway rows, removed 225 exact redelivery duplicates (4.76%), and flagged 122 latency/error signals (2.71% of unique rows).
  - Compression produced a verified Zstd Parquet analytical copy (1,728,947 → 79,010 bytes, 95.4% smaller) while retaining the raw S3/CloudWatch evidence.
  - Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); human approval still required — AWS archive is intentionally disabled until durable approvals exist.
  - Partition production datasets by UTC date. Add symbol only when partition sizes justify it. Compact to 128–512 MiB files; this small demo stays in one file.
  - Private AWS plan estimate $49.28/mo (within $60 budget). Keep AI optional, group alerts, and use S3 gateway access for bulk logs.
  - Incident inbox: Execution failures ×122 — Inspect gateway health and upstream rejection metrics. Validate the cause before intervention.
  - Sequence Evidence reviewed 0 cohorts and surfaced 0 candidate motif changes (review-only; no causal claim).
  - Composite help score 58.7/100 for this AWS-primary specialist firm (noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences).

## Caveats

- Firms are synthetic AWS-primary specialists in TradeOps target niches; they are not public megacap issuers.
- Live Glue/Athena/CloudWatch pulls were not executed; AWSAdapter.plan_event and network_plan provide the deployment boundary estimates.
- CostAgent figures are illustrative file-based rates with raw retained; not measured Athena bills.
- Help score is a transparent weighted composite for comparison across this corpus only.
