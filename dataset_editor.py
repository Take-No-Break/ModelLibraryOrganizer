"""Dataset editor UI. All writes are explicit and use dataset_files conflict checks."""
import tkinter as tk
from pathlib import Path
from PIL import Image,ImageTk,ImageOps
from i18n import ttk,filedialog,messagebox,ChoiceVar,StatusVar,tr
from dataset_files import list_dataset,read_caption,make_change,apply_changes,transform_caption,undo_changes

class DatasetEditor:
 def init_text_editor(self):
  page=self.pages['caption_texts'];self.editing_item=None;self.editing_state=None;self.edit_dirty=False;self.editor_loading=False;self.dataset_rows=[]
  ttk.Label(page,text='画像と同名の学習用TXTを編集します。他のソフトで作ったTXTも利用できます。保存すると元のTXTが更新されます。',wraplength=1100).pack(anchor='w')
  bar=ttk.Frame(page);bar.pack(fill='x',pady=5)
  self.dataset_path=tk.StringVar(value=self.training_settings.get('image_folder',''));self.dataset_recursive=tk.BooleanVar(value=False)
  ttk.Entry(bar,textvariable=self.dataset_path).pack(side='left',fill='x',expand=True)
  ttk.Button(bar,text='選択…',command=lambda:self.choose_root(self.dataset_path)).pack(side='left')
  ttk.Checkbutton(bar,text='サブフォルダー',variable=self.dataset_recursive).pack(side='left')
  self._dataset_timer=None;self._dataset_loaded=None
  self.dataset_path.trace_add('write',lambda *args:self.schedule_dataset_load())
  self.dataset_recursive.trace_add('write',lambda *args:self.schedule_dataset_load())
  self.root.after(600,self.schedule_dataset_load)
  actions=ttk.Frame(page);actions.pack(fill='x')
  ttk.Button(actions,text='すべて選択',command=lambda:self.dataset_list.selection_set(self.dataset_list.get_children())).pack(side='left')
  ttk.Button(actions,text='編集中のTXTを保存',command=lambda:self.save_editor(notify=True)).pack(side='left',padx=5)
  ttk.Button(actions,text='TXT変更を元に戻す…',command=self.undo_texts).pack(side='left')
  self.editor_status=StatusVar(value='未保存の変更は、一覧切替・終了時に確認します。');ttk.Label(actions,textvariable=self.editor_status).pack(side='left',padx=8)
  panes=ttk.Panedwindow(page,orient='horizontal');panes.pack(fill='both',expand=True,pady=6)
  left=ttk.Frame(panes);right=ttk.Frame(panes);panes.add(left,weight=2);panes.add(right,weight=3)
  self.dataset_list=ttk.Treeview(left,columns=('file','status'),show='headings',selectmode='extended',height=10)
  self.dataset_list.heading('file',text='画像／TXT');self.dataset_list.heading('status',text='TXT')
  self.dataset_list.column('file',width=260);self.dataset_list.column('status',width=90)
  scroll=ttk.Scrollbar(left,command=self.dataset_list.yview);scroll.pack(side='right',fill='y');self.dataset_list.configure(yscrollcommand=scroll.set);self.dataset_list.pack(fill='both',expand=True)
  self.dataset_list.bind('<<TreeviewSelect>>',self.select_dataset);self.dataset_list.bind('<Control-a>',lambda e:self.dataset_list.selection_set(self.dataset_list.get_children()))
  self.editor_image=ttk.Label(right,text=tr('画像を選択'),anchor='center');self.editor_image.pack(fill='x')
  self.editor=tk.Text(right,height=9,wrap='word',undo=True);self.editor.pack(fill='both',expand=True)
  self.editor.bind('<<Modified>>',self.editor_modified)
  bulk=ttk.LabelFrame(page,text='選択したTXTを一括編集（変更プレビュー後に保存）',padding=6);bulk.pack(fill='x')
  self.bulk_op=ChoiceVar(value='< >で囲む');ttk.Combobox(bulk,textvariable=self.bulk_op,state='readonly',values=['< >で囲む','先頭に追加','末尾に追加','削除','置換'],width=14).grid(row=0,column=0,padx=3)
  self.bulk_value=tk.StringVar();self.bulk_replace=tk.StringVar()
  ttk.Label(bulk,text='対象の語／追加する語').grid(row=0,column=1);ttk.Entry(bulk,textvariable=self.bulk_value,width=23).grid(row=0,column=2,padx=3)
  ttk.Label(bulk,text='置換後').grid(row=0,column=3);ttk.Entry(bulk,textvariable=self.bulk_replace,width=23).grid(row=0,column=4,padx=3)
  self.bulk_match=ChoiceVar(value='タグ完全一致');ttk.Combobox(bulk,textvariable=self.bulk_match,state='readonly',values=['タグ完全一致','単語境界'],width=12).grid(row=1,column=0,pady=4)
  ttk.Button(bulk,text='変更をプレビュー',command=self.preview_bulk).grid(row=1,column=4,padx=4,sticky='e')
  ttk.Label(bulk,text='< >はEmbeddingの設定と一致させる場合などに使用。LoRAの普通のトリガーワードに必須ではありません。',wraplength=1100).grid(row=2,column=0,columnspan=5,sticky='w',pady=4)
 def editor_modified(self,event=None):
  if self.editor.edit_modified():
   if not self.editor_loading:self.edit_dirty=True;self.editor_status.set('未保存の変更あり')
   self.editor.edit_modified(False)
 def editor_guard(self):
  if not self.edit_dirty:return True
  answer=messagebox.askyesnocancel('未保存のTXT','変更を保存しますか？ はい＝保存、いいえ＝破棄、キャンセル＝戻る。')
  if answer is None:return False
  if answer:return self.save_editor()
  self.edit_dirty=False;return True
 def schedule_dataset_load(self):
  if self._dataset_timer:self.root.after_cancel(self._dataset_timer)
  self._dataset_timer=self.root.after(450,self.load_dataset)
 def load_dataset(self):
  self._dataset_timer=None
  folder=self.dataset_path.get().strip();recursive=self.dataset_recursive.get()
  if not folder or not Path(folder).is_dir():return
  key=(str(Path(folder).resolve()),recursive)
  if key==self._dataset_loaded:return
  if self.busy or getattr(self,'review_active',False):self.schedule_dataset_load();return
  if not self.editor_guard():
   if self._dataset_loaded:self.dataset_path.set(self._dataset_loaded[0])
   return
  self.work(lambda:(key,list_dataset(folder,recursive)),'dataset_auto')
 def receive_auto_dataset(self,value):
  key,rows=value
  if key!=(str(Path(self.dataset_path.get()).resolve()),self.dataset_recursive.get()):self.schedule_dataset_load();return
  self._dataset_loaded=key;self.receive_dataset(rows,select=False)
 def receive_dataset(self,rows,select=True):
  self.dataset_rows=rows;self.editing_item=None;self.editing_state=None;self.dataset_list.delete(*self.dataset_list.get_children())
  self.editor_loading=True;self.editor.configure(state='normal');self.editor.delete('1.0','end');self.editor.edit_modified(False);self.editor_loading=False;self.edit_dirty=False
  self.editor_image.configure(image='',text=tr('画像を選択'));self.editor_image.image=None
  for i,item in enumerate(rows):
   label=self.short_path(item['images'][0] if item['images'] else item['text_path'],self.dataset_path.get())
   status='同名画像が複数' if len(item['images'])>1 else 'あり' if Path(item['text_path']).exists() else '未作成'
   self.dataset_list.insert('','end',iid=str(i),values=(label,status))
  self.editor_status.set(f'{len(rows)} TXT targets')
  if select:self.select_page(self.pages['texts'])
 def select_dataset(self,event=None):
  ids=self.dataset_list.selection()
  if not ids:return
  focus=self.dataset_list.focus();index=int(focus if focus in ids else ids[0]);item=self.dataset_rows[index]
  if self.editing_item==item:return
  if not self.editor_guard():return
  try:state=read_caption(item['text_path'])
  except Exception as exc:messagebox.showerror('TXTを読み込めません',str(exc));return
  self.editing_item=item;self.editing_state=state;self.editor_loading=True
  self.editor.delete('1.0','end');self.editor.insert('1.0',state['text']);self.editor.edit_reset();self.editor.edit_modified(False);self.editor_loading=False;self.edit_dirty=False
  self.editor_status.set(item['text_path']);self.editor_image.configure(image='',text=tr('対応する画像なし'));self.editor_image.image=None
  if item['images']:
   try:
    with Image.open(item['images'][0]) as src:
     image=ImageOps.exif_transpose(src).convert('RGB');image.thumbnail((480,230))
    photo=ImageTk.PhotoImage(image,master=self.editor_image);self.editor_image.configure(image=photo,text='');self.editor_image.image=photo
   except Exception as exc:self.editor_image.configure(text=tr('画像を表示できません: ')+str(exc))
 def save_editor(self,notify=False):
  if self.busy:messagebox.showinfo('処理中','処理の完了を待ってください。');return False
  if not self.editing_item:return True
  try:
   change=make_change(self.editing_item['text_path'],self.editor.get('1.0','end-1c'),self.editing_state)
   result=apply_changes([change],self.engine.data);self.editing_state=read_caption(self.editing_item['text_path']);self.edit_dirty=False;self.editor_status.set('保存済み / '+str(result['count'])+' file(s)')
   if notify:self.notify_result('TXT保存完了',self.editing_item['text_path'])
   else:self.record_result('TXT保存完了',self.editing_item['text_path'])
   return True
  except Exception as exc:messagebox.showerror('保存できません',str(exc));return False
 def preview_bulk(self):
  if not self.ready() or not self.editor_guard():return
  ids=self.dataset_list.selection()
  if not ids:messagebox.showinfo('選択','一括編集するTXTを選択してください。Ctrl/Shiftまたは「すべて選択」が使えます。');return
  operations={'先頭に追加':'prepend','末尾に追加':'append','削除':'remove','置換':'replace','< >で囲む':'wrap'}
  op=operations[self.bulk_op.get()];value=self.bulk_value.get();replacement=self.bulk_replace.get();match='tag' if self.bulk_match.get()=='タグ完全一致' else 'word'
  items=[dict(self.dataset_rows[int(i)]) for i in ids]
  def prepare():
   changes=[]
   for item in items:
    state=read_caption(item['text_path']);text=transform_caption(state['text'],op,value,replacement,match)
    if text!=state['text']:changes.append(make_change(item['text_path'],text,state))
   return changes
  self.work(prepare,'caption_plan')
 def show_caption_plan(self,changes):
  if not changes:self.show_text('変更なし','対象のTXTに変更はありません。');return
  self.caption_plan=changes
  self.record_result('キャプション解析・編集結果',str(len(changes))+' files — 未保存\n\n'+'\n\n'.join(c['path']+'\nBEFORE\n'+c['before_text']+'\nAFTER\n'+c['after_text'] for c in changes))
  page=self.open_panel('results','TXT変更プレビュー — '+str(len(changes))+' files')
  ttk.Label(page,text='保存すると元のTXTを変更します。既存TXTはアプリ内caption-backupsにバックアップします。',wraplength=1100).pack(anchor='w')
  pane=ttk.Panedwindow(page,orient='horizontal');pane.pack(fill='both',expand=True)
  names=tk.Listbox(pane,width=38,exportselection=False);box=tk.Text(pane,wrap='word');pane.add(names,weight=1);pane.add(box,weight=3)
  for c in changes:names.insert('end',c['path'])
  def show(event=None):
   ids=names.curselection()
   if not ids:return
   c=changes[ids[0]];box.configure(state='normal');box.delete('1.0','end');box.insert('1.0','BEFORE\n'+c['before_text']+'\n\nAFTER\n'+c['after_text']);box.configure(state='disabled')
  names.bind('<<ListboxSelect>>',show);names.selection_set(0);show()
  def save():
   if not self.ready():return
   if messagebox.askyesno('TXT保存の確認',f'{len(changes)}個のTXTを作成／更新しますか？ 画像は変更しません。'):
    page.destroy();self.work(lambda:apply_changes(changes,self.engine.data),'caption_saved')
  button=ttk.Button(page,text='この変更を保存',command=save);button.pack(anchor='e',pady=8)
 def captions_saved(self,result):
  self.edit_dirty=False
  if self.dataset_path.get() and Path(self.dataset_path.get()).is_dir():self.receive_dataset(list_dataset(self.dataset_path.get(),self.dataset_recursive.get()),select=False)
  self.show_text('TXT保存完了',f"{result['count']} file(s)\nBackup manifest: {result['manifest']}")
 def undo_texts(self):
  if not self.ready() or not self.editor_guard():return
  manifest=filedialog.askopenfilename(initialdir=self.engine.data/'caption-backups',filetypes=[('Caption backup manifest','manifest.json')])
  if manifest and messagebox.askyesno('TXT復元','選択した変更を元に戻しますか？ 後から編集されたTXTがあれば停止します。'):
   self.work(lambda:('TXT復元完了',str(undo_changes(manifest,self.engine.data))+' file(s)'),'report')
