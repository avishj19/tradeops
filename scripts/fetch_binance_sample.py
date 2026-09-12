"""Download one fixed public sample and verify the publisher SHA-256."""
import hashlib, io, json, urllib.request, zipfile, ssl
import certifi
from pathlib import Path
BASE='https://data.binance.vision/data/spot/daily/trades/BTCUSDT/BTCUSDT-trades-2017-08-17.zip'
def fetch(url,limit):
    with urllib.request.urlopen(url,timeout=30,context=ssl.create_default_context(cafile=certifi.where())) as r:
        b=r.read(limit+1)
    if len(b)>limit:raise ValueError('Sample exceeds download limit')
    return b
if __name__=='__main__':
    data=fetch(BASE,20*1024*1024)
    expected=fetch(BASE+'.CHECKSUM',4096).decode().split()[0]
    actual=hashlib.sha256(data).hexdigest()
    if actual!=expected:raise ValueError('Publisher checksum mismatch')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        member=z.infolist()[0]
        if len(z.infolist())!=1 or member.file_size>20*1024*1024:raise ValueError('Unexpected archive')
        raw=z.read(member)
    root=Path(__file__).resolve().parents[1]/'samples'
    root.mkdir(exist_ok=True)
    (root/'BTCUSDT-trades-2017-08-17.csv').write_bytes(raw)
    (root/'binance-provenance.json').write_text(json.dumps(dict(source=BASE,archive_sha256=actual,checksum_verified=True,raw_sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),rows=len(raw.splitlines())),indent=2))
    print((root/'binance-provenance.json').read_text())
