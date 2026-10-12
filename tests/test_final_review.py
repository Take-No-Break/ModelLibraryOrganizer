import tempfile,unittest,tkinter as tk
from pathlib import Path
from unittest.mock import patch,MagicMock
import i18n
from core import Engine,atomic_json,digest,read_json
from test_core import model

class ReviewSafety(unittest.TestCase):
 def test_forged_history_cannot_delete_unrelated_file(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory)/'models';root.mkdir();engine=Engine(Path(directory)/'data')
   model(root/'demo.safetensors',['clip_l'])
   rows=engine.scan(root,root,False)
   for row in rows:row['decision']='承認'
   journal=engine.execute(rows,root);doc=read_json(journal)
   unrelated=root/'user-notes.txt';unrelated.write_text('retain')
   doc['ops'][0]['notes']=[{'path':str(unrelated),'sha':digest(unrelated)}];atomic_json(journal,doc)
   with self.assertRaisesRegex(ValueError,'sidecar'):engine.rollback(journal)
   self.assertEqual(unrelated.read_text(),'retain');self.assertTrue(Path(rows[0]['destination']).exists())
 def test_centering_uses_physical_pixels_without_rescaling(self):
  from display import center_popup
  window=MagicMock();parent=MagicMock()
  window.winfo_width.return_value=800;window.winfo_height.return_value=600
  window.winfo_screenwidth.return_value=1920;window.winfo_screenheight.return_value=1080
  parent.winfo_width.return_value=1000;parent.winfo_height.return_value=800
  parent.winfo_rootx.return_value=100;parent.winfo_rooty.return_value=100
  with patch('display.tk.Wm.geometry') as geometry:center_popup(window,parent)
  geometry.assert_called_once_with(window,'800x600+200+200');window.geometry.assert_not_called()
 def test_all_languages_have_about_and_usage(self):
  from help_pages import ABOUT,JA,EN
  from help_pages_locales import GUIDES
  self.assertEqual(set(ABOUT),set(i18n.LANGS))
  self.assertEqual(set(GUIDES),set(i18n.LANGS)-{'ja','en'})
  self.assertEqual(set(JA),set(EN))
  for sections in GUIDES.values():self.assertEqual(len(sections),len(EN))

class ReviewUI(unittest.TestCase):
 def test_short_about_separate_guide_and_readable_diagnostics(self):
  from app import App
  with tempfile.TemporaryDirectory() as directory:
   root=tk.Tk();root.withdraw()
   try:
    app=App(root,Path(directory));root.update_idletasks()
    self.assertIn('howto',app.pages)
    labels=[app.tabs.tab(tab,'text') for tab in app.tabs.tabs()]
    self.assertEqual(labels[labels.index('About')+1],'How to use')
    about=app.pages['help']
    self.assertFalse(any(w.winfo_class()=='TNotebook' for w in about.winfo_children()))
    app.network_report()
    windows=[w for w in root.winfo_children() if isinstance(w,tk.Toplevel)]
    self.assertEqual(len(windows),1);windows[0].withdraw()
    def walk(widget):
     for child in widget.winfo_children():yield child;yield from walk(child)
    widgets=list(walk(windows[0]))
    text='\n'.join(w.get('1.0','end') for w in widgets if w.winfo_class()=='Text')
    self.assertIn('記録済みエラー',text);self.assertNotIn('"privacy"',text)
    self.assertTrue(any(w.winfo_class()=='TButton' and w.cget('text')=='Discord support' for w in widgets))
   finally:
    for job in root.tk.splitlist(root.tk.call('after','info')):root.after_cancel(job)
    root.destroy();i18n.set_language('ja')

if __name__=='__main__':unittest.main()
