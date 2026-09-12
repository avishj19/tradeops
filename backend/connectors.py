"""Read-only ingestion CLI. Single process per local workspace; no source mutations."""
import argparse, csv, fcntl, hashlib, io, json, os, time
from pathlib import Path
from datetime import datetime, timezone
import pyarrow as pa
import pyarrow.parquet as pq
from . import app as application
from .agents import SupervisorAgent
from .datasets import optimize_market
LIMIT=20*1024*1024

def digest(value):return hashlib.sha256(value).hexdigest()
def bounded(stream):
    data=stream.read(LIMIT+1)
    if len(data)>LIMIT:raise ValueError('Input exceeds 20 MiB; rotate/batch smaller files.')
    return data

def records(data,fmt,delimiter=None):
    from .datasets import unpack,sniff_reader
    data=unpack(data,'')  # transparent gz/lz4 by magic; zip needs a name so stays dataset-only
    text=data.decode('utf-8-sig')
    if fmt=='json':rows=json.loads(text)
    elif fmt in ('csv','tsv'):
        if delimiter:rows=list(csv.DictReader(io.StringIO(text),delimiter=delimiter))
        elif fmt=='tsv':rows=list(csv.DictReader(io.StringIO(text),delimiter='\t'))
        else:
            reader,d=sniff_reader(text);rows=list(reader)
            if rows and len(rows[0])==1 and ('\t' in next(iter(rows[0])) or ';' in next(iter(rows[0]))):raise ValueError('CSV parsed to a single column; the file looks delimited by something other than a comma. Set "delimiter" or format "tsv".')
    elif fmt=='jsonl':rows=[json.loads(x) for x in text.splitlines() if x.strip()]
    elif fmt=='text':rows=[{'message':line} for line in text.splitlines()]
    else:raise ValueError('format must be csv, tsv, json, jsonl or text')
    if not isinstance(rows,list) or not rows or len(rows)>200000 or any(not isinstance(r,dict) for r in rows):raise ValueError('Expected 1–200,000 record objects.')
    return rows

class Runner:
    def __init__(self,config,root=None,session=None):
        self.config=config;self.root=Path(root or application.DATA);self.root.mkdir(parents=True,exist_ok=True)
        from . import store
        # Connectors share the desk DB with the API (WAL + busy_timeout).
        desk=config.get('desk') or os.getenv('TRADEOPS_DESK') or 'default'
        self.desk=store.normalize_desk(desk)
        self.db=store.connect(store.db_path(self.root,self.desk))
        identity={k:config[k] for k in ('type','bucket','prefix','keys','path','pattern','dataset','format','mapping','log_group','filter_pattern','recursive','delimiter','desk') if k in config}
        self.namespace=digest(json.dumps(identity,sort_keys=True).encode())
        self.session=session
        if config['type'] not in ('folder','s3','cloudwatch'):raise ValueError('Unknown connector type')
        self.failures=[]
    def state(self,key,default=None):
        r=self.db.execute('SELECT value FROM connector_state WHERE key=?',(self.namespace+':'+key,)).fetchone()
        return json.loads(r[0]) if r else default
    def put(self,key,value):self.db.execute('INSERT OR REPLACE INTO connector_state VALUES (?,?)',(self.namespace+':'+key,json.dumps(value)))
    def client(self,name):
        if self.session is None:
            import boto3
            from botocore.config import Config
            self.session=boto3.Session(profile_name=self.config.get('profile'),region_name=self.config.get('region'))
        from botocore.config import Config
        from botocore import UNSIGNED
        options=dict(connect_timeout=10,read_timeout=30,retries={'mode':'standard','max_attempts':3})
        if self.config.get('anonymous'):options['signature_version']=UNSIGNED
        return self.session.client(name,config=Config(**options))
    def s3args(self):
        if not self.config.get('request_payer'):return {}
        if self.config.get('accept_requester_pays_charges') is not True:raise ValueError('request_payer is set but accept_requester_pays_charges is not true. Your AWS account will be billed for requests and transfer; set it explicitly to proceed.')
        if self.config.get('anonymous'):raise ValueError('Requester-pays buckets need signed requests; remove "anonymous".')
        return {'RequestPayer':'requester'}
    def ingest(self,data,identity,name,fmt=None):
        key=digest((self.namespace+identity+digest(data)).encode())
        if self.state(key):return False
        if not self.config.get('dataset') and not (fmt or self.config.get('format')):raise ValueError('Connector config needs either "dataset" (market data) or "format" (csv/tsv/json/jsonl/text).')
        try:return self._ingest(data,identity,name,fmt,key)
        except Exception:
            import shutil;shutil.rmtree(self.root/key,ignore_errors=True);raise
    def safe_ingest(self,data,identity,name,fmt=None):
        # Per-object isolation for scans: one bad file must not abort or wedge the prefix.
        try:return self.ingest(data,identity,name,fmt)
        except (ValueError,UnicodeDecodeError,KeyError,OSError) as e:
            self.failures.append({'source':identity,'name':name,'error':str(e)});return False
    def _ingest(self,data,identity,name,fmt,key):
        rows=None if self.config.get('dataset') else records(data,fmt or self.config['format'],self.config.get('delimiter'))
        mapping=self.config.get('mapping',{})
        folder=self.root/key;folder.mkdir(exist_ok=True)
        if self.config.get('dataset'):
            symbol=self.config.get('symbol','')
            if self.config['dataset'].startswith('binance') and not symbol:
                import re;m=re.match(r'^([A-Za-z0-9_]+)-(?:agg)?[Tt]rades-',name)
                if not m:raise ValueError('Cannot derive symbol from '+name+'; set "symbol" in the config.')
                symbol=m.group(1)
            result=optimize_market(data,name,self.config['dataset'],folder/'optimized',symbol)
        elif mapping:
            normalized=[]
            for row in rows:
                mapped={}
                for dest,src in mapping.items():
                    value=row
                    for part in src.split('.'):
                        if not isinstance(value,dict) or part not in value:raise ValueError('Missing mapped field: '+src)
                        value=value[part]
                    mapped[dest]=value
                mapped['source_record']=json.dumps(row,sort_keys=True,separators=(',',':'))
                normalized.append(mapped)
            result=SupervisorAgent().run(json.dumps(normalized).encode(),'mapped.json',folder/'optimized')
            result['input_bytes']=len(data)
            result['measurement_note']='Optimization sizes compare normalized JSON to Parquet; input_bytes records original source size.'
            # Copies are never eligible to archive the external source.
            result['storage']={'eligible':False,'age_days':0,'recommendation':'External source is read-only. Source retention stays in your existing system.'}
            result['approval']='not_required'
        else:
            table=pa.Table.from_pylist([{'source_record':json.dumps(r,sort_keys=True,separators=(',',':'))} for r in rows])
            out=folder/'optimized';out.mkdir(exist_ok=True);path=out/'logs.parquet'
            pq.write_table(table,path,compression='zstd')
            if not pq.read_table(path).equals(table):raise ValueError('Parquet verification failed')
            size=path.stat().st_size
            result=dict(kind='external_logs',rows=len(rows),before_bytes=len(data),after_bytes=size,reduction_pct=round(100*(1-size/len(data)),1),approval='not_required',incidents=[],events=[],message='Original records preserved. No operational fields inferred. Add field mapping to enable latency/error analysis.')
        (folder/'raw.source').write_bytes(data)
        run=dict(**result,id=key,name=name,scenario='connector:'+self.config['type'],created=datetime.now(timezone.utc).isoformat(),connector={'type':self.config['type'],'identity':identity,'input_sha256':digest(data)})
        from . import store
        with store.path_lock(store.db_path(self.root,self.desk)):
            with self.db:
                summary=store.summarize_run(run)
                self.db.execute(
                    'INSERT OR REPLACE INTO runs(id, created, summary, payload) VALUES (?,?,?,?)',
                    (key, run.get('created'), json.dumps(summary), json.dumps(run)),
                )
                self.put(key,True)
        return True
    def folder(self):
        root=Path(self.config['path']).resolve(strict=True)
        if not root.is_dir():raise ValueError('Folder path must be a directory')
        imported=0
        # Nonrecursive by design. Read closed/rotated files, not active tails.
        pattern=self.config.get('pattern','*.jsonl');recursive=bool(self.config.get('recursive'))
        for p in sorted(root.rglob(pattern) if recursive else root.glob(pattern)):
            if p.is_symlink() or not p.is_file():continue
            if not recursive and p.resolve().parent!=root:continue
            if recursive and root not in p.resolve().parents:continue
            st=p.stat()
            if time.time()-st.st_mtime<self.config.get('settle_seconds',60):continue
            with p.open('rb') as f:data=bounded(f)
            after=p.stat()
            if (st.st_size,st.st_mtime_ns,st.st_ino)!=(after.st_size,after.st_mtime_ns,after.st_ino):continue
            imported+=self.safe_ingest(data,str(p),p.name)
        return imported
    def discover(self):
        if self.config.get('blocked_reason'):raise ValueError(self.config['blocked_reason'])
        client=self.client('s3');bucket=self.config['bucket'];prefix=self.config['prefix']
        if not prefix:raise ValueError('A nonempty S3 prefix is required')
        keys=self.config.get('keys')
        if keys:
            for key in keys:
                if not key.startswith(prefix):raise ValueError('Selected key outside configured prefix')
                r=client.head_object(Bucket=bucket,Key=key,**self.s3args())
                yield {'Key':key,'Size':r['ContentLength'],'ETag':r['ETag']}
            return
        args=dict(Bucket=bucket,Prefix=prefix,**self.s3args(),PaginationConfig={'PageSize':100,'MaxItems':min(1000,int(self.config.get('max_listed',100)))})
        if self.config.get('start_after'):args['StartAfter']=self.config['start_after']
        for page in client.get_paginator('list_objects_v2').paginate(**args):
            yield from page.get('Contents',[])
    def s3(self):
        client=self.client('s3');bucket=self.config['bucket'];imported=0;downloaded=0
        for obj in self.discover():
            key=obj['Key']
            if key.endswith('/') or not key.endswith(self.config.get('suffix','.jsonl')):continue
            if obj['Size']>LIMIT:continue
            marker='s3:'+key+':'+obj['ETag']
            if self.state(marker):continue
            if downloaded>=int(self.config.get('max_objects',3)):break
            r=client.get_object(Bucket=bucket,Key=key,IfMatch=obj['ETag'],**self.s3args())
            try:data=bounded(r['Body'])
            finally:r['Body'].close()
            downloaded+=1
            if self.config.get('checksum'):
                check=client.get_object(Bucket=bucket,Key=key+'.CHECKSUM',**self.s3args())
                try:expected=check['Body'].read(4096).decode().split()[0]
                finally:check['Body'].close()
                if digest(data)!=expected:raise ValueError('Publisher checksum mismatch: '+key)
            imported+=self.safe_ingest(data,'s3://'+bucket+'/'+key+':'+r.get('VersionId',obj['ETag']),Path(key).name)
            with self.db:self.put(marker,True)  # marked even on parse failure; a new ETag or config identity will retry
        return imported
    def cloudwatch(self):
        client=self.client('logs');group=self.config['log_group']
        start=int(self.config['start_ms'])
        # Replay overlap handles ordinary late delivery; arbitrarily late events require backfill.
        start=max(start,self.state('watermark',start)-int(self.config.get('overlap_ms',300000)))
        end=int(time.time()*1000)-int(self.config.get('lag_ms',60000))
        if start>=end:return 0
        args=dict(logGroupName=group,startTime=start,endTime=end,limit=1000)
        if self.config.get('filter_pattern'):args['filterPattern']=self.config['filter_pattern']
        imported=0;seen_tokens=set()
        while True:
            page=client.filter_log_events(**args)
            for event in page.get('events',[]):
                identity='cw:'+group+':'+event['eventId']
                if self.state(identity):continue
                # Preserve envelope and message; mappings can reference parsed_message fields.
                row=dict(event)
                try:row['parsed_message']=json.loads(event['message'])
                except json.JSONDecodeError:pass
                imported+=self.ingest(json.dumps([row]).encode(),identity,'cloudwatch-event.json','json')
                with self.db:self.put(identity,True)
            token=page.get('nextToken')
            if not token:break
            if token in seen_tokens:raise ValueError('Repeated pagination token; watermark unchanged')
            seen_tokens.add(token);args['nextToken']=token
        with self.db:self.put('watermark',end)
        return imported
    def run(self):return getattr(self,self.config['type'])()
    def close(self):self.db.close()

def main():
    p=argparse.ArgumentParser(description='Read-only TradeOps connector')
    p.add_argument('--config',required=True);p.add_argument('--list',action='store_true',help='List bounded S3 candidates without downloading');p.add_argument('--interval',type=int,default=0,help='Repeat interval seconds, 0 for one scan; minimum 60')
    args=p.parse_args()
    if args.interval and args.interval<60:p.error('interval must be at least 60 seconds')
    config=json.loads(Path(args.config).read_text())
    application.DATA.mkdir(parents=True,exist_ok=True)
    import sys
    with (application.DATA/'connector.lock').open('a') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:sys.exit('Another connector process holds the lock; stop it first.')
        try:runner=Runner(config)
        except (ValueError,KeyError) as e:sys.exit('Config error: '+str(e))
        try:
            while True:
                if args.list:
                    print(json.dumps(list(runner.discover()),default=str,indent=2));break
                n=runner.run();out={'imported':n,'failed':len(runner.failures),'source':config['type']}
                if runner.failures:out['failures']=runner.failures
                print(json.dumps(out),flush=True);runner.failures.clear()
                if not args.interval:break
                time.sleep(args.interval)
        except Exception as e:
            import botocore.exceptions as be
            if isinstance(e,be.ClientError):
                code=e.response.get('Error',{}).get('Code','')
                hint={'403':' (AccessDenied: for requester-pays buckets set request_payer and accept_requester_pays_charges with signed credentials)','AccessDenied':' (AccessDenied: for requester-pays buckets set request_payer and accept_requester_pays_charges with signed credentials)','NoSuchBucket':' (bucket not found)','PreconditionFailed':' (object changed after listing; rescan)'}.get(code,'')
                sys.exit(f'S3 error {code}{hint}: {e}')
            sys.exit(f'{type(e).__name__}: {e}')
        finally:runner.close()
if __name__=='__main__':main()
