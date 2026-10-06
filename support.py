"""Version checks and privacy-minimized local support records. Never auto-install."""
import json,re,sys,traceback
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urlparse
from core import atomic_json,read_json
from network import request_json,diagnostics
VERSION='1.0.31'

def valid_repo(repo):
    repo=repo.strip()
    if repo.startswith('https://github.com/'):repo=repo[len('https://github.com/'):].rstrip('/')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo):raise ValueError('Use owner/repository or its GitHub HTTPS URL.')
    if '..' in repo.split('/'):raise ValueError('Invalid repository.')
    return repo

def version_tuple(value):
    m=re.fullmatch(r'v?(\d+)\.(\d+)\.(\d+)',str(value))
    if not m:raise ValueError('Stable versions must use MAJOR.MINOR.PATCH.')
    return tuple(map(int,m.groups()))

def check_release(repo):
    repo=valid_repo(repo)
    data=request_json('https://api.github.com/repos/'+repo+'/releases/latest')
    if data.get('draft') or data.get('prerelease'):raise ValueError('No stable published release was returned.')
    version=data.get('tag_name','');newer=version_tuple(version)>version_tuple(VERSION)
    url=data.get('html_url','');parsed=urlparse(url)
    if parsed.scheme!='https' or parsed.netloc!='github.com' or not parsed.path.startswith('/'+repo+'/releases/'):raise ValueError('Unexpected release URL.')
    return {'current':VERSION,'latest':version,'newer':newer,'url':url,'notes':str(data.get('body') or '')[:16000]}

def load_publisher(data_dir):
    base=Path(sys.executable).parent if getattr(sys,'frozen',False) else Path(__file__).parent
    defaults=read_json(base/'publisher.json',{}) or {}
    overrides=read_json(Path(data_dir)/'publisher-settings.json',{}) or {}
    return {**defaults,**overrides}

def safe_error(exc,context):
    # No exception messages or source lines: these may contain filenames, tokens or prompts.
    frames=[]
    for frame in traceback.extract_tb(exc.__traceback__):
        if Path(frame.filename).name in {'app.py','core.py','features.py','feature_ui.py','providers.py','network.py','support.py','support_ui.py','i18n.py'}:
            frames.append({'module':Path(frame.filename).name,'function':frame.name,'line':frame.lineno})
    return {'utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'context':context,'exception':type(exc).__name__,'frames':frames,'version':VERSION}

def record_error(data_dir,exc,context):
    p=Path(data_dir)/'support-errors.json';records=read_json(p,[]) or [];records.append(safe_error(exc,context));atomic_json(p,records[-100:])

def support_report(data_dir):
    return {'app_version':VERSION,'platform':'Windows','network':diagnostics(),'errors':read_json(Path(data_dir)/'support-errors.json',[]),'privacy':'No model names, local paths, prompts, credentials, exception messages or response bodies. No automatic upload.'}
