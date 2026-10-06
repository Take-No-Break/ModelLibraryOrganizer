"""Display-only localization; filesystem paths and internal decision codes stay unchanged."""
import tkinter as tk
from tkinter import ttk as native_ttk,messagebox as native_messagebox,filedialog as native_filedialog,simpledialog as native_simpledialog
from locales import CATALOG,LANGS
LANG='ja'

def set_language(code):
 global LANG
 LANG=code if code in LANGS else 'ja'

def tr(value):
 if not isinstance(value,str) or LANG=='ja':return value
 table={**CATALOG["en"],**CATALOG[LANG]}
 if value in table:return table[value]
 # Only presentation strings are passed here. Never write translated text back into a model record.
 import re
 keys=sorted((k for k in table if len(k)>1),key=len,reverse=True)
 if not keys:return value
 pattern=re.compile('|'.join(re.escape(k) for k in keys))
 pieces=re.split(r'([A-Za-z]:[\\/][^\n]*|https?://[^\s]+)',value)
 return ''.join(part if i%2 else pattern.sub(lambda m:table[m.group()],part) for i,part in enumerate(pieces))

class ChoiceVar(tk.StringVar):
 def __init__(self,*args,**kwargs):
  if 'value' in kwargs:kwargs['value']=tr(kwargs['value'])
  super().__init__(*args,**kwargs)
 def get(self):
  value=super().get()
  table={**CATALOG['en'],**CATALOG[LANG]}
  return next((k for k,v in table.items() if v==value),value) if LANG!='ja' else value
 def set(self,value):super().set(tr(value))

class StatusVar(tk.StringVar):
 def __init__(self,*args,**kwargs):
  if 'value' in kwargs:kwargs['value']=tr(kwargs['value'])
  super().__init__(*args,**kwargs)
 def set(self,value):super().set(tr(value))

class Tooltip:
 def __init__(self,widget,text):
  self.widget=widget;self.scheduler=widget._root();self.text=text;self.timer=None;self.win=None
  widget.bind('<Enter>',self.schedule,add='+');widget.bind('<Leave>',self.hide,add='+');widget.bind('<ButtonPress>',self.hide,add='+');widget.bind('<Destroy>',self.hide,add='+')
 def schedule(self,event=None):
  self.hide();self.timer=self.scheduler.after(600,self.show)
 def show(self):
  self.timer=None
  if not self.widget.winfo_exists():return
  self.win=tk.Toplevel(self.widget);self.win.wm_overrideredirect(True)
  x=min(self.widget.winfo_pointerx()+12,self.widget.winfo_screenwidth()-440);y=min(self.widget.winfo_pointery()+18,self.widget.winfo_screenheight()-180)
  self.win.geometry(f'+{max(0,x)}+{max(0,y)}')
  native_ttk.Label(self.win,text=tr(self.text),wraplength=420,padding=10,background='#fff7cf',foreground='#161616',relief='solid').pack()
 def hide(self,event=None):
  if self.timer:
   try:self.scheduler.after_cancel(self.timer)
   except tk.TclError:pass
   self.timer=None
  if self.win:
   try:self.win.destroy()
   except tk.TclError:pass
   self.win=None

class LocalizedText(tk.Text):
 def insert(self,index,chars,*args):return super().insert(index,tr(chars),*args)
class LocalizedToplevel(tk.Toplevel):
 def title(self,string=None):return super().title(tr(string) if string is not None else None)
 def geometry(self,value=None):
  if value is not None:
   import re
   from display import scaled_window_size
   match=re.fullmatch(r'(\d+)x(\d+)(.*)',str(value))
   if match:
    width,height=scaled_window_size(self,int(match[1]),int(match[2]))
    value=f'{width}x{height}'+match[3]
  return super().geometry(value)
class LocalizedTreeview(native_ttk.Treeview):
 def heading(self,column,option=None,**kw):
  if 'text' in kw:kw['text']=tr(kw['text'])
  return super().heading(column,option,**kw)
 def insert(self,parent,index,iid=None,**kw):
  if 'values' in kw:
   values=list(kw['values'])
   # Do not translate filenames, source or destination paths.
   for n,column in enumerate(self.cget('columns')):
    if column in ('decision','confidence','status') and len(values)>n:values[n]=tr(values[n])
   kw['values']=values
  return super().insert(parent,index,iid,**kw)

class TtkProxy:
 def __getattr__(self,name):
  if name=='Treeview':return LocalizedTreeview
  original=getattr(native_ttk,name)
  if name not in ('Button','Label','Checkbutton','Combobox','Entry','LabelFrame'):return original
  def factory(*args,**kw):
   text=kw.get('text','');tooltip=kw.pop('tooltip',None)
   if 'text' in kw:kw['text']=tr(kw['text'])
   if name=='Combobox' and isinstance(kw.get('textvariable'),ChoiceVar):kw['values']=[tr(v) for v in kw.get('values',[])]
   widget=original(*args,**kw)
   from tips import TIPS
   hint=tooltip or TIPS.get(text)
   if not hint and name=='Entry':hint=TIPS['__entry']
   if not hint and name=='Combobox':hint=TIPS['__choice']
   if not hint and name=='Button':hint=text+'\n'+TIPS['__button']
   if hint:widget._tooltip=Tooltip(widget,hint)
   return widget
  return factory
class DialogProxy:
 def __init__(self,original):self.original=original
 def __getattr__(self,name):
  fn=getattr(self.original,name)
  def call(*args,**kwargs):
   args=tuple(tr(x) if isinstance(x,str) else x for x in args)
   for key in ('title','message','prompt','detail'):
    if key in kwargs:kwargs[key]=tr(kwargs[key])
   return fn(*args,**kwargs)
  return call
ttk=TtkProxy();messagebox=DialogProxy(native_messagebox);filedialog=DialogProxy(native_filedialog);simpledialog=DialogProxy(native_simpledialog)
