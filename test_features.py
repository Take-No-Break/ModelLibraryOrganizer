import unittest,tempfile,threading,os,json
from pathlib import Path
from unittest.mock import patch
from core import Engine,digest
from features import duplicates,workflow_plan,repair_workflows,compatibility,enrich

class FeaturesTest(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.root=Path(self.t.name);self.models=self.root/'models';self.models.mkdir();self.engine=Engine(self.root/'app')
 def tearDown(self):self.t.cleanup()
 def test_new_scan(self):
  p=self.models/'a.pt';p.write_bytes(b'a');self.assertEqual(len(self.engine.scan(self.models,self.models,False)),1)
  self.assertEqual(self.engine.scan(self.models,self.models,False,only_new=True),[])
  p.write_bytes(b'changed');self.assertEqual(len(self.engine.scan(self.models,self.models,False,only_new=True)),1)
 def test_duplicates(self):
  a=self.models/'a.pt';a.write_bytes(b'identical');b=self.models/'b.pt';b.write_bytes(a.read_bytes());os.link(a,self.models/'c.pt')
  r=duplicates(self.models);self.assertEqual(len(r),1);self.assertEqual(r[0]['physical_copies'],2);self.assertEqual(r[0]['extra_bytes'],9)
 def test_workflow_repair_scoped(self):
  old=self.models/'loras'/'a.safetensors';new=self.models/'loras'/'Style'/'a.safetensors';old.parent.mkdir();old.write_bytes(b'a')
  wf=self.root/'workflows';wf.mkdir();p=wf/'demo.json';doc={'nodes':[{'type':'LoraLoader','widgets_values':['a.safetensors',1,1]},{'type':'CLIPTextEncode','widgets_values':['a.safetensors']}]};p.write_text(json.dumps(doc))
  rows=[{'source':str(old),'destination':str(new),'decision':'承認'}];plan=workflow_plan(wf,self.models,rows);self.assertEqual(len(plan),1);self.assertEqual(plan[0]['document']['nodes'][1]['widgets_values'][0],'a.safetensors')
  with self.assertRaises(ValueError):repair_workflows(plan,self.root/'backups')
  new.parent.mkdir();old.rename(new);backup=repair_workflows(plan,self.root/'backups');self.assertTrue(Path(backup,'manifest.json').exists());self.assertEqual(json.loads(p.read_text())['nodes'][0]['widgets_values'][0],'Style/a.safetensors')
 def test_changed_workflow_rejected(self):
  p=self.root/'w.json';p.write_text('{}');plan={'path':str(p),'before':digest(p),'changes':[],'document':{'x':1}};p.write_text('{"x":2}')
  with self.assertRaises(ValueError):repair_workflows([plan],self.root/'backup')
 def test_info_and_note(self):
  sha='a'*64;row={'sha':sha,'source':'test.safetensors'};v={'files':[{'hashes':{'SHA256':sha}}],'trainedWords':['my_style'],'modelId':1,'id':2}
  with patch('features.fetch_json',side_effect=[v,{'creator':{'username':'author'}}]):enrich(self.engine,row,'https://civitai.red')
  self.assertIn('my_style',self.engine.note_content(row));self.assertIn('author',self.engine.note_content(row))
 def test_compat_not_promise(self):
  p=self.models/'a.pt';p.write_bytes(b'a');result=compatibility({'family':'Illustrious','source':str(p)},[{'source':str(p),'kind':'checkpoints','family':'Illustrious'}]);self.assertIn('未検証',result[0]['assessment'])
if __name__=='__main__':unittest.main()
