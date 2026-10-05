"""Persistent, app-local operation results, separate from move/restore journals."""
import uuid
from datetime import datetime
from i18n import ttk,LocalizedText,messagebox,tr
from core import atomic_json,read_json

class ResultUI:
 def init_results(self):
  page=self.pages['results']
  ttk.Label(page,text='過去の調査・キャプション・書き出し結果').pack(anchor='w',pady=6)
  pane=ttk.Panedwindow(page,orient='horizontal');pane.pack(fill='both',expand=True)
  left=ttk.Frame(pane);right=ttk.Frame(pane);pane.add(left,weight=1);pane.add(right,weight=3)
  self.result_list=ttk.Treeview(left,columns=('date','title'),show='headings',selectmode='browse')
  for key,label,width in [('date','日時',150),('title','結果',260)]:
   self.result_list.heading(key,text=tr(label));self.result_list.column(key,width=width)
  scroll=ttk.Scrollbar(left,orient='vertical',command=self.result_list.yview);self.result_list.configure(yscrollcommand=scroll.set)
  scroll.pack(side='right',fill='y');self.result_list.pack(fill='both',expand=True)
  self.result_body=LocalizedText(right,wrap='word',state='disabled')
  text_scroll=ttk.Scrollbar(right,orient='vertical',command=self.result_body.yview);self.result_body.configure(yscrollcommand=text_scroll.set)
  text_scroll.pack(side='right',fill='y');self.result_body.pack(fill='both',expand=True)
  self.result_list.bind('<<TreeviewSelect>>',self.display_result)
  self.refresh_results()
 def refresh_results(self,selected=None):
  self.result_records={}
  self.result_list.delete(*self.result_list.get_children())
  folder=self.engine.data/'operation-results'
  for path in sorted(folder.glob('*.json'),reverse=True):
   record=read_json(path,{})
   if not record.get('id'):continue
   ident=record['id'];self.result_records[ident]=record
   self.result_list.insert('','end',iid=ident,values=(record.get('date',''),tr(record.get('title',''))))
  # Preserve access to older stored results that predate the operation-result journal.
  catalog=self.engine.cache.get('catalog',{})
  if catalog:
   text='\n\n'.join(r.get('source','')+'\n'+r.get('family','')+' / '+r.get('kind','')+'\n'+r.get('evidence','')+'\n'+r.get('url','') for r in catalog.values())
   record={'id':'saved-catalog','title':'保存済みモデル調査（キャッシュ）','date':'','text':text}
   self.result_records[record['id']]=record
   self.result_list.insert('','end',iid=record['id'],values=('',tr(record['title'])))
  for manifest in sorted((self.engine.data/'caption-backups').glob('*/manifest.json'),reverse=True):
   ident='caption-'+manifest.parent.name
   record={'id':ident,'title':'TXT backup / saved changes','date':datetime.fromtimestamp(manifest.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'),'text':str(manifest)+'\n\n'+__import__('json').dumps(read_json(manifest,{}),ensure_ascii=False,indent=2)}
   self.result_records[ident]=record
   self.result_list.insert('','end',iid=ident,values=(record['date'],record['title']))
  if selected and selected in self.result_records:
   self.result_list.selection_set(selected);self.display_result()
 def display_result(self,event=None):
  selected=self.result_list.selection()
  if not selected:return
  record=self.result_records[selected[0]]
  self.linked_text(self.result_body,record.get('title','')+'\n'+record.get('date','')+'\n\n'+record.get('text',''))
 def record_result(self,title,text):
  now=datetime.now();ident=now.strftime('%Y%m%d-%H%M%S-%f')+'-'+uuid.uuid4().hex[:6]
  record={'id':ident,'date':now.strftime('%Y-%m-%d %H:%M:%S'),'title':str(title),'text':str(text)}
  atomic_json(self.engine.data/'operation-results'/(ident+'.json'),record)
  self.refresh_results(ident)
  return record
 def notify_result(self,title,text):
  self.record_result(title,text)
  messagebox.showinfo(title,str(text)[:1400]+('\n\n詳細は「調査結果」で確認できます。' if len(str(text))>1400 else ''),parent=self.root)
