#!/usr/bin/env python3
"""Benchmark TradeOps help for 100+ AWS-primary target firms.

Target niches match the product focus in aws/PRIVATE_DEPLOYMENT.md and the
Private AWS plan UI: boutique trading firms, specialist fintech SaaS, and
specialist brokers. Each firm is modeled as running primarily on AWS
(S3 raw logs + CloudWatch application logs), not as a generic public equity.

Outputs machine-readable results under benchmarks/ and a summary markdown path
passed via --summary.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import random
import statistics
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.agents import SupervisorAgent  # noqa: E402
from backend.planning import NetworkPlan, network_plan  # noqa: E402
from aws.adapter import AWSAdapter  # noqa: E402

# Execution symbols these specialist firms trade or custody — not the firm itself.
SYMBOLS = [
    'AAPL', 'MSFT', 'NVDA', 'SPY', 'QQQ', 'IWM', 'TSLA', 'AMZN', 'META', 'GOOGL',
    'JPM', 'GS', 'XLF', 'GLD', 'TLT', 'EURUSD', 'BTCUSDT', 'ETHUSDT',
]

SCENARIOS = ('normal', 'duplicates', 'latency_spike', 'mixed_errors')

PREFIXES = {
    'boutique_trading': [
        'Apex', 'Northbridge', 'Harbor', 'Lattice', 'Meridian', 'Vector', 'Cascade',
        'Quorum', 'Signal', 'Ridge', 'Cobalt', 'Summit', 'Prairie', 'Kinetic',
        'Aurora', 'Falcon', 'Horizon', 'Nexus', 'Pulse', 'Sterling', 'Atlas',
        'Beacon', 'Cipher', 'Delta', 'Echo', 'Forge', 'Granite', 'Helix', 'Ion',
        'Jade', 'Keystone', 'Lumen', 'Monad', 'Noble', 'Orbit',
    ],
    'fintech_saas': [
        'Ledger', 'Clearpath', 'Routeline', 'Opsfolio', 'TradeNest', 'Auditly',
        'Reconcile', 'Flowkit', 'PostTrade', 'Risklane', 'OrderMesh', 'Fillbook',
        'CustodyIQ', 'MarginHub', 'TickForge', 'Bookstack', 'Wireframe', 'Clipstream',
        'Matchbox', 'SettleOS', 'Logyard', 'Vaultline', 'PrimeOps', 'Quota',
        'Stackfill', 'Relaybook', 'Nightwatch', 'Controlbay', 'Datapath', 'Fleetlog',
        'Portside', 'Shipshape', 'Tracebay', 'Unitops', 'Workbench',
    ],
    'specialist_broker': [
        'Harbor', 'Seaboard', 'Continental', 'Pacific', 'Midwest', 'Atlantic',
        'Crossborder', 'Institutional', 'Private', 'Prime', 'Agency', 'Desk',
        'Clearing', 'Execution', 'Access', 'Gateway', 'Market', 'Order',
        'Client', 'Wealth', 'Family', 'Boutique', 'Regional', 'Specialty',
        'Direct', 'Electron', 'Floor', 'Block', 'Dark', 'Lit', 'Smart',
        'Trusted', 'United', 'Vista', 'West',
    ],
}

SUFFIXES = {
    'boutique_trading': [
        'Capital', 'Trading', 'Markets', 'Securities', 'Partners', 'Strategies',
        'Execution', 'Liquidity', 'Quant', 'Desk',
    ],
    'fintech_saas': [
        'Labs', 'Systems', 'Platform', 'Software', 'Cloud', 'Data', 'Ops',
        'Analytics', 'Infrastructure', 'Services',
    ],
    'specialist_broker': [
        'Brokerage', 'Securities', 'Markets', 'Brokers', 'Trading', 'Agency',
        'Clearing', 'Access', 'Partners', 'Group',
    ],
}

AWS_REGIONS = ['us-east-1', 'us-east-2', 'us-west-2', 'eu-west-1', 'ap-northeast-1']


def build_catalogue(n: int = 120) -> list[dict]:
    """Deterministic catalogue of AWS-primary target firms (not public megacaps)."""
    firms = []
    niches = ['boutique_trading', 'fintech_saas', 'specialist_broker']
    counts = {k: 0 for k in niches}
    i = 0
    while len(firms) < n:
        niche = niches[i % 3]
        prefixes, suffixes = PREFIXES[niche], SUFFIXES[niche]
        name = f"{prefixes[counts[niche] % len(prefixes)]} {suffixes[(counts[niche] // len(prefixes)) % len(suffixes)]}"
        # Avoid accidental duplicates by appending a stable desk/tenant id.
        counts[niche] += 1
        slug = f"{niche[:3]}-{counts[niche]:03d}"
        display = f"{name} ({slug.upper()})"
        region = AWS_REGIONS[i % len(AWS_REGIONS)]
        scenario = SCENARIOS[i % len(SCENARIOS)]
        # Firm-size proxies: boutique smaller logs, SaaS multi-tenant medium, brokers denser.
        base_rows = {'boutique_trading': 1800, 'fintech_saas': 3200, 'specialist_broker': 4500}[niche]
        rows = base_rows + (i % 17) * 40
        budget = {'boutique_trading': 50, 'fintech_saas': 75, 'specialist_broker': 60}[niche]
        endpoints = {'boutique_trading': 2, 'fintech_saas': 3, 'specialist_broker': 2}[niche]
        allowance = {'boutique_trading': 15, 'fintech_saas': 25, 'specialist_broker': 20}[niche]
        az = 2 if niche != 'boutique_trading' or i % 5 else 1
        firms.append(dict(
            firm_id=slug,
            name=display,
            niche=niche,
            aws_primary=True,
            region=region,
            s3_bucket=f"to-{slug}-raw-logs",
            s3_prefix='raw/execution/',
            cloudwatch_group=f"/tradeops/{slug}/execution-gateway",
            scenario=scenario,
            row_count=rows,
            monthly_budget=budget,
            interface_endpoints=endpoints,
            service_allowance=allowance,
            availability_zones=az,
            cloud_stack='S3 raw + CloudWatch app logs + private VPC worker (planned)',
        ))
        i += 1
    return firms


def generate_firm_logs(firm: dict, seed: int) -> list[dict]:
    rng = random.Random(seed)
    scenario = firm['scenario']
    count = firm['row_count']
    base = datetime(2026, 6, 1, 13, 30, tzinfo=timezone.utc) - timedelta(days=100 + (seed % 20))
    source = {
        'boutique_trading': 'execution-gateway',
        'fintech_saas': 'tenant-execution-api',
        'specialist_broker': 'broker-oms-gateway',
    }[firm['niche']]
    strategies = {
        'boutique_trading': ['momentum', 'market-making', 'stat-arb'],
        'fintech_saas': ['customer-routing', 'smart-order', 'post-trade'],
        'specialist_broker': ['agency', 'riskless-principal', 'block'],
    }[firm['niche']]
    rows = []
    for i in range(count):
        late = scenario == 'latency_spike' and i > count * 0.78
        err = (scenario == 'mixed_errors' and i % 37 == 0) or (late and i % 4 == 0)
        dup_burst = scenario == 'duplicates' and i > count * 0.9
        status = 'ERROR' if err else ('REJECTED' if late and i % 11 == 0 else 'FILLED')
        latency = rng.uniform(350, 1400) if late else rng.uniform(4, 55)
        if dup_burst:
            latency = rng.uniform(8, 40)
            status = 'FILLED'
        row = dict(
            timestamp=(base + timedelta(seconds=i * 7 + rng.randint(0, 2))).isoformat().replace('+00:00', 'Z'),
            event_id=f"{firm['firm_id'].upper()}-{i:07d}",
            symbol=rng.choice(SYMBOLS),
            latency_ms=round(latency, 2),
            status=status,
            quantity=rng.randint(1, 800),
            price=round(rng.uniform(10, 900), 2),
            source=source,
            strategy=rng.choice(strategies),
            aws_region=firm['region'],
            cloudwatch_group=firm['cloudwatch_group'],
            s3_object=f"s3://{firm['s3_bucket']}/{firm['s3_prefix']}{firm['firm_id']}-{(base + timedelta(days=i // 500)).date()}.json",
        )
        rows.append(row)
    # Exact duplicate injection (normalized rows) — mirrors real redelivery noise.
    dup_rate = 0.12 if scenario == 'duplicates' else (0.05 if scenario == 'mixed_errors' else 0.03)
    rows += [dict(r) for r in rows[: max(1, int(count * dup_rate))]]
    return rows


def rows_to_bytes(rows: list[dict], fmt: str = 'json') -> bytes:
    if fmt == 'csv':
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
        return buf.getvalue().encode()
    return json.dumps(rows, separators=(',', ':')).encode()


class _NullClients:
    """AWSAdapter needs clients only for live Glue/Athena; plan_event is pure."""

    def client(self, _name):
        raise RuntimeError('Live AWS clients disabled in offline firm analysis')


def aws_ingest_plan(firm: dict) -> dict:
    adapter = AWSAdapter.__new__(AWSAdapter)
    adapter.s3 = adapter.glue = adapter.athena = None
    adapter.raw_bucket = firm['s3_bucket']
    adapter.optimized_bucket = f"to-{firm['firm_id']}-optimized"
    adapter.glue_job = f"tradeops-{firm['firm_id']}-transform"
    adapter.athena_workgroup = f"tradeops-{firm['firm_id']}"
    key = f"{firm['s3_prefix']}{firm['firm_id']}-batch.json"
    version = hashlib.sha256(f"{firm['firm_id']}:{key}".encode()).hexdigest()[:32]
    event = {'detail': {'bucket': {'name': firm['s3_bucket']}, 'object': {'key': key, 'version-id': version}}}
    plan = adapter.plan_event(event)
    return dict(plan, cloudwatch_group=firm['cloudwatch_group'], region=firm['region'], live_submit=False)


def help_score(result: dict, plan: dict) -> dict:
    a = result['analysis']
    cost = result['cost']
    seq = result['sequence_evidence']
    incidents = result['incidents']
    # Composite "how much we helped" — transparent weights summing to 1.0 (not a learned model).
    noise_removed = a['duplicates'] / max(a['rows'], 1)
    signal_found = a['anomalies'] / max(a['unique_rows'], 1)
    size_help = max(0.0, result['reduction_pct']) / 100.0
    archive_help = 1.0 if result['storage']['eligible'] else 0.35
    budget_help = 1.0 if plan['within_budget'] else 0.4
    incident_help = min(1.0, sum(i['count'] for i in incidents) / max(a['unique_rows'], 1) * 8)
    sequence_help = min(1.0, seq['candidate_count'] / 20.0)
    # Full credit thresholds: ≥10% exact dupes removed; ≥15% anomaly rate; Parquet size cut.
    score = 100.0 * (
        0.20 * min(1.0, noise_removed / 0.10)
        + 0.15 * min(1.0, signal_found / 0.15)
        + 0.25 * size_help
        + 0.10 * archive_help
        + 0.10 * budget_help
        + 0.12 * incident_help
        + 0.08 * sequence_help
    )
    return dict(
        help_score=round(min(100.0, score), 1),
        noise_removed_pct=round(noise_removed * 100, 2),
        anomalies_pct=round(signal_found * 100, 2),
        size_reduction_pct=result['reduction_pct'],
        archive_eligible=result['storage']['eligible'],
        aws_plan_within_budget=plan['within_budget'],
        incident_kinds=len(incidents),
        sequence_candidates=seq['candidate_count'],
        illustrative_monthly_delta_usd=round(cost['savings_monthly'], 6),
    )


def feedback_for(firm: dict, result: dict, plan: dict, help_metrics: dict) -> list[str]:
    a = result['analysis']
    notes = []
    notes.append(
        f"{firm['name']} ({firm['niche']}) ingests primarily from AWS "
        f"{firm['region']} via s3://{firm['s3_bucket']}/{firm['s3_prefix']} and {firm['cloudwatch_group']}."
    )
    notes.append(
        f"Log Analysis validated {a['rows']:,} gateway rows, removed {a['duplicates']:,} exact redelivery "
        f"duplicates ({help_metrics['noise_removed_pct']}%), and flagged {a['anomalies']:,} latency/error signals "
        f"({help_metrics['anomalies_pct']}% of unique rows)."
    )
    notes.append(
        f"Compression produced a verified Zstd Parquet analytical copy "
        f"({result['before_bytes']:,} → {result['after_bytes']:,} bytes, {result['reduction_pct']}% smaller) "
        f"while retaining the raw S3/CloudWatch evidence."
    )
    if result['storage']['eligible']:
        notes.append(
            'Storage Optimization marked cold raw objects archive-eligible (≥90 days, ≥128 KiB); '
            'human approval still required — AWS archive is intentionally disabled until durable approvals exist.'
        )
    else:
        notes.append(result['storage']['recommendation'])
    notes.append(result['query']['recommendation'])
    notes.append(
        f"Private AWS plan estimate ${plan['estimated_total']:.2f}/mo "
        f"({'within' if plan['within_budget'] else 'over'} ${firm['monthly_budget']} budget). {plan['recommendation']}"
    )
    for inc in result['incidents']:
        notes.append(f"Incident inbox: {inc['title']} ×{inc['count']} — {inc['recommendation']}")
    seq = result['sequence_evidence']
    notes.append(
        f"Sequence Evidence reviewed {seq['tested_cohorts']} cohorts and surfaced "
        f"{seq['candidate_count']} candidate motif changes (review-only; no causal claim)."
    )
    notes.append(
        f"Composite help score {help_metrics['help_score']}/100 for this AWS-primary specialist firm "
        f"(noise reduction, anomaly signal, size, archive gating, budget fit, incidents, sequences)."
    )
    return notes


def analyze_firm(firm: dict, work: Path) -> dict:
    seed = int(hashlib.sha256(firm['firm_id'].encode()).hexdigest()[:8], 16)
    rows = generate_firm_logs(firm, seed)
    payload = rows_to_bytes(rows, 'json')
    dest = work / firm['firm_id']
    dest.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    result = SupervisorAgent().run(payload, f"{firm['firm_id']}-execution-logs.json", dest / 'optimized')
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
    (dest / 'raw.json').write_bytes(payload)
    plan = network_plan(NetworkPlan(
        company=firm['niche'],
        monthly_budget=firm['monthly_budget'],
        availability_zones=firm['availability_zones'],
        interface_endpoints=firm['interface_endpoints'],
        service_allowance=firm['service_allowance'],
        endpoint_gb=12 if firm['niche'] == 'fintech_saas' else 8,
    ))
    ingest = aws_ingest_plan(firm)
    help_metrics = help_score(result, plan)
    feedback = feedback_for(firm, result, plan, help_metrics)
    return dict(
        firm=firm,
        elapsed_ms=elapsed_ms,
        analysis=result['analysis'],
        before_bytes=result['before_bytes'],
        after_bytes=result['after_bytes'],
        reduction_pct=result['reduction_pct'],
        storage=result['storage'],
        cost=result['cost'],
        query=result['query'],
        incidents=result['incidents'],
        sequence_evidence={
            'tested_cohorts': result['sequence_evidence']['tested_cohorts'],
            'candidate_count': result['sequence_evidence']['candidate_count'],
        },
        agent_events=result['events'],
        aws_network_plan=plan,
        aws_ingest_plan=ingest,
        help=help_metrics,
        detailed_feedback=feedback,
    )


def summarize(results: list[dict]) -> dict:
    helps = [r['help']['help_score'] for r in results]
    dups = [r['analysis']['duplicates'] for r in results]
    anoms = [r['analysis']['anomalies'] for r in results]
    reds = [r['reduction_pct'] for r in results]
    savings = [r['cost']['savings_monthly'] for r in results]
    by_niche = {}
    for r in results:
        niche = r['firm']['niche']
        by_niche.setdefault(niche, []).append(r)
    niche_summary = {}
    for niche, items in by_niche.items():
        niche_summary[niche] = dict(
            firms=len(items),
            mean_help_score=round(statistics.mean(x['help']['help_score'] for x in items), 2),
            median_help_score=round(statistics.median(x['help']['help_score'] for x in items), 2),
            total_duplicates_removed=sum(x['analysis']['duplicates'] for x in items),
            total_anomalies_flagged=sum(x['analysis']['anomalies'] for x in items),
            mean_size_reduction_pct=round(statistics.mean(x['reduction_pct'] for x in items), 2),
            archive_eligible_firms=sum(1 for x in items if x['storage']['eligible']),
            aws_within_budget=sum(1 for x in items if x['aws_network_plan']['within_budget']),
            mean_aws_monthly_usd=round(statistics.mean(x['aws_network_plan']['estimated_total'] for x in items), 2),
        )
    top = sorted(results, key=lambda r: r['help']['help_score'], reverse=True)[:10]
    bottom = sorted(results, key=lambda r: r['help']['help_score'])[:10]
    return dict(
        generated_at=datetime.now(timezone.utc).isoformat(),
        dataset_count=len(results),
        aws_primary_firms=sum(1 for r in results if r['firm']['aws_primary']),
        niches=sorted(by_niche),
        totals=dict(
            rows=sum(r['analysis']['rows'] for r in results),
            unique_rows=sum(r['analysis']['unique_rows'] for r in results),
            duplicates_removed=sum(dups),
            anomalies_flagged=sum(anoms),
            raw_bytes=sum(r['before_bytes'] for r in results),
            parquet_bytes=sum(r['after_bytes'] for r in results),
            mean_size_reduction_pct=round(statistics.mean(reds), 2),
            mean_help_score=round(statistics.mean(helps), 2),
            median_help_score=round(statistics.median(helps), 2),
            p10_help_score=round(sorted(helps)[max(0, math.ceil(len(helps) * 0.10) - 1)], 2),
            p90_help_score=round(sorted(helps)[min(len(helps) - 1, math.ceil(len(helps) * 0.90) - 1)], 2),
            illustrative_monthly_cost_delta_sum_usd=round(sum(savings), 4),
            archive_eligible=sum(1 for r in results if r['storage']['eligible']),
            aws_plans_within_budget=sum(1 for r in results if r['aws_network_plan']['within_budget']),
            mean_runtime_ms=round(statistics.mean(r['elapsed_ms'] for r in results), 2),
        ),
        by_niche=niche_summary,
        top_helped=[{'firm_id': r['firm']['firm_id'], 'name': r['firm']['name'], 'niche': r['firm']['niche'], 'help_score': r['help']['help_score'], 'feedback': r['detailed_feedback'][1]} for r in top],
        least_helped=[{'firm_id': r['firm']['firm_id'], 'name': r['firm']['name'], 'niche': r['firm']['niche'], 'help_score': r['help']['help_score'], 'feedback': r['detailed_feedback'][1]} for r in bottom],
        scope_notes=[
            'Firms are synthetic AWS-primary specialists in TradeOps target niches; they are not public megacap issuers.',
            'Live Glue/Athena/CloudWatch pulls were not executed; AWSAdapter.plan_event and network_plan provide the deployment boundary estimates.',
            'CostAgent figures are illustrative file-based rates with raw retained; not measured Athena bills.',
            'Help score is a transparent weighted composite for comparison across this corpus only.',
        ],
    )


def render_markdown(summary: dict, results: list[dict]) -> str:
    t = summary['totals']
    lines = [
        '# TradeOps help analysis: AWS-primary target firms',
        '',
        f"Generated: `{summary['generated_at']}`",
        '',
        '## Scope',
        '',
        f"- **{summary['dataset_count']} datasets** — one operational execution-log batch per firm.",
        '- **Target niches only:** boutique trading firms, specialist fintech SaaS, specialist brokers.',
        '- **Cloud posture:** every firm is modeled as **AWS-primary** (S3 raw evidence + CloudWatch gateway logs + private-VPC worker plan).',
        '- Not a survey of public equity issuers; symbols inside logs (AAPL, SPY, …) are traded instruments, not the customer firm.',
        '',
        '## How much TradeOps helped (corpus)',
        '',
        '| Metric | Value |',
        '|---|---:|',
        f"| Firms / datasets | {summary['dataset_count']} |",
        f"| Total log rows ingested | {t['rows']:,} |",
        f"| Exact duplicates removed from analytical copy | {t['duplicates_removed']:,} |",
        f"| Anomaly signals (latency / ERROR / REJECTED) | {t['anomalies_flagged']:,} |",
        f"| Raw bytes → Parquet bytes | {t['raw_bytes']:,} → {t['parquet_bytes']:,} |",
        f"| Mean analytical size reduction | {t['mean_size_reduction_pct']}% |",
        f"| Mean / median help score (0–100) | {t['mean_help_score']} / {t['median_help_score']} |",
        f"| Help score p10 / p90 | {t['p10_help_score']} / {t['p90_help_score']} |",
        f"| Archive-eligible firms (policy gate) | {t['archive_eligible']} |",
        f"| Private AWS plans within stated budget | {t['aws_plans_within_budget']} / {summary['dataset_count']} |",
        f"| Mean Supervisor runtime | {t['mean_runtime_ms']} ms |",
        f"| Sum of illustrative monthly cost deltas (raw retained) | ${t['illustrative_monthly_cost_delta_sum_usd']} |",
        '',
        '## By target niche',
        '',
        '| Niche | Firms | Mean help | Dupes removed | Anomalies | Mean size ↓ | Archive OK | AWS in budget | Mean AWS $/mo |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|',
    ]
    labels = {
        'boutique_trading': 'Boutique trading',
        'fintech_saas': 'Specialist fintech SaaS',
        'specialist_broker': 'Specialist broker',
    }
    for niche, s in summary['by_niche'].items():
        lines.append(
            f"| {labels.get(niche, niche)} | {s['firms']} | {s['mean_help_score']} | "
            f"{s['total_duplicates_removed']:,} | {s['total_anomalies_flagged']:,} | "
            f"{s['mean_size_reduction_pct']}% | {s['archive_eligible_firms']} | "
            f"{s['aws_within_budget']} | {s['mean_aws_monthly_usd']} |"
        )
    lines += [
        '',
        '## AWS deployment boundary (what was exercised)',
        '',
        '1. **Private AWS plan** (`POST /api/network-plan` / `network_plan`) per firm — S3 gateway, interface endpoints, budget headroom.',
        '2. **Ingest planner** (`AWSAdapter.plan_event`) — versioned `raw/` object → idempotent optimized prefix (no live Glue submit).',
        '3. **Local Supervisor pipeline** on each firm’s execution logs — the same agents the dashboard runs.',
        '',
        'Live AWS account provisioning was **not** performed in this run (no credentials / no destructive cloud writes).',
        '',
        '## Top helped firms',
        '',
    ]
    for row in summary['top_helped']:
        lines.append(f"- **{row['name']}** (`{row['niche']}`) — help {row['help_score']}: {row['feedback']}")
    lines += ['', '## Least helped firms', '']
    for row in summary['least_helped']:
        lines.append(f"- **{row['name']}** (`{row['niche']}`) — help {row['help_score']}: {row['feedback']}")
    lines += [
        '',
        '## Detailed per-firm feedback',
        '',
        'Each firm below includes agent outcomes and AWS plan notes.',
        '',
    ]
    for r in results:
        f = r['firm']
        lines.append(f"### {f['name']}")
        lines.append('')
        lines.append(
            f"- Niche: `{f['niche']}` · Region: `{f['region']}` · Scenario: `{f['scenario']}` · "
            f"Help score: **{r['help']['help_score']}** · Runtime: {r['elapsed_ms']} ms"
        )
        lines.append(f"- S3: `s3://{f['s3_bucket']}/{f['s3_prefix']}` · CW: `{f['cloudwatch_group']}`")
        lines.append(
            f"- Rows {r['analysis']['rows']:,} (unique {r['analysis']['unique_rows']:,}); "
            f"dupes {r['analysis']['duplicates']:,}; anomalies {r['analysis']['anomalies']:,}; "
            f"size {r['before_bytes']:,}→{r['after_bytes']:,} ({r['reduction_pct']}%)"
        )
        lines.append(
            f"- AWS plan ${r['aws_network_plan']['estimated_total']:.2f}/mo; "
            f"ingest idempotency `{r['aws_ingest_plan']['idempotency_key'][:16]}…`"
        )
        for note in r['detailed_feedback']:
            lines.append(f"  - {note}")
        lines.append('')
    lines += ['## Caveats', '']
    for note in summary['scope_notes']:
        lines.append(f'- {note}')
    lines.append('')
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--count', type=int, default=120)
    ap.add_argument('--out', type=Path, default=ROOT / 'benchmarks' / 'target-firm-aws-analysis.json')
    ap.add_argument('--summary-md', type=Path, default=ROOT / 'benchmarks' / 'TARGET_FIRM_AWS_ANALYSIS.md')
    ap.add_argument('--catalogue', type=Path, default=ROOT / 'benchmarks' / 'target-firm-catalogue.json')
    args = ap.parse_args()
    if args.count < 100:
        raise SystemExit('--count must be at least 100')

    firms = build_catalogue(args.count)
    args.catalogue.write_text(json.dumps(firms, indent=2))
    results = []
    with tempfile.TemporaryDirectory(prefix='tradeops-firm-') as tmp:
        work = Path(tmp)
        for i, firm in enumerate(firms, 1):
            results.append(analyze_firm(firm, work))
            if i % 20 == 0 or i == len(firms):
                print(f'analyzed {i}/{len(firms)}', flush=True)

    summary = summarize(results)
    payload = dict(summary=summary, results=results)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload))
    args.summary_md.write_text(render_markdown(summary, results))
    print(json.dumps({
        'datasets': summary['dataset_count'],
        'mean_help_score': summary['totals']['mean_help_score'],
        'duplicates_removed': summary['totals']['duplicates_removed'],
        'anomalies_flagged': summary['totals']['anomalies_flagged'],
        'out': str(args.out),
        'summary_md': str(args.summary_md),
    }, indent=2))


if __name__ == '__main__':
    main()
