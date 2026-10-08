"""Anonymous public API client. Diagnostics never contain paths, queries, tokens or bodies."""
import json,time,threading,urllib.request,urllib.error
from urllib.parse import urlparse
from email.utils import parsedate_to_datetime
from datetime import datetime,timezone
OFFLINE=False
RECORDS=[];COOLDOWN={};LOCK=threading.Lock()
class ServicePaused(Exception):pass

def record(host,operation,status,seconds=0):
    with LOCK:
        RECORDS.append({'utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'host':host,'operation':operation,'status':str(status),'retry_seconds':round(seconds)})
        del RECORDS[:-1000]

def diagnostics():
    with LOCK:return list(RECORDS)

def request_json(url):
    if OFFLINE:raise RuntimeError("Offline mode: network access disabled.")
    u=urlparse(url);host=u.hostname or ''
    if u.scheme!='https':raise ValueError('HTTPS APIのみ対応します')
    operation='hash_lookup' if '/by-hash/' in u.path else 'repository_details' if host=='huggingface.co' and u.path.count('/')>2 else 'search' if u.query else 'model_details'
    remaining=COOLDOWN.get(host,0)-time.time()
    if remaining>0:
        record(host,operation,'一時停止中',remaining);raise ServicePaused(f'{host}: 一時停止中。約{int(remaining)+1}秒後に再調査してください')
    req=urllib.request.Request(url,headers={'User-Agent':'ModelLibraryOrganizer/1.2','Accept':'application/json'})
    from civitai_auth import bearer,NoRedirect
    token=bearer() if host in ('civitai.com','civitai.red') and u.path.startswith('/api/v1/') else ''
    if token:req.add_header('Authorization','Bearer '+token)
    opener=urllib.request.build_opener(NoRedirect()) if token else urllib.request.build_opener()
    try:
        with opener.open(req,timeout=18) as response:
            body=response.read(8*1024*1024+1)
            if len(body)>8*1024*1024:raise ValueError('API応答サイズ超過')
            data=json.loads(body)
        record(host,operation,200);return data
    except urllib.error.HTTPError as e:
        delay=0
        if e.code==429:
            retry=e.headers.get('Retry-After','60')
            try:delay=max(1,float(retry))
            except ValueError:
                try:delay=max(1,parsedate_to_datetime(retry).timestamp()-time.time())
                except Exception:delay=60
        elif e.code in (401,403):delay=120
        elif e.code>=500:delay=30
        if delay:COOLDOWN[host]=time.time()+delay
        record(host,operation,e.code,delay);raise
    except Exception as e:
        record(host,operation,type(e).__name__)
        raise RuntimeError(f'{host}: {type(e).__name__}（接続・応答形式を確認してください）') from e
