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
  from display import center_popup
  center_popup(win,self.root)
  try:self.root.wait_window(win)
  finally:self.review_active=False
  return answer[0]

 def init_restore(self):
  page=self.pages['restore']
  ttk.Label(page,text='選択した履歴の変更前の配置へ戻します。復元済みの履歴も再確認できます。記録済みの場所から同じファイルを特定できない場合や競合がある場合は停止します。',wraplength=1100).pack(anchor='w',pady=6)
  from caption_labels import RESTORE_NOTICE
  import i18n
  self.restore_notice=ttk.Label(page,text=RESTORE_NOTICE.get(i18n.LANG,RESTORE_NOTICE['en']),wraplength=1000)
  self.restore_notice.pack(anchor='w',pady=5)
  bar=ttk.Frame(page);bar.pack(fill='x')
  ttk.Button(bar,text='履歴JSONを開く…',command=self.import_restore).pack(side='left')
  self.restore_action=ttk.Button(bar,text='この配置へ戻す…',command=self.restore_selected,state='disabled');self.restore_action.pack(side='left',padx=6)
  self.restore_reason=tk.StringVar(value='')
  ttk.Label(page,textvariable=self.restore_reason,wraplength=1000).pack(anchor='w',pady=4)
  self.show_move_warning=tk.BooleanVar(value=not self.preferences.get('skip_move_warning',False))
  def toggle():self.preferences['skip_move_warning']=not self.show_move_warning.get();self.save_preferences()
  ttk.Checkbutton(bar,text='移動前の警告を表示',variable=self.show_move_warning,command=toggle).pack(side='right')
  self.restore_table=ttk.Treeview(page,columns=('time','count','status'),show='headings',height=8)
  for name,label,width in [('time','実行日時',260),('count','記録件数',100),('status','状態',240)]:self.restore_table.heading(name,text=label);self.restore_table.column(name,width=width)
  self.restore_table.pack(fill='both',expand=True,pady=8);self.restore_table.bind('<<TreeviewSelect>>',self.restore_details)
  self.restore_text=LocalizedText(page,height=12,wrap='word');self.restore_text.pack(fill='both',expand=True)
  ttk.Label(page,text=tr('履歴の保存場所：')+' '+str(self.engine.data/'scan-history')+' / '+str(self.engine.data/'history'),wraplength=1100).pack(anchor='w',pady=5)
  self.refresh_restore()

 def refresh_restore(self):
  self.restore_entries=[];self.restore_table.delete(*self.restore_table.get_children())
  paths=[*(self.engine.data/'history').glob('*.json'),*(self.engine.data/'scan-history').glob('*.json')]
  for p in sorted(paths,key=lambda p:p.name,reverse=True):
   doc=read_json(p)
   if not isinstance(doc,dict) or not isinstance(doc.get('ops'),list):continue
   self.add_restore_entry(p,doc)
  self.restore_action.configure(state='disabled');self.restore_reason.set(tr('元に戻す履歴を選択してください。'))
  self.restore_text.configure(state='normal');self.restore_text.delete('1.0','end');self.restore_text.configure(state='disabled')

 def add_restore_entry(self,path,doc):
  index=str(len(self.restore_entries));self.restore_entries.append((Path(path),doc))
  status='復元済み' if doc.get('restored') else '実行完了' if doc.get('complete') else '途中終了・確認が必要'
  if doc.get('kind')=='scan_snapshot':
   from scan_history import journals_for
   try:status='調査前の配置記録（変更なし）' if not doc.get('move_journals') else '変更履歴から復元可能' if journals_for(path) else '復元済み'
   except ValueError:status='途中終了・確認が必要'
  self.restore_table.insert('','end',iid=index,values=(doc.get('created_at',Path(path).stem),len(doc.get('files',doc.get('ops',[]))),status))
  return index

 def restore_details(self,event=None):
  ids=self.restore_table.selection()
  if not ids:return
  path,doc=self.restore_entries[int(ids[0])]
  self.restore_action.configure(state='disabled')
  import i18n
  def reason(ja,en):self.restore_reason.set(ja if i18n.LANG=='ja' else en)
  if doc.get('kind')=='scan_snapshot':
   from scan_history import journals_for
   text=tr('調査前の配置記録')+'\n'+str(path)+'\n\n'+tr('ファイル数：')+str(len(doc['files']))+' / '+tr('フォルダー数：')+str(len(doc['folders']))+'\n\n'
   text+=tr('調査だけでは移動していません。整理を実行すると復元用の変更履歴が関連付けられます。')+'\n\n'
   text+='\n'.join(f['path'] for f in doc['files'])
   text+='\n\n'+tr('関連する変更履歴：')+'\n'+'\n'.join(doc.get('move_journals',[]))
   self.restore_text.configure(state='normal');self.restore_text.delete('1.0','end');tk.Text.insert(self.restore_text,'1.0',text);self.restore_text.configure(state='disabled')
   try:
    if journals_for(path):
     self.restore_action.configure(state='normal');reason('関連する変更履歴を使って復元できます。','Restore is available using linked move history.')
    elif doc.get('move_journals'):
     self.restore_action.configure(state='normal');reason('以前に復元した履歴です。現在の記録済みファイル位置を再確認して復元できます。','Previously restored. The current recorded locations will be checked again.')
    else:reason('このJSONは調査時の配置記録です。移動履歴が関連付いていないため、この記録からは復元できません。実際に整理を実行した日時の変更履歴を選んでください。','This JSON is a scan inventory with no linked moves. Select the move history from when organization was executed.')
   except ValueError as error:
    self.restore_reason.set(str(error))
    self.restore_text.configure(state='normal');tk.Text.insert(self.restore_text,'end','\n\n'+str(error));self.restore_text.configure(state='disabled')
   return
  if doc.get('ops'):
   self.restore_action.configure(state='normal');reason('復元可能な変更履歴です。ボタンで確認してから復元します。','Move history is available. The button asks for confirmation before restoring.')
  elif doc.get('restored'):reason('この履歴はすでに復元されています。','This history has already been restored.')
  else:reason('この履歴には復元する変更がありません。','This history contains no changes to restore.')
  plans=doc.get('before_state',doc['ops']);lines=[tr('履歴ファイル：')+' '+str(path),tr('変更前 → 変更後'), '']
  for op in plans:
   lines.extend([op['source'],' → '+op['destination']])
   for link in op.get('links',[]):lines.append(' + '+link)
  created=[item['path'] for item in doc.get('created_dirs',[]) if isinstance(item,dict) and item.get('path')]
  if created:lines.extend(['','Created folders:',*created])
  if doc.get('retained_dirs'):lines.extend(['',tr('空でない等の理由で残したフォルダー：'),*doc['retained_dirs']])
  self.restore_text.configure(state='normal');self.restore_text.delete('1.0','end')
  # Paths and filenames are user data, not UI translation keys.
  tk.Text.insert(self.restore_text,'1.0','\n'.join(lines));self.restore_text.configure(state='disabled')
  from display import highlight_folder_paths
  highlight_folder_paths(self.restore_text,created)

 def import_restore(self):
  if not self.ready():return
  filename=filedialog.askopenfilename(initialdir=self.engine.data/'history',filetypes=[('Move history','*.json')])
  if not filename:return
  doc=read_json(filename)
  if not isinstance(doc,dict) or not isinstance(doc.get('ops'),list) or 'root' not in doc:messagebox.showerror('確認が必要です','復元できる履歴ではありません');return
  if doc.get('kind')=='scan_snapshot' and (not isinstance(doc.get('files'),list) or not isinstance(doc.get('folders'),list) or not isinstance(doc.get('move_journals'),list) or any(not isinstance(f,dict) or not isinstance(f.get('path'),str) for f in doc['files'])):
   messagebox.showerror('確認が必要です','復元できる履歴ではありません');return
  index=self.add_restore_entry(filename,doc);self.restore_table.selection_set(index);self.restore_details()

 def restore_selected(self):
  if not self.ready():return
  ids=self.restore_table.selection()
  if not ids:messagebox.showinfo('選択','元に戻す履歴を選択してください。');return
  path,_=self.restore_entries[int(ids[0])];doc=read_json(path)
  if not doc:messagebox.showinfo('確認','この履歴は復元済み、または読み込めません。');return
  if not messagebox.askyesno('復元の確認','選択した履歴の配置へ戻しますか？変更後のファイルや元パスに競合がある場合は停止します。今回作成したフォルダーは空の場合だけ削除します。'):return
  from history_layout import restore_layout
  self.work(lambda:restore_layout(self.engine,path),'undone')
