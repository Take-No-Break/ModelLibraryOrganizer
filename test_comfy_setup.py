import unittest,tempfile,threading,json
from pathlib import Path
from unittest.mock import patch
from comfy_setup import resolve_folder,find_running,probe_running,build_ui_workflow
from comfy_client import NODE

class ComfySetupTests(unittest.TestCase):
 def test_parent_folder_and_ambiguity(self):
  with tempfile.TemporaryDirectory() as tmp:
   parent=Path(tmp);comfy=parent/'ComfyUI';comfy.mkdir();(comfy/'main.py').touch();(comfy/'custom_nodes').mkdir()
   self.assertEqual(resolve_folder(parent,'comfy'),str(comfy))
   models=parent/'pixai';model=models/'v1.0';model.mkdir(parents=True);(model/'tagger_pipeline.py').touch()
   self.assertEqual(resolve_folder(models,'pixai'),str(model))
   self.assertEqual(resolve_folder(model,'pixai'),str(model))
   other=models/'v2';other.mkdir();(other/'tagger_pipeline.py').touch()
   with self.assertRaises(ValueError):resolve_folder(models,'pixai')
 def test_running_probe_missing_bridge_is_setup_state(self):
  with patch('comfy_setup.ComfyClient.request',side_effect=[{'system':{}},{}]):
   self.assertEqual(probe_running('http://127.0.0.1:8188')['bridge'],False)
  with patch('comfy_setup.ComfyClient.request',side_effect=[{'system':{}},{NODE:{}}]):
   self.assertTrue(probe_running('http://127.0.0.1:8188')['bridge'])
 def test_discovery_bounded_and_multiple_servers(self):
  with patch('comfy_setup.probe_running',side_effect=lambda url:{'url':url,'bridge':True}) as probe:
   found=find_running('http://127.0.0.1:8188',threading.Event())
   self.assertEqual(len(found),2);self.assertEqual(probe.call_count,2)
  with patch('comfy_setup.probe_running') as probe:
   with self.assertRaises(ValueError):find_running('http://remote.example',threading.Event())
   probe.assert_not_called()
 def test_template_widget_order_and_no_file_writes(self):
  thresholds=dict(general=.17,character=.27,style=.15,copyright=.24,meta=.17,rating=.41)
  result=build_ui_workflow(['C:/images/猫.png'],'C:/pixai',thresholds)
  self.assertEqual(result['version'],.4);self.assertEqual(result['nodes'][0]['type'],NODE)
  self.assertEqual(result['nodes'][0]['widgets_values'][3:],[.17,.27,.15,.24,.17,.41])
  self.assertEqual(json.loads(result['nodes'][0]['widgets_values'][0]),['C:/images/猫.png'])
  self.assertEqual(result['nodes'][1]['type'],'PreviewAny')
  self.assertEqual(result['links'][0],[1,1,0,2,0,'STRING'])
  self.assertNotIn('SaveImage',json.dumps(result));self.assertIn('does NOT write',result['nodes'][2]['widgets_values'][0])
  thresholds['general']=float('nan')
  with self.assertRaises(ValueError):build_ui_workflow([],'',thresholds)

if __name__=='__main__':unittest.main()
