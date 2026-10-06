import tempfile,unittest,tkinter as tk,re
from pathlib import Path
from app import App
from core import atomic_json,read_json
from features import family_relation,pair_key
import i18n

class Release17Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.data=Path(self.tmp.name)
  atomic_json(self.data/'preferences.json',{'language':'es'})
  self.root=tk.Tk();self.root.withdraw();self.app=App(self.root,self.data);self.root.update()
 def tearDown(self):
  for j in self.root.tk.splitlist(self.root.tk.call('after','info')):self.root.after_cancel(j)
  self.root.update_idletasks();self.root.destroy();self.tmp.cleanup();i18n.set_language('ja')
 def widgets(self,parent):
  for child in parent.winfo_children():yield child;yield from self.widgets(child)
 def test_spanish_static_ui_and_about(self):
  bad=[];about=False
  for w in self.widgets(self.root):
   texts=[]
   if 'text' in w.keys():texts.append(str(w.cget('text')))
   if 'textvariable' in w.keys() and w.cget('textvariable'):
    texts.append(str(w.getvar(w.cget('textvariable'))))
   if isinstance(w,tk.Text):
    text=w.get('1.0','end');texts.append(text)
    if 'A desktop utility for inspecting' in text:about=True
   for text in texts:
    if re.search('[ぁ-んァ-ヶ一-龯]',text) and text not in i18n.LANGS.values():bad.append(text)
  self.assertEqual(bad,[]);self.assertTrue(about)
 def test_families(self):
  for a in ['SDXL','Pony','Illustrious','NoobAI','Animagine']:
   for b in ['SDXL','Pony','Illustrious','NoobAI','Animagine']:
    self.assertEqual(family_relation(a,b),'same' if a==b else 'related')
  self.assertEqual(family_relation('Anima','SDXL'),'different')
  self.assertEqual(family_relation('Unknown','Unknown'),'unknown')
 def test_pair_edit_persisted_separately(self):
  a=self.data/'lora.safetensors';b=self.data/'base.safetensors';a.touch();b.touch()
  rows=[{'source':str(a),'kind':'loras','family':'Illustrious','sha':'a'*64},{'source':str(b),'kind':'checkpoints','family':'SDXL','sha':'b'*64}]
  self.app.rows=rows;self.app.populate_compatibility()
  self.assertEqual(self.app.compat_table.item('0','tags'),('related',))
  self.app.compat_table.selection_set('0');self.app.select_compat_pair()
  self.app.compat_rating.set('使用できた（緑）');self.app.compat_note.set('My test');self.app.save_compat_pair()
  self.assertEqual(self.app.compat_table.item('0','tags'),('same',))
  self.assertEqual(rows[0]['family'],'Illustrious')
  self.assertEqual(read_json(self.data/'compatibility-assessments.json',{})[pair_key(*rows)]['note'],'My test')
  self.app.compat_rating.set('自動判定');self.app.save_compat_pair()
  self.assertEqual(self.app.compat_table.item('0','tags'),('related',))
 def test_specific_checkpoint_selection(self):
  paths=[self.data/name for name in ['adapter.safetensors','one.safetensors','two.safetensors']]
  for p in paths:p.touch()
  rows=[{'source':str(p),'kind':'loras' if i==0 else 'checkpoints','family':'Pony' if i<2 else 'Anima','sha':str(i)*64} for i,p in enumerate(paths)]
  self.app.rows=rows;self.app.populate_compatibility()
  self.assertEqual(len(self.app.compat_checkpoints),2)
  self.assertEqual(self.app.compat_pairs[0]['checkpoint'],str(paths[1]))
  self.assertEqual(self.app.compat_table.item('0','tags'),('same',))
  self.app.compat_checkpoint_choice.current(1);self.app.compat_selected()
  self.assertEqual(len(self.app.compat_table.get_children()),1)
  self.assertEqual(self.app.compat_pairs[0]['checkpoint'],str(paths[2]))
  self.assertEqual(self.app.compat_table.item('0','tags'),('different',))
  self.assertIn(str(paths[2]),self.app.compat_summary.get('1.0','end'))
  self.app.compat_rating.set('要調整（黄）');self.app.save_compat_pair()
  self.assertEqual(read_json(self.data/'compatibility-assessments.json',{})[pair_key(rows[0],rows[2])]['rating'],'要調整（黄）')
  self.app.compat_checkpoint_choice.current(0);self.app.compat_selected()
  self.assertEqual(self.app.compat_table.item('0','tags'),('same',))
 def test_language_change_and_all_filter(self):
  self.app.scan_dir.set('C:/my models');self.app.language.set('日本語');self.app.change_language();self.root.update()
  self.assertEqual(i18n.LANG,'ja');self.assertEqual(self.app.scan_dir.get(),'C:/my models')
  self.app.language.set('Español');self.app.change_language();self.root.update()
  self.assertEqual(i18n.LANG,'es')
  self.app.select_page(self.app.pages['tools']);self.root.update();self.app.filter.set('判別できなかったモデル')
  self.app.select_page(self.app.pages['models']);self.root.update();self.assertEqual(self.app.filter.get(),'すべて')

if __name__=='__main__':unittest.main()
