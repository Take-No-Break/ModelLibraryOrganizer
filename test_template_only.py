import json,tempfile,time,unittest,tkinter as tk
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from app import App
from template_generator import build_template
from comfy_bridge import NODE_CLASS_MAPPINGS
from comfy_bridge.backend import DEFAULTS
from comfy_bridge.save_text import OrganizerSaveCaptionTXT

class TemplateOnlyTests(unittest.TestCase):
 def test_all_model_graphs_have_valid_connections_and_widgets(self):
  for backend in ('PixAI','JoyCaption','CL Tagger','Taggerine'):
   for expanded in (False,True):
    graph=build_template([], '',backend,expanded,DEFAULTS);nodes={n['id']:n for n in graph['nodes']}
    for node in nodes.values():
     if node['type'] in ('PreviewAny','Note'):continue
     cls=NODE_CLASS_MAPPINGS[node['type']];schema=cls.INPUT_TYPES()['required']
     self.assertEqual([o['type'] for o in node['outputs']],list(cls.RETURN_TYPES))
     widgets=[k for k,v in schema.items() if k not in [i['name'] for i in node['inputs']]]
     self.assertEqual(len(widgets),len(node['widgets_values']),node['type'])
    for ident,source,slot,target,input_slot,typ in graph['links']:
     self.assertIn(ident,nodes[source]['outputs'][slot]['links']);self.assertEqual(nodes[target]['inputs'][input_slot]['link'],ident)
    writer=next(n for n in nodes.values() if n['type']=='OrganizerSaveCaptionTXT');self.assertEqual(writer['widgets_values'],[False])
 def test_writer_opt_in_and_existing_caption_protection(self):
  with tempfile.TemporaryDirectory() as folder:
   image=Path(folder)/'one.png';Image.new('RGB',(8,8)).save(image);txt=image.with_suffix('.txt')
   payload=json.dumps([dict(image=str(image),caption='one girl')]);writer=OrganizerSaveCaptionTXT()
   writer.save(payload,False);self.assertFalse(txt.exists())
   writer.save(payload,True);self.assertEqual(txt.read_text(encoding='utf-8'),'one girl\n')
   writer.save(json.dumps([dict(image=str(image),caption='changed')]),True);self.assertEqual(txt.read_text(encoding='utf-8'),'one girl\n')
 def test_auto_load_and_small_window_scroll(self):
  with tempfile.TemporaryDirectory() as folder:
   data=Path(folder);images=data/'images';images.mkdir();Image.new('RGB',(8,8)).save(images/'sample.png')
   root=tk.Tk()
   try:
    app=App(root,data/'settings');root.geometry('760x480');root.update();app.select_page(app.pages['captions']);root.update()
    host=app.page_hosts['captions'];host.resize();root.update()
    self.assertGreater(float(host.canvas.cget('scrollregion').split()[3]),host.canvas.winfo_height())
    host.canvas.yview_moveto(1);root.update();self.assertGreater(host.canvas.yview()[0],0)
    app.dataset_path.set(str(images));end=time.monotonic()+4
    while time.monotonic()<end and not app.dataset_rows:root.update();time.sleep(.03)
    self.assertEqual(len(app.dataset_rows),1);self.assertFalse((images/'sample.txt').exists())
   finally:
    for timer in root.tk.splitlist(root.tk.call('after','info')):root.after_cancel(timer)
    root.destroy()

if __name__=='__main__':unittest.main()
