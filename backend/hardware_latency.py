"""Workstation hardware-path latency: refresh rate + input timing (no keylogging)."""
from __future__ import annotations

import math
import statistics
from datetime import datetime, timezone


ALLOWED_KINDS = {'keydown', 'keyup', 'pointerdown', 'pointerup', 'frame', 'ack'}


def _finite(values):
    return [float(v) for v in values if v is not None and math.isfinite(float(v))]


def summarize_hardware_samples(samples, execution_latency_ms=None):
    """Aggregate opt-in desk-probe samples into platform metrics.

    Samples must not include key characters or free-text. Only timing + kind.
    """
    if not isinstance(samples, list) or not samples:
        raise ValueError('Provide at least one hardware latency sample.')
    if len(samples) > 20000:
        raise ValueError('Maximum 20,000 hardware samples per batch.')

    frames = []
    key_to_frame = []
    click_to_ack = []
    refresh_hz_reads = []
    kinds = {}

    for i, sample in enumerate(samples):
        if not isinstance(sample, dict):
            raise ValueError(f'Sample {i} must be an object.')
        kind = str(sample.get('kind', '')).lower()
        if kind not in ALLOWED_KINDS:
            raise ValueError(f'Sample {i} has unsupported kind.')
        # Privacy: reject any attempt to store key characters / codes.
        for banned in ('key', 'code', 'key_code', 'char', 'text', 'value'):
            if banned in sample and sample[banned] not in (None, '', False):
                raise ValueError('Hardware probe must not include key characters or codes.')
        kinds[kind] = kinds.get(kind, 0) + 1
        if kind == 'frame' and sample.get('frame_delta_ms') is not None:
            frames.append(float(sample['frame_delta_ms']))
        if sample.get('refresh_hz') is not None:
            refresh_hz_reads.append(float(sample['refresh_hz']))
        if sample.get('key_to_frame_ms') is not None:
            key_to_frame.append(float(sample['key_to_frame_ms']))
        if sample.get('click_to_ack_ms') is not None:
            click_to_ack.append(float(sample['click_to_ack_ms']))

    frames = _finite(frames)
    key_to_frame = _finite(key_to_frame)
    click_to_ack = _finite(click_to_ack)
    refresh_hz_reads = _finite(refresh_hz_reads)

    refresh_hz = statistics.median(refresh_hz_reads) if refresh_hz_reads else (
        (1000.0 / statistics.median(frames)) if frames else None
    )
    frame_budget_ms = (1000.0 / refresh_hz) if refresh_hz and refresh_hz > 0 else None
    frame_jitter_ms = statistics.pstdev(frames) if len(frames) >= 2 else 0.0

    def pct(vals, p):
        if not vals:
            return None
        ranked = sorted(vals)
        idx = min(len(ranked) - 1, max(0, math.ceil(len(ranked) * p) - 1))
        return round(ranked[idx], 3)

    summary = dict(
        kind='hardware_latency',
        measured_at=datetime.now(timezone.utc).isoformat(),
        samples=len(samples),
        kinds=kinds,
        refresh_hz=round(refresh_hz, 2) if refresh_hz else None,
        frame_budget_ms=round(frame_budget_ms, 3) if frame_budget_ms else None,
        frame_jitter_ms=round(frame_jitter_ms, 3),
        key_to_frame_ms=dict(
            count=len(key_to_frame),
            p50=pct(key_to_frame, .5),
            p95=pct(key_to_frame, .95),
            max=round(max(key_to_frame), 3) if key_to_frame else None,
        ),
        click_to_ack_ms=dict(
            count=len(click_to_ack),
            p50=pct(click_to_ack, .5),
            p95=pct(click_to_ack, .95),
            max=round(max(click_to_ack), 3) if click_to_ack else None,
        ),
        privacy='No key characters or codes are stored. Only event kind and timing fields are accepted.',
        scope='Workstation input→display path and local ack RTT. This complements exchange/gateway latency_ms; it does not replace it.',
    )

    if execution_latency_ms is not None:
        exec_vals = _finite(execution_latency_ms)
        if exec_vals and key_to_frame:
            # Rough composition: desk path vs gateway path share of observed total.
            desk = summary['key_to_frame_ms']['p50'] or 0
            gate = statistics.median(exec_vals)
            total = desk + gate
            summary['linked_execution'] = dict(
                gateway_latency_p50_ms=round(gate, 3),
                desk_key_to_frame_p50_ms=desk,
                combined_p50_ms=round(total, 3),
                desk_share_pct=round(100 * desk / total, 2) if total else None,
                note='Combined figure is illustrative: desk probe + log gateway latency_ms, not a single synchronized trade clock.',
            )
    return summary
