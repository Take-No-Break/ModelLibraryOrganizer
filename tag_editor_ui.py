import tkinter as tk
from pathlib import Path
from PIL import Image,ImageTk,ImageOps
from i18n import ttk,tr,messagebox,filedialog,LocalizedToplevel
from dataset_files import apply_changes
from tag_dataset import load_tags,split_tags,frequencies,edit_tags,tag_changes
from locales import CATALOG

TAG_STRINGS={
 'TXT内のタグを、登場するファイル数の多い順に表示します。同じTXT内の重複は1回と数えます。':'Ranks tags by the number of caption TXT files containing them. Repetition in one TXT counts once.',
 'タグをクリックして画像を絞り込み、×で削除できます。変更は保存するまで元のTXTに反映されません。':'Click a tag to filter images; click × to remove it. Changes affect original TXT only when saved.',
 'タグを検索':'Find tag','順位':'Rank','登場TXT数':'TXT count','出現率':'Frequency',
 '選択した画像に追加':'Add to selected','選択した画像から削除':'Remove from selected',
 '絞り込みを解除':'Clear filter','タグをクリックして編集':'Click tags to edit',
 'すべての変更を保存':'Save all changes','未保存のタグ変更':'Unsaved tag edits',
 'タグ変更プレビュー':'Tag change preview','変更を破棄してフォルダーを読み込みますか？':'Discard tag edits and reload the folder?',
 'ランキングからこのタグで絞り込む':'Filter Tag editor by this tag',
 'ランキングはモデルの確信度ではありません。例：200個のTXTのうち100個に登場＝50%。':'This is usage frequency, not model confidence. Example: present in 100 of 200 TXT files = 50%.',
 '再読み込み':'Reload',
}
CATALOG['en'].update(TAG_STRINGS)
PT={
 'TXT内のタグを、登場するファイル数の多い順に表示します。同じTXT内の重複は1回と数えます。':'Ordena as tags pela quantidade de arquivos TXT que as contêm. Repetições no mesmo TXT contam uma vez.',
 'タグをクリックして画像を絞り込み、×で削除できます。変更は保存するまで元のTXTに反映されません。':'Clique em uma tag para filtrar imagens e em × para removê-la. O TXT original só muda ao salvar.',
 'タグを検索':'Pesquisar tag','順位':'Posição','登場TXT数':'Quantidade de TXT','出現率':'Frequência',
 '選択した画像に追加':'Adicionar às selecionadas','選択した画像から削除':'Remover das selecionadas',
 '絞り込みを解除':'Limpar filtro','タグをクリックして編集':'Clique nas tags para editar',
 'すべての変更を保存':'Salvar todas as alterações','未保存のタグ変更':'Tags não salvas',
 'タグ変更プレビュー':'Prévia das alterações de tags','変更を破棄してフォルダーを読み込みますか？':'Descartar alterações e carregar a pasta?',
 'ランキングからこのタグで絞り込む':'Filtrar por esta tag no editor',
 'ランキングはモデルの確信度ではありません。例：200個のTXTのうち100個に登場＝50%。':'É frequência de uso, não confiança do modelo. Exemplo: em 100 de 200 TXT = 50%.',
 '再読み込み':'Recarregar',
}
for key,english in TAG_STRINGS.items():
 CATALOG['pt-BR'][key]=PT[key];CATALOG['pt-BR'][english]=PT[key]

class TagEditorUI:
 def init_tag_editor(self):
  self.tag_records=[];self.tag_loaded_key=None;self.tag_load_timer=None;self.tag_filter='';self.tag_selected_index=None
  self.tag_folder=tk.StringVar(value=self.dataset_path.get());self.tag_recursive=tk.BooleanVar(value=False)
  self.tag_search=tk.StringVar();self.tag_value=tk.StringVar()
  for key in ('tag_ranking','tag_editor'):
   page=self.pages[key];bar=ttk.Frame(page);bar.pack(fill='x',pady=6)
   ttk.Entry(bar,textvariable=self.tag_folder).pack(side='left',fill='x',expand=True)
   ttk.Button(bar,text='選択…',command=lambda:self.choose_root(self.tag_folder)).pack(side='left')
   ttk.Checkbutton(bar,text='サブフォルダー',variable=self.tag_recursive).pack(side='left',padx=5)
   ttk.Button(bar,text='再読み込み',command=lambda:self.reload_tags(True)).pack(side='left')
  page=self.pages['tag_ranking']
  ttk.Label(page,text='TXT内のタグを、登場するファイル数の多い順に表示します。同じTXT内の重複は1回と数えます。',wraplength=1100).pack(anchor='w')
  bar=ttk.Frame(page);bar.pack(fill='x',pady=5);ttk.Label(bar,text='タグを検索').pack(side='left')
  ttk.Entry(bar,textvariable=self.tag_search).pack(side='left',fill='x',expand=True,padx=6)
  self.tag_rank_status=ttk.Label(page,text='—');self.tag_rank_status.pack(anchor='w',pady=6)
  pane=ttk.Frame(page);pane.pack(fill='both',expand=True)
  self.tag_rank_table=ttk.Treeview(pane,columns=('rank','tag','count','percent'),show='headings',height=12)
  for c,label,w in [('rank','順位',70),('tag','タグ',500),('count','登場TXT数',140),('percent','出現率',150)]:self.tag_rank_table.heading(c,text=label);self.tag_rank_table.column(c,width=w)
  self.tag_rank_table.pack(side='left',fill='both',expand=True);scroll=ttk.Scrollbar(pane,command=self.tag_rank_table.yview);scroll.pack(side='right',fill='y');self.tag_rank_table.configure(yscrollcommand=scroll.set)
  self.tag_rank_table.bind('<<TreeviewSelect>>',self.show_tag_frequency)
  self.tag_frequency_bar=ttk.Progressbar(page,maximum=100,mode='determinate');self.tag_frequency_bar.pack(fill='x',pady=8)
  self.tag_frequency_label=ttk.Label(page,text='—');self.tag_frequency_label.pack(anchor='w')
  ttk.Button(page,text='ランキングからこのタグで絞り込む',command=self.filter_ranked_tag).pack(anchor='w',pady=6)
  ttk.Label(page,text='ランキングはモデルの確信度ではありません。例：200個のTXTのうち100個に登場＝50%。',wraplength=1100).pack(anchor='w',pady=6)
  page=self.pages['tag_editor']
  ttk.Label(page,text='タグをクリックして画像を絞り込み、×で削除できます。変更は保存するまで元のTXTに反映されません。',wraplength=1100).pack(anchor='w')
  actions=ttk.Frame(page);actions.pack(fill='x',pady=6)
  ttk.Entry(actions,textvariable=self.tag_value,width=30).pack(side='left')
  ttk.Button(actions,text='選択した画像に追加',command=lambda:self.bulk_tag_edit(False)).pack(side='left',padx=4)
  ttk.Button(actions,text='選択した画像から削除',command=lambda:self.bulk_tag_edit(True)).pack(side='left')
  ttk.Button(actions,text='すべて選択',command=lambda:self.tag_image_list.selection_set(self.tag_image_list.get_children())).pack(side='left',padx=4)
  ttk.Button(actions,text='すべての変更を保存',command=self.preview_tag_save).pack(side='right')
  self.tag_stats=ttk.Label(page,text='—');self.tag_stats.pack(anchor='w')
  self.tag_cloud=ttk.Frame(page);self.tag_cloud.pack(fill='x',pady=6)
  filter_bar=ttk.Frame(page);filter_bar.pack(fill='x')
  self.tag_filter_label=ttk.Label(filter_bar,text='All');self.tag_filter_label.pack(side='left')
  ttk.Button(filter_bar,text='絞り込みを解除',command=lambda:self.set_tag_filter('')).pack(side='left',padx=8)
  panes=ttk.Panedwindow(page,orient='horizontal');panes.pack(fill='both',expand=True,pady=6)
  left=ttk.Frame(panes);right=ttk.Frame(panes);panes.add(left,weight=2);panes.add(right,weight=4)
  self.tag_image_list=ttk.Treeview(left,columns=('file','tags','status'),show='headings',height=13,selectmode='extended')
  for c,label,w in [('file','画像／TXT',240),('tags','タグ',55),('status','状態',95)]:self.tag_image_list.heading(c,text=label);self.tag_image_list.column(c,width=w)
  self.tag_image_list.pack(fill='both',expand=True);scroll=ttk.Scrollbar(left,command=self.tag_image_list.yview);scroll.pack(side='right',fill='y');self.tag_image_list.configure(yscrollcommand=scroll.set)
  self.tag_image_list.bind('<<TreeviewSelect>>',self.select_tag_image)
  self.tag_photo=ttk.Label(right,text=tr('画像を選択'));self.tag_photo.pack(anchor='center')
  self.tag_chip_canvas=tk.Canvas(right,height=300,highlightthickness=0,background='#edf1f6');self.tag_chip_canvas.pack(side='left',fill='both',expand=True)
  scroll=ttk.Scrollbar(right,command=self.tag_chip_canvas.yview);scroll.pack(side='right',fill='y');self.tag_chip_canvas.configure(yscrollcommand=scroll.set)
  self.tag_chip_canvas.bind('<Configure>',lambda _:self.draw_tag_chips());self.tag_chip_canvas.bind('<MouseWheel>',lambda e:(self.tag_chip_canvas.yview_scroll(-int(e.delta/120),'units'),'break')[-1])
  self.tag_folder.trace_add('write',lambda *_:self.schedule_tags());self.tag_recursive.trace_add('write',lambda *_:self.schedule_tags())
  def follow_text_folder(*_):
   if not tag_changes(self.tag_records):self.tag_folder.set(self.dataset_path.get())
  self.dataset_path.trace_add('write',follow_text_folder)
  self.tag_search.trace_add('write',lambda *_:self.render_tag_ranking())
  self.root.after(700,self.schedule_tags)

 def schedule_tags(self):
  if self.tag_load_timer:self.root.after_cancel(self.tag_load_timer)
  self.tag_load_timer=self.root.after(450,self.reload_tags)

 def tag_guard(self):
  if not tag_changes(self.tag_records):return True
  answer=messagebox.askyesnocancel('未保存のタグ変更','変更を保存しますか？ はい＝保存、いいえ＝破棄、キャンセル＝戻る。')
  if answer is None:return False
  if answer:self.preview_tag_save();return False
  for r in self.tag_records:r['draft']=r['state']['text']
  return True

 def reload_tags(self,force=False):
  self.tag_load_timer=None;folder=self.tag_folder.get().strip()
  if not folder or not Path(folder).is_dir():return
  key=(str(Path(folder).resolve()),self.tag_recursive.get())
  if key==self.tag_loaded_key and not force:return
  if self.busy or getattr(self,'review_active',False):self.schedule_tags();return
  if not self.editor_guard() or not self.tag_guard():return
  try:
   records=load_tags(*key)
   self.tag_records=records;self.tag_loaded_key=key;self.tag_filter='';self.tag_selected_index=None;self.refresh_tag_views()
  except Exception as error:messagebox.showerror('TXTを読み込めません',str(error))

 def refresh_tag_views(self):
  total,counts=frequencies(self.tag_records);dirty=len(tag_changes(self.tag_records))
  self.tag_stats.configure(text=f'{len(self.tag_records)} images/TXT | {total} TXT | {len(counts)} tags | {dirty} unsaved files')
  self.render_tag_ranking()
  for w in self.tag_cloud.winfo_children():w.destroy()
  for i,(tag,count) in enumerate(counts[:30]):ttk.Button(self.tag_cloud,text=f'{tag[:35]}{"…" if len(tag)>35 else ""}  {count}',command=lambda t=tag:self.set_tag_filter(t)).grid(row=i//5,column=i%5,sticky='w',padx=3,pady=2)
  selected=self.tag_image_list.selection();self.tag_image_list.delete(*self.tag_image_list.get_children())
  for i,r in enumerate(self.tag_records):
   tags=split_tags(r['draft'])
   if self.tag_filter and self.tag_filter not in tags:continue
   changed=r['draft']!=r['state']['text'];label=self.short_path(r['images'][0] if r['images'] else r['text_path'],self.tag_folder.get())
   self.tag_image_list.insert('','end',iid=str(i),values=(label,len(tags),'未保存' if changed else 'あり' if r['state']['raw'] is not None else '未作成'))
  self.tag_filter_label.configure(text=self.tag_filter or 'All')
  retained=[i for i in selected if self.tag_image_list.exists(i)]
  if retained:self.tag_image_list.selection_set(retained)
  else:self.tag_selected_index=None;self.tag_photo.configure(image='',text=tr('画像を選択'));self.tag_photo.image=None
  self.draw_tag_chips()

 def render_tag_ranking(self):
  total,counts=frequencies(self.tag_records);query=self.tag_search.get().casefold();self.tag_rank_table.delete(*self.tag_rank_table.get_children());self.tag_rank_rows={}
  for rank,(tag,count) in enumerate(counts,1):
   if query not in tag.casefold():continue
   ident=str(rank);self.tag_rank_rows[ident]=(tag,count,total);self.tag_rank_table.insert('','end',iid=ident,values=(rank,tag,count,f'{100*count/total:.1f}%' if total else '0%'))
  self.tag_rank_status.configure(text=f'{total} TXT | {len(counts)} tags');self.tag_frequency_bar['value']=0;self.tag_frequency_label.configure(text='—')

 def show_tag_frequency(self,*_):
  ids=self.tag_rank_table.selection()
  if not ids:return
  tag,count,total=self.tag_rank_rows[ids[0]];self.tag_frequency_bar['value']=100*count/total if total else 0;self.tag_frequency_label.configure(text=f'{tag}: {count}/{total} TXT')

 def filter_ranked_tag(self):
  ids=self.tag_rank_table.selection()
  if ids:self.set_tag_filter(self.tag_rank_rows[ids[0]][0]);self.select_page(self.pages['tag_editor'])

 def set_tag_filter(self,tag):self.tag_filter=tag;self.refresh_tag_views()

 def select_tag_image(self,*_):
  ids=self.tag_image_list.selection()
  if not ids:return
  focus=self.tag_image_list.focus();self.tag_selected_index=int(focus if focus in ids else ids[0]);record=self.tag_records[self.tag_selected_index]
  self.tag_photo.configure(image='',text=Path(record['text_path']).name);self.tag_photo.image=None
  if record['images']:
   try:
    with Image.open(record['images'][0]) as im:image=ImageOps.exif_transpose(im).convert('RGB');image.thumbnail((380,200))
    photo=ImageTk.PhotoImage(image,master=self.tag_photo);self.tag_photo.configure(image=photo,text='');self.tag_photo.image=photo
   except Exception:self.tag_photo.configure(text=tr('画像を表示できません'))
  self.draw_tag_chips()

 def draw_tag_chips(self):
  canvas=self.tag_chip_canvas;canvas.delete('all');index=self.tag_selected_index
  if index is None:return
  tags=split_tags(self.tag_records[index]['draft']);width=max(330,canvas.winfo_width());x=8;y=8
  for tag in tags:
   display=tag[:70]+('…' if len(tag)>70 else '')
   text=canvas.create_text(x+6,y+14,anchor='w',text=display,font=('Yu Gothic UI',10),fill='#26364d');box=canvas.bbox(text);w=min(width-16,box[2]-box[0]+34)
   if x+w>width-8:x=8;y+=34;canvas.coords(text,x+6,y+14)
   rect=canvas.create_rectangle(x,y,x+w,y+28,fill='#dce7f5',outline='#b4c6dd');canvas.tag_lower(rect,text)
   close=canvas.create_text(x+w-12,y+14,text='×',fill='#a33535',font=('Yu Gothic UI',11,'bold'))
   canvas.tag_bind(close,'<Button-1>',lambda e,t=tag,i=index:self.remove_one_tag(i,t));canvas.tag_bind(text,'<Button-1>',lambda e,t=tag:self.set_tag_filter(t));x+=w+6
  canvas.configure(scrollregion=(0,0,width,y+40))

 def remove_one_tag(self,index,tag):
  edit_tags(self.tag_records[index],tag,True);self.refresh_tag_views()

 def bulk_tag_edit(self,remove):
  ids=self.tag_image_list.selection()
  if not ids:messagebox.showinfo('選択','一括編集するTXTを選択してください。Ctrl/Shiftまたは「すべて選択」が使えます。');return
  try:
   for ident in ids:edit_tags(self.tag_records[int(ident)],self.tag_value.get(),remove)
   self.refresh_tag_views()
  except Exception as error:messagebox.showerror('確認が必要です',str(error))

 def preview_tag_save(self):
  if not self.ready() or not self.editor_guard():return
  changes=tag_changes(self.tag_records)
  if not changes:messagebox.showinfo('変更なし','対象のTXTに変更はありません。');return
  win=LocalizedToplevel(self.root);win.title('タグ変更プレビュー');win.geometry('850x570');win.transient(self.root);win.grab_set();self.review_active=True
  ttk.Label(win,text='保存すると元のTXTを変更します。既存TXTはアプリ内caption-backupsにバックアップします。',wraplength=810).pack(anchor='w',padx=12,pady=8)
  names=ttk.Combobox(win,state='readonly',values=[c['path'] for c in changes]);names.pack(fill='x',padx=12);box=tk.Text(win,wrap='word');box.pack(fill='both',expand=True,padx=12,pady=8)
  def show(*_):
   c=changes[names.current()];box.configure(state='normal');box.delete('1.0','end');box.insert('1.0','BEFORE\n'+c['before_text']+'\n\nAFTER\n'+c['after_text']);box.configure(state='disabled')
  names.current(0);names.bind('<<ComboboxSelected>>',show);show()
  def finish():self.review_active=False;win.destroy()
  def save():
   try:
    result=apply_changes(changes,self.engine.data)
    # Refresh both editors from disk; image files are never written.
    self.tag_records=load_tags(*self.tag_loaded_key);self.refresh_tag_views();self._dataset_loaded=None;self.schedule_dataset_load();finish()
    self.notify_result('TXT保存完了',f"{result['count']} file(s)\nBackup manifest: {result['manifest']}")
   except Exception as error:messagebox.showerror('保存できません',str(error))
  bar=ttk.Frame(win);bar.pack(fill='x',padx=12,pady=8);ttk.Button(bar,text='この変更を保存',command=save).pack(side='right');ttk.Button(bar,text='キャンセル',command=finish).pack(side='right',padx=6);win.protocol('WM_DELETE_WINDOW',finish)
