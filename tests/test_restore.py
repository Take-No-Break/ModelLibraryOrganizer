import tempfile,unittest,tkinter as tk
from pathlib import Path
from unittest.mock import patch
from core import Engine,read_json
from test_core import model
from app import App
import i18n

class RestoreEngineTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)/'models';self.root.mkdir();self.engine=Engine(Path(self.tmp.name)/'data')
 def tearDown(self):self.tmp.cleanup()
 def rows(self):
  model(self.root/'a.safetensors',['clip_l']);model(self.root/'b.safetensors',['clip_l'])
  rows=self.engine.scan(self.root,self.root,False)
  for r in rows:r['decision']='承認'
  return rows
 def test_full_before_state_precedes_first_move(self):
  rows=self.rows();original=Path.rename;observed=[]
  def rename(source,destination):
   if not observed:
    logs=list((self.engine.data/'history').glob('*.json'));self.assertEqual(len(logs),1)
    before=read_json(logs[0])['before_state'];self.assertEqual(len(before),2)
    self.assertTrue(all(Path(x['source']).exists() for x in before));self.assertTrue(all(x['source_snapshot'] for x in before))
    self.assertFalse(before[0]['folders_before'][str(Path(rows[0]['destination']).parent)]['exists'])
    observed.append(True)
   return original(source,destination)
  with patch.object(Path,'rename',rename):journal=self.engine.execute(rows,self.root)
  self.assertTrue(observed);self.engine.rollback(journal)
  self.assertFalse((self.root/'embeddings').exists())
  self.assertTrue(all(Path(r['source']).exists() for r in rows))
 def test_snapshot_write_failure_prevents_moves(self):
  rows=self.rows()
  with patch('core.atomic_json',side_effect=OSError('disk full')):
   with self.assertRaises(OSError):self.engine.execute(rows,self.root)
  self.assertTrue(all(Path(r['source']).exists() for r in rows));self.assertFalse((self.root/'embeddings').exists())
 def test_restore_preserves_foreign_files_and_existing_dirs(self):
  rows=self.rows();existing=self.root/'embeddings';existing.mkdir()
  rows[0]['destination']=str(existing/'New'/'a.safetensors')
  journal=self.engine.execute(rows,self.root);foreign=existing/'New'/'user.txt';foreign.write_text('keep')
  self.engine.rollback(journal)
  self.assertTrue(existing.is_dir());self.assertEqual(foreign.read_text(),'keep')
  self.assertIn(str(foreign.parent),read_json(journal)['retained_dirs'])

class RestoreUITests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=tk.Tk();self.root.withdraw();self.app=App(self.root,self.tmp.name);self.root.update()
 def tearDown(self):
  for job in self.root.tk.splitlist(self.root.tk.call('after','info')):self.root.after_cancel(job)
  self.root.update_idletasks();self.root.destroy();self.tmp.cleanup();i18n.set_language('ja')
 def descendants(self,parent):
  for w in parent.winfo_children():yield w;yield from self.descendants(w)
 def answer(self,yes,hide):
  def respond():
   windows=[w for w in self.root.winfo_children() if isinstance(w,tk.Toplevel)]
   if not windows:return
   widgets=list(self.descendants(windows[0]))
   if hide:
    for w in widgets:
     if w.winfo_class()=='TCheckbutton':w.invoke()
   label='はい（続ける）' if yes else 'いいえ（中止）'
   for w in widgets:
    if w.winfo_class()=='TButton' and w.cget('text')==label:w.invoke();return
   windows[0].destroy()
  self.root.after(25,respond)
 def test_cancel_does_not_save_suppression(self):
  self.answer(False,True);self.assertFalse(self.app.confirm_move_warning());self.assertFalse(self.app.preferences.get('skip_move_warning',False))
 def test_yes_suppresses_only_warning_and_can_reenable(self):
  self.answer(True,True);self.assertTrue(self.app.confirm_move_warning());self.assertTrue(read_json(Path(self.tmp.name)/'preferences.json')['skip_move_warning'])
  self.assertTrue(self.app.confirm_move_warning())
  # Even with warning suppressed, the normal final confirmation is mandatory.
  self.app.scan_target=self.tmp.name;self.app.target_dir.set(self.tmp.name);self.app.rows=[{'decision':'承認','source':'a','destination':'b'}]
  with patch('app.messagebox.askyesno',return_value=False) as confirm,patch.object(self.app,'work') as execute:
   self.app.apply();confirm.assert_called_once();execute.assert_not_called()
  self.assertEqual(self.app.tabs.tabs()[-1],str(self.app.page_hosts['restore']))
  for w in self.descendants(self.app.pages['restore']):
   if w.winfo_class()=='TCheckbutton':w.invoke()
  self.assertFalse(self.app.preferences['skip_move_warning'])
 def test_history_browser_lists_legacy(self):
  from core import atomic_json
  atomic_json(Path(self.tmp.name)/'history'/'old.json',{'root':self.tmp.name,'ops':[],'complete':True})
  self.app.refresh_restore();self.assertEqual(len(self.app.restore_entries),1)
  self.app.restore_table.selection_set('0');self.app.restore_details()
  self.assertIn('old.json',self.app.restore_text.get('1.0','end'))

if __name__=='__main__':unittest.main()
