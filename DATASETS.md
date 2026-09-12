# Market dataset integration and verification

## What was tested

| Source | Local support | Evidence |
|---|---|---|
| Binance | Seven-column SPOT trades CSV, optional `id`/`trade_id` header, single CSV ZIP | Real BTCUSDT daily file for 2017-08-17; publisher SHA-256 verified |
| Algoseek | Trade Only CSV/CSV.GZ with documented field names | Invented schema fixtures; no licensed/sandbox export downloaded |
| Hyperliquid | API-format fill arrays or one fill per JSONL line | Invented API schema fixtures; no requester-pays archive downloaded |

Open **Market datasets**, then **Analyze verified sample**, or select the source and upload an export. Downloads are never triggered by arbitrary URLs supplied to the app. The Binance sample button only reads the bundled file and verifies its local provenance hash.

## Binance result

3,427 records; 231,002-byte CSV → 109,463-byte Parquet (52.6% smaller). No repeated source rows. UTC coverage 2017-08-17 04:00:28.322 through 23:58:40.719. Full round-trip equality checked. `samples/binance-provenance.json` records download URL and compressed/uncompressed SHA-256 hashes. Reproduce with `python scripts/fetch_binance_sample.py`; network access required. The fetch is bounded to 20 MiB, verifies TLS and publisher checksum, and does not execute downloaded code.

The adapter handles millisecond and microsecond epochs without float conversion. Symbol is explicitly supplied because it is not a CSV column. Klines, aggTrades, futures formats and live trading APIs are outside this adapter.

## Algoseek details

The adapter uses Date, Timestamp, EventType, Ticker, Price, Quantity, Exchange and Conditions. Exact nanosecond text, condition flags and event types remain in the original row payload inside Parquet. Cancellation events are preserved; the app does not compute adjusted volume or pretend to reconcile corrections. No provider trade ID is invented.

The source guide says EST. Default conversion is fixed UTC−05:00; the uploader can explicitly choose America/New_York when their export uses daylight-saving-aware Eastern time. Confirm with the provider before analyzing summer sessions. Original timestamp text remains preserved regardless of the selected interpretation.

## Hyperliquid details

Requires `coin`, `px`, `sz`, `time` (milliseconds) and `tid`. Other fill fields are preserved in `source_record`. New block-batched archives, legacy node_trades, L2 order books and asset contexts are different formats and are rejected. Decompress LZ4 externally before uploading a supported API-format fills export; the app does not process LZ4 or download requester-pays S3 objects. Access to private wallet histories is not requested.

## Data semantics and limits

Inputs and expanded archives are limited to 20 MiB and accepted datasets to 200,000 rows. Price and quantity retain decimal strings, avoiding binary floating-point rounding. All records survive optimization, including repeated rows; repeats are reported for review. Source payload and original uploaded bytes are preserved. JSON source payloads are semantically preserved, while original bytes retain formatting. No operational latency, errors or security incidents are inferred from market trade data. No market anomaly detection or trading strategy backtest is claimed.

Parquet output includes canonical UTC timestamp text, symbol, price, quantity and source_record. Canonical timestamp text preserves precision; cast deliberately to a suitable query timestamp type in production. One file is produced for bounded local imports; partitions remain recommendations. Size comparisons use the uploaded file bytes, so a compressed upload can outperform Parquet. Cost estimates are illustrative file-based comparisons, not measured Athena billing, and exclude provider licenses and transfer fees. Sensitive source fields remain in local files; incident screens do not publish them.

## Sources

- [Algoseek product and sandbox access](https://algoseek.com/dataset/us-equities-trade-only/)
- [Algoseek schema guide](https://algoseek.com/data-docs/equity-market-data/algoseek.US.Equity.Trades.Only.pdf)
- [Hyperliquid historical archives and requester costs](https://hyperliquid.gitbook.io/hyperliquid-docs/historical-data)
- [Hyperliquid API fill schema](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
- [Binance public-data formats and checksums](https://github.com/binance/binance-public-data)

No Algoseek license was purchased and no Hyperliquid requester-pays transfer was initiated. Real export validation for those two sources remains pending supplied files.

## S3 connector expansion

The connector update adds Binance USD-M six-column trade files and BitMEX trade CSV.GZ. Both have real sample verification; see `samples/s3-verification.json`. Earlier futures exclusion above applies to the spot adapter, not the new `binance_um` adapter. Hyperliquid node_fills_by_block remains blocked and is not the API-format fills adapter.
