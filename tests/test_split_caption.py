import json,tempfile,unittest,tkinter as tk
from pathlib import Path
from unittest.mock import patch,Mock
from comfy_bridge.backend import select_tags,format_records,DEFAULTS,limits
from comfy_bridge import NODE_CLASS_MAPPINGS
from split_template import build_split_workflow
from comfy_client import install_bridge
from app import App

class SplitCaptionTests(unittest.TestCase):
 def test_thresholds_and_order_without_inference(self):
  raw={'tags':['sky','best_quality','1girl','hero','series','artist','meta','safe'], 'splits':[('general',3),('character',1),('copyright',1),('style',1),('meta',1),('rating',1)],'items':[{'image':'a.png','scores':[.17,.9,.8,.8,.8,.8,.8,.8]}]}
  selected=select_tags(raw,DEFAULTS)
  caption=json.loads(format_records(selected))[0]['caption']
  self.assertEqual(caption,'best_quality, meta, safe, hero, series, artist, 1girl')
  lower={**DEFAULTS,'general':0.}
  self.assertTrue(json.loads(format_records(select_tags(raw,lower)))[0]['caption'].endswith('sky'))
  with self.assertRaises(ValueError):limits({**DEFAULTS,'general':float('nan')})
 def test_template_links_match_registered_node_schemas(self):
  workflow=build_split_workflow(['a.png'],'model',DEFAULTS)
  nodes={n['id']:n for n in workflow['nodes']}
  for node in nodes.values():
   if node['type'] not in ('PreviewAny','Note'):
    cls=NODE_CLASS_MAPPINGS[node['type']]
    self.assertEqual([o['type'] for o in node['outputs']],list(cls.RETURN_TYPES))
    schema=cls.INPUT_TYPES()['required']
    self.assertTrue(all(i['name'] in schema for i in node['inputs']))
  for ident,source,slot,target,input_slot,typ in workflow['links']:
   self.assertIn(ident,nodes[source]['outputs'][slot]['links'])
   self.assertEqual(nodes[target]['inputs'][input_slot]['link'],ident)
   self.assertEqual(nodes[source]['outputs'][slot]['type'],typ)
  self.assertEqual(nodes[4]['widgets_values'],list(DEFAULTS.values()))
  self.assertFalse(any('Save' in n['type'] for n in nodes.values()))
 def test_bridge_installs_all_stages(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);(root/'main.py').touch();(root/'custom_nodes').mkdir()
   target=Path(install_bridge(root,Path(__file__).resolve().parents[1]/'src'/'comfy_bridge'))
   for name in ('__init__.py','stages.py','backend.py','tag_order.py'):self.assertTrue((target/name).is_file())
 def test_local_execution_keeps_template_export_and_no_launcher(self):
  with tempfile.TemporaryDirectory() as folder:
   root=tk.Tk();root.withdraw()
   try:
    app=App(root,Path(folder));root.update()
    self.assertTrue(hasattr(app,'cap_url'));self.assertTrue(hasattr(app,'cap_output'))
    for name in ('cap_comfy','cap_launcher','cap_open_mode'):self.assertFalse(hasattr(app,name))
    self.assertTrue(hasattr(app,'export_caption_ui_workflow'))
   finally:
    for timer in root.tk.splitlist(root.tk.call('after','info')):root.after_cancel(timer)
    root.update_idletasks();root.destroy()
