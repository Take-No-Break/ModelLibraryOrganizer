import json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import library_models as m
from preview_lookup import preview_candidates
class LibraryTests(unittest.TestCase):
 def test_update_public_versions_and_comparison(self):
  card={'modelVersions':[{'id':1,'publishedAt':'2025-01-01','description':'old','trainedWords':['a']},{'id':2,'publishedAt':'2026-01-01','description':'new','trainedWords':['a','b']},{'id':3,'publishedAt':'2027-01-01','availability':'EarlyAccess'}]}
  self.assertEqual([v['id'] for v in m.newer_versions(card,1)[0]],[2])
  lines=m.changes(card['modelVersions'][0],card['modelVersions'][1])
  self.assertIn('+ new',lines);self.assertIn('- old',lines)
  self.assertTrue(m.newer_versions(card,99)[1])
 def test_triggers_and_resource_identity(self):
  rows=[{'source':'a.safetensors','sha':'a'*64,'info':{'triggers':['tag','other'],'version_id':12},'url':'https://civitai.red/models/2?modelVersionId=12'}]
  self.assertEqual(m.triggers(rows+rows,{}),'tag, other')
  self.assertEqual(m.match_resource({'hash':'a'*10},rows,{})[0],'Matched hash')
  self.assertEqual(m.match_resource({'version':12},rows,{})[0],'Matched version')
  self.assertEqual(m.match_resource({'name':'a.safetensors'},rows,{})[0],'Name match only (unverified)')
  self.assertEqual(m.match_resource({'name':'missing'},rows,{})[0],'Not identified in scanned library')
 def test_inventory_only_existing_files_and_png_metadata(self):
  from PIL import Image,PngImagePlugin
  with tempfile.TemporaryDirectory() as directory:
   path=Path(directory)/'demo.png';model=Path(directory)/'a.safetensors';model.write_bytes(b'example')
   engine=SimpleNamespace(cache={'catalog':{}})
   self.assertEqual(len(m.inventory(engine,[{'source':str(model)},{'source':str(model)},{'source':str(model)+'missing'}])),1)
   png=PngImagePlugin.PngInfo();png.add_text('prompt',json.dumps({'1':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':'a.safetensors'}},'2':{'inputs':{'lora_name':'b.safetensors'}}}))
   Image.new('RGB',(16,16),'gray').save(path,pnginfo=png)
   self.assertEqual([r['name'] for r in m.resources(m.png_metadata(path))],['a.safetensors','b.safetensors'])
 def test_multiple_previews_keep_only_general_audience(self):
  version={'id':3,'files':[{'hashes':{'SHA256':'a'*64}}],'images':[{'nsfwLevel':1,'url':'https://example.invalid/1'}]}
  page={'items':[{'nsfwLevel':1,'url':'https://example.invalid/1','meta':{'resources':[{'name':'model'}]}},{'nsfwLevel':'None','url':'https://example.invalid/2'},{'nsfwLevel':8,'url':'https://example.invalid/3'}]}
  with patch('preview_lookup.fetch_json',side_effect=[version,page]) as fetch:
   images,error=preview_candidates({'sha':'a'*64},{},'https://civitai.red',full=True)
  self.assertEqual(len(images),2);self.assertTrue(images[0]['meta']);self.assertFalse(error)
  self.assertIn('withMeta=true',fetch.call_args.args[0])
 def test_ui_navigation_authors_and_comparison(self):
  import tkinter as tk
  from app import App
  import library_ui
  with tempfile.TemporaryDirectory() as directory:
   root=tk.Tk();root.withdraw()
   try:
    app=App(root,Path(directory));root.update()
    path=Path(directory)/'example.safetensors';path.write_bytes(b'neutral demo')
    row={'source':str(path),'sha':'a'*64,'family':'SDXL','kind':'loras','author':'Example creator','title':'Example','info':{'version':'v1'}}
    app.gallery_rows=[row];library_ui.refresh_authors(app)
    self.assertEqual(len(app.author_tree.get_children()),1)
    app.gallery_candidates=[{'url':'https://example.invalid/1'},{'url':'https://example.invalid/2'}];app.gallery_index=0;app.update_gallery_buttons()
    self.assertEqual(str(app.gallery_previous.cget('state')),'disabled');self.assertEqual(str(app.gallery_next.cget('state')),'normal')
    library_ui.comparison_result(app,[{'id':1,'description':'old'},{'id':2,'description':'new'}],1)
    root.update()
   finally:
    for timer in root.tk.splitlist(root.tk.call('after','info')):root.after_cancel(timer)
    root.destroy()

 def test_reverse_compatibility_tree_scroll_and_metadata(self):
  import tkinter as tk
  from app import App
  from features import compatibility
  from gallery import preview_content
  import library_ui
  with tempfile.TemporaryDirectory() as directory:
   root=tk.Tk();root.withdraw()
   try:
    app=App(root,Path(directory));root.update()
    records=[]
    for name,kind,family in [('lora','loras','Pony'),('checkpoint','checkpoints','SDXL'),('other','loras','Anima')]:
     path=Path(directory)/(name+'.safetensors');path.write_bytes(b'neutral')
     records.append(dict(source=str(path),kind=kind,family=family,sha=name,title=name,author='Demo',url=''))
    app.rows=records;app.populate_compatibility()
    forward=compatibility(records[0],[records[1]])[0]
    app.compat_direction.set('Checkpoint → LoRA');app.populate_compatibility()
    self.assertEqual(len(app.compat_pairs),2)
    self.assertEqual(app.compat_pairs[0]['pair_key'],forward['pair_key'])
    self.assertEqual({r['relation'] for r in app.compat_pairs},{'related','different'})
    app.gallery_rows=records;library_ui.refresh_authors(app)
    parent=app.author_tree.get_children()[0]
    self.assertFalse(app.author_tree.item(parent,'open'))
    library_ui.expand_authors(app,True);self.assertTrue(app.author_tree.item(parent,'open'))
    self.assertTrue(app.author_tree.cget('yscrollcommand'));self.assertTrue(app.author_tree.cget('xscrollcommand'))
    self.assertFalse(app.author_tree.column('type','stretch'))
    self.assertTrue(app.gallery_list.cget('yscrollcommand'))
    content=preview_content({**records[0],'metadata':{'ss_datasets':'[{"num_train_images":196,"tag_frequency":{"img":{"muk":49}}}]'}})
    self.assertIn('Public API / Safetensors metadata',content)
    self.assertIn('196',content);self.assertIn('49',content)
    self.assertNotIn('ss_datasets:\n  [{',content)
   finally:
    for timer in root.tk.splitlist(root.tk.call('after','info')):root.after_cancel(timer)
    root.destroy()

if __name__=='__main__':unittest.main()
