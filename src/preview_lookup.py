"""Anonymous fallback lookup for explicitly general-audience preview images."""
from urllib.error import HTTPError
from urllib.parse import urlparse
from core import fetch_json
import network

NO_IMAGE='公開APIから一般向けのプレビュー画像が返されませんでした。'
AUTH='画像APIへのアクセスが制限されています（HTTP 401/403）。認証またはサービス側のアクセス条件を確認してください。'
FAILED='プレビューの検索に失敗しました。通信診断・サポートログで接続状況を確認してください。'

def general_image(item):
 if not isinstance(item,dict) or item.get('type','image')!='image':return False
 if item.get('nsfw') is True:return False
 level=item.get('nsfwLevel')
 rated=type(level) is int and level==1 or isinstance(level,str) and level.lower() in ('none','1')
 if level is not None and not rated:return False
 if 'browsingLevel' in item:return type(item['browsingLevel']) is int and item['browsingLevel']==1
 return rated

def preview_candidates(row,info,host,online=True):
 cached=[i for i in info.get('images',[]) if general_image(i)]
 if cached:return cached,''
 if not online or network.OFFLINE:return [],NO_IMAGE
 sha=row.get('sha','')
 if not sha:return [],NO_IMAGE
 origin=urlparse(row.get('url','')).hostname
 preferred=host if host in ('https://civitai.com','https://civitai.red') else 'https://'+origin if origin in ('civitai.com','civitai.red') else 'https://civitai.com'
 hosts=[preferred, 'https://civitai.red' if preferred.endswith('.com') else 'https://civitai.com']
 errors=[];success=False
 for base in hosts:
  try:
   version=fetch_json(base+'/api/v1/model-versions/by-hash/'+sha)
   if not isinstance(version,dict):raise ValueError('Invalid version response')
   if not any(str(f.get('hashes',{}).get('SHA256','')).lower()==sha.lower() for f in version.get('files',[])):continue
   success=True
   candidates=[i for i in version.get('images',[]) if general_image(i)]
   if not candidates and version.get('id'):
    page=fetch_json(base+'/api/v1/images?modelVersionId='+str(int(version['id']))+'&browsingLevel=1&type=image&limit=20')
    candidates=[i for i in page.get('items',[]) if general_image(i)]
   if candidates:return candidates,''
  except HTTPError as exc:
   if exc.code!=404:errors.append('auth' if exc.code in (401,403) else 'failed')
  except Exception:errors.append('failed')
 if 'auth' in errors:return [],AUTH
 if errors and not success:return [],FAILED
 return [],NO_IMAGE

from locales import CATALOG
CATALOG['en'].update({NO_IMAGE:'No general-audience preview image was returned by the public API.',AUTH:'Preview API access was restricted (HTTP 401/403). Authentication or service access rules may apply.',FAILED:'Preview lookup failed. Check Diagnostics / support for connection details.'})
