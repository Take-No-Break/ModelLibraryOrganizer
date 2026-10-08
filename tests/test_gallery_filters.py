import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from app import App


class GalleryFilterTests(unittest.TestCase):
    def test_combined_filters_search_and_sort_keep_record_ids(self):
        with tempfile.TemporaryDirectory() as folder:
            root = tk.Tk()
            root.withdraw()
            try:
                app = App(root, Path(folder))
                app.gallery_list.unbind('<<TreeviewSelect>>')
                app.set_gallery_rows([
                    dict(source='/demo/zeta.safetensors', family='Pony', kind='loras'),
                    dict(source='/demo/Alpha.safetensors', family='SDXL', kind='checkpoints'),
                    dict(source='/demo/beta.safetensors', family='SDXL', kind='loras'),
                ], select=False)
                self.assertEqual(app.gallery_list.get_children(), ('1', '2', '0'))
                app.gallery_family.set('SDXL')
                app.gallery_kind.set('LoRA')
                app.filter_gallery_rows()
                self.assertEqual(app.gallery_list.get_children(), ('2',))
                app.gallery_search.set('BETA')
                self.assertEqual(app.gallery_list.get_children(), ('2',))
                app.gallery_search.set('missing')
                self.assertFalse(app.gallery_list.get_children())
                app.gallery_search.set('')
                app.gallery_family.set('すべて')
                app.gallery_kind.set('すべて')
                app.sort_gallery('name')
                self.assertEqual(app.gallery_list.get_children(), ('1', '2', '0'))
                app.gallery_family.set('Pony')
                app.set_gallery_rows([dict(source='/demo/new.safetensors', family='SDXL', kind='vae')], select=False)
                self.assertEqual(app.gallery_family.get(), 'すべて')
                self.assertEqual(app.gallery_list.get_children(), ('0',))
            finally:
                root.update_idletasks()
                root.destroy()
