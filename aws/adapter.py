"""Explicit AWS integration boundary. The web demo never creates this adapter."""
import hashlib

class AWSAdapter:
    def __init__(self,raw_bucket,optimized_bucket,glue_job,athena_workgroup,session=None):
        if session is None:
            import boto3
            session=boto3.Session()
        self.s3=session.client('s3');self.glue=session.client('glue');self.athena=session.client('athena')
        self.raw_bucket=raw_bucket;self.optimized_bucket=optimized_bucket
        self.glue_job=glue_job;self.athena_workgroup=athena_workgroup

    def plan_event(self,event):
        detail=event['detail'];bucket=detail['bucket']['name'];obj=detail['object'];key=obj['key']
        if bucket!=self.raw_bucket or not key.startswith('raw/') or not key.lower().endswith(('.csv','.json')):
            raise ValueError('Event outside allowed raw log boundary')
        version=obj.get('version-id')
        if not version:raise ValueError('Versioned raw objects required')
        token=hashlib.sha256(f'{bucket}/{key}/{version}'.encode()).hexdigest()
        return dict(input_bucket=bucket,input_key=key,input_version=version,output_bucket=self.optimized_bucket,output_prefix=f'optimized/{token}/',idempotency_key=token)

    def start_transform(self,plan):
        """Call only after a durable conditional claim of the idempotency key."""
        return self.glue.start_job_run(JobName=self.glue_job,Arguments={
            '--input_bucket':plan['input_bucket'],'--input_key':plan['input_key'],
            '--input_version':plan['input_version'],'--output_bucket':plan['output_bucket'],
            '--output_prefix':plan['output_prefix']})

    def query_statistics(self,execution_id):
        result=self.athena.get_query_execution(QueryExecutionId=execution_id)['QueryExecution']
        return dict(status=result['Status']['State'],bytes_scanned=result.get('Statistics',{}).get('DataScannedInBytes',0))

    def archive(self,*args,**kwargs):
        raise NotImplementedError('AWS archive disabled: integrate authenticated durable approvals and retention checks first.')
