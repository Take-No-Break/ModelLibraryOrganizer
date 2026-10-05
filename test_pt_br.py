import tempfile, unittest
from pathlib import Path
import tkinter as tk
import i18n
from locales import CATALOG, LANGS
from guide import GUIDE
from app import App

class BrazilianPortugueseTests(unittest.TestCase):
 def tearDown(self): i18n.set_language('ja')
 def test_catalog_and_choices(self):
  self.assertEqual(LANGS['pt-BR'], 'Português (Brasil)')
  self.assertTrue(all(key in CATALOG['pt-BR'] for key in CATALOG['en']))
  self.assertEqual(len(GUIDE['pt-BR']),5)
  i18n.set_language('pt-BR')
  self.assertEqual(i18n.tr('全件調査'),'Verificar tudo')
  self.assertEqual(i18n.tr('Copy'),'Copiar')
  self.assertEqual(i18n.tr('Image to Text'),'Image to Text')
  self.assertEqual(i18n.tr('About'),'About')
  self.assertEqual(i18n.tr('C:/models/All/Model.safetensors'),'C:/models/All/Model.safetensors')
  root=tk.Tk();root.withdraw()
  try:
   choice=i18n.ChoiceVar(root,value='分解版')
   self.assertEqual(root.getvar(choice._name),'Dividido em etapas')
   self.assertEqual(choice.get(),'分解版')
  finally:
    for timer in root.tk.splitlist(root.tk.call("after","info")):root.after_cancel(timer)
    root.destroy()
 def test_app_portuguese(self):
  from core import atomic_json
  with tempfile.TemporaryDirectory() as temp:
   data=Path(temp);atomic_json(data/'preferences.json',{'language':'pt-BR','offline':True})
   root=tk.Tk();root.withdraw()
   try:
    app=App(root,data);root.update()
    self.assertEqual(app.language.get(),'Português (Brasil)')
    self.assertEqual(i18n.tr('モデル一覧'),'Modelos')
    self.assertEqual(app.cap_template_mode.get(),'一体型')
    app.save_training_settings()
   finally:
    for timer in root.tk.splitlist(root.tk.call("after","info")):root.after_cancel(timer)
    root.destroy()

if __name__=='__main__':unittest.main()
