import tempfile,unittest,tkinter as tk
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from app import App
from dataset_files import list_dataset

class DatasetUITests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.folder=Path(self.temp.name);self.root=tk.Tk();self.root.withdraw();self.app=App(self.root,self.folder/'data');self.root.update()
 def tearDown(self):
  self.root.update_idletasks()
  for job in self.root.tk.splitlist(self.root.tk.call('after','info')):self.root.after_cancel(job)
  self.root.destroy();self.temp.cleanup()
 def test_edit_image_paired_text_and_save(self):
  image=self.folder/'image.png';Image.new('RGB',(12,12),'blue').save(image);txt=image.with_suffix('.txt');txt.write_text('cat',encoding='utf-8')
  self.app.dataset_path.set(str(self.folder));self.app.receive_dataset(list_dataset(self.folder));self.app.dataset_list.selection_set('0');self.app.dataset_list.focus('0');self.app.select_dataset();self.root.update()
  self.app.editor.insert('end',', my_style');self.root.update();self.assertTrue(self.app.edit_dirty)
  self.assertTrue(self.app.save_editor());self.assertEqual(txt.read_text(encoding='utf-8'),'cat, my_style')
  self.assertTrue(list((self.folder/'data'/'caption-backups').glob('*/manifest.json')))
 def test_new_pc_compatibility_empty(self):
  self.app.populate_compatibility();self.assertEqual(self.app.compat_loras,[]);self.assertEqual(self.app.compat_table.get_children(),())
 def test_cancel_unsaved_edit(self):
  self.app.edit_dirty=True
  with patch('dataset_editor.messagebox.askyesnocancel',return_value=None):self.assertFalse(self.app.editor_guard())
 def test_caption_config_uses_user_paths(self):
  self.assertEqual(self.app.cap_url.get(),'http://127.0.0.1:8188');self.assertEqual(self.app.cap_output.get(),'');self.assertEqual(self.app.cap_model.get(),'');self.assertEqual(self.app.cap_folder.get(),'')
 def test_automatic_model_output_location(self):
  self.app.cap_folder.set(str(self.folder))
  self.assertEqual(self.app.cap_output.get(),str(self.folder/'PixAI'))
  self.app.cap_backend.set('JoyCaption')
  self.assertEqual(self.app.cap_output.get(),str(self.folder/'JoyCaption'))
 def test_compact_header_and_footer(self):
  self.root.deiconify();self.root.geometry('1000x680');self.root.update()
  self.assertLess(self.app.tabs.winfo_rooty()-self.root.winfo_rooty(),65)
  self.assertLessEqual(self.app.progress.winfo_rooty()+self.app.progress.winfo_height(),self.root.winfo_rooty()+680)

if __name__=='__main__':unittest.main()
