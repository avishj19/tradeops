# Existing-workflow connections

The CLI reads existing folders, S3 objects and CloudWatch logs, writes copies and verified Parquet to TradeOps, and records progress in the same SQLite database as the dashboard. Source systems receive no write/delete/retention API calls. No application code changes are required for importing supported formats. Use Linux/macOS; file locking uses fcntl.

## Four requested S3 presets

| Config | Source | Status |
|---|---|---|
| connectors/binance-spot.json | s3://data.binance.vision/data/spot/daily/trades/ | Anonymous access; ZIP spot trades, publisher checksum verification |
| connectors/binance-futures.json | s3://data.binance.vision/data/futures/um/daily/trades/ | Anonymous access; ZIP USD-M trades, publisher checksum verification |
| connectors/bitmex.json | s3://public.bitmex.com/data/trade/ | Anonymous access; CSV.GZ trade records |
| connectors/hyperliquid.json | s3://hl-mainnet-node-data/node_fills_by_block/ | Blocked: anonymous listing returned Requester Pays AccessDenied |

Hyperliquid's block-batched archive is not the API-fill format. Its preset refuses execution before any listing/download. Supporting it requires cost authorization, authenticated access and a real block/LZ4 sample to validate a dedicated adapter. No RequestPayer parameter is sent. Do not remove the block and assume the existing API-fills parser supports block archives.

## Run a bounded scan

From the repository with installed requirements:

```sh
.venv/bin/python -m backend.connectors --config connectors/binance-spot.json --list
.venv/bin/python -m backend.connectors --config connectors/binance-spot.json
```

`--list` reads metadata only. Default presets inspect at most 100 listed objects and download at most one supported object per scan. Select exact `keys` in your config or narrow `prefix` to a symbol/date before practical use. `keys` must stay inside the prefix. Example selected key:

```json
{"keys":["data/futures/um/daily/trades/BTCUSDT/BTCUSDT-trades-2019-09-08.zip"]}
```

Add that property to the futures preset, retaining its other fields. `max_objects` controls downloads; `max_listed` controls listing up to 1,000 records. `start_after` can move a bounded scan beyond a previous key. A broad preset is a bounded preview, not a complete historical sync; it does not automatically traverse beyond its listing bound. Oversized objects are skipped, not marked completed. Expanded archives and inputs remain limited to 20 MiB and 200,000 records; larger archives need a streaming/batch worker. There is no claim of full-archive coverage.

S3 conditional reads use the listed ETag to reject an object overwritten during download. Completed object content is checkpointed; retrying skips it. VersionId is recorded when returned. Historical overwritten versions are not enumerated. Binance downloads verify the companion SHA-256 checksum before importing. BitMEX records a local SHA-256, without claiming publisher checksum verification.

## Existing folders

Copy `connectors/folder.example.json`, set a trusted absolute input directory and format (`csv`, `json`, `jsonl`, `text`). The connector reads nonrecursive, nonsymlink files that have not changed for `settle_seconds`. Use completed/rotated files or atomic producer renames; a settling delay is a heuristic, not a guarantee a producer has finished. Active-file tailing is not implemented. If a file later changes, its whole new snapshot is ingested, potentially repeating old records in another run. Originals stay untouched. Do not put the TradeOps output directory inside the input folder.

## Existing CloudWatch

Copy `connectors/cloudwatch.example.json`; choose your region, exact log group and explicit `start_ms`. The CLI uses the normal AWS role/profile chain. Optional `profile` selects an existing configured profile; never put access keys in configuration files. No credentials have been requested or saved by this implementation.

CloudWatch reads use FilterLogEvents, including empty pages with continuation tokens. Event IDs are checkpointed. A completed scan advances its watermark and replays a five-minute overlap by default; arbitrarily late arrivals need a deliberate backfill. Failures leave the watermark unchanged. An optional `filter_pattern` restricts ingestion, but excluded events will not appear in TradeOps. This version stores each event as a separate local run; it is suited to low-volume validation, not high-volume production ingestion. Use bounded time windows, or add batching before production. CloudWatch permissions/API costs still apply.

## Optional field mapping

Without mapping, arbitrary records are preserved as JSON inside Parquet; no operational metrics are invented. Add a `mapping` object using the shape in `connectors/mapping.example.json`. Keys are canonical TradeOps fields, values are dotted source paths. For JSON messages in CloudWatch, use `parsed_message.time`, etc. Required operational fields must actually exist. Mapping failures fail the import without checkpointing. UTC ISO timestamps with explicit timezone and latency in milliseconds remain required; unit conversion is not inferred.

Mapped size metrics compare normalized JSON against Parquet; original byte size is recorded separately as `input_bytes`. External-source archival is always disabled. Source payloads remain in local copies and may contain sensitive fields; protect the local data directory accordingly.

## Repeated execution

```sh
.venv/bin/python -m backend.connectors --config connectors/folder.example.json --interval 60
```

This is an optional foreground polling process; no scheduler was installed. Stop with Ctrl+C. One connector process per data directory is enforced by a file lock. Database commits couple each run with its checkpoint. Re-running after failure is safe for completed inputs. Output files written before a failed transaction may remain and will be overwritten on retry. Config changes produce a new checkpoint namespace and may re-import sources intentionally.

## AWS access

Public presets use unsigned requests and do not require AWS keys. Private S3 roles need `s3:ListBucket` restricted to the prefix and `s3:GetObject` restricted to its objects. SSE-KMS reads may also need key-scoped `kms:Decrypt`. CloudWatch requires `logs:FilterLogEvents` scoped to the chosen log group. These connectors do not require source write/delete or retention permissions. S3 and Logs private endpoints can be used where required by the deployment; this update provisions no VPC resources.

Tests cover folder checkpoints, S3 conditional reads and retries, CloudWatch empty-page pagination/replay, failed mappings and prefix boundaries. CloudWatch/private-account tests use fake clients; no company account has been connected.
