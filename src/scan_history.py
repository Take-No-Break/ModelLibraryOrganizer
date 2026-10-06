"""Read-only inventory before scanning; linked to real move journals, never a backup."""
import os, time, uuid
from pathlib import Path
from core import atomic_json, read_json, stamp, has_link, Cancelled

def capture(engine, source, target, stop):
    files=[];folders=[]
    for base, dirs, names in os.walk(source, followlinks=False):
        if stop.is_set():raise Cancelled()
        dirs[:]=[d for d in dirs if not has_link(Path(base,d)) and Path(base,d).resolve()!=engine.data.resolve()]
        folders.append(str(Path(base)))
        for name in names:
            p=Path(base,name)
            if not has_link(p):files.append({'path':str(p),'stamp':stamp(p)[:4]})
    path=engine.data/'scan-history'/(time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]+'.json')
    doc={'kind':'scan_snapshot','version':1,'created_at':time.strftime('%Y-%m-%d %H:%M:%S'),
         'source_root':str(source),'root':str(target),'folders':folders,'files':files,
         'scope':'Paths and file state only. No contents backup. Restore uses linked move journals.',
         'move_journals':[],'ops':[],'complete':True}
    atomic_json(path,doc)
    engine.scan_snapshot=path
    return path

def link(engine,journal):
    path=getattr(engine,'scan_snapshot',None)
    if not path:return None
    doc=read_json(path)
    if not doc or doc.get('kind')!='scan_snapshot':raise ValueError('Scan snapshot is unavailable; rescan before moving.')
    if str(journal) not in doc['move_journals']:doc['move_journals'].append(str(journal))
    atomic_json(path,doc)
    return str(path)

def journals_for(snapshot):
    """Only resolve locally stored move logs; no moves are inferred from an inventory."""
    doc=read_json(snapshot,{})
    pending=[]
    for p in reversed(doc.get('move_journals',[])):
        journal=read_json(p)
        if not isinstance(journal,dict) or not isinstance(journal.get('ops'),list):
            raise ValueError('Linked move history is missing or unreadable: '+str(p))
        if not journal.get('restored'):pending.append(Path(p))
    return pending
