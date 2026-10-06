import tempfile,time,unittest,tkinter as tk
from pathlib import Path
from unittest.mock import patch
from app import App
from core import read_json

class CleanupTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=tk.Tk();self.root.withdraw();self.app=App(self.root,self.temp.name);self.root.update()
 def tearDown(self):
  for timer in self.root.tk.splitlist(self.root.tk.call('after','info')):self.root.after_cancel(timer)
  self.root.destroy();self.temp.cleanup()
 def buttons(self,parent):
  out=[]
  for widget in parent.winfo_children():
   if widget.winfo_class()=='TButton':out.append(str(widget.cget('text')))
   out+=self.buttons(widget)
  return out
 def test_tools_have_no_duplicates_and_hf_is_in_models(self):
  tools=self.buttons(self.app.pages['tools']);models=self.buttons(self.app.pages['models']);captions=self.buttons(self.app.pages['captions'])
  for text in ('一覧を保存…','HF配布元を照合…','プレビュー','互換性の候補'):self.assertNotIn(text,tools)
  self.assertNotIn('HF配布元を照合…',models);self.assertNotIn('設定を保存',captions)
  self.assertLessEqual(int(self.app.cap_canvas.cget('width')),320);self.assertLessEqual(int(self.app.cap_canvas.cget('height')),290)
 def test_auto_preferences_include_options_and_do_not_write_workflow(self):
  self.app.cap_folder.set('example');self.app.cap_device.set('cpu');self.app.cap_thresholds['general'].set('0.22');self.app.cap_recursive.set(True);self.app.cap_joy.set('Describe this image.');self.app.save_training_settings()
  saved=read_json(Path(self.temp.name)/'training-settings.json',{})
  self.assertEqual(saved['thresholds']['general'],'0.22');self.assertTrue(saved['recursive']);self.assertEqual(saved['device'],'cpu');self.assertEqual(saved['joy_prompt'],'Describe this image.')
  self.assertEqual(list(Path(self.temp.name).glob('*.json')), [Path(self.temp.name)/'cache.json',Path(self.temp.name)/'training-settings.json'])
 def test_github_repository_link_uses_configured_owner(self):
  self.app.publisher={'github_repository':'Take-No-Break/ModelLibraryOrganizer'}
  with patch.object(self.app,'open_external') as open_url:self.app.open_repository()
  open_url.assert_called_once_with('https://github.com/Take-No-Break/ModelLibraryOrganizer')

if __name__=='__main__':unittest.main()
