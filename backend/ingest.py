"""Ingest helpers: decompress uploads and normalize common log JSON shapes."""
from __future__ import annotations

import csv
import gzip
import io
import json
from pathlib import Path

# Map common alternate headers onto the canonical TradeOps log schema.
_ALIASES = {
    'timestamp': {'timestamp', 'time', 'ts', 'event_time', 'transact_time', 'datetime', 'date_time'},
    'event_id': {'event_id', 'eventid', 'id', 'trade_id', 'tradeid', 'exec_id', 'execution_id', 'tid', 'agg_trade_id'},
    'symbol': {'symbol', 'sym', 'ticker', 'instrument', 'coin', 'pair', 'market'},
    'latency_ms': {'latency_ms', 'latency', 'latency_millis', 'rtt_ms', 'delay_ms', 'exec_latency_ms'},
    'status': {'status', 'state', 'result', 'exec_status', 'order_status'},
}

_WRAPPER_KEYS = ('records', 'rows', 'data', 'logs', 'events', 'fills', 'trades', 'items', 'results')


def strip_compression_suffix(name: str) -> str:
    lower = name.lower()
    if lower.endswith('.gz'):
        return name[:-3]
    if lower.endswith('.gzip'):
        return name[:-5]
    return name


def maybe_decompress(data: bytes, filename: str = '') -> tuple[bytes, str]:
    """Return (payload, logical_filename). Handles .gz names and gzip magic bytes."""
    logical = strip_compression_suffix(filename or 'upload.json')
    lower = (filename or '').lower()
    gzipped = lower.endswith('.gz') or lower.endswith('.gzip') or data[:2] == b'\x1f\x8b'
    if gzipped:
        try:
            data = gzip.decompress(data)
        except OSError as e:
            raise ValueError('Could not decompress gzip upload.') from e
    return data, logical


def _normalize_row(row: dict) -> dict:
    lower_map = {str(k).strip().lower(): k for k in row}
    out = dict(row)
    for canonical, aliases in _ALIASES.items():
        if canonical in row and row[canonical] is not None and str(row[canonical]).strip() != '':
            continue
        for alias in aliases:
            if alias in lower_map:
                src = lower_map[alias]
                if row.get(src) is None or str(row.get(src)).strip() == '':
                    continue
                out[canonical] = row[src]
                break
    return out


def parse_log_records(data: bytes, filename: str) -> list[dict]:
    """Parse CSV/JSON(/NDJSON) trading logs into a list of row dicts."""
    data, filename = maybe_decompress(data, filename)
    text = data.decode('utf-8-sig')
    logical = strip_compression_suffix(filename or '').lower()

    if logical.endswith('.csv'):
        rows = list(csv.DictReader(io.StringIO(text)))
        if not rows:
            raise ValueError('CSV file has no data rows.')
        return [_normalize_row(r) for r in rows]

    # JSON array, object wrapper, or NDJSON
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        lines = [ln for ln in text.splitlines() if ln.strip()]
        if not lines:
            raise ValueError('JSON file is empty.')
        try:
            parsed = [json.loads(ln) for ln in lines]
        except json.JSONDecodeError as e:
            raise ValueError('Invalid CSV/JSON log data.') from e

    if isinstance(parsed, dict):
        for key in _WRAPPER_KEYS:
            if isinstance(parsed.get(key), list):
                parsed = parsed[key]
                break
        else:
            raise ValueError(
                'JSON object must contain a list under one of: '
                + ', '.join(_WRAPPER_KEYS)
                + ' — or be a top-level array of log records.'
            )

    if not isinstance(parsed, list) or not parsed:
        raise ValueError('Provide 1–200,000 log records.')
    if len(parsed) > 200000:
        raise ValueError('Provide 1–200,000 log records.')
    if not all(isinstance(r, dict) for r in parsed):
        raise ValueError('Each log record must be a JSON object.')
    return [_normalize_row(r) for r in parsed]


def allowed_upload_name(name: str) -> bool:
    logical = strip_compression_suffix(name or '').lower()
    return Path(logical).suffix in {'.csv', '.json', '.jsonl'}
