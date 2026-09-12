"""Bounded Glue Python Shell example. Package backend/ and install pyarrow.
Inputs above 20 MiB require a distributed Spark job instead.
"""
import sys, tempfile, json
from pathlib import Path
import boto3
from awsglue.utils import getResolvedOptions
from backend.agents import SupervisorAgent

def main():
    args=getResolvedOptions(sys.argv,['input_bucket','input_key','input_version','output_bucket','output_prefix'])
    s3=boto3.client('s3')
    obj=s3.get_object(Bucket=args['input_bucket'],Key=args['input_key'],VersionId=args['input_version'])
    if obj['ContentLength']>20*1024*1024:raise ValueError('Input exceeds bounded worker size')
    data=obj['Body'].read(20*1024*1024+1)
    with tempfile.TemporaryDirectory() as tmp:
        folder=Path(tmp);result=SupervisorAgent().run(data,args['input_key'],folder)
        prefix=args['output_prefix']
        s3.upload_file(str(folder/'logs.parquet'),args['output_bucket'],prefix+'logs.parquet')
        s3.put_object(Bucket=args['output_bucket'],Key=prefix+'report.json',Body=json.dumps(result).encode(),ContentType='application/json')
if __name__=='__main__':main()
