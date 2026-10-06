import tempfile,unittest,tkinter as tk
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
from PIL import Image
from tag_dataset import load_tags,frequencies,split_tags,edit_tags,tag_changes
from dataset_files import apply_changes,undo_changes
from tag_categories import category_of
from tag_widgets import ThumbnailStrip,chip_flow

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
 def make_app(self):
  from app import App
  root=tk.Tk();root.withdraw()
  def close():
   for job in root.tk.splitlist(root.tk.call('after','info')):root.after_cancel(job)
   root.destroy()
  self.addCleanup(close)
  app=App(root,self.root/'data');root.update();app.tag_folder.set(str(self.folder));app.reload_tags();root.update()
  return root,app
 def test_category_rules_are_explicit_and_overridable(self):
  for tag,category in [('long_hair','Face'),('blush','Expr'),('navel','Body'),('jacket','Outfit'),('standing','Pose'),('simple_background','BG'),('monochrome','Style'),('artist:example','Artist'),('unknown_name','Other')]:
   self.assertEqual(category_of(tag),category)
  self.assertEqual(category_of('unknown_name',{'unknown_name':'Chara'}),'Chara')
 def test_scope_registry_inline_and_destructive_actions_stage_only(self):
  root,app=self.make_app();before={p.name:p.read_bytes() for p in self.folder.iterdir()};app.tag_image_list.selection_set('0')
  self.assertIsInstance(app.tag_image_list,ThumbnailStrip)
  app.tag_value.set('new_tag');app.bulk_tag_edit(False)
  self.assertIn('new_tag',app.tag_records[0]['draft']);self.assertNotIn('new_tag',app.tag_records[1]['draft'])
  app.tag_scope.set('All');app.register_unwanted('1girl');self.assertIn('1girl',app.tag_records[0]['draft'])
  app.tag_value.set('1girl, all_tag');app.bulk_tag_edit(False)
  self.assertIn('all_tag',app.tag_records[2]['draft']);self.assertNotIn('1girl',app.tag_records[2]['draft'])
  app.tag_scope.set('Filtered');app.set_tag_filter('long_hair');app.tag_value.set('filtered_tag');app.bulk_tag_edit(False)
  self.assertIn('filtered_tag',app.tag_records[0]['draft']);self.assertNotIn('filtered_tag',app.tag_records[1]['draft'])
  app.replace_image_tag(0,'long_hair','short_hair, ribbon');self.assertIn('ribbon',app.tag_records[0]['draft']);self.assertNotIn('long_hair',app.tag_records[0]['draft'])
  app.tag_scope.set('All');app.remove_unwanted();self.assertTrue(all('1girl' not in split_tags(r['draft']) for r in app.tag_records))
  drafts=[r['draft'] for r in app.tag_records]
  with patch('tag_editor_ui.messagebox.askyesno',return_value=False):app.clear_scoped_tags(False)
  self.assertEqual(drafts,[r['draft'] for r in app.tag_records])
  app.tag_category.set('Face')
  with patch('tag_editor_ui.messagebox.askyesno',return_value=True):app.clear_scoped_tags(True)
  self.assertTrue(all(not any(category_of(t)=='Face' for t in split_tags(r['draft'])) for r in app.tag_records))
  self.assertIn('ribbon',app.tag_records[0]['draft'])
  self.assertEqual(before,{p.name:p.read_bytes() for p in self.folder.iterdir()})
 def test_thumbnail_virtualization_and_chip_callback_cleanup(self):
  root,app=self.make_app();strip=app.tag_image_list
  app.tag_records=[dict(app.tag_records[0]) for _ in range(200)];app.refresh_tag_views();root.update()
  self.assertEqual(len(strip.get_children()),200);self.assertLess(len(strip.visible_photos),12)
  strip.yview('moveto',1);root.update();self.assertLess(len(strip.visible_photos),12);self.assertLessEqual(len(strip.cache),48)
  canvas=app.tag_cloud_canvas
  for _ in range(30):chip_flow(canvas,[('test',3)],lambda *_:None,remove=lambda *_:None,context=lambda *_:None)
  self.assertLess(len(canvas._tclCommands),15)
  app.assign_tag_category('long_hair','Chara')
  self.assertEqual(category_of('long_hair',app.tag_category_overrides),'Chara')
  self.assertTrue((app.engine.data/'tag-editor-settings.json').exists())
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
   root.update()
   self.assertTrue(any(app.tag_cloud_canvas.itemcget(i,'fill')==__import__('tag_theme').SELECT for i in app.tag_cloud_canvas.find_all()))
   app.tag_image_list.selection_set('0');app.select_tag_image();app.remove_one_tag(0,'1girl')
   self.assertEqual(dict(frequencies(app.tag_records)[1])['1girl'],1);self.assertIn('1girl',(self.folder/'a.txt').read_text())
  finally:
   for job in root.tk.splitlist(root.tk.call('after','info')):root.after_cancel(job)
   root.destroy()
 def test_reference_rows_edit_their_own_caption_and_stay_virtual(self):
  root,app=self.make_app();rows=app.tag_rows
  self.assertEqual(rows.ids,['0','1','2'])
  app.tag_image_list.selection_set('0');rows.see('1');root.update()
  tag_hit=next(h for h in rows.hits if h[1]=='tag' and h[2]=='1' and h[3]=='short_hair')
  bounds=tag_hit[0];event=SimpleNamespace(x=bounds[2]-3,y=(bounds[1]+bounds[3])/2-rows.canvas.canvasy(0))
  rows.clicked(event)
  self.assertNotIn('short_hair',app.tag_records[1]['draft']);self.assertIn('long_hair',app.tag_records[0]['draft'])
  self.assertIn('short_hair',(self.folder/'b.txt').read_text(encoding='utf-8-sig'))
  root.update();rows.see('0');root.update()
  hit=next(h for h in rows.hits if h[1]=='tag' and h[2]=='0' and h[3]=='long_hair')
  bounds=hit[0];event=SimpleNamespace(x=bounds[0]+4,y=(bounds[1]+bounds[3])/2-rows.canvas.canvasy(0))
  rows.clicked(event);self.assertEqual(app.tag_inline_editor.get(),'long_hair')
  app.cancel_inline_tag_edit();self.assertIsNone(app.tag_inline_editor)
  app.tag_records=[dict(app.tag_records[0]) for _ in range(400)];app.refresh_tag_views();root.update()
  self.assertEqual(len(rows.ids),400);self.assertLess(len(rows.visible_ids),10)

if __name__=='__main__':unittest.main()
