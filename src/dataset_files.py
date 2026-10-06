"""Caption files: explicit edits, conflict checks and recoverable backups; never touch image bytes."""
import hashlib,json,os,re,uuid
from pathlib import Path
from core import atomic_json
IMAGE_EXTS={'.png','.jpg','.jpeg','.webp','.bmp','.tif','.tiff'}

def digest(raw):return hashlib.sha256(raw).hexdigest() if raw is not None else None

def read_caption(path):
 p=Path(path)
 if p.is_symlink():raise ValueError('Symbolic link TXT is not editable: '+str(p))
 if not p.exists():return {'raw':None,'text':'','encoding':'utf-8','hash':None}
 if p.stat().st_size>8*1024*1024:raise ValueError('TXT exceeds 8 MB: '+str(p))
 raw=p.read_bytes();encoding='utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig' if raw.startswith(b'\xef\xbb\xbf') else 'utf-8'
 try:text=raw.decode(encoding)
 except UnicodeDecodeError:raise ValueError('Unsupported text encoding; convert this file to UTF-8 first: '+str(p))
 return {'raw':raw,'text':text,'encoding':encoding,'hash':digest(raw)}

def list_dataset(folder,recursive=False,include_text=True):
 root=Path(folder).resolve(strict=True)
 if not root.is_dir():raise ValueError('Select an existing folder.')
 entries={}
 for p in sorted(root.rglob('*') if recursive else root.iterdir()):
  if not p.is_file() or p.is_symlink() or not p.resolve().is_relative_to(root):continue
  ext=p.suffix.lower()
  if ext not in IMAGE_EXTS and not (include_text and ext=='.txt'):continue
  txt=p.with_suffix('.txt') if ext in IMAGE_EXTS else p
  key=str(txt).casefold();item=entries.setdefault(key,{'text_path':str(txt),'images':[]})
  if ext in IMAGE_EXTS:item['images'].append(str(p))
 return list(entries.values())

def transform_caption(text,operation,value='',replacement='',match='tag'):
 value=value.strip()
 if not value:raise ValueError('Enter a non-empty word/tag.')
 if operation in ('prepend','append'):
  tags=[v.strip() for v in text.strip().split(',') if v.strip()]
  if value in tags:return text
  return (value+', '+text.strip() if operation=='prepend' else text.strip()+', '+value).strip(', ')+'\n'
 if operation=='wrap':
  if '<' in value or '>' in value:raise ValueError('Enter the word without < >.')
  replacement='<'+value+'>'
 if operation=='remove':replacement=''
 if match=='tag':
  tags=[t.strip() for t in text.strip().split(',') if t.strip()]
  changed=[replacement if t==value else t for t in tags]
  if changed==tags:return text
  return ', '.join(t for t in changed if t)+'\n'
 pattern=r'(?<![\w<>])'+re.escape(value)+r'(?![\w<>])'
 result=re.sub(pattern,lambda m:replacement,text)
 return result

def make_change(path,text,baseline=None):
 baseline=read_caption(path) if baseline is None else baseline
 return {'path':str(Path(path).resolve()),'before':baseline['raw'],'after':text.encode(baseline['encoding']),'before_text':baseline['text'],'after_text':text}

def apply_changes(changes,data_dir):
 changes=[c for c in changes if c['before']!=c['after']]
 if not changes:return {'count':0,'manifest':''}
 paths=[str(Path(c['path']).resolve()).casefold() for c in changes]
 if len(paths)!=len(set(paths)):raise ValueError('Duplicate TXT targets in this operation.')
 for c in changes:
  if Path(c['path']).suffix.lower()!='.txt':raise ValueError('Only .txt files can be edited.')
  if read_caption(c['path'])['raw']!=c['before']:raise ValueError('TXT changed since preview; reload before saving: '+c['path'])
 backup=Path(data_dir)/'caption-backups'/uuid.uuid4().hex;backup.mkdir(parents=True)
 manifest=backup/'manifest.json';records=[]
 for i,c in enumerate(changes):
  before=backup/(str(i)+'.txt')
  if c['before'] is not None:before.write_bytes(c['before'])
  records.append({'path':c['path'],'backup':str(before) if c['before'] is not None else None,'before_hash':digest(c['before']),'after_hash':digest(c['after']),'applied':False})
 atomic_json(manifest,records)
 for c,r in zip(changes,records):
  p=Path(c['path'])
  if read_caption(p)['raw']!=c['before']:raise ValueError('TXT changed during save. Backup manifest: '+str(manifest))
  if c['before'] is None:
   with p.open('xb') as f:f.write(c['after'])
  else:
   temp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
   try:temp.write_bytes(c['after']);os.replace(temp,p)
   finally:
    if temp.exists():temp.unlink()
  r['applied']=True;atomic_json(manifest,records)
 return {'count':len(changes),'manifest':str(manifest)}

def undo_changes(manifest,data_dir):
 p=Path(manifest).resolve(strict=True);root=(Path(data_dir)/'caption-backups').resolve()
 if not p.is_relative_to(root):raise ValueError('Select a caption-backups manifest from this app.')
 records=json.loads(p.read_text(encoding='utf-8'));changes=[]
 for r in records:
  if not r.get('applied'):continue
  if Path(r['path']).suffix.lower()!='.txt':raise ValueError('Only .txt files can be restored.')
  state=read_caption(r['path'])
  if state['hash']!=r['after_hash']:raise ValueError('TXT was edited after this operation: '+r['path'])
  if r['backup']:
   backup=Path(r['backup']).resolve(strict=True)
   if not backup.is_relative_to(p.parent):raise ValueError('Invalid backup path.')
   raw=backup.read_bytes()
   if digest(raw)!=r['before_hash']:raise ValueError('Backup checksum mismatch.')
   changes.append({'path':r['path'],'before':state['raw'],'after':raw})
  else:changes.append({'path':r['path'],'before':state['raw'],'after':None})
 # Save the undo inputs too, and check every target before changing anything.
 for c in changes:
  if Path(c['path']).suffix.lower()!='.txt':raise ValueError('Only .txt files can be edited.')
  if read_caption(c['path'])['raw']!=c['before']:raise ValueError('Concurrent TXT modification.')
 for c in changes:
  target=Path(c['path'])
  if c['after'] is None:target.unlink()
  else:target.write_bytes(c['after'])
 for r in records:r['applied']=False
 atomic_json(p,records)
 return len(changes)
