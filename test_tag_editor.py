import tempfile,unittest,tkinter as tk
from pathlib import Path
from PIL import Image
from tag_dataset import load_tags,frequencies,split_tags,edit_tags,tag_changes
from dataset_files import apply_changes,undo_changes

class TagTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.folder=self.root/'images';self.folder.mkdir()
  Image.new('RGB',(10,10)).save(self.folder/'a.png')
  (self.folder/'a.txt').write_text('1girl, long_hair, 1girl\n',encoding='utf-8')
  (self.folder/'b.txt').write_text('1girl, short_hair\n',encoding='utf-8-sig')
  (self.folder/'c.txt').write_text('',encoding='utf-8')
 def test_frequency_is_per_txt_not_token_confidence(self):
  records=load_tags(self.folder);total,counts=frequencies(records)
  self.assertEqual(total,3);self.assertEqual(dict(counts)['1girl'],2);self.assertEqual(counts[0],('1girl',2))
  Image.new('RGB',(10,10)).save(self.folder/'missing.png');(self.folder/'model.safetensors.source.txt').write_text('ignored')
  self.assertEqual(frequencies(load_tags(self.folder)),(total,counts))
 def test_brackets_exact_delete_and_multiple_insert(self):
  self.assertEqual(split_tags('1girl, (red, blue:1.2), <custom>,\n hat'),['1girl','(red, blue:1.2)','<custom>','hat'])
  record={'draft':'1girl, 10girls, hats'};edit_tags(record,'1girl',True);self.assertEqual(split_tags(record['draft']),['10girls','hats'])
  edit_tags(record,'hats, jacket');self.assertEqual(split_tags(record['draft']),['10girls','hats','jacket'])
 def test_pending_save_backup_conflict_and_restore(self):
  records=load_tags(self.folder);image=(self.folder/'a.png').read_bytes()
  for record in records:edit_tags(record,'custom')
  self.assertNotIn('custom',(self.folder/'a.txt').read_text())
  result=apply_changes(tag_changes(records),self.root/'data')
  self.assertEqual(result['count'],3);self.assertEqual((self.folder/'a.png').read_bytes(),image)
  undo_changes(result['manifest'],self.root/'data');self.assertEqual((self.folder/'a.txt').read_text(),'1girl, long_hair, 1girl\n')
  records=load_tags(self.folder);edit_tags(records[0],'newtag');(self.folder/'a.txt').write_text('external edit')
  with self.assertRaises(ValueError):apply_changes(tag_changes(records),self.root/'data')
 def test_ui_tabs_rank_filter_and_unsaved_chips(self):
  from app import App
  root=tk.Tk();root.withdraw()
  try:
   app=App(root,self.root/'data');root.update()
   parent,book=app.page_notebooks['tag_editor'];labels=[book.tab(tab,'text') for tab in book.tabs()]
   self.assertEqual(labels[-2:],['Tag rankings','Tag editor'])
   app.tag_folder.set(str(self.folder));app.reload_tags();root.update()
   self.assertEqual(len(app.tag_rank_table.get_children()),3)
   app.tag_rank_table.selection_set('1');app.show_tag_frequency();self.assertAlmostEqual(float(app.tag_frequency_bar['value']),200/3)
   app.filter_ranked_tag();self.assertEqual(len(app.tag_image_list.get_children()),2)
   app.tag_image_list.selection_set('0');app.select_tag_image();app.remove_one_tag(0,'1girl')
   self.assertEqual(dict(frequencies(app.tag_records)[1])['1girl'],1);self.assertIn('1girl',(self.folder/'a.txt').read_text())
  finally:
   for job in root.tk.splitlist(root.tk.call('after','info')):root.after_cancel(job)
   root.destroy()

if __name__=='__main__':unittest.main()
