"""Read-only model-library helpers."""
import re,difflib
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from note_format import plain
def identity(row):
 url=urlparse(row.get('url','') or row.get('info',{}).get('source_url',''))
 if url.hostname not in ('civitai.com','civitai.red'):return None
 match=re.fullmatch(r'/models/(\d+)/?',url.path)
 if not match:return None
 version=parse_qs(url.query).get('modelVersionId',[''])[0]
 return url.scheme+'://'+url.netloc,int(match[1]),int(version) if version.isdigit() else None
def inventory(engine,rows):
 result={}
 for r in [*engine.cache.get('catalog',{}).values(),*rows]:
  location=r.get('destination') if r.get('decision')=='実行済み' else r.get('source')
  if location and Path(location).is_file():result[str(Path(location).resolve())]=r
 return list(result.values())
def triggers(rows,details):
 words=[];seen=set()
 for row in rows:
  info=row.get('info') or details.get(row.get('sha'),{}) or {}
  for word in info.get('triggers',[]):
   word=str(word).strip()
   if word and word.casefold() not in seen:seen.add(word.casefold());words.append(word)
 return ', '.join(words)
def newer_versions(card,current):
 versions=[v for v in card.get('modelVersions',[]) if v.get('id') and v.get('status','Published')=='Published' and v.get('availability','Public')=='Public']
 local=next((v for v in versions if v['id']==current),None)
 if not local:return [],'Current version could not be compared.'
 stamp=local.get('publishedAt') or local.get('createdAt')
 if not stamp:return [],'Publication date is unavailable.'
 return sorted([v for v in versions if v['id']!=current and (v.get('publishedAt') or v.get('createdAt') or '')>stamp],key=lambda v:v.get('publishedAt') or v.get('createdAt') or '',reverse=True),''
def version_text(v):
 return 'Description:\n'+plain(v.get('description') or '')+'\n\nTrigger words:\n'+', '.join(v.get('trainedWords') or [])
def changes(old,new):
 return list(difflib.ndiff(version_text(old).splitlines(),version_text(new).splitlines()))
def resources(meta):
 found=[]
 for key in ('civitaiResources','resources'):
  for item in meta.get(key,[]) if isinstance(meta.get(key),list) else []:
   if not isinstance(item,dict):continue
   found.append(dict(name=item.get('modelName') or item.get('name') or str(item.get('modelVersionId') or item.get('versionId') or ''),hash=item.get('hash') or item.get('sha256') or '',version=item.get('modelVersionId') or item.get('versionId'),type=item.get('type','')))
 if meta.get('Model') or meta.get('Model hash'):found.append(dict(name=meta.get('Model','Checkpoint'),hash=meta.get('Model hash',''),version=None,type='checkpoint'))
 hashes=meta.get('Lora hashes')
 if isinstance(hashes,str):
  for part in hashes.split(','):
   name,sep,value=part.partition(':')
   if sep:found.append(dict(name=name.strip(),hash=value.strip(),version=None,type='lora'))
 return found
def match_resource(resource,rows,details):
 hashed=str(resource.get('hash','')).lower()
 # SHA256 or Civitai AutoV2 prefix; don't mistake arbitrary short strings for identity.
 if re.fullmatch('[0-9a-f]{10,64}',hashed):
  hits=[r for r in rows if str(r.get('sha','')).lower().startswith(hashed)]
  if len(hits)==1:return 'Matched hash',Path(hits[0]['source']).name
 version=resource.get('version')
 if version:
  hits=[r for r in rows if str((r.get('info') or details.get(r.get('sha'),{}) or {}).get('version_id') or (identity(r) or ('',0,None))[2])==str(version)]
  if hits:return 'Matched version',Path(hits[0]['source']).name
 name=Path(str(resource.get('name',''))).stem.casefold()
 hits=[r for r in rows if name and name==Path(r['source']).stem.casefold()]
 if hits:return 'Name match only (unverified)',Path(hits[0]['source']).name
 return 'Not identified in scanned library',''
def png_metadata(path):
 import json
 from PIL import Image
 with Image.open(path) as image:info=dict(image.info)
 meta={}
 raw=info.get('parameters','')
 if isinstance(raw,str):
  for key in ('Model','Model hash','Lora hashes'):
   match=re.search(r'(?:^|,\s*)'+re.escape(key)+r':\s*([^\n]+?)(?=,\s*[A-Z][\w ]*:|$)',raw,re.M)
   if match:meta[key]=match.group(1).strip().strip('"')
 prompt=info.get('prompt')
 if prompt:
  try:
   graph=json.loads(prompt) if isinstance(prompt,str) else prompt
   for node in graph.values():
    fields=node.get('inputs',{})
    for key,kind in [('ckpt_name','checkpoint'),('lora_name','lora')]:
     if fields.get(key):meta.setdefault('resources',[]).append(dict(name=fields[key],type=kind))
  except (ValueError,AttributeError,TypeError):pass
 return meta
