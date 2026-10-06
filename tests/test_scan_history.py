import tempfile,unittest,threading,os,json,tkinter as tk
from pathlib import Path
from unittest.mock import patch
from core import Engine,read_json,atomic_json
from test_core import model
from scan_history import journals_for
from features import duplicates
from duplicate_report import format_report,parse

class HistoryTests(unittest.TestCase):
 def test_missing_journal_is_not_claimed_restored(self):
  with tempfile.TemporaryDirectory() as temp:
   path=Path(temp)/'snapshot.json';atomic_json(path,{'move_journals':[str(Path(temp)/'missing.json')]})
   with self.assertRaises(ValueError):journals_for(path)
 def test_inventory_created_before_move_and_linked_restore(self):
  with tempfile.TemporaryDirectory() as temp:
   base=Path(temp);models=base/'models';models.mkdir();source=model(models/'a.safetensors',['clip_l'])
   (models/'caption.txt').write_text('original',encoding='utf-8');(models/'empty').mkdir()
   engine=Engine(base/'data');rows=engine.scan(models,models,False)
   snapshot=engine.scan_snapshot;doc=read_json(snapshot)
   self.assertIn(str(source),[f['path'] for f in doc['files']]);self.assertIn(str(models/'caption.txt'),[f['path'] for f in doc['files']])
   self.assertIn(str(models/'empty'),doc['folders']);self.assertEqual(journals_for(snapshot),[]);self.assertTrue(source.exists())
   rows[0]['decision']='承認';journal=engine.execute(rows,models)
   self.assertEqual(journals_for(snapshot),[journal]);self.assertEqual(read_json(journal)['scan_snapshot'],str(snapshot))
   engine.rollback(journal);self.assertTrue(source.exists());self.assertEqual(journals_for(snapshot),[])
 def test_inventory_write_failure_stops_scan(self):
  with tempfile.TemporaryDirectory() as temp:
   base=Path(temp);source=model(base/'models/a.safetensors',['clip_l']);engine=Engine(base/'data')
   with patch('scan_history.atomic_json',side_effect=OSError('disk full')):
    with self.assertRaises(OSError):engine.scan(source.parent,source.parent,False)
   self.assertTrue(source.exists());self.assertFalse((source.parent/'embeddings').exists())
 def test_duplicate_copy_and_hardlink_are_distinguished(self):
  with tempfile.TemporaryDirectory() as temp:
   base=Path(temp);source=model(base/'a.safetensors',['clip_l']);os.link(source,base/'b.safetensors');(base/'c.safetensors').write_bytes(source.read_bytes())
   groups=duplicates(base);self.assertEqual(groups[0]['physical_copies'],2);self.assertEqual(groups[0]['extra_bytes'],source.stat().st_size)
   report=format_report(groups);self.assertIn('独立した重複コピーあり',report);self.assertNotIn('physical_copies',report)
   self.assertEqual(parse('old introduction\n\n'+json.dumps(groups)),groups)
 def test_import_snapshot_and_result_table(self):
  from app import App
  with tempfile.TemporaryDirectory() as temp:
   base=Path(temp);root=tk.Tk();root.withdraw()
   try:
    app=App(root,base/'data');root.update();model(base/'models/a.safetensors',['clip_l'])
    rows=app.engine.scan(base/'models',base/'models',False);app.refresh_restore()
    self.assertEqual(len(app.restore_entries),1);app.restore_table.selection_set('0');app.restore_details()
    self.assertIn('調査前の配置記録',app.restore_text.get('1.0','end'));self.assertEqual(app.restore_action.winfo_manager(),'pack');self.assertIn('disabled',app.restore_action.state())
    rows[0]['decision']='承認';app.engine.execute(rows,base/'models');app.refresh_restore()
    index=next(str(i) for i,(_,doc) in enumerate(app.restore_entries) if doc.get('kind')=='scan_snapshot')
    app.restore_table.selection_set(index);app.restore_details();self.assertEqual(app.restore_action.winfo_manager(),'pack');self.assertNotIn('disabled',app.restore_action.state())
    g=[{'sha256':'a'*64,'files':[{'path':'A','identity':[1,2],'size':4},{'path':'B','identity':[1,2],'size':4}], 'physical_copies':1,'extra_bytes':0}]
    app.record_result('SHA256による重複検出',json.dumps(g));self.assertEqual(len(app.duplicate_table.get_children()),1)
    self.assertIn('ハードリンクのみ',app.result_body.get('1.0','end'))
    self.assertEqual(app.host.get(),'まとめて調査（Civitai + HF）')
   finally:
    for timer in root.tk.splitlist(root.tk.call('after','info')):root.after_cancel(timer)
    root.destroy()

if __name__=='__main__':unittest.main()
