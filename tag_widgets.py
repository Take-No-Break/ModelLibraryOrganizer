"""Compact canvas chips and a virtual, bounded-cache image thumbnail strip."""
import tkinter as tk
from tkinter import font
from collections import OrderedDict
from pathlib import Path
from PIL import Image,ImageOps,ImageTk
from i18n import ttk,tr

def rounded(canvas,x,y,w,h,fill,outline='',radius=7,**kwargs):
 r=min(radius,h/2,w/2)
 return canvas.create_polygon(x+r,y,x+w-r,y,x+w,y,x+w,y+r,x+w,y+h-r,x+w,y+h,x+w-r,y+h,x+r,y+h,x,y+h,x,y+h-r,x,y+r,x,y,smooth=True,splinesteps=16,fill=fill,outline=outline,**kwargs)

def chip_flow(canvas,items,click,remove=None,context=None):
 for item,sequence,command in getattr(canvas,'_chip_bindings',[]):canvas.tag_unbind(item,sequence,command)
 canvas._chip_bindings=[]
 def bind(item,sequence,callback):
  command=canvas.tag_bind(item,sequence,callback);canvas._chip_bindings.append((item,sequence,command))
 canvas.delete('all');scale=max(1,canvas.winfo_fpixels('1i')/96);width=max(280,canvas.winfo_width());gap=round(4*scale);height=round(23*scale)
 textfont=font.Font(root=canvas,family='Yu Gothic UI',size=9);x=gap;y=gap
 for index,(tag,badge) in enumerate(items):
  suffix=('  '+str(badge)) if badge is not None else '';display=tag
  maxtext=width-44*scale
  while textfont.measure(display+suffix)>maxtext and len(display)>8:display=display[:-2]
  if display!=tag:display+='…'
  w=min(width-gap*2,round(textfont.measure(display+suffix)+18*scale+(16*scale if remove else 0)))
  if x+w>width-gap:x=gap;y+=height+gap
  group='chip'+str(index);rounded(canvas,x,y,w,height,'#dce7f5','#becfe6',radius=8*scale,tags=(group,))
  canvas.create_text(x+7*scale,y+height/2,anchor='w',text=display+suffix,font=textfont,fill='#25364d',tags=(group,))
  bind(group,'<Button-1>',lambda e,t=tag:click(t,e))
  if context:bind(group,'<Button-3>',lambda e,t=tag:context(t,e))
  if remove:
   close=canvas.create_text(x+w-10*scale,y+height/2,text='×',font=('Yu Gothic UI',9,'bold'),fill='#a53b49')
   bind(close,'<Button-1>',lambda e,t=tag:remove(t))
  x+=w+gap
 canvas.configure(scrollregion=(0,0,width,y+height+gap))
 # Hold the font to avoid deleting its Tcl name while the canvas items use it.
 canvas._chip_font=textfont

class ThumbnailStrip(ttk.Frame):
 def __init__(self,parent,records):
  super().__init__(parent);self.records=records;self.ids=[];self.values={};self.selected=set();self.current='';self.anchor=None;self.cache=OrderedDict();self.pending=None;self.scheduler=self.winfo_toplevel()
  self.scale=max(1,self.winfo_fpixels('1i')/96);self.rowheight=round(178*self.scale)
  self.canvas=tk.Canvas(self,width=round(190*self.scale),height=round(510*self.scale),highlightthickness=0,background='#edf1f6')
  scroll=ttk.Scrollbar(self,command=self.yview);scroll.pack(side='right',fill='y');self.canvas.pack(side='left',fill='both',expand=True);self.canvas.configure(yscrollcommand=scroll.set)
  self.canvas.bind('<Configure>',lambda _:self.schedule());self.canvas.bind('<Button-1>',self.clicked);self.canvas.bind('<MouseWheel>',self.wheel)
 def schedule(self):
  if self.pending:self.scheduler.after_cancel(self.pending)
  self.pending=self.scheduler.after_idle(self.draw)
 def yview(self,*args):self.canvas.yview(*args);self.schedule()
 def wheel(self,event):self.canvas.yview_scroll(-int(event.delta/120),'units');self.schedule();return 'break'
 def get_children(self):return tuple(self.ids)
 def selection(self):return tuple(i for i in self.ids if i in self.selected)
 def selection_set(self,items):
  items=(items,) if isinstance(items,str) else items;self.selected={str(i) for i in items if str(i) in self.values}
  if self.selected and self.current not in self.selected:self.current=next(i for i in self.ids if i in self.selected)
  self.schedule();self.event_generate('<<TreeviewSelect>>')
 def focus(self):return self.current
 def exists(self,item):return str(item) in self.values
 def delete(self,*items):
  for item in items:
   self.values.pop(str(item),None);self.selected.discard(str(item))
  self.ids=[i for i in self.ids if i in self.values];self.schedule()
 def insert(self,parent,index,iid,values):
  iid=str(iid);self.ids.append(iid);self.values[iid]=values;self.schedule();return iid
 def clicked(self,event):
  position=int(self.canvas.canvasy(event.y)//self.rowheight)
  if not 0<=position<len(self.ids):return
  iid=self.ids[position]
  if event.state&1 and self.anchor in self.ids:
   a=self.ids.index(self.anchor);self.selected=set(self.ids[min(a,position):max(a,position)+1])
  elif event.state&4:
   if iid in self.selected:self.selected.remove(iid)
   else:self.selected.add(iid)
  else:self.selected={iid}
  self.current=iid;self.anchor=iid;self.schedule();self.event_generate('<<TreeviewSelect>>')
 def thumbnail(self,path,width,height):
  try:
   p=Path(path);s=p.stat();key=(str(p),s.st_mtime_ns,width,height)
   if key in self.cache:self.cache.move_to_end(key);return self.cache[key]
   with Image.open(p) as src:
    image=ImageOps.exif_transpose(src).convert('RGB');image.thumbnail((width,height))
   photo=ImageTk.PhotoImage(image,master=self.canvas);self.cache[key]=photo
   while len(self.cache)>48:self.cache.popitem(last=False)
   return photo
  except Exception:return None
 def draw(self):
  self.pending=None;c=self.canvas;c.delete('all');width=max(round(150*self.scale),c.winfo_width());height=max(1,len(self.ids)*self.rowheight)
  c.configure(scrollregion=(0,0,width,height));top=c.canvasy(0);first=max(0,int(top//self.rowheight)-1);last=min(len(self.ids),int((top+c.winfo_height())//self.rowheight)+2)
  self.visible_photos=[];records=self.records()
  for position in range(first,last):
   iid=self.ids[position];y=position*self.rowheight;r=records[int(iid)];label,count,status=self.values[iid]
   rounded(c,4,y+3,width-8,self.rowheight-6,'#d6e5fc' if iid in self.selected else '#f9fafc','#729bd3' if iid in self.selected else '#d6dce5',radius=8)
   photo=self.thumbnail(r['images'][0],width-18,round(130*self.scale)) if r['images'] else None
   if photo:c.create_image(width/2,y+round(69*self.scale),image=photo);self.visible_photos.append(photo)
   else:c.create_text(width/2,y+round(65*self.scale),text='TXT' if not r['images'] else tr('画像を表示できません'),fill='#65758b',font=('Yu Gothic UI',9),width=width-20)
   c.create_text(10,y+round(144*self.scale),text=Path(label).name[:34],anchor='w',font=('Yu Gothic UI',9),fill='#25364d',width=width-16)
   c.create_text(10,y+round(162*self.scale),text=f'{count} tags · '+tr(status),anchor='w',font=('Yu Gothic UI',8),fill='#52657c')
