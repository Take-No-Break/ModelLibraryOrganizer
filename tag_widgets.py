"""Reference-style compact tags, rounded controls and virtual image strip."""
import tkinter as tk
from tkinter import font
from collections import OrderedDict
from pathlib import Path
from PIL import Image,ImageOps,ImageTk
from i18n import tr
import tag_theme as theme

def rounded(canvas,x,y,w,h,fill,outline='',radius=7,**kwargs):
 r=min(radius,h/2,w/2)
 return canvas.create_polygon(x+r,y,x+w-r,y,x+w,y,x+w,y+r,x+w,y+h-r,x+w,y+h,x+w-r,y+h,x+r,y+h,x,y+h,x,y+h-r,x,y+r,x,y,smooth=True,splinesteps=16,fill=fill,outline=outline,**kwargs)

def metrics(canvas):
 scale=max(1,canvas.winfo_fpixels('1i')/96)
 if not hasattr(canvas,'_chip_font'):canvas._chip_font=font.Font(root=canvas,family='Segoe UI',size=8)
 return scale,canvas._chip_font

def layout_chips(canvas,items,width,remove=False):
 scale,f=metrics(canvas);gap=3*scale;height=19*scale;x=0;y=0;result=[]
 for tag,badge in items:
  display=tag;bw=(f.measure(str(badge))+9*scale) if badge is not None else 0;extra=bw+(12*scale if remove else 0)+10*scale
  while f.measure(display)+extra>width and len(display)>4:display=display[:-1]
  if display!=tag:display=display[:-1]+'…'
  w=min(width,f.measure(display)+extra)
  if x and x+w>width:x=0;y+=height+gap
  result.append((tag,badge,display,x,y,w,height,bw));x+=w+gap
 return result,y+height if items else 0

def draw_chip(canvas,item,x0=0,y0=0,remove=False,selected=False):
 tag,badge,display,x,y,w,h,bw=item;scale,f=metrics(canvas);x+=x0;y+=y0
 rounded(canvas,x,y,w,h,theme.FIELD if not selected else theme.SELECT,outline=theme.BLUE if selected else '',radius=(8 if badge is not None else 4)*scale)
 canvas.create_text(x+5*scale,y+h/2,anchor='w',text=display,font=f,fill=theme.TEXT)
 if badge is not None:
  rounded(canvas,x+w-bw-2*scale,y+2*scale,bw,h-4*scale,theme.BLUE,radius=7*scale)
  canvas.create_text(x+w-bw/2-2*scale,y+h/2,text=str(badge),font=f,fill=theme.BADGE_TEXT)
 if remove:canvas.create_text(x+w-6*scale,y+h/2,text='×',font=f,fill=theme.RED)
 return (x,y,x+w,y+h)

def chip_flow(canvas,items,click,remove=None,context=None,selected=None):
 canvas.delete('all');scale,_=metrics(canvas);width=max(120,canvas.winfo_width());pad=4*scale
 layouts,height=layout_chips(canvas,items,width-pad*2,bool(remove));hits=[]
 for item in layouts:hits.append((draw_chip(canvas,item,pad,pad,bool(remove),item[0]==selected),item[0]))
 canvas._chip_hits=hits;canvas._chip_click=click;canvas._chip_remove=remove;canvas._chip_context=context
 if not getattr(canvas,'_chip_events_installed',False):
  def handle(event):
   x=canvas.canvasx(event.x);y=canvas.canvasy(event.y)
   for (x1,y1,x2,y2),tag in canvas._chip_hits:
    if x1<=x<=x2 and y1<=y<=y2:
     if event.num==3:
      if canvas._chip_context:canvas._chip_context(tag,event)
     elif canvas._chip_remove and x>=x2-12*scale:canvas._chip_remove(tag)
     else:canvas._chip_click(tag,event)
     return 'break'
  canvas.bind('<Button-1>',handle);canvas.bind('<Button-3>',handle);canvas._chip_events_installed=True
 canvas.configure(scrollregion=(0,0,width,height+pad*2))

class PillButton(tk.Canvas):
 def __init__(self,parent,text,command,selected=False,small=False):
  super().__init__(parent,highlightthickness=0,bd=0,bg=parent.cget('bg'),cursor='hand2',takefocus=True)
  self.label=tr(text);self.command=command;self.active=selected;self.danger=text.lower().startswith('delete');self.scale=max(1,self.winfo_fpixels('1i')/96)
  self.f=font.Font(root=self,family='Segoe UI',size=8 if small else 9)
  self.configure(width=self.f.measure(self.label)+(15 if small else 20)*self.scale,height=(22 if small else 28)*self.scale)
  self.bind('<Configure>',lambda _:self.draw());self.bind('<Button-1>',lambda _:self.command());self.bind('<Return>',lambda _:self.command());self.bind('<space>',lambda _:self.command())
  self.bind('<Enter>',lambda _:self.draw(True));self.bind('<Leave>',lambda _:self.draw());self.bind('<FocusIn>',lambda _:self.draw(True));self.bind('<FocusOut>',lambda _:self.draw())
 def set_active(self,value):self.active=value;self.draw()
 def draw(self,hover=False):
  self.delete('all');w=max(self.winfo_width(),self.winfo_reqwidth());h=max(self.winfo_height(),self.winfo_reqheight())
  rounded(self,1,1,w-2,h-2,theme.BLUE if self.active else theme.HOVER if hover else theme.FIELD,radius=8*self.scale)
  self.create_text(w/2,h/2,text=self.label,font=self.f,fill=theme.BADGE_TEXT if self.active else theme.RED if self.danger else theme.TEXT)

class ThumbnailStrip(tk.Frame):
 def __init__(self,parent,records):
  super().__init__(parent,bg=theme.BG);self.records=records;self.ids=[];self.values={};self.selected=set();self.current='';self.anchor=None;self.cache=OrderedDict();self.pending=None;self.scheduler=self._root()
  self.scale=max(1,self.winfo_fpixels('1i')/96);self.rowheight=round(185*self.scale)
  self.canvas=tk.Canvas(self,width=round(190*self.scale),height=round(380*self.scale),highlightthickness=0,bg=theme.BG,yscrollincrement=round(22*self.scale))
  from tkinter import ttk
  scroll=ttk.Scrollbar(self,command=self.yview,style='Tag.Vertical.TScrollbar');scroll.pack(side='right',fill='y');self.canvas.pack(side='left',fill='both',expand=True);self.canvas.configure(yscrollcommand=scroll.set)
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
  for item in items:self.values.pop(str(item),None);self.selected.discard(str(item))
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
    image=ImageOps.exif_transpose(src).convert('RGB');image.thumbnail((int(width),int(height)))
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
   rounded(c,2,y+2,width-4,self.rowheight-4,'#33364f' if iid in self.selected else theme.BG,theme.BLUE if iid in self.selected else '',radius=4*self.scale)
   photo=self.thumbnail(r['images'][0],width-12,140*self.scale) if r['images'] else None
   if photo:c.create_image(width/2,y+75*self.scale,image=photo);self.visible_photos.append(photo)
   else:c.create_text(width/2,y+75*self.scale,text='TXT',fill=theme.MUTED,font=('Segoe UI',10))
   c.create_text(7*self.scale,y+156*self.scale,text=Path(label).name[:32],anchor='w',font=('Segoe UI',8),fill=theme.TEXT,width=width-14)
   c.create_text(7*self.scale,y+173*self.scale,text=f'{count} tags'+(' · unsaved' if status=='未保存' else ''),anchor='w',font=('Segoe UI',8),fill=theme.MUTED)
