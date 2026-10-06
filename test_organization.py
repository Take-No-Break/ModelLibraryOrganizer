import tempfile,unittest,threading,json,os
from pathlib import Path
from core import Engine,digest,read_json,enumerate_units
from organization import creator,folder_name
from test_core import model

class OrganizationTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.base=Path(self.temp.name);self.root=self.base/'models';self.root.mkdir();self.engine=Engine(self.base/'data')
 def cached(self,path):
  sha=digest(path)
  self.engine.cache['models'][sha]={'kind':'loras','family':'Illustrious','title':'Example','source':'https://civitai.com/models/123','author':'Creator A','tags':['character']}
  return sha
 def test_existing_layout_switch_move_txt_empty_cleanup_and_restore(self):
  path=model(self.root/'loras/Character/Illustrious/example.safetensors',['lora_unet_a.lora_down.weight']);self.cached(path)
  note=path.with_name(path.name+'.source.txt');note.write_text('User edited original note',encoding='utf-8')
  rows=self.engine.scan(self.root,self.root,False,layout='creator');r=rows[0]
  self.assertEqual(Path(r['destination']),self.root/'Civitai/Creator A/loras/Illustrious/example.safetensors')
  self.assertEqual(r['kind'],'loras');self.assertTrue(path.exists())
  r['decision']='承認';journal=self.engine.execute(rows,self.root);dest=Path(r['destination'])
  self.assertFalse(path.exists());self.assertFalse(self.root.joinpath('loras').exists())
  self.assertEqual(dest.with_name(dest.name+'.source.txt').read_text(), 'User edited original note')
  self.assertTrue(read_json(journal)['removed_source_dirs'])
  again=self.engine.scan(self.root,self.root,False,layout='category')[0]
  self.assertEqual(Path(again['destination']),path);self.assertEqual(again['kind'],'loras')
  self.engine.rollback(journal);self.assertTrue(path.exists());self.assertTrue(note.exists());self.assertFalse(dest.exists())
 def test_nonempty_folders_and_other_hardlinks_are_kept(self):
  path=model(self.root/'loras/Character/a.safetensors',['lora_unet_a.lora_down.weight']);self.cached(path)
  extra=self.root/'loras/Character/notes.txt';extra.write_text('Do not remove')
  link=self.root/'loras/Multi/a.safetensors';link.parent.mkdir();os.link(path,link)
  row=next(r for r in self.engine.scan(self.root,self.root,False,layout='creator') if r['source']==str(path))
  row['decision']='承認';self.engine.execute([row],self.root)
  self.assertTrue(extra.exists());self.assertTrue(link.exists());self.assertTrue(os.path.samefile(link,row['destination']))
 def test_previous_category_rule_survives_layout_switch(self):
  path=model(self.root/'loras/Special/Illustrious/a.safetensors',['lora_unet_a.lora_down.weight']);sha=self.cached(path)
  old={'relative':'loras/Special/Illustrious','links':[],'family':'Illustrious','url':'https://civitai.com/models/123'}
  self.engine.cache['choices'][sha]=old
  r=self.engine.scan(self.root,self.root,False,layout='creator')[0];r['decision']='承認';self.engine.execute([r],self.root)
  back=self.engine.scan(self.root,self.root,False,layout='category')[0]
  self.assertEqual(Path(back['destination']),path);self.assertEqual(back['kind'],'loras')
 def test_aliases_do_not_propose_colliding_moves(self):
  path=model(self.root/'loras/Character/a.safetensors',['lora_unet_a.lora_down.weight']);self.cached(path)
  link=self.root/'loras/Multi/a.safetensors';link.parent.mkdir();os.link(path,link)
  rows=self.engine.scan(self.root,self.root,False,layout='creator')
  moves=[r for r in rows if r['destination']!=r['source']]
  self.assertEqual(len(moves),1)
  moves[0]['decision']='承認';journal=self.engine.execute(moves,self.root);self.engine.rollback(journal)
  self.assertTrue(path.exists());self.assertTrue(link.exists());self.assertTrue(os.path.samefile(path,link))
 def test_unknown_creator_preserves_location(self):
  path=model(self.root/'loras/Creator_guess.safetensors',['lora_unet_a.lora_down.weight'])
  r=self.engine.scan(self.root,self.root,False,layout='creator')[0]
  self.assertEqual(r['destination'],str(path));self.assertEqual(r['decision'],'変更なし');self.assertEqual(r['confidence'],'要確認')
 def test_hf_namespace_and_safe_folder_names(self):
  self.assertEqual(creator({'url':'https://huggingface.co/org-name/repo'}),('Hugging Face','org-name'))
  self.assertEqual(folder_name('../CON:Test'), '_CON_Test')
  self.assertEqual(folder_name('CON'),'_CON')
 def test_collision_refused_without_overwriting(self):
  path=model(self.root/'loras/a.safetensors',['lora_unet_a.lora_down.weight']);self.cached(path)
  dest=self.root/'Civitai/Creator A/loras/Illustrious/a.safetensors';dest.parent.mkdir(parents=True);dest.write_bytes(b'existing')
  rows=self.engine.scan(self.root,self.root,False,layout='creator');r=next(r for r in rows if r['source']==str(path))
  self.assertTrue(r['blocked']);r['decision']='承認'
  with self.assertRaises(ValueError):self.engine.execute([r],self.root)
  self.assertTrue(path.exists());self.assertEqual(dest.read_bytes(),b'existing')
 def test_only_recognized_workflow_json_included(self):
  workflow=self.root/'workflow.json';workflow.write_text(json.dumps({'nodes':[{'type':'LoadImage','id':1}],'links':[]}))
  (self.root/'settings.json').write_text('{"theme":"dark"}')
  self.assertEqual(enumerate_units(self.root,threading.Event()),[(workflow,False)])
  r=self.engine.scan(self.root,self.root,False)[0];self.assertEqual(r['kind'],'workflows')

if __name__=='__main__':unittest.main()
