import tkinter as tk
from pathlib import Path
import os,re,io,urllib.request
from i18n import ttk,LocalizedText,tr,filedialog,messagebox,ChoiceVar,StatusVar
from features import enrich,compatibility
from PIL import Image,ImageTk
from note_format import plain,note_content
import network

PREVIEW_TYPES={
 'checkpoints':'Checkpoint','loras':'LoRA','embeddings':'Embedding',
 'diffusion_models':'Diffusion model','diffusers':'Diffusers',
 'Img2txtModels':'Image to Text model','Image_to_txt_models':'Image to Text model','workflows':'Workflow','workflow':'Workflow',
 'text_encoders':'Text encoder','clip_vision':'CLIP Vision','clip':'CLIP',
 'vae':'VAE','vae_approx':'VAE approximation','controlnet':'ControlNet',
 'background_removal':'Background removal','upscale_models':'Upscale model',
 'latent_upscale_models':'Latent upscale model','style_models':'Style model',
 'model_patches':'Model patch','audio_encoders':'Audio encoder',
 'detection':'Detection model','sams':'SAM','ultralytics':'Ultralytics',
 'frame_interpolation':'Frame interpolation','geometry_estimation':'Geometry estimation',
 'optical_flow':'Optical flow','gligen':'GLIGEN','hypernetworks':'Hypernetwork',
 'classifiers':'Classifier','photomaker':'PhotoMaker','onnx':'ONNX model','unet':'UNet',
 'Not Found':'Unknown type'}

def preview_classification(row):
 family=row.get('family') or 'Unknown family'
 kind=row.get('kind') or ''
 return family+' / '+PREVIEW_TYPES.get(kind,kind or 'Unknown type')

def preview_content(row):
 lines=note_content(row).splitlines()
 triggers=[line for line in lines if line.startswith('Trigger words: ')]
 details=[line for line in lines if line.startswith(('Evidence: ','SHA256: '))]
 lines=[line for line in lines if not line.startswith(('Trigger words: ','Evidence: ','SHA256: '))]
 index=next((i+1 for i,line in enumerate(lines) if line.startswith('Model: ')),0)
 lines[index:index]=triggers+['']
 return '\n'.join(lines+['',*details])

class Gallery:
 def short_path(self,path,root):
  if not path:return ''
  try:return str(Path(path).resolve().relative_to(Path(root).resolve())) if root else path
  except ValueError:return path
 def install_interactions(self):
  def menu(event):
   w=event.widget
   if not hasattr(w,'winfo_class'):return
   if w.winfo_class() not in ('Text','Entry','TEntry','TCombobox'):return
   m=tk.Menu(self.root,tearoff=False)
   for label,action in [('コピー','<<Copy>>'),('貼り付け','<<Paste>>'),('切り取り','<<Cut>>'),('すべて選択','<<SelectAll>>')]:
    m.add_command(label=tr(label),command=lambda a=action:w.event_generate(a))
   m.tk_popup(event.x_root,event.y_root)
  self.root.bind_all('<Button-3>',menu)
  self.table.bind('<Button-3>',self.path_menu)
 def path_menu(self,event):
  iid=self.table.identify_row(event.y)
  if not iid:return
  self.table.selection_set(iid);r=self.rows[int(iid)];m=tk.Menu(self.root,tearoff=False)
  def copy(value):self.root.clipboard_clear();self.root.clipboard_append(value)
  for label,key in [('現在の場所','source'),('移動先','destination')]:
   path=r.get(key,'')
   if path:
    m.add_command(label=tr(label+'をコピー'),command=lambda p=path:copy(p))
    m.add_command(label=tr(label+'のフォルダーを開く'),command=lambda p=path:self.open_folder(p))
  if r.get('url'):m.add_command(label=tr('配布元を開く'),command=lambda:self.open_external(r['url']))
  m.tk_popup(event.x_root,event.y_root)
 def open_folder(self,path):
  folder=Path(path) if Path(path).is_dir() else Path(path).parent
  if folder.is_dir():os.startfile(str(folder))
  else:messagebox.showinfo('確認','この保存先はまだ作成されていません。')
 def linked_text(self,box,text):
  box.configure(state='normal');box.delete('1.0','end');box.insert('1.0',text)
  # Tag offsets are based on the actual displayed text, including localization.
  actual=box.get('1.0','end-1c')
  for i,m in enumerate(re.finditer(r'https://[^\s<>"\)]+',actual)):
   tag='link'+str(i);box.tag_add(tag,'1.0 + %d chars'%m.start(),'1.0 + %d chars'%m.end());box.tag_configure(tag,foreground=__import__('tag_theme').BLUE,underline=True)
   box.tag_bind(tag,'<Button-1>',lambda e,u=m.group():self.open_external(u));box.tag_bind(tag,'<Enter>',lambda e:box.configure(cursor='hand2'));box.tag_bind(tag,'<Leave>',lambda e:box.configure(cursor='xterm'))
  box.configure(state='disabled')
 def init_gallery(self):
  page=self.pages['preview'];bar=ttk.Frame(page);bar.pack(fill='x')
  self.gallery_path=tk.StringVar(value=self.scan_dir.get())
  ttk.Entry(bar,textvariable=self.gallery_path,width=1).pack(side='left',fill='x',expand=True)
  def browse():
   p=filedialog.askdirectory()
   if p:self.gallery_path.set(p)
  ttk.Button(bar,text='選択…',command=browse).pack(side='left')
  ttk.Button(bar,text='このフォルダーを調査',command=self.scan_gallery).pack(side='left')
  ttk.Button(bar,text='今回の調査結果',command=lambda:self.set_gallery_rows(self.rows)).pack(side='left')
  filters=ttk.Frame(page);filters.pack(fill='x',pady=(6,0))
  self.gallery_family=ChoiceVar(value='すべて');self.gallery_kind=ChoiceVar(value='すべて')
  self.gallery_filters={}
  for key,label,var in [('family','系統',self.gallery_family),('kind','種類',self.gallery_kind)]:
   ttk.Label(filters,text=label).pack(side='left',padx=(0,4))
   box=ttk.Combobox(filters,textvariable=var,state='readonly',width=24);box.pack(side='left',padx=(0,12))
   box.bind('<<ComboboxSelected>>',lambda event:self.filter_gallery_rows());self.gallery_filters[key]=box
  ttk.Label(filters,text='ファイル名検索').pack(side='left')
  self.gallery_search=tk.StringVar();ttk.Entry(filters,textvariable=self.gallery_search,width=24).pack(side='left',fill='x',expand=True,padx=6)
  self.gallery_search.trace_add('write',lambda *args:self.filter_gallery_rows())
  self.gallery_sort='name';self.gallery_descending=False
  pane=ttk.Panedwindow(page,orient='horizontal');pane.pack(fill='both',expand=True,pady=8)
  left=ttk.Frame(pane);right=ttk.Frame(pane);pane.add(left,weight=3);pane.add(right,weight=2)
  self.gallery_vertical=ttk.Panedwindow(left,orient='vertical');self.gallery_vertical.pack(fill='both',expand=True)
  upper=ttk.Frame(self.gallery_vertical);lower=ttk.Frame(self.gallery_vertical);self.gallery_vertical.add(upper,weight=1);self.gallery_vertical.add(lower,weight=2)
  self.gallery_list=ttk.Treeview(upper,columns=('name','family'),show='headings',height=9)
  self.gallery_list.heading('name',text='モデル／ファイル',command=lambda:self.sort_gallery('name'));self.gallery_list.heading('family',text='系統 / 種類',command=lambda:self.sort_gallery('family'));self.gallery_list.column('name',width=320);self.gallery_list.column('family',width=230)
  self.gallery_list.pack(fill='both',expand=True)
  self.gallery_list.bind('<<TreeviewSelect>>',self.gallery_selected)
  self.gallery_text=LocalizedText(lower,height=14,wrap='word');self.gallery_text.pack(fill='both',expand=True,pady=4)
  self.gallery_photo=ttk.Label(right,text='モデルを選ぶと公開画像を表示します。',anchor='center');self.gallery_photo.pack(fill='both',expand=True)
  self.gallery_rows=[];self.gallery_generation=0
 def set_gallery_rows(self,rows,select=True):
  self.gallery_rows=list(rows)
  for key,var in [('family',self.gallery_family),('kind',self.gallery_kind)]:
   values=sorted({(r.get('family') or 'Unknown family') if key=='family' else PREVIEW_TYPES.get(r.get('kind'),r.get('kind') or 'Unknown type') for r in self.gallery_rows},key=str.casefold)
   self.gallery_filters[key].configure(values=['すべて',*values])
   if var.get() not in values:var.set('すべて')
  self.filter_gallery_rows()
  if select:self.select_page(self.pages['preview'])
 def filter_gallery_rows(self):
  previous=self.gallery_list.selection()
  self.gallery_list.delete(*self.gallery_list.get_children())
  family=self.gallery_family.get();kind=self.gallery_kind.get()
  query=self.gallery_search.get().strip().casefold()
  def sort_key(item):
   r=item[1];name=Path(r['source']).name.casefold()
   return (preview_classification(r).casefold(),name) if self.gallery_sort=='family' else (name,)
  for i,r in sorted(enumerate(self.gallery_rows),key=sort_key,reverse=self.gallery_descending):
   if query not in Path(r['source']).name.casefold():continue
   row_family=r.get('family') or 'Unknown family'
   row_kind=PREVIEW_TYPES.get(r.get('kind'),r.get('kind') or 'Unknown type')
   if family!='すべて' and family!=row_family:continue
   if kind!='すべて' and kind!=row_kind:continue
   self.gallery_list.insert('','end',iid=str(i),values=(Path(r['source']).name,preview_classification(r)))
  if previous and self.gallery_list.exists(previous[0]):self.gallery_list.selection_set(previous[0])
  else:
   self.gallery_generation+=1
   self.linked_text(self.gallery_text,'')
   self.gallery_photo.configure(image='',text=tr('モデルを選ぶと公開画像を表示します。'));self.gallery_photo.image=None
 def sort_gallery(self,column):
  self.gallery_descending=not self.gallery_descending if self.gallery_sort==column else False
  self.gallery_sort=column;self.filter_gallery_rows()
 def scan_gallery(self):
  if not self.ready():return
  p=self.gallery_path.get()
  if not p or not Path(p).is_dir():return
  self.stop.clear();online=self.online.get() and not network.OFFLINE;host=self.host.get();target=self.target_dir.get() or p
  self.work(lambda:self.engine.scan(p,target,online,host,self.stop,lambda x:self.events.put(('status',x))),'gallery_rows')
 def choose_gallery_row(self,row):
  for i,r in enumerate(self.gallery_rows):
   if r['source']==row['source']:
    if not self.gallery_list.exists(str(i)):
     self.gallery_family.set('すべて');self.gallery_kind.set('すべて');self.gallery_search.set('');self.filter_gallery_rows()
    self.gallery_list.selection_set(str(i));self.gallery_list.see(str(i));return
 def gallery_selected(self,event=None):
  ids=self.gallery_list.selection()
  if not ids:return
  row=self.gallery_rows[int(ids[0])];self.gallery_generation+=1;generation=self.gallery_generation
  self.gallery_photo.configure(image='',text=tr('読み込み中…'));self.gallery_photo.image=None
  self.linked_text(self.gallery_text,preview_content(row))
  def begin():
   if generation!=self.gallery_generation:return
   if self.busy:self.root.after(150,begin);return
   host=self.host.get();online=self.online.get() and not network.OFFLINE
   def run():
    info=enrich(self.engine,row,host,online);im=None;error='公開APIに一般向け画像がありません。'
    from preview_lookup import preview_candidates
    candidates,error=preview_candidates(row,info,host,online)
    if network.OFFLINE:error='オフラインでは画像を取得できません。'
    elif candidates:
     for candidate in candidates[:3]:
      try:
       url=candidate.get('url','')
       if not url.startswith('https://'):raise ValueError('HTTPS image required')
       with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'ModelLibraryOrganizer/1.5'}),timeout=20) as response:raw=response.read(20*1024*1024+1)
       if len(raw)>20*1024*1024:raise ValueError('Image exceeds 20 MB')
       im=Image.open(io.BytesIO(raw));im.thumbnail((450,480));im=im.convert('RGB');error='';break
      except Exception as exc:error='画像を取得できません: '+str(exc)
    return generation,row,info,im,error
   self.work(run,'gallery_image')
  begin()
 def gallery_image(self,value):
  generation,row,info,image,error=value
  if generation!=self.gallery_generation:return
  self.display_gallery(row,info,image,error)
 def display_gallery(self,row,info,image,error=''):
  text=preview_content({**row,'info':info});self.linked_text(self.gallery_text,text)
  if image:
   photo=ImageTk.PhotoImage(image,master=self.gallery_photo);self.gallery_photo.configure(image=photo,text='');self.gallery_photo.image=photo
  else:self.gallery_photo.configure(image='',text=tr(error),wraplength=380);self.gallery_photo.image=None
  self.select_page(self.pages['preview'])
 def init_compatibility(self):
  page=self.pages['compatibility'];ttk.Label(page,text='LoRAをチェックポイントへ読み込む際の互換性の目安です。配布元の系統を比較し、同じ系統は緑、関連するSDXL派生は黄、不明・異なる系統は灰で表示します。実際のローダーでの読み込みや生成結果を保証しません。',wraplength=1100).pack(anchor='w')
  from core import read_json
  saved=read_json(self.engine.data/'compatibility-folders.json',{})
  self.compat_roots={}
  for key,label in [('checkpoints','チェックポイントのフォルダー'),('loras','LoRAのフォルダー')]:
   bar=ttk.Frame(page);bar.pack(fill='x',pady=3);ttk.Label(bar,text=label,width=27).pack(side='left')
   var=tk.StringVar(value=saved.get(key,''));self.compat_roots[key]=var;ttk.Entry(bar,textvariable=var).pack(side='left',fill='x',expand=True)
   def choose(v=var):
    path=filedialog.askdirectory()
    if path:
     v.set(path);self.populate_compatibility()
     if not self.busy:self.scan_compatibility_folders()
   ttk.Button(bar,text='選択…',command=choose).pack(side='left')
  ttk.Button(page,text='指定フォルダーを追加調査',command=self.scan_compatibility_folders).pack(anchor='w')
  self.compat_origin=StatusVar(value='候補はこのPCの調査履歴と今回の結果のみです。未調査のPCでは空です。全ドライブを自動探索しません。')
  ttk.Label(page,textvariable=self.compat_origin,wraplength=1100).pack(anchor='w',pady=5)
  ttk.Button(page,text='調査済みモデルから一覧を更新',command=self.populate_compatibility).pack(anchor='w',pady=8)
  ttk.Label(page,text='LoRA').pack(anchor='w')
  self.compat_choice=ttk.Combobox(page,state='readonly',width=90);self.compat_choice.pack(fill='x');self.compat_choice.bind('<<ComboboxSelected>>',self.compat_selected)
  self.compat_summary=LocalizedText(page,height=5,wrap='word');self.compat_summary.pack(fill='x',pady=8)
  self.compat_table=ttk.Treeview(page,columns=('model','family','result'),show='headings')
  for key,label,width in [('model','チェックポイント',450),('family','系統',120),('result','判定',400)]:self.compat_table.heading(key,text=label);self.compat_table.column(key,width=width)
  self.compat_table.pack(fill='both',expand=True)
  for tag,color in [('same','#e4f4e6'),('related','#fff2d8'),('different','#e5e5e5'),('unknown','#e5e5e5')]:self.compat_table.tag_configure(tag,background=color)
  self.compat_table.bind('<<TreeviewSelect>>',self.select_compat_pair)
  self.compat_overrides=read_json(self.engine.data/'compatibility-assessments.json',{}) or {}
  self.compat_pairs=[]
  edit=ttk.LabelFrame(page,text='行をクリックして、この組み合わせの評価を記録',padding=5);edit.pack(fill='x')
  self.compat_rating=ChoiceVar(value='自動判定');self.compat_note=tk.StringVar()
  ttk.Combobox(edit,textvariable=self.compat_rating,values=['自動判定','使用できた（緑）','要調整（黄）','使用不可（灰）'],state='readonly',width=24).pack(side='left')
  ttk.Label(edit,text='メモ').pack(side='left');ttk.Entry(edit,textvariable=self.compat_note).pack(side='left',fill='x',expand=True)
  ttk.Button(edit,text='評価を保存',command=self.save_compat_pair).pack(side='left')
 def populate_compatibility(self):
  old_lora=self.compat_choice.current()
  previous_lora=self.compat_loras[old_lora]['source'] if hasattr(self,'compat_loras') and 0<=old_lora<len(self.compat_loras) else None
  catalog={r['source']:r for r in self.engine.cache.get('catalog',{}).values()};catalog.update({r['source']:r for r in self.rows})
  roots={k:v.get().strip() for k,v in self.compat_roots.items()}
  def allowed(row):
   key='loras' if row.get('kind')=='loras' else 'checkpoints'
   return not roots[key] or Path(row['source']).resolve().is_relative_to(Path(roots[key]).resolve())
  self.compat_catalog=[r for r in catalog.values() if Path(r['source']).exists() and allowed(r)];self.compat_loras=[r for r in self.compat_catalog if r.get('kind')=='loras' and Path(r['source']).exists()]
  self.compat_choice.configure(values=[Path(r['source']).name+' / '+r.get('family','') for r in self.compat_loras])
  self.compat_checkpoints=[r for r in self.compat_catalog if r.get('kind') in ('checkpoints','diffusion_models')]
  def caption(r,key):
   path=Path(r['source']);root=self.compat_roots[key].get().strip()
   return (str(path.relative_to(Path(root))) if root and path.is_relative_to(Path(root)) else str(path))+' / '+(r.get('family') or 'Unknown')
  self.compat_choice.configure(values=[caption(r,'loras') for r in self.compat_loras])
  self.compat_pairs=[]
  self.compat_table.delete(*self.compat_table.get_children())
  self.compat_origin.set('このPCの調査履歴＋今回の結果 / LoRA: '+str(len(self.compat_loras))+' / Checkpoint: '+str(sum(r.get('kind') in ('checkpoints','diffusion_models') for r in self.compat_catalog))+' — 入力したフォルダー内に候補を限定します。空欄では過去の調査全体です。')
  if self.compat_loras:
   self.compat_choice.current(next((i for i,r in enumerate(self.compat_loras) if r['source']==previous_lora),0));self.compat_selected()
  else:self.compat_choice.set('');self.linked_text(self.compat_summary,'未調査または候補なし。フォルダーを指定して追加調査してください。')
 def compat_selected(self,event=None):
  index=self.compat_choice.current()
  if index<0:return
  row=self.compat_loras[index]
  summary='LoRA: '+row['source']+'\nBase family: '+(row.get('family') or 'Unknown')+'\n'
  summary+='Compared with all '+str(len(self.compat_checkpoints))+' checkpoint / diffusion models in the selected folder.\n'
  if not self.compat_checkpoints:summary+='No checkpoint available. Scan the selected checkpoint folder first.\n'
  summary+='Family estimate only; no model loading or image generation is performed.\n'+row.get('url','')
  self.linked_text(self.compat_summary,summary)
  self.compat_table.delete(*self.compat_table.get_children())
  self.compat_pairs=compatibility(row,self.compat_checkpoints)
  self.compat_rating.set('自動判定');self.compat_note.set('')
  for i,r in enumerate(self.compat_pairs):
   override=self.compat_overrides.get(r['pair_key'],{});rating=override.get('rating','自動判定')
   tag={'使用できた（緑）':'same','要調整（黄）':'related','使用不可（灰）':'different'}.get(rating,r['relation'])
   assessment=tr(r['assessment']) if rating=='自動判定' else tr('手動評価')+': '+tr(rating)
   self.compat_table.insert('','end',iid=str(i),values=(Path(r['checkpoint']).name,r['family'],row.get('family','?')+' → '+r['family']+' / '+assessment),tags=(tag,))
  if self.compat_pairs:self.compat_table.selection_set('0');self.select_compat_pair()
 def select_compat_pair(self,event=None):
  ids=self.compat_table.selection()
  if not ids:return
  r=self.compat_pairs[int(ids[0])];v=self.compat_overrides.get(r['pair_key'],{})
  self.compat_rating.set(v.get('rating','自動判定'));self.compat_note.set(v.get('note',''))
 def save_compat_pair(self):
  from core import atomic_json
  ids=self.compat_table.selection()
  if not ids:return
  key=self.compat_pairs[int(ids[0])]['pair_key'];rating=self.compat_rating.get()
  if rating=='自動判定':self.compat_overrides.pop(key,None)
  else:self.compat_overrides[key]={'rating':rating,'note':self.compat_note.get()}
  atomic_json(self.engine.data/'compatibility-assessments.json',self.compat_overrides)
  self.compat_selected();self.compat_table.selection_set(ids[0])

 def scan_compatibility_folders(self):
  if not self.ready():return
  from core import atomic_json
  roots={k:v.get().strip() for k,v in self.compat_roots.items()}
  chosen=[p for p in roots.values() if p]
  if not chosen or any(not Path(p).is_dir() for p in chosen):messagebox.showerror('フォルダー未指定','存在するチェックポイント／LoRAフォルダーを選択してください。');return
  atomic_json(self.engine.data/'compatibility-folders.json',roots);host=self.host.get();online=self.online.get() and not network.OFFLINE;target=self.target_dir.get();self.stop.clear()
  def run():
   for folder in dict.fromkeys(chosen):self.engine.scan(folder,target if target and Path(target).is_dir() else folder,online,host,self.stop,lambda x:self.events.put(('status',x)))
   return '互換性の調査完了。'
  self.work(run,'compat_scanned')
