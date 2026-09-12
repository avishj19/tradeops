"""AWS-shaped artifact mirror and live boto3 adapter for the agent workflow.

TradeOps targets AWS-native firms: the same agent pipeline always emits the
S3 / EventBridge / Glue / Athena contract. Without cloud credentials it mirrors
that contract on local disk so demos stay isomorphic to production.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_ENV = ('TRADEOPS_AWS_RAW_BUCKET', 'TRADEOPS_AWS_OPTIMIZED_BUCKET', 'TRADEOPS_AWS_GLUE_JOB')


def aws_config_from_env(environ=None):
    env = environ or os.environ
    raw = (env.get('TRADEOPS_AWS_RAW_BUCKET') or '').strip()
    optimized = (env.get('TRADEOPS_AWS_OPTIMIZED_BUCKET') or '').strip()
    glue = (env.get('TRADEOPS_AWS_GLUE_JOB') or '').strip()
    workgroup = (env.get('TRADEOPS_AWS_ATHENA_WORKGROUP') or 'tradeops').strip()
    region = (env.get('AWS_REGION') or env.get('AWS_DEFAULT_REGION') or 'us-east-1').strip()
    event_bus = (env.get('TRADEOPS_AWS_EVENT_BUS') or 'default').strip()
    enabled = bool(raw and optimized and glue) and env.get('TRADEOPS_AWS_LIVE', '').strip().lower() in {'1', 'true', 'yes'}
    return dict(
        live=enabled,
        raw_bucket=raw or 'tradeops-raw-local',
        optimized_bucket=optimized or 'tradeops-optimized-local',
        glue_job=glue or 'tradeops-transform',
        athena_workgroup=workgroup,
        region=region,
        event_bus=event_bus,
    )


class AWSAdapter:
    """Explicit AWS API boundary used by the embedded agent workflow."""

    def __init__(self, raw_bucket, optimized_bucket, glue_job, athena_workgroup, session=None, event_bus='default', region='us-east-1'):
        if session is None:
            import boto3
            session = boto3.Session(region_name=region)
        self.s3 = session.client('s3')
        self.glue = session.client('glue')
        self.athena = session.client('athena')
        self.events = session.client('events')
        self.raw_bucket = raw_bucket
        self.optimized_bucket = optimized_bucket
        self.glue_job = glue_job
        self.athena_workgroup = athena_workgroup
        self.event_bus = event_bus
        self.region = region
        self.mode = 'live'

    def plan_event(self, event):
        detail = event['detail']
        bucket = detail['bucket']['name']
        obj = detail['object']
        key = obj['key']
        if bucket != self.raw_bucket or not key.startswith('raw/') or not key.lower().endswith(('.csv', '.json')):
            raise ValueError('Event outside allowed raw log boundary')
        version = obj.get('version-id')
        if not version:
            raise ValueError('Versioned raw objects required')
        token = hashlib.sha256(f'{bucket}/{key}/{version}'.encode()).hexdigest()
        return dict(
            input_bucket=bucket,
            input_key=key,
            input_version=version,
            output_bucket=self.optimized_bucket,
            output_prefix=f'optimized/{token}/',
            idempotency_key=token,
            glue_job=self.glue_job,
            athena_workgroup=self.athena_workgroup,
        )

    def start_transform(self, plan):
        """Call only after a durable conditional claim of the idempotency key."""
        return self.glue.start_job_run(JobName=self.glue_job, Arguments={
            '--input_bucket': plan['input_bucket'], '--input_key': plan['input_key'],
            '--input_version': plan['input_version'], '--output_bucket': plan['output_bucket'],
            '--output_prefix': plan['output_prefix'],
        })

    def query_statistics(self, execution_id):
        result = self.athena.get_query_execution(QueryExecutionId=execution_id)['QueryExecution']
        return dict(status=result['Status']['State'], bytes_scanned=result.get('Statistics', {}).get('DataScannedInBytes', 0))

    def put_bytes(self, bucket, key, body, content_type='application/octet-stream', metadata=None):
        args = dict(Bucket=bucket, Key=key, Body=body, ContentType=content_type)
        if metadata:
            args['Metadata'] = {str(k): str(v) for k, v in metadata.items()}
        return self.s3.put_object(**args)

    def put_file(self, bucket, key, path, content_type='application/octet-stream'):
        extra = {'ContentType': content_type}
        return self.s3.upload_file(str(path), bucket, key, ExtraArgs=extra)

    def emit_event(self, detail_type, detail, source='tradeops.agents'):
        entry = dict(
            Source=source,
            DetailType=detail_type,
            Detail=json.dumps(detail),
            EventBusName=self.event_bus,
        )
        return self.events.put_events(Entries=[entry])

    def start_athena_query(self, sql, database='tradeops', output_prefix=None):
        out = output_prefix or f's3://{self.optimized_bucket}/athena-results/'
        return self.athena.start_query_execution(
            QueryString=sql,
            QueryExecutionContext={'Database': database},
            ResultConfiguration={'OutputLocation': out},
            WorkGroup=self.athena_workgroup,
        )

    def archive(self, *args, **kwargs):
        raise NotImplementedError('AWS archive disabled: integrate authenticated durable approvals and retention checks first.')


class LocalAWSMirror:
    """Filesystem mirror of the AWS contract used when live credentials are off."""

    def __init__(self, root: Path, config: dict):
        self.root = Path(root)
        self.config = config
        self.mode = 'embedded_local'
        self.raw_bucket = config['raw_bucket']
        self.optimized_bucket = config['optimized_bucket']
        self.glue_job = config['glue_job']
        self.athena_workgroup = config['athena_workgroup']
        self.event_bus = config['event_bus']
        self.region = config['region']
        (self.root / 's3' / self.raw_bucket).mkdir(parents=True, exist_ok=True)
        (self.root / 's3' / self.optimized_bucket).mkdir(parents=True, exist_ok=True)
        (self.root / 'events').mkdir(parents=True, exist_ok=True)
        (self.root / 'glue').mkdir(parents=True, exist_ok=True)
        (self.root / 'athena').mkdir(parents=True, exist_ok=True)

    def _object_path(self, bucket, key):
        path = self.root / 's3' / bucket / key
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def plan_event(self, event):
        return AWSAdapter.plan_event(self, event)

    def start_transform(self, plan):
        run_id = plan['idempotency_key'][:16]
        payload = dict(job_name=self.glue_job, plan=plan, status='SUBMITTED', job_run_id=f'local-{run_id}')
        (self.root / 'glue' / f'{payload["job_run_id"]}.json').write_text(json.dumps(payload, indent=2))
        return {'JobRunId': payload['job_run_id']}

    def put_bytes(self, bucket, key, body, content_type='application/octet-stream', metadata=None):
        path = self._object_path(bucket, key)
        data = body if isinstance(body, (bytes, bytearray)) else str(body).encode()
        path.write_bytes(data)
        meta = dict(content_type=content_type, metadata=metadata or {}, bytes=len(data))
        path.with_suffix(path.suffix + '.meta.json').write_text(json.dumps(meta))
        return dict(ETag=hashlib.sha256(data).hexdigest(), VersionId='local-v1')

    def put_file(self, bucket, key, path, content_type='application/octet-stream'):
        return self.put_bytes(bucket, key, Path(path).read_bytes(), content_type=content_type)

    def emit_event(self, detail_type, detail, source='tradeops.agents'):
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        entry = dict(Source=source, DetailType=detail_type, Detail=detail, EventBusName=self.event_bus, Time=stamp, Region=self.region)
        (self.root / 'events' / f'{stamp}-{detail_type.replace(" ", "_")}.json').write_text(json.dumps(entry, indent=2))
        return dict(FailedEntryCount=0, Entries=[{'EventId': hashlib.sha256(stamp.encode()).hexdigest()[:16]}])

    def start_athena_query(self, sql, database='tradeops', output_prefix=None):
        qid = hashlib.sha256(sql.encode()).hexdigest()[:16]
        payload = dict(query_execution_id=qid, sql=sql, database=database, workgroup=self.athena_workgroup, output=output_prefix or f's3://{self.optimized_bucket}/athena-results/')
        (self.root / 'athena' / f'{qid}.json').write_text(json.dumps(payload, indent=2))
        return {'QueryExecutionId': qid}

    def query_statistics(self, execution_id):
        path = self.root / 'athena' / f'{execution_id}.json'
        if not path.exists():
            return dict(status='FAILED', bytes_scanned=0)
        return dict(status='SUCCEEDED', bytes_scanned=0)

    def archive(self, *args, **kwargs):
        raise NotImplementedError('AWS archive disabled: integrate authenticated durable approvals and retention checks first.')


def get_aws_backend(data_root: Path, environ=None, session=None):
    config = aws_config_from_env(environ)
    mirror_root = Path(data_root) / 'aws-mirror'
    if config['live']:
        adapter = AWSAdapter(
            config['raw_bucket'], config['optimized_bucket'], config['glue_job'],
            config['athena_workgroup'], session=session, event_bus=config['event_bus'], region=config['region'],
        )
        return adapter, config
    return LocalAWSMirror(mirror_root, config), config


def embed_run_in_aws(run_id, raw_bytes, raw_name, parquet_path, report, data_root, environ=None, session=None):
    """Stage agent outputs onto the AWS contract and emit a run-completed event."""
    backend, config = get_aws_backend(data_root, environ=environ, session=session)
    suffix = Path(raw_name).suffix.lower() or '.json'
    if suffix not in {'.csv', '.json'}:
        suffix = '.json'
    version = hashlib.sha256(raw_bytes).hexdigest()[:16]
    raw_key = f'raw/{run_id}/logs{suffix}'
    out_prefix = f'optimized/{run_id}/'
    backend.put_bytes(
        config['raw_bucket'], raw_key, raw_bytes,
        content_type='text/csv' if suffix == '.csv' else 'application/json',
        metadata={'tradeops-run-id': run_id, 'version': version},
    )
    parquet_key = out_prefix + 'logs.parquet'
    report_key = out_prefix + 'report.json'
    if parquet_path and Path(parquet_path).exists():
        backend.put_file(config['optimized_bucket'], parquet_key, parquet_path, content_type='application/octet-stream')
    backend.put_bytes(
        config['optimized_bucket'], report_key, json.dumps(report).encode(),
        content_type='application/json', metadata={'tradeops-run-id': run_id},
    )
    ingest_event = {
        'detail': {
            'bucket': {'name': config['raw_bucket']},
            'object': {'key': raw_key, 'version-id': version, 'size': len(raw_bytes)},
        }
    }
    plan = backend.plan_event(ingest_event)
    sql = (report.get('query') or {}).get('sql') or "SELECT 1"
    athena = backend.start_athena_query(sql)
    event_result = backend.emit_event('TradeOps Run Completed', dict(
        run_id=run_id,
        mode=backend.mode,
        region=config['region'],
        raw={'bucket': config['raw_bucket'], 'key': raw_key, 'version': version},
        optimized={'bucket': config['optimized_bucket'], 'prefix': out_prefix, 'parquet_key': parquet_key, 'report_key': report_key},
        glue_job=config['glue_job'],
        athena_workgroup=config['athena_workgroup'],
        athena_query_execution_id=athena.get('QueryExecutionId'),
        plan=plan,
        asset_classes=(report.get('analysis') or {}).get('asset_classes'),
    ))
    return dict(
        embedded=True,
        mode=backend.mode,
        cloud='aws',
        region=config['region'],
        live=config['live'],
        raw_uri=f"s3://{config['raw_bucket']}/{raw_key}",
        optimized_uri=f"s3://{config['optimized_bucket']}/{out_prefix}",
        parquet_uri=f"s3://{config['optimized_bucket']}/{parquet_key}",
        report_uri=f"s3://{config['optimized_bucket']}/{report_key}",
        event_bus=config['event_bus'],
        glue_job=config['glue_job'],
        athena_workgroup=config['athena_workgroup'],
        athena_query_execution_id=athena.get('QueryExecutionId'),
        plan=plan,
        event_result={'failed': event_result.get('FailedEntryCount', 0)},
        services=['s3', 'events', 'glue', 'athena'],
        note='Agent outputs follow the AWS S3→EventBridge→Glue→Athena contract. Live mode requires TRADEOPS_AWS_LIVE=1 and bucket/job env vars; otherwise a local aws-mirror is used so the workflow stays identical.',
    )
