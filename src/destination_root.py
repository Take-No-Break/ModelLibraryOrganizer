"""Destination root hints; never silently reroute a user's files."""
from pathlib import Path
import tkinter as tk
from core import CATEGORIES
from i18n import tr,messagebox

HINT='例：C:/ComfyUI-Shared/models（lorasなどの種類別フォルダーではなく、models全体）'
NOTE='保存先の下に loras・checkpoints・vae・embeddings などを作成します。既存フォルダーは再利用し、移動前に確認します。'
WARNING='保存先が種類別フォルダーの中です。このままだと、その中に別の種類のフォルダーが作られます。\n\n推奨する保存先へ変更しますか？'
def suggested_root(value):
 p=Path(value)
 for ancestor in p.parents:
  if ancestor.name.casefold()=='models':return ancestor
 if p.name.casefold() in {c.casefold() for c in CATEGORIES}:return p.parent
 return None

def confirm_root(app):
 value=app.target_dir.get().strip()
 if not value:return False
 suggested=suggested_root(value)
 if suggested is None:return True
 if messagebox.askyesno(tr('保存先の確認'),tr(WARNING)+'\n\n'+str(suggested),parent=app.root):
  app.target_dir.set(str(suggested));return True
 return False

def placeholder(entry,variable):
 label=tk.Label(entry,text=tr(HINT),foreground='#707070',anchor='w',font=('Yu Gothic UI',9))
 def refresh(*args):
  if variable.get() or entry.focus_get()==entry:label.place_forget()
  else:label.place(x=4,y=2,relwidth=.98,relheight=.85)
 label.bind('<Button-1>',lambda e:entry.focus_set())
 entry.bind('<FocusIn>',refresh,add='+');entry.bind('<FocusOut>',refresh,add='+')
 variable.trace_add('write',refresh);entry.after_idle(refresh)

from locales import CATALOG
_TRANSLATIONS={"en":["Example: C:/ComfyUI-Shared/models (the models root, not loras)","Creates loras, checkpoints, vae, embeddings, etc. under this folder. Existing folders are reused; moves require review.","This destination is inside a model-type folder. Other type folders would be created inside it. Switch to the recommended root?"],"es":["Ejemplo: C:/ComfyUI-Shared/models (raíz models, no loras)","Crea loras, checkpoints, vae, embeddings, etc. dentro del destino. Reutiliza carpetas existentes; revise los movimientos.","El destino está dentro de una carpeta de tipo. Se crearían otros tipos dentro de ella. ¿Cambiar a la raíz recomendada?"],"zh-CN":["示例：C:/ComfyUI-Shared/models（models 根目录，不是 loras）","在目标下创建 loras、checkpoints、vae、embeddings 等目录。复用现有目录，移动前审核。","目标位于类型目录内部，其他类型目录会建在其中。改为推荐的根目录吗？"],"zh-TW":["範例：C:/ComfyUI-Shared/models（models 根目錄，不是 loras）","在目標下建立 loras、checkpoints、vae、embeddings 等目錄。重用既有目錄，移動前確認。","目標位於類型目錄內，其他類型目錄會建在其中。改為建議的根目錄嗎？"],"pt-BR":["Exemplo: C:/ComfyUI-Shared/models (raiz models, não loras)","Cria loras, checkpoints, vae, embeddings etc. no destino. Reutiliza pastas existentes; revise antes de mover.","O destino está dentro de uma pasta de tipo. Outros tipos seriam criados dentro dela. Usar a raiz recomendada?"],"de":["Beispiel: C:/ComfyUI-Shared/models (models-Stammordner, nicht loras)","Erstellt loras, checkpoints, vae, embeddings usw. unter dem Ziel. Bestehende Ordner werden verwendet; Verschiebungen vorher prüfen.","Das Ziel liegt in einem Typordner. Andere Typordner würden darin erstellt. Zum empfohlenen Stammordner wechseln?"],"th":["ตัวอย่าง: C:/ComfyUI-Shared/models (โฟลเดอร์หลัก models ไม่ใช่ loras)","สร้าง loras, checkpoints, vae, embeddings ใต้โฟลเดอร์นี้ ใช้โฟลเดอร์เดิมได้ ตรวจสอบก่อนย้าย","ปลายทางอยู่ในโฟลเดอร์ประเภทโมเดล จะสร้างประเภทอื่นไว้ข้างใน เปลี่ยนเป็นโฟลเดอร์หลักที่แนะนำหรือไม่?"]}
for code,values in _TRANSLATIONS.items():
 if code in CATALOG:CATALOG[code].update(dict(zip((HINT,NOTE,WARNING),values)))
