import tempfile,time,unittest,threading
from pathlib import Path
from unittest.mock import patch
import tkinter as tk
from PIL import Image
from app import App
from note_format import note_content,plain

class UIChanges(unittest.TestCase):
 def setUp(self):
  popup=patch("result_ui.messagebox.showinfo");popup.start();self.addCleanup(popup.stop)
  self.temp=tempfile.TemporaryDirectory();self.root=tk.Tk();self.root.withdraw();self.app=App(self.root,self.temp.name)
 def tearDown(self):
  for job in self.root.tk.splitlist(self.root.tk.call('after','info')):self.root.after_cancel(job)
  self.root.destroy();self.temp.cleanup()
 def wait(self):
  end=time.monotonic()+3
  while self.app.busy and time.monotonic()<end:self.root.update();time.sleep(.01)
  self.assertFalse(self.app.busy)
 def test_busy_and_error(self):
  gate=threading.Event();self.app.work(lambda:(gate.wait(2) or 'result'),'status')
  self.assertTrue(self.app.busy);self.root.update();gate.set();self.wait()
  self.app.work(lambda:1/0,'status');self.wait()
  self.assertEqual(self.app.current_page(),str(self.app.pages['models']))
 def test_reports_and_preview_inside_app(self):
  self.app.show_text('Report','hello');self.app.identification_report()
  self.app.show_preview((Image.new('RGB',(12,12)),{'title':'Sample','source':'demo.safetensors','kind':'loras','family':'SDXL','url':''},{'description':'<p>Readable</p>'}))
  self.assertEqual(self.app.current_page(),str(self.app.pages['preview']))
  self.assertFalse(any(isinstance(w,tk.Toplevel) for w in self.root.winfo_children()))
 def test_html_and_note_backup(self):
  self.assertEqual(plain('<p>Hello</p><img src="https://image"><script>secret</script><p>World</p>'),'Hello\n\nWorld')
  p=Path(self.temp.name)/'model.safetensors';p.write_bytes(b'test')
  row={'source':str(p),'title':'Model','info':{'model_description':'<p>Hello</p>','images':[{'url':'IMAGE_URL'}]},'metadata':{},'blocked':False}
  content=note_content(row);self.assertIn('Hello',content);self.assertNotIn('<p>',content);self.assertNotIn('IMAGE_URL',content)
  note=p.with_name(p.name+'.source.txt');original='Model Library Organizer — 配布元情報\n<p>Old</p>';note.write_text(original,encoding='utf-8-sig')
  with patch.object(self.app,'selected',return_value=[row]),patch.object(self.app,'enrich_rows'),patch('panels.messagebox.askyesno',return_value=True):self.app.refresh_notes();self.wait()
  self.assertIn('Hello',note.read_text(encoding='utf-8-sig'));self.assertEqual(len(list((Path(self.temp.name)/'note-backups').glob('*/manifest.json'))),1)
  backup=next((Path(self.temp.name)/'note-backups').glob('*/0.txt'));self.assertEqual(backup.read_text(encoding='utf-8-sig'),original)

class LayoutAndOptions(UIChanges):
 def test_review_only_for_changes_no_automatic_move(self):
  row={'source':str(Path(self.temp.name)/'a.safetensors'),'destination':str(Path(self.temp.name)/'new'/'a.safetensors'),'decision':'保留','links':[],'blocked':False,'evidence':'test proposal'}
  self.app.review_moves(rows=[row]);self.assertTrue(self.app.review_active)
  def walk(w):
   yield w
   for child in w.winfo_children():yield from walk(child)
  buttons=[w for w in walk(self.root) if w.winfo_class()=='TButton' and w.cget('text')=='はい（賛成）']
  self.assertEqual(len(buttons),1);buttons[0].invoke()
  self.assertEqual(row['decision'],'承認');self.assertFalse(self.app.review_active)
  self.assertFalse(Path(row['destination']).parent.exists())
  row['decision']='変更なし';self.app.review_moves(rows=[row]);self.assertFalse(self.app.review_active)
 def test_review_close_leaves_pending(self):
  row={'source':'a','destination':'b','decision':'保留','links':[],'blocked':False}
  self.app.review_moves(rows=[row]);win=next(w for w in self.root.winfo_children() if isinstance(w,tk.Toplevel))
  win.tk.call(win.protocol('WM_DELETE_WINDOW'))
  self.assertFalse(self.app.review_active);self.assertEqual(row['decision'],'保留')
 def test_footer_visible_and_relative_path(self):
  self.root.deiconify();self.root.geometry('1000x680');self.root.update()
  self.assertGreater(self.app.progress.winfo_height(),5)
  self.assertLess(self.app.progress.winfo_rooty()+self.app.progress.winfo_height(),self.root.winfo_rooty()+self.root.winfo_height()+1)
  self.assertEqual(self.app.short_path('C:/models/loras/a.safetensors','C:/models'),'loras\\a.safetensors')
 def test_compact_navigation_progress_is_above_tabs(self):
  self.root.deiconify();self.root.geometry('1000x680');self.root.update()
  self.assertLess(self.app.progress.winfo_rooty(),self.app.tabs.winfo_rooty())
  self.assertLess(self.app.progress.winfo_height(),30)
  self.assertEqual(self.root.cget('background'),'#d9d8d2');self.assertFalse(hasattr(self.app,'theme_color'))
 def test_window_size_saved_on_close(self):
  self.root.deiconify();self.root.geometry('900x600');self.root.update()
  scale=max(1,self.root.winfo_fpixels('1i')/96)
  expected=[round(self.root.winfo_width()/scale),round(self.root.winfo_height()/scale)]
  with patch.object(self.root,'destroy'):self.app.close()
  from core import read_json
  self.assertEqual(read_json(Path(self.temp.name)/'preferences.json')['window_size'],expected)
 def test_notes_english_and_sections(self):
  row={'source':'demo.safetensors','kind':'loras','info':{'triggers':['unique'],'description':'desc'},'metadata':{'secret':'data'}}
  from note_format import note_content
  text=note_content(row,['triggers'])
  self.assertIn('Type: loras',text);self.assertIn('unique',text);self.assertNotIn('secret',text);self.assertNotIn('[Model description]',text)
 def test_stale_preview_ignored(self):
  self.app.gallery_generation=2
  with patch.object(self.app,'display_gallery') as display:
   self.app.gallery_image((1,{}, {},None,''));display.assert_not_called()
 def test_link_tags(self):
  self.app.linked_text(self.app.gallery_text,'Source: https://example.com/model')
  self.assertTrue(self.app.gallery_text.tag_ranges('link0'))

if __name__=='__main__':unittest.main()
