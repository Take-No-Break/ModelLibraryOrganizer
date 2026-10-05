"""Explicit move warning and in-app history browser."""
from pathlib import Path
import tkinter as tk
from core import read_json,atomic_json
from i18n import ttk,tr,LocalizedToplevel,LocalizedText,messagebox,filedialog

from restore_strings import WARNING

class RestoreUI:
 def confirm_move_warning(self):
  if self.preferences.get('skip_move_warning',False):return True
  win=LocalizedToplevel(self.root);win.title('保存場所を変更する前の警告');win.transient(self.root);win.grab_set();win.geometry('730x440')
  self.review_active=True;answer=[False];hide=tk.BooleanVar(value=False)
  body=LocalizedText(win,wrap='word',height=12);body.pack(fill='both',expand=True,padx=18,pady=15);body.insert('1.0',WARNING);body.configure(state='disabled')
  ttk.Checkbutton(win,text='この警告を再度表示しない（最終確認は残ります）',variable=hide).pack(anchor='w',padx=18)
  bar=ttk.Frame(win);bar.pack(fill='x',padx=18,pady=14)
  def finish(accepted):
   answer[0]=accepted
   if accepted:
    self.preferences['skip_move_warning']=hide.get();self.save_preferences();self.show_move_warning.set(not hide.get())
   win.destroy()
  ttk.Button(bar,text='はい（続ける）',command=lambda:finish(True)).pack(side='right',padx=5)
  no=ttk.Button(bar,text='いいえ（中止）',command=lambda:finish(False));no.pack(side='right',padx=5);no.focus_set()
  win.protocol('WM_DELETE_WINDOW',lambda:finish(False));win.bind('<Escape>',lambda e:finish(False))
  try:self.root.wait_window(win)
  finally:self.review_active=False
  return answer[0]

 def init_restore(self):
  page=self.pages['restore']
  ttk.Label(page,text='変更前の保存場所へ戻します。複数回変更した場合は、新しい履歴から順に戻してください。',wraplength=1100).pack(anchor='w',pady=6)
  bar=ttk.Frame(page);bar.pack(fill='x')
  ttk.Button(bar,text='履歴を更新',command=self.refresh_restore).pack(side='left')
  ttk.Button(bar,text='選択した履歴を元に戻す',command=self.restore_selected).pack(side='left',padx=5)
  ttk.Button(bar,text='履歴JSONを開く…',command=self.import_restore).pack(side='left')
  self.show_move_warning=tk.BooleanVar(value=not self.preferences.get('skip_move_warning',False))
  def toggle():self.preferences['skip_move_warning']=not self.show_move_warning.get();self.save_preferences()
  ttk.Checkbutton(bar,text='移動前の警告を表示',variable=self.show_move_warning,command=toggle).pack(side='right')
  self.restore_table=ttk.Treeview(page,columns=('time','count','status'),show='headings',height=8)
  for name,label,width in [('time','実行日時',260),('count','変更件数',100),('status','状態',240)]:self.restore_table.heading(name,text=label);self.restore_table.column(name,width=width)
  self.restore_table.pack(fill='both',expand=True,pady=8);self.restore_table.bind('<<TreeviewSelect>>',self.restore_details)
  self.restore_text=LocalizedText(page,height=12,wrap='word');self.restore_text.pack(fill='both',expand=True)
  ttk.Label(page,text=tr('履歴の保存場所：')+' '+str(self.engine.data/'history'),wraplength=1100).pack(anchor='w',pady=5)
  self.refresh_restore()

 def refresh_restore(self):
  self.restore_entries=[];self.restore_table.delete(*self.restore_table.get_children())
  for p in sorted((self.engine.data/'history').glob('*.json'),reverse=True):
   doc=read_json(p)
   if not isinstance(doc,dict) or not isinstance(doc.get('ops'),list):continue
   self.add_restore_entry(p,doc)
  self.restore_text.configure(state='normal');self.restore_text.delete('1.0','end');self.restore_text.configure(state='disabled')

 def add_restore_entry(self,path,doc):
  index=str(len(self.restore_entries));self.restore_entries.append((Path(path),doc))
  status='復元済み' if doc.get('restored') else '実行完了' if doc.get('complete') else '途中終了・確認が必要'
  self.restore_table.insert('','end',iid=index,values=(doc.get('created_at',Path(path).stem),len(doc.get('ops',[])),status))
  return index

 def restore_details(self,event=None):
  ids=self.restore_table.selection()
  if not ids:return
  path,doc=self.restore_entries[int(ids[0])]
  plans=doc.get('before_state',doc['ops']);lines=[tr('履歴ファイル：')+' '+str(path),tr('変更前 → 変更後'), '']
  for op in plans:
   lines.extend([op['source'],' → '+op['destination']])
   for link in op.get('links',[]):lines.append(' + '+link)
  if doc.get('retained_dirs'):lines.extend(['',tr('空でない等の理由で残したフォルダー：'),*doc['retained_dirs']])
  self.restore_text.configure(state='normal');self.restore_text.delete('1.0','end')
  # Paths and filenames are user data, not UI translation keys.
  tk.Text.insert(self.restore_text,'1.0','\n'.join(lines));self.restore_text.configure(state='disabled')

 def import_restore(self):
  if not self.ready():return
  filename=filedialog.askopenfilename(initialdir=self.engine.data/'history',filetypes=[('Move history','*.json')])
  if not filename:return
  doc=read_json(filename)
  if not isinstance(doc,dict) or not isinstance(doc.get('ops'),list) or 'root' not in doc:messagebox.showerror('確認が必要です','復元できる履歴ではありません');return
  index=self.add_restore_entry(filename,doc);self.restore_table.selection_set(index);self.restore_details()

 def restore_selected(self):
  if not self.ready():return
  ids=self.restore_table.selection()
  if not ids:messagebox.showinfo('選択','元に戻す履歴を選択してください。');return
  path,_=self.restore_entries[int(ids[0])];doc=read_json(path)
  if not doc or doc.get('restored'):messagebox.showinfo('確認','この履歴は復元済み、または読み込めません。');return
  if not messagebox.askyesno('復元の確認','選択した履歴の配置へ戻しますか？変更後のファイルや元パスに競合がある場合は停止します。今回作成したフォルダーは空の場合だけ削除します。'):return
  self.work(lambda:self.engine.rollback(path),'undone')
