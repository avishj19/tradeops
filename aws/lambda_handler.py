"""EventBridge Lambda planning entrypoint. Does not submit jobs automatically."""
import os
from .adapter import AWSAdapter

def handler(event,context):
    adapter=AWSAdapter(os.environ['RAW_BUCKET'],os.environ['OPTIMIZED_BUCKET'],os.environ['GLUE_JOB'],os.environ.get('ATHENA_WORKGROUP','tradeops'))
    return {'status':'planned','plan':adapter.plan_event(event),'next_step':'Persist and claim idempotency key, then submit Glue transform.'}
