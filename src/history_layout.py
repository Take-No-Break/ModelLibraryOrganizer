"""Reapply a historical layout from recorded paths, without resetting old journals."""
import os,time,uuid
from pathlib import Path
from core import read_json,atomic_json,snapshot,safe_tree,has_link

def restore_layout(engine,path):
 doc=read_json(path,{})
 if doc.get('kind')=='scan_snapshot':
  linked=[read_json(p,{}) for p in doc.get('move_journals',[])]
  if not linked:raise ValueError('This scan inventory has no linked move history.')
  targets=[item for log in linked for item in log.get('before_state',log.get('ops',[]))]
 else:targets=doc.get('before_state',doc.get('ops',[]))
 if not targets:raise ValueError('This history has no recorded model moves.')
 logs=[doc,*[read_json(p,{}) for p in (engine.data/'history').glob('*.json')]]
 paths=set()
 for log in logs:
  for op in log.get('before_state',[])+log.get('ops',[]):
   paths.update(op.get(k) for k in ('source','destination') if op.get(k))
   paths.update(op.get('links',[]))
 ops=[];seen=set()
 for item in targets:
  desired=Path(item['source']).resolve()
  if str(desired) in seen:continue
  seen.add(str(desired))
  expected=item.get('source_snapshot',item.get('snapshot'))
  if expected is None:raise ValueError('History has no file identity for: '+str(desired))
  if desired.exists():
   if not safe_tree(desired) or snapshot(desired)!=expected:raise ValueError('Original location contains a changed or different file: '+str(desired))
   continue
  candidates=[]
  for candidate in paths:
   p=Path(candidate)
   if p.exists() and safe_tree(p) and snapshot(p)==expected:candidates.append(p.resolve())
  candidates=list(dict.fromkeys(candidates))
  if len(candidates)!=1:raise ValueError('Cannot uniquely locate the unchanged model in recorded history: '+str(desired))
  current=candidates[0]
  if has_link(desired.parent):raise ValueError('Cannot restore through a directory link.')
  op={'source':str(desired),'destination':str(current),'snapshot':expected,'links':[],'notes':[],'done':True}
  note=current.with_name(current.name+'.source.txt');target_note=desired.with_name(desired.name+'.source.txt')
  if note.exists():
   if target_note.exists() or not safe_tree(note):raise ValueError('Source TXT conflict: '+str(target_note))
   op['moved_note']={'source':str(target_note),'destination':str(note),'snapshot':snapshot(note)}
  ops.append(op)
 if not ops:return 0
 root=Path(os.path.commonpath([str(Path(op['destination']).parent) for op in ops]))
 journal=engine.data/'history'/(time.strftime('%Y%m%d-%H%M%S')+'-layout-'+uuid.uuid4().hex[:8]+'.json')
 atomic_json(journal,{'version':2,'root':str(root),'created_at':time.strftime('%Y-%m-%d %H:%M:%S'),'complete':True,'ops':ops,'created_dirs':[],'layout_restore_from':str(path)})
 return engine.rollback(journal)
