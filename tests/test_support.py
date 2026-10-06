import unittest,tempfile,json,tkinter as tk
from pathlib import Path
from unittest.mock import patch
import network,i18n
from core import atomic_json
from support import valid_repo,version_tuple,check_release,record_error,support_report,load_publisher

class SupportTests(unittest.TestCase):
 def tearDown(self):network.OFFLINE=False;i18n.set_language('ja')
 def test_release_validation(self):
  data={'tag_name':'v1.10.0','html_url':'https://github.com/owner/repo/releases/tag/v1.10.0','body':'Test release'}
  with patch('support.request_json',return_value=data):self.assertTrue(check_release('owner/repo')['newer'])
  data['html_url']='https://evil.example/run.exe'
  with patch('support.request_json',return_value=data):
   with self.assertRaises(ValueError):check_release('owner/repo')
 def test_versions_and_repository(self):
  self.assertGreater(version_tuple('v1.10.0'),version_tuple('1.9.9'))
  self.assertEqual(valid_repo('https://github.com/owner/repo/'),'owner/repo')
  for bad in ['https://evil.test/a/b','../repo','owner/repo?token=secret']:
   with self.assertRaises(ValueError):valid_repo(bad)
 def test_offline_does_not_connect(self):
  network.OFFLINE=True
  with patch('network.urllib.request.urlopen') as connection:
   with self.assertRaises(RuntimeError):network.request_json('https://api.github.com/repos/a/b/releases/latest')
   connection.assert_not_called()
 def test_report_omits_private_error_message(self):
  with tempfile.TemporaryDirectory() as d:
   try:raise ValueError('C:/Users/Secret/PrivateModel.safetensors token=password')
   except Exception as e:record_error(d,e,'test')
   report=json.dumps(support_report(d));self.assertNotIn('PrivateModel',report);self.assertNotIn('password',report);self.assertIn('ValueError',report)
 def test_choice_labels_preserve_logic(self):
  for code in i18n.LANGS:
   i18n.set_language(code);interp=tk.Tcl();value=i18n.ChoiceVar(master=interp,value='すべて')
   self.assertEqual(value.get(),'すべて');value.set('判別できなかったモデル');self.assertEqual(value.get(),'判別できなかったモデル')
 def test_translated_paths_not_changed(self):
  i18n.set_language('en');path='C:/Users/姓名/フォルダー/モデル.safetensors'
  self.assertEqual(i18n.tr(path),path)
 def test_localized_windows_and_tooltip(self):
  from app import App
  for code in i18n.LANGS:
   with tempfile.TemporaryDirectory() as d:
    atomic_json(Path(d)/'preferences.json',{'language':code,'offline':True})
    root=tk.Tk();root.withdraw()
    try:
     app=App(root,d);root.update_idletasks();app.help_center();app.publisher_settings();app.network_report();root.update_idletasks()
     self.assertTrue(network.OFFLINE);self.assertFalse(app.online.get())
     self.assertEqual(app.host.get(),'まとめて調査（Civitai + HF）')
     self.assertEqual(app.filter.get(),'すべて')
     tip=i18n.Tooltip(root,'全件調査');tip.show();self.assertIsNotNone(tip.win);tip.hide();self.assertIsNone(tip.win)
    finally:
     for job in root.tk.splitlist(root.tk.call('after','info')):root.after_cancel(job)
     root.destroy()
if __name__=='__main__':unittest.main()
