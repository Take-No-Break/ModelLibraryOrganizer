import unittest,tempfile,json,threading
from pathlib import Path
from unittest.mock import patch
from dataset_files import *
from comfy_client import base_url,build_prompt,ComfyClient,install_bridge,NODE

class DatasetTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
 def tearDown(self):self.tmp.cleanup()
 def test_scan_pairing_collision_and_standalone(self):
  (self.root/'a.png').write_bytes(b'image');(self.root/'a.jpg').write_bytes(b'image');(self.root/'b.txt').write_text('hello')
  items=list_dataset(self.root);self.assertEqual(len(items),2);self.assertEqual(len(items[0]['images']),2)
  self.assertEqual(len(list_dataset(self.root,include_text=False)),1)
 def test_tags_exact_not_substring_and_no_double_wrap(self):
  self.assertEqual(transform_caption('hair, blue hair, <hair>','wrap','hair'),'<hair>, blue hair, <hair>\n')
  self.assertEqual(transform_caption('<hair>, blue hair','wrap','hair'),'<hair>, blue hair')
  self.assertEqual(transform_caption('cat, cat ears','remove','cat'),'cat ears\n')
  self.assertEqual(transform_caption('a cat and bobcat','wrap','cat',match='word'),'a <cat> and bobcat')
  self.assertEqual(transform_caption('style, cat','prepend','style'),'style, cat')
 def test_utf16_preserved_backup_and_undo(self):
  p=self.root/'a.txt';p.write_text('こんにちは',encoding='utf-16');old=p.read_bytes()
  result=apply_changes([make_change(p,'new')],self.root/'data');self.assertEqual(p.read_text(encoding='utf-16'),'new')
  self.assertEqual(undo_changes(result['manifest'],self.root/'data'),1);self.assertEqual(p.read_bytes(),old)
 def test_conflict_preflight_changes_nothing(self):
  a=self.root/'a.txt';b=self.root/'b.txt';a.write_text('old');b.write_text('old')
  changes=[make_change(a,'new'),make_change(b,'new')];b.write_text('external')
  with self.assertRaises(ValueError):apply_changes(changes,self.root/'data')
  self.assertEqual(a.read_text(),'old');self.assertEqual(b.read_text(),'external')
 def test_new_caption_undo_and_refuse_image(self):
  p=self.root/'new.txt';result=apply_changes([make_change(p,'text')],self.root/'data');self.assertTrue(p.exists());undo_changes(result['manifest'],self.root/'data');self.assertFalse(p.exists())
  bad={'path':str(self.root/'photo.png'),'before':None,'after':b'bad'}
  with self.assertRaises(ValueError):apply_changes([bad],self.root/'data')
 def test_external_change_blocks_undo(self):
  p=self.root/'a.txt';result=apply_changes([make_change(p,'text')],self.root/'data');p.write_text('edited')
  with self.assertRaises(ValueError):undo_changes(result['manifest'],self.root/'data')
 def test_unsupported_encoding_does_not_overwrite(self):
  p=self.root/'a.txt';p.write_bytes(b'\xffbad')
  with self.assertRaises(ValueError):read_caption(p)
 def test_loopback_only(self):
  self.assertEqual(base_url('http://127.0.0.1:8188/'),'http://127.0.0.1:8188')
  for url in ['https://remote.example','http://evil.test','http://127.0.0.1@evil.test','http://localhost:80/other']:
   with self.assertRaises(ValueError):base_url(url)
 def test_prompt_returns_not_saves(self):
  prompt=build_prompt(['C:/images/a.png'],'C:/pixai',{'general':.17})
  self.assertEqual(prompt['1']['class_type'],NODE);self.assertNotIn('save_txt',prompt['1']['inputs'])
 def test_job_result_and_targeted_cancel(self):
  client=ComfyClient('http://127.0.0.1:8188');responses=[{'prompt_id':'job'}, {'job':{'outputs':{'1':{'text':['[{"image":"a","caption":"cat"}]']}}}}]
  with patch.object(client,'request',side_effect=responses):self.assertEqual(client.run({},threading.Event())[0]['caption'],'cat')
  stop=threading.Event();stop.set()
  with patch.object(client,'request',side_effect=[{'prompt_id':'job'},{}]) as request:
   with self.assertRaises(RuntimeError):client.run({},stop)
   self.assertEqual(request.call_args.args,('/queue',{'delete':['job']}))
 def test_bridge_install_preserves_unmanaged(self):
  root=self.root/'comfy';root.mkdir();(root/'main.py').touch();(root/'custom_nodes').mkdir()
  target=root/'custom_nodes'/'model_library_organizer_bridge';target.mkdir();(target/'__init__.py').write_text('owned')
  with self.assertRaises(ValueError):install_bridge(root,Path(__file__).parent/'comfy_bridge')
  self.assertEqual((target/'__init__.py').read_text(),'owned')

if __name__=='__main__':unittest.main()
