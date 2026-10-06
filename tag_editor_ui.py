import tkinter as tk
from pathlib import Path
from PIL import Image,ImageTk,ImageOps
from i18n import ttk,tr,messagebox,filedialog,LocalizedToplevel,Tooltip
from dataset_files import apply_changes
from tag_dataset import load_tags,split_tags,frequencies,edit_tags,tag_changes
from tag_widgets import ThumbnailStrip,chip_flow
from tag_categories import CATEGORIES,category_of
from core import read_json,atomic_json
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
 'カテゴリーはローカルの語句ルールによる分類です。右クリックで変更できます。':'Categories use local keyword rules. Right-click a tag to change its category.',
 'タグを変更':'Edit tag','カテゴリーを変更':'Set category',
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
 'カテゴリーはローカルの語句ルールによる分類です。右クリックで変更できます。':'As categorias usam regras locais de palavras. Clique com o botão direito para alterá-las.',
 'タグを変更':'Editar tag','カテゴリーを変更':'Definir categoria',
}
for key,english in TAG_STRINGS.items():
 CATALOG['pt-BR'][key]=PT[key];CATALOG['pt-BR'][english]=PT[key]

class TagEditorUI:
 def init_tag_editor(self):
  self.tag_records=[];self.tag_loaded_key=None;self.tag_load_timer=None;self.tag_filter='';self.tag_selected_index=None
  self.tag_folder=tk.StringVar(value=self.dataset_path.get());self.tag_recursive=tk.BooleanVar(value=False)
  self.tag_search=tk.StringVar();self.tag_value=tk.StringVar()
  settings=read_json(self.engine.data/'tag-editor-settings.json',{}) or {}
  if not isinstance(settings,dict):settings={}
  overrides=settings.get('categories',{});unwanted=settings.get('unwanted',[])
  self.tag_category_overrides={k:v for k,v in overrides.items() if isinstance(k,str) and v in CATEGORIES[1:]} if isinstance(overrides,dict) else {}
  self.tag_unwanted={v for v in unwanted if isinstance(v,str)} if isinstance(unwanted,list) else set()
  self.tag_category=tk.StringVar(value='All');self.tag_sort=tk.StringVar(value='By count');self.tag_scope=tk.StringVar(value='Selected');self.tag_cloud_search=tk.StringVar();self.tag_image_search=tk.StringVar();self.tag_unwanted_value=tk.StringVar();self.tag_inline_editor=None
  style=ttk.Style();style.configure('TagCompact.TButton',font=('Yu Gothic UI',9),padding=(5,2));style.configure('TagCompact.TRadiobutton',font=('Yu Gothic UI',9),padding=(3,2))
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
  ttk.Label(page,text='タグをクリックして画像を絞り込み、×で削除できます。変更は保存するまで元のTXTに反映されません。',wraplength=1100,font=('Yu Gothic UI',9)).pack(anchor='w')
  actions=ttk.Frame(page);actions.pack(fill='x',pady=6)
  ttk.Button(actions,text='すべて選択',style='TagCompact.TButton',command=lambda:self.tag_image_list.selection_set(self.tag_image_list.get_children())).pack(side='left')
  ttk.Label(actions,text='Ctrl / Shift: multiple images',font=('Yu Gothic UI',9)).pack(side='left',padx=8)
  ttk.Button(actions,text='すべての変更を保存',style='TagCompact.TButton',command=self.preview_tag_save).pack(side='right')
  panes=ttk.Panedwindow(page,orient='horizontal');panes.pack(fill='both',expand=True,pady=6)
  left=ttk.Frame(panes);right=ttk.Frame(panes);panes.add(left,weight=0);panes.add(right,weight=1)
  ttk.Entry(left,textvariable=self.tag_image_search,width=22,font=('Yu Gothic UI',9)).pack(fill='x',pady=(0,4))
  self.tag_image_list=ThumbnailStrip(left,lambda:self.tag_records);self.tag_image_list.pack(fill='both',expand=True)
  self.tag_image_list.bind('<<TreeviewSelect>>',self.select_tag_image)
  stats_bar=ttk.Frame(right);stats_bar.pack(fill='x')
  self.tag_stats=ttk.Label(stats_bar,text='—',font=('Yu Gothic UI',9));self.tag_stats.pack(side='left')
  sort=ttk.Combobox(stats_bar,textvariable=self.tag_sort,values=['By count','By name'],state='readonly',width=11,font=('Yu Gothic UI',9));sort.pack(side='right');sort.bind('<<ComboboxSelected>>',lambda _:self.refresh_tag_views())
  self.tag_cloud=ttk.Frame(right);self.tag_cloud.pack(fill='x',pady=4)
  self.tag_cloud_canvas=tk.Canvas(self.tag_cloud,height=140,highlightthickness=0,background='#f1f4f9');self.tag_cloud_canvas.pack(side='left',fill='x',expand=True)
  scroll=ttk.Scrollbar(self.tag_cloud,command=self.tag_cloud_canvas.yview);scroll.pack(side='right',fill='y');self.tag_cloud_canvas.configure(yscrollcommand=scroll.set)
  self.tag_cloud_canvas.bind('<Configure>',lambda _:self.draw_tag_cloud());self.tag_cloud_canvas.bind('<MouseWheel>',lambda e:(self.tag_cloud_canvas.yview_scroll(-int(e.delta/120),'units'),'break')[-1])
  categories=ttk.Frame(right);categories.pack(fill='x',pady=3)
  for i,category in enumerate(CATEGORIES):
   ttk.Radiobutton(categories,text=category,variable=self.tag_category,value=category,style='TagCompact.TRadiobutton',command=self.refresh_tag_views).grid(row=i//12,column=i%12,padx=1)
  ttk.Label(right,text='カテゴリーはローカルの語句ルールによる分類です。右クリックで変更できます。',font=('Yu Gothic UI',8),wraplength=900).pack(anchor='w')
  filter_bar=ttk.Frame(right);filter_bar.pack(fill='x',pady=3)
  self.tag_filter_label=ttk.Label(filter_bar,text='All',font=('Yu Gothic UI',9));self.tag_filter_label.pack(side='left')
  ttk.Button(filter_bar,text='絞り込みを解除',style='TagCompact.TButton',command=lambda:self.set_tag_filter('')).pack(side='left',padx=6)
  ttk.Entry(filter_bar,textvariable=self.tag_cloud_search,font=('Yu Gothic UI',9),width=22).pack(side='left',fill='x',expand=True)
  ttk.Button(filter_bar,text='Delete selected tag',style='TagCompact.TButton',command=self.delete_filtered_tag).pack(side='right')
  tools=ttk.Frame(right);tools.pack(fill='x',pady=3)
  ttk.Label(tools,text='Bulk Insert',font=('Yu Gothic UI',9)).grid(row=0,column=0,sticky='w')
  ttk.Entry(tools,textvariable=self.tag_value,width=24,font=('Yu Gothic UI',9)).grid(row=0,column=1,padx=4,sticky='ew')
  ttk.Button(tools,text='Insert',style='TagCompact.TButton',command=lambda:self.bulk_tag_edit(False)).grid(row=0,column=2,padx=3)
  ttk.Button(tools,text='Remove',style='TagCompact.TButton',command=lambda:self.bulk_tag_edit(True)).grid(row=0,column=3,padx=3)
  scope=ttk.Combobox(tools,textvariable=self.tag_scope,values=['Selected','Filtered','All'],state='readonly',width=10,font=('Yu Gothic UI',9));scope.grid(row=0,column=4,padx=3)
  Tooltip(scope,'Selected: highlighted thumbnails. Filtered: currently visible results. All: every image/TXT in this dataset. Applies to bulk operations.')
  ttk.Button(tools,text='Delete category',style='TagCompact.TButton',command=lambda:self.clear_scoped_tags(True)).grid(row=0,column=5,padx=3)
  ttk.Label(tools,text='Unwanted Tag',font=('Yu Gothic UI',9)).grid(row=1,column=0,sticky='w',pady=3)
  ttk.Entry(tools,textvariable=self.tag_unwanted_value,width=24,font=('Yu Gothic UI',9)).grid(row=1,column=1,padx=4,sticky='ew')
  ttk.Button(tools,text='Register',style='TagCompact.TButton',command=self.register_unwanted).grid(row=1,column=2,padx=3)
  ttk.Button(tools,text='Remove unwanted',style='TagCompact.TButton',command=self.remove_unwanted).grid(row=1,column=3,columnspan=2,padx=3)
  ttk.Button(tools,text='Delete all tags',style='TagCompact.TButton',command=lambda:self.clear_scoped_tags(False)).grid(row=1,column=5,padx=3)
  tools.columnconfigure(1,weight=1)
  self.tag_unwanted_canvas=tk.Canvas(right,height=28,highlightthickness=0,background='#edf1f6');self.tag_unwanted_canvas.pack(fill='x');self.tag_unwanted_canvas.bind('<Configure>',lambda _:self.draw_unwanted())
  header=ttk.Frame(right);header.pack(fill='x',pady=4)
  self.tag_photo=ttk.Label(header,text=tr('画像を選択'),font=('Yu Gothic UI',9));self.tag_photo.pack(side='left')
  ttk.Label(header,text='Click: edit · Enter: apply · Esc: cancel · ×: remove',font=('Yu Gothic UI',9)).pack(side='right')
  chip_area=ttk.Frame(right);chip_area.pack(fill='both',expand=True)
  self.tag_chip_canvas=tk.Canvas(chip_area,height=260,highlightthickness=0,background='#edf1f6');self.tag_chip_canvas.pack(side='left',fill='both',expand=True)
  scroll=ttk.Scrollbar(chip_area,command=self.tag_chip_canvas.yview);scroll.pack(side='right',fill='y');self.tag_chip_canvas.configure(yscrollcommand=scroll.set)
  self.tag_chip_canvas.bind('<Configure>',lambda _:self.draw_tag_chips());self.tag_chip_canvas.bind('<MouseWheel>',lambda e:(self.tag_chip_canvas.yview_scroll(-int(e.delta/120),'units'),'break')[-1])
  self.tag_folder.trace_add('write',lambda *_:self.schedule_tags());self.tag_recursive.trace_add('write',lambda *_:self.schedule_tags())
  def follow_text_folder(*_):
   if not tag_changes(self.tag_records):self.tag_folder.set(self.dataset_path.get())
  self.dataset_path.trace_add('write',follow_text_folder)
  self.tag_search.trace_add('write',lambda *_:self.render_tag_ranking())
  self.tag_cloud_search.trace_add('write',lambda *_:self.draw_tag_cloud());self.tag_image_search.trace_add('write',lambda *_:self.refresh_tag_views())
  self.draw_unwanted()
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
  self.draw_tag_cloud()
  selected=self.tag_image_list.selection();self.tag_image_list.delete(*self.tag_image_list.get_children())
  for i,r in enumerate(self.tag_records):
   tags=split_tags(r['draft'])
   if self.tag_filter and self.tag_filter not in tags:continue
   if self.tag_image_search.get().casefold() not in Path(r['text_path']).name.casefold():continue
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
    with Image.open(record['images'][0]) as im:image=ImageOps.exif_transpose(im).convert('RGB');image.thumbnail((90,65))
    photo=ImageTk.PhotoImage(image,master=self.tag_photo);self.tag_photo.configure(image=photo,text='');self.tag_photo.image=photo
   except Exception:self.tag_photo.configure(text=tr('画像を表示できません'))
  self.draw_tag_chips()

 def draw_tag_chips(self):
  if self.tag_inline_editor:self.tag_inline_editor.destroy();self.tag_inline_editor=None
  canvas=self.tag_chip_canvas;index=self.tag_selected_index
  if index is None:chip_flow(canvas,[],lambda *_:None);return
  tags=[tag for tag in split_tags(self.tag_records[index]['draft']) if self.matches_tag_category(tag)]
  chip_flow(canvas,[(tag,None) for tag in tags],lambda tag,event:self.inline_tag_edit(index,tag,event),lambda tag:self.remove_one_tag(index,tag),self.tag_category_menu)

 def remove_one_tag(self,index,tag):
  edit_tags(self.tag_records[index],tag,True);self.refresh_tag_views()

 def matches_tag_category(self,tag):
  return self.tag_category.get()=='All' or category_of(tag,self.tag_category_overrides)==self.tag_category.get()

 def draw_tag_cloud(self):
  _,counts=frequencies(self.tag_records);query=self.tag_cloud_search.get().casefold()
  counts=[pair for pair in counts if self.matches_tag_category(pair[0]) and query in pair[0].casefold()]
  if self.tag_sort.get()=='By name':counts.sort(key=lambda pair:pair[0].casefold())
  chip_flow(self.tag_cloud_canvas,counts,lambda tag,event:self.set_tag_filter(tag),context=self.tag_category_menu)

 def tag_scope_indices(self):
  scope=self.tag_scope.get()
  if scope=='All':return tuple(str(i) for i in range(len(self.tag_records)))
  if scope=='Filtered':return self.tag_image_list.get_children()
  return self.tag_image_list.selection()

 def save_tag_options(self):
  atomic_json(self.engine.data/'tag-editor-settings.json',{'categories':self.tag_category_overrides,'unwanted':sorted(self.tag_unwanted)})

 def tag_category_menu(self,tag,event):
  previous=getattr(self,'tag_context_menu',None)
  if previous:previous.destroy()
  menu=tk.Menu(self.root,tearoff=False);menu.add_command(label=tag,state='disabled')
  self.tag_context_menu=menu
  choices=tk.Menu(menu,tearoff=False)
  for category in CATEGORIES[1:]:
   choices.add_command(label=category,command=lambda c=category:self.assign_tag_category(tag,c))
  choices.add_separator();choices.add_command(label='Automatic',command=lambda:self.assign_tag_category(tag,None))
  menu.add_cascade(label=tr('カテゴリーを変更'),menu=choices)
  menu.add_command(label='Register unwanted',command=lambda:self.register_unwanted(tag))
  try:menu.tk_popup(event.x_root,event.y_root)
  finally:menu.grab_release()

 def assign_tag_category(self,tag,category):
  if category:self.tag_category_overrides[tag]=category
  else:self.tag_category_overrides.pop(tag,None)
  self.save_tag_options();self.refresh_tag_views()

 def register_unwanted(self,value=None):
  values=split_tags(self.tag_unwanted_value.get() if value is None else value)
  if not values:return
  self.tag_unwanted.update(values);self.tag_unwanted_value.set('');self.save_tag_options();self.draw_unwanted()

 def unregister_unwanted(self,tag):
  self.tag_unwanted.discard(tag);self.save_tag_options();self.draw_unwanted()

 def draw_unwanted(self):
  chip_flow(self.tag_unwanted_canvas,[(tag,None) for tag in sorted(self.tag_unwanted)],lambda tag,event:None,self.unregister_unwanted)
  bounds=self.tag_unwanted_canvas.bbox('all');self.tag_unwanted_canvas.configure(height=min(80,max(28,bounds[3]+5 if bounds else 28)))
  self.tag_unwanted_canvas.bind('<MouseWheel>',lambda e:(self.tag_unwanted_canvas.yview_scroll(-int(e.delta/120),'units'),'break')[-1])

 def remove_unwanted(self):
  ids=self.tag_scope_indices()
  if not ids or not self.tag_unwanted:return
  for ident in ids:edit_tags(self.tag_records[int(ident)],', '.join(sorted(self.tag_unwanted)),True)
  self.refresh_tag_views()

 def delete_filtered_tag(self):
  if not self.tag_filter:return
  ids=self.tag_scope_indices()
  for ident in ids:edit_tags(self.tag_records[int(ident)],self.tag_filter,True)
  self.refresh_tag_views()

 def clear_scoped_tags(self,only_category):
  ids=self.tag_scope_indices()
  if not ids:return
  category=self.tag_category.get()
  if only_category and category=='All':messagebox.showinfo('Category','Choose a category first.');return
  action='category '+category if only_category else 'all tags'
  if not messagebox.askyesno('Delete tags',f'Remove {action} from {len(ids)} images/TXT in scope {self.tag_scope.get()}? This stages edits only; files are changed after save review.'):return
  for ident in ids:
   record=self.tag_records[int(ident)]
   if only_category:
    tags=[tag for tag in split_tags(record['draft']) if category_of(tag,self.tag_category_overrides)==category]
    if tags:edit_tags(record,', '.join(tags),True)
   else:record['draft']=''
  self.refresh_tag_views()

 def replace_image_tag(self,index,old,new):
  requested=split_tags(new)
  if not requested:raise ValueError('Enter a non-empty tag; use × to remove a tag.')
  record=self.tag_records[index];original=split_tags(record['draft']);updated=[]
  for tag in original:
   for value in (requested if tag==old else [tag]):
    if value not in updated:updated.append(value)
  if updated!=original:record['draft']=', '.join(updated)+'\n';self.refresh_tag_views()

 def inline_tag_edit(self,index,tag,event):
  canvas=self.tag_chip_canvas
  if self.tag_inline_editor:self.tag_inline_editor.destroy()
  entry=tk.Entry(canvas,font=('Yu Gothic UI',9),relief='flat',borderwidth=0,background='white');self.tag_inline_editor=entry
  entry.insert(0,tag);entry.select_range(0,'end');width=min(260,max(130,canvas.winfo_width()-20));x=min(max(4,event.x),max(4,canvas.winfo_width()-width-4));y=canvas.canvasy(event.y)
  from tag_widgets import rounded
  scale=max(1,canvas.winfo_fpixels('1i')/96);height=round(26*scale)
  border=rounded(canvas,x,y-height/2,width,height,'white','#729bd3',radius=7*scale)
  item=canvas.create_window(x+7*scale,y,anchor='w',window=entry,width=width-14*scale,height=height-6*scale)
  def cancel(*_):
   if self.tag_inline_editor is entry:self.tag_inline_editor=None
   entry.destroy();canvas.delete(item);canvas.delete(border)
  def commit(*_):
   value=entry.get()
   try:cancel();self.replace_image_tag(index,tag,value)
   except Exception as error:messagebox.showerror('確認が必要です',str(error))
   return 'break'
  entry.bind('<Return>',commit);entry.bind('<Escape>',lambda e:(cancel(),'break')[-1]);entry.focus_set()

 def bulk_tag_edit(self,remove):
  ids=self.tag_scope_indices()
  if not ids:messagebox.showinfo('選択','一括編集するTXTを選択してください。Ctrl/Shiftまたは「すべて選択」が使えます。');return
  try:
   value=self.tag_value.get()
   if not remove:
    value=', '.join(t for t in split_tags(value) if t not in self.tag_unwanted)
    if not value:messagebox.showinfo('Unwanted tags','All entered tags are registered as unwanted, or the field is empty.');return
   for ident in ids:edit_tags(self.tag_records[int(ident)],value,remove)
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
