# Verification — 2026-09-11

- Python 3.14; exact installed dependencies captured in requirements.txt.
- `python -m pytest -q`: **48 passed**. Two upstream dependency deprecation warnings; no test failures.
- `node --check frontend/app.js`: passed.
- Running FastAPI health endpoint: HTTP 200, local mode, six agents.
- Browser: dashboard rendered populated results; archive review dialog opened and cancelled; reload retained history.
- Synthetic latency scenario: 10,400 input rows, 10,000 unique records, 400 exact duplicates, 1,999 anomaly signals; 2.30 MB JSON to about 146.5 KB Parquet (93.6% smaller analytical copy).
- Approval tests verify unconfirmed archival is rejected, approved raw data remains recoverable, repeated approval is rejected, and rejection preserves raw data.
- Malformed schema, missing fields, invalid latency, hostile Origin and Host checks pass.
- AWS event validation uses an injected fake session. No live AWS call, deployment or cloud billing test was performed.

Update: endpoint budget calculation and invalid AZ inputs tested; aggregate incident summaries tested against sensitive extra fields. Frontend syntax check passes.

Dataset update: 3,427 real Binance trades passed checksum and Parquet round-trip validation; 231,002 → 109,463 bytes. Browser sample action successfully rendered results. Algoseek/Hyperliquid tested with invented schema fixtures only; real provider exports remain pending.

S3 update: anonymously listed spot/futures/BitMEX prefixes; actual selected-object ingestion and zero-new-record repeat scans passed. Binance companion checksums verified. Hyperliquid anonymous listing returned Requester Pays AccessDenied; no billable opt-in sent. See samples/s3-verification.json. Folder and CloudWatch retry/pagination behavior tested locally with fakes.

History UI: verified 33 saved events across 7 runs, search narrowed BitMEX to 2 events, and expansion exposed source metadata and download links. Frontend syntax check passed.

## Sequence evidence extension

- Full suite: 56 tests passed (two upstream deprecation warnings).
- Frontend: `node --check frontend/app.js` passed.
- Eight sequence tests exercise known changes, stable controls, duplicate inflation,
  reference-only calibration, cohort isolation, ambiguity, missing/insufficient
  evidence, long gaps, and provider-neutral AI context.
- No real-world sensitivity/specificity or causal diagnosis claim is made.
