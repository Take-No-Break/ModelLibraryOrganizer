import os,tempfile,unittest,threading
from pathlib import Path
from unittest.mock import patch
from caption_output import save_output,run_local,output_folder

class OutputTests(unittest.TestCase):
 def test_overview_all_languages(self):
  from caption_labels import TEXT,labels
  from i18n import LANGS
  self.assertEqual(set(TEXT),set(LANGS))
  for code in LANGS:self.assertGreater(len(labels(code)[0]),60)
 def test_preview_information_order(self):
  from gallery import preview_content
  text=preview_content({'source':'test.safetensors','sha':'sample_hash','evidence':'sample_evidence','info':{'triggers':['trigger_example'],'description':'readable_description'}})
  self.assertLess(text.index('Trigger words:'),text.index('[Model description]'))
  self.assertGreater(text.index('Evidence:'),text.index('[File metadata]'))
  self.assertGreater(text.index('SHA256:'),text.index('[File metadata]'))
 def test_model_named_output(self):
  self.assertEqual(output_folder(Path.cwd(),"PixAI"),Path.cwd()/"PixAI")
  with self.assertRaises(ValueError):output_folder(Path.cwd(),"../unsafe")
 def test_hardlink_and_existing_caption(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);image=root/'landscape.png';image.write_bytes(b'sample');out=root/'PixAI'
   records=[{'image':str(image),'caption':'mountain, sky'}]
   save_output(records,out,[image]);self.assertTrue(os.path.samefile(image,out/image.name))
   self.assertEqual((out/'landscape.txt').read_text(),'mountain, sky\n')
   records[0]['caption']='changed';save_output(records,out,[image])
   self.assertEqual((out/'landscape.txt').read_text(),'mountain, sky\n');self.assertEqual(image.read_bytes(),b'sample')
 def test_missing_result_does_not_create_outputs(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);a=root/'a.png';b=root/'b.png';a.touch();b.touch();out=root/'output'
   with self.assertRaises(ValueError):save_output([{'image':str(a),'caption':'sky'}],out,[a,b])
   self.assertFalse(out.exists())
 def test_model_prompt_and_missing_nodes(self):
  with patch('comfy_client.ComfyClient') as cls:
   client=cls.return_value;client.request.return_value={}
   with self.assertRaises(ValueError):run_local('http://127.0.0.1:8188',[], '', 'PixAI',{},'auto',[], '',threading.Event(),lambda s:None,None)
   client.run.assert_not_called()
   client.request.return_value={'OrganizerCaptionBatch':{}};client.run.return_value=[]
   with patch('caption_output.save_output',return_value='OK'):
    self.assertEqual(run_local('http://127.0.0.1:8188',[], '', 'JoyCaption',{},'cpu',[.55,.4,'describe',128], '',threading.Event(),lambda s:None,None),'OK')
   self.assertEqual(client.run.call_args.args[0]['1']['inputs']['joy_max_tokens'],128)

if __name__=='__main__':unittest.main()
