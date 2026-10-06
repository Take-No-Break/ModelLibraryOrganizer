"""Explicit layout proposals; never infer a creator from the model filename."""
from pathlib import Path
from urllib.parse import urlparse
import re

def folder_name(value):
    value=re.sub(r'[<>:"/\\|?*\x00-\x1f]','_',str(value)).strip(' .')[:80]
    if not value or value in ('.','..'):return 'Unknown'
    if re.fullmatch(r'(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?',value):value='_'+value
    return value

def creator(row):
    url=urlparse(row.get('url',''));host=(url.hostname or '').lower()
    if host in ('huggingface.co','www.huggingface.co'):
        parts=url.path.strip('/').split('/')
        if len(parts)>=2 and parts[0] not in ('models','datasets','spaces','api'):
            return 'Hugging Face',parts[0]
    if host in ('civitai.red','civitai.com','www.civitai.com'):
        author=row.get('author') or row.get('info',{}).get('author')
        if author:return 'Civitai',author
    return None

def apply_layout(row,root,layout):
    row['layout']=layout
    if layout!='creator':return
    origin=creator(row)
    if not origin or not row.get('kind') or row['kind']=='Not Found':
        row.update(destination=row['source'],links=[],decision='変更なし')
        row['confidence']='要確認'
        row['evidence']+=' / Creator or file type is unknown; current location retained.'
        return
    site,author=origin
    row['author']=author;row['provider']=site
    row['destination']=str(Path(root)/folder_name(site)/folder_name(author)/folder_name(row['kind'])/folder_name(row.get('family') or 'Unknown')/Path(row['source']).name)
    row['links']=[]
    row['evidence']+=' / Layout: provider / creator / type / family.'

def is_workflow(path):
    """Only recognized ComfyUI JSON, not arbitrary settings or metadata."""
    if path.suffix.lower()!='.json' or path.stat().st_size>16*1024*1024:return False
    import json
    try:doc=json.loads(path.read_text(encoding='utf-8-sig'))
    except (ValueError,OSError):return False
    if not isinstance(doc,dict):return False
    if isinstance(doc.get('nodes'),list) and isinstance(doc.get('links'),list):
        return bool(doc['nodes']) and all(isinstance(n,dict) and isinstance(n.get('type'),str) for n in doc['nodes'])
    return bool(doc) and all(isinstance(n,dict) and isinstance(n.get('class_type'),str) and isinstance(n.get('inputs'),dict) for n in doc.values())

def cleanup_empty_sources(record,journal,flush):
    """Remove only now-empty source ancestors from completed moves, never files."""
    from core import has_link,stamp
    root=Path(record['cleanup_root']).resolve()
    candidates=set()
    for op in record['ops']:
        if not op.get('done') or op.get('no_move'):continue
        p=Path(op['source']).parent
        while p.is_relative_to(root) and p!=root:
            candidates.add(p);p=p.parent
    for p in sorted(candidates,key=lambda p:len(p.parts),reverse=True):
        if not p.exists() or has_link(p) or not p.resolve().is_relative_to(root) or p.resolve()==root or any(p.iterdir()):continue
        # Record intent before each change; rmdir itself refuses nonempty folders.
        entry={'path':str(p),'identity':stamp(p)[:2],'removed':False}
        record.setdefault('removed_source_dirs',[]).append(entry);flush()
        try:p.rmdir()
        except OSError:continue
        entry['removed']=True;flush()
