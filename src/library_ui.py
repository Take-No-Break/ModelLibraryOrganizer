"""Read-only library updates, authors, caption words and version comparison."""
from pathlib import Path
import tkinter as tk
from i18n import ttk,LocalizedToplevel,LocalizedText,messagebox,filedialog,tr,Tooltip
from core import fetch_json
from features import enrich
import network,library_models as models
from responsive_controls import ControlFlow
from gallery import PREVIEW_TYPES
from locales import CATALOG
TEXTS={'作者別一覧':'Authors','一覧を更新':'Refresh list','モデルの更新確認':'Check model updates','トリガーワードをコピー':'Copy trigger words','バージョンの説明を比較':'Compare version descriptions','画像から使用モデルを探す':'Find models used in image','この画像の使用モデル':'Models used in this image','作者':'Author','手持ちモデル':'Installed model','追加部分は緑、削除部分は赤で表示します。':'Additions are green; removals are red.','調査済みで現在も存在するモデルのみを一覧表示します。':'Only scanned models still present on this PC are listed.','公開APIが返す一般向け画像を切り替えます。':'Browse general-audience images returned by the public API.','前の画像':'Previous image','次の画像':'Next image'}
TEXTS.update({'タグをすべて開く':'Expand all','すべて閉じる':'Collapse all'})
CATALOG['en'].update(TEXTS)
IMAGE_MODEL_HELP='生成情報を含むPNG専用です。対応するモデル名・ハッシュ値、またはComfyUIの生成用ノード情報を、調査済みライブラリと照合します。Civitaiの画像に限りません。情報のない通常のPNGや、見た目だけでは使用モデルを判別できません。情報があっても一部のモデルを特定できない場合があります。'
CATALOG['en'][IMAGE_MODEL_HELP]='Requires a PNG containing supported generation metadata: model names/hashes or a ComfyUI prompt graph. Matches these records against the scanned library; images need not come from Civitai. Ordinary PNGs without this metadata cannot identify models from appearance alone. Even with metadata, some models may remain unidentified.'

def selected(app):
 return [app.gallery_rows[int(i)] for i in app.gallery_list.selection()]
def init(app):
 bar=ControlFlow(app.pages['preview']);bar.pack(fill='x',before=app.gallery_filters['family'].master,pady=3)
 for label,action in [('モデルの更新確認',lambda:check_updates(app)),('トリガーワードをコピー',lambda:copy_words(app)),('バージョンの説明を比較',lambda:compare(app)),('作者別一覧',lambda:show_authors(app)),('画像から使用モデルを探す',lambda:from_png(app))]:
  button=ttk.Button(bar,text=label,command=action);button.pack(side='left')
  if label=='画像から使用モデルを探す':
   app.image_model_tip=Tooltip(button,IMAGE_MODEL_HELP)
 page=app.pages['authors']
 ttk.Label(page,text='調査済みで現在も存在するモデルのみを一覧表示します。').pack(anchor='w')
 controls=ttk.Frame(page);controls.pack(fill='x',pady=4)
 ttk.Button(controls,text='一覧を更新',command=lambda:refresh_authors(app)).pack(side='left')
 ttk.Button(controls,text='タグをすべて開く',command=lambda:expand_authors(app,True)).pack(side='left',padx=5)
 ttk.Button(controls,text='すべて閉じる',command=lambda:expand_authors(app,False)).pack(side='left')
 frame=ttk.Frame(page);frame.pack(fill='both',expand=True);frame.rowconfigure(0,weight=1);frame.columnconfigure(0,weight=1)
 tree=ttk.Treeview(frame,columns=('version','type','family'),show='tree headings')
 tree.heading('#0',text=tr('作者')+' / '+tr('手持ちモデル'))
 for key,label in [('version','Version'),('type','モデル種類'),('family','ベースモデル系統')]:tree.heading(key,text=tr(label));tree.column(key,width={'version':90,'type':110,'family':150}[key],minwidth=55,stretch=False)
 tree.column('#0',width=280,minwidth=180,stretch=False)
 tree.grid(row=0,column=0,sticky='nsew')
 y=ttk.Scrollbar(frame,orient='vertical',command=tree.yview);y.grid(row=0,column=1,sticky='ns')
 x=ttk.Scrollbar(frame,orient='horizontal',command=tree.xview);x.grid(row=1,column=0,sticky='ew');tree.configure(yscrollcommand=y.set,xscrollcommand=x.set)
 app.author_tree=tree;app.author_records={}
 tree.bind('<Double-1>',lambda event:open_author_model(app))
def refresh_authors(app):
 tree=app.author_tree;tree.delete(*tree.get_children());app.author_records={}
 groups={}
 for row in models.inventory(app.engine,[*app.rows,*app.gallery_rows]):
  info=row.get('info') or app.engine.cache.get('details',{}).get(row.get('sha'),{}) or {}
  author=row.get('author') or info.get('author') or 'Unknown author'
  if author not in groups:groups[author]=[]
  groups[author].append((row,info))
 for author,items in sorted(groups.items(),key=lambda x:x[0].casefold()):
  parent=tree.insert('','end',text=author,open=False)
  by_model={}
  for row,info in items:
   identity=models.identity(row)
   key=str(identity[1]) if identity else row.get('title') or Path(row['source']).name
   if key not in by_model:by_model[key]=tree.insert(parent,'end',text=row.get('title') or Path(row['source']).name,open=False)
   child=tree.insert(by_model[key],'end',text=Path(row['source']).name,values=(info.get('version') or ((identity or ('',0,''))[2] or 'Unknown'),PREVIEW_TYPES.get(row.get('kind'),row.get('kind','')),row.get('family','')))
   app.author_records[child]=row
def expand_authors(app,opened):
 def visit(parent):
  for child in app.author_tree.get_children(parent):
   app.author_tree.item(child,open=opened);visit(child)
 visit('')
def show_authors(app):
 refresh_authors(app);app.select_page(app.pages['authors'])
def open_author_model(app):
 ids=app.author_tree.selection()
 if ids and ids[0] in app.author_records:
  row=app.author_records[ids[0]];app.set_gallery_rows(models.inventory(app.engine,[*app.rows,*app.gallery_rows]),select=False);app.choose_gallery_row(row);app.select_page(app.pages['preview'])
def need_rows(app):
 rows=selected(app)
 if not rows:messagebox.showinfo('確認','Select models in Preview (Ctrl / Shift for multiple selection).')
 return rows
def require_online(app):
 if network.OFFLINE or not app.online.get():messagebox.showinfo('確認','Enable public API lookup for this action.');return False
 return True
def copy_words(app):
 rows=need_rows(app)
 if not rows:return
 def finish():
  words=models.triggers(rows,app.engine.cache.get('details',{}))
  if words:app.root.clipboard_clear();app.root.clipboard_append(words);messagebox.showinfo('完了','Trigger words copied:\n'+words)
  else:messagebox.showinfo('確認','No trigger words were provided for the selected models.')
 if not network.OFFLINE and app.online.get() and app.ready():
  host=app.host.get()
  app.work(lambda:([enrich(app.engine,r,host,True) for r in rows],finish),'library_callback')
 else:finish()
def check_updates(app):
 rows=need_rows(app)
 if not rows or not require_online(app) or not app.ready():return
 host=app.host.get();app.stop.clear()
 def run():
  results=[]
  cards={}
  for n,row in enumerate(rows,1):
   if app.stop.is_set():break
   enrich(app.engine,row,host,True);identity=models.identity(row)
   if not identity:results.append((row,None,[],'Source is not identified or this provider is unsupported.'));continue
   base,model,current=identity
   try:
    if (base,model) not in cards:cards[base,model]=fetch_json(base+'/api/v1/models/'+str(model))
    newer,error=models.newer_versions(cards[base,model],current)
    results.append((row,identity,newer,error))
   except Exception as exc:results.append((row,identity,[],type(exc).__name__))
   app.report_progress(n,len(rows))
  return results,lambda:updates_result(app,results)
 app.work(run,'library_callback')
def updates_result(app,results):
 window=LocalizedToplevel(app.root);window.title(tr('モデルの更新確認'));window.geometry('850x450')
 ttk.Label(window,text='Newer public versions are listed by publication date. Families may differ; compare before downloading.').pack(anchor='w')
 tree=ttk.Treeview(window,columns=('current','new','family','result'),show='tree headings')
 tree.heading('#0',text='Model')
 for key,label in [('current','Installed version ID'),('new','New version'),('family','ベースモデル系統'),('result','Result')]:tree.heading(key,text=label);tree.column(key,width=145)
 tree.pack(fill='both',expand=True);links={}
 for row,identity,newer,error in results:
  current=identity[2] if identity else ''
  if newer:
   for version in newer:
    child=tree.insert('','end',text=Path(row['source']).name,values=(current,version.get('name',version['id']),version.get('baseModel',''),'Newer version available'))
    links[child]=identity[0]+'/models/'+str(identity[1])+'?modelVersionId='+str(version['id'])
  else:tree.insert('','end',text=Path(row['source']).name,values=(current,'','',error or 'No newer public version'))
 def open_link():
  ids=tree.selection()
  if ids and ids[0] in links:app.open_external(links[ids[0]])
 ttk.Button(window,text='Open selected version',command=open_link).pack(anchor='w')
def compare(app):
 rows=need_rows(app)
 if not rows or not require_online(app) or not app.ready():return
 row=rows[0];host=app.host.get()
 def run():
  enrich(app.engine,row,host,True);identity=models.identity(row)
  if not identity:raise ValueError('Civitai source is not identified.')
  base,model,current=identity
  card=fetch_json(base+'/api/v1/models/'+str(model))
  versions=card.get('modelVersions',[])
  return versions,lambda:comparison_result(app,versions,current)
 app.work(run,'library_callback')
def comparison_result(app,versions,current):
 window=LocalizedToplevel(app.root);window.title(tr('バージョンの説明を比較'));window.geometry('850x650')
 legend=ttk.Frame(window);legend.pack(fill='x',padx=8,pady=8)
 from i18n import LANG
 parts=[('追加部分は ',None),('緑','#187331'),('、削除部分は ',None),('赤','#a33e42'),(' で表示します。',None)] if LANG=='ja' else [('Additions: ',None),('green','#187331'),(' / Removals: ',None),('red','#a33e42')]
 for word,color in parts:
  kwargs={'text':word,'font':('Yu Gothic UI',12,'bold')}
  if color:kwargs['foreground']=color
  ttk.Label(legend,**kwargs).pack(side='left')

 labels=[str(v.get('name') or v['id'])+' / '+str(v['id'])+' / '+str(v.get('baseModel','')) for v in versions]
 bar=ttk.Frame(window);bar.pack(fill='x')
 a=ttk.Combobox(bar,values=labels,state='readonly');a.pack(side='left',fill='x',expand=True)
 b=ttk.Combobox(bar,values=labels,state='readonly');b.pack(side='left',fill='x',expand=True)
 text=LocalizedText(window,wrap='word');text.pack(fill='both',expand=True)
 text.tag_configure('added',foreground='#187331');text.tag_configure('removed',foreground='#a33e42')
 def render(*args):
  if a.current()<0 or b.current()<0:return
  text.configure(state='normal');text.delete('1.0','end')
  for line in models.changes(versions[a.current()],versions[b.current()]):
   if line.startswith('? '):continue
   text.insert('end',line+'\n','added' if line.startswith('+ ') else 'removed' if line.startswith('- ') else '')
  text.configure(state='disabled')
 a.bind('<<ComboboxSelected>>',render);b.bind('<<ComboboxSelected>>',render)
 if versions:
  a.current(next((i for i,v in enumerate(versions) if v['id']==current),0));b.current(0 if a.current()!=0 else min(1,len(versions)-1));render()
def used_resources(app,meta):
 rows=models.inventory(app.engine,[*app.rows,*app.gallery_rows]);items=models.resources(meta)
 if not items:messagebox.showinfo('確認','This image has no supported model metadata. No models can be inferred from its appearance.');return
 window=LocalizedToplevel(app.root);window.title(tr('この画像の使用モデル'));window.geometry('800x420')
 ttk.Label(window,text='Compared with scanned files still on this PC. Unidentified does not prove the model is absent.').pack(anchor='w')
 tree=ttk.Treeview(window,columns=('type','result','file'),show='tree headings');tree.heading('#0',text='Resource')
 for key,label in [('type','モデル種類'),('result','Match'),('file','Local file')]:tree.heading(key,text=label);tree.column(key,width=190)
 tree.pack(fill='both',expand=True)
 for item in items:
  status,file=models.match_resource(item,rows,app.engine.cache.get('details',{}))
  tree.insert('','end',text=item['name'] or str(item.get('version')),values=(item.get('type',''),status,file))
def from_png(app):
 path=filedialog.askopenfilename(filetypes=[('PNG image','*.png')])
 if path:
  try:used_resources(app,models.png_metadata(path))
  except Exception as exc:messagebox.showerror('確認',type(exc).__name__+': Could not read PNG metadata.')
