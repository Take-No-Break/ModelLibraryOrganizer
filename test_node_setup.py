import tempfile,unittest
from pathlib import Path
from node_setup import install,node_directory

class NodeSetupTests(unittest.TestCase):
 def test_direct_install_update_and_backup(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);comfy=root/'ComfyUI';nodes=comfy/'custom_nodes';nodes.mkdir(parents=True)
   bundle=root/'bundle';bundle.mkdir();(bundle/'__init__.py').write_text('version=1')
   self.assertEqual(node_directory(comfy),nodes)
   target=Path(install(nodes,bundle));self.assertEqual(target.parent,nodes)
   self.assertEqual((target/'__init__.py').read_text(),'version=1')
   (bundle/'__init__.py').write_text('version=2');install(nodes,bundle)
   self.assertEqual((target/'__init__.py').read_text(),'version=2')
   self.assertEqual(len(list(target.glob('*.bak'))),1)
 def test_unmanaged_folder_is_not_overwritten(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);nodes=root/'custom_nodes';nodes.mkdir();bundle=root/'bundle';bundle.mkdir()
   (bundle/'__init__.py').write_text('new')
   target=nodes/'model_library_organizer_bridge';target.mkdir();(target/'__init__.py').write_text('user custom code')
   with self.assertRaises(ValueError):install(nodes,bundle)
   self.assertEqual((target/'__init__.py').read_text(),'user custom code')
 def test_generated_outputs_excluded(self):
  from caption_output import collect_images
  from PIL import Image
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);Image.new('RGB',(8,8)).save(root/'landscape.png')
   for name in ['PixAI','JoyCaption','CL-Tagger','Taggerine']:
    (root/name).mkdir();Image.new('RGB',(8,8)).save(root/name/'generated.png')
   self.assertEqual(collect_images(root,True),[str(root/'landscape.png')])

if __name__=='__main__':unittest.main()
