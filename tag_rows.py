"""Virtualized image/caption rows, matching the dataset tag editor reference."""
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from bisect import bisect_right
from tag_dataset import split_tags
from tag_widgets import metrics,layout_chips,draw_chip,rounded
import tag_theme as theme

class CaptionRows(tk.Frame):
 def __init__(self,parent,app):
  super().__init__(parent,bg=theme.BG);self.app=app;self.ids=[];self.rows=[];self.tops=[];self.total_height=1;self.pending=None;self.relayout=True;self.visible_ids=[];self.hits=[]
  scale=max(1,self.winfo_fpixels('1i')/96)
  self.canvas=tk.Canvas(self,height=220*scale,highlightthickness=0,bg=theme.BG,yscrollincrement=22*scale)
  scroll=ttk.Scrollbar(self,command=self.yview,style='Tag.Vertical.TScrollbar');scroll.pack(side='right',fill='y');self.canvas.pack(side='left',fill='both',expand=True);self.canvas.configure(yscrollcommand=scroll.set)
  self.canvas.bind('<Configure>',lambda _:self.schedule(True));self.canvas.bind('<MouseWheel>',self.wheel);self.canvas.bind('<Button-1>',self.clicked);self.canvas.bind('<Button-3>',self.context)
 def set_items(self,ids):self.ids=list(ids);self.schedule(True)
 def schedule(self,relayout=False):
  self.relayout|=relayout
  if self.pending:self.app.root.after_cancel(self.pending)
  self.pending=self.app.root.after_idle(self.draw)
 def yview(self,*args):self.canvas.yview(*args);self.schedule()
 def wheel(self,event):self.canvas.yview_scroll(-int(event.delta/120),'units');self.schedule();return 'break'
 def make_layout(self):
  c=self.canvas;s,_=metrics(c);width=max(280,c.winfo_width());self.tag_x=205*s;available=max(70,width-self.tag_x-12*s);self.rows=[];self.tops=[];y=0
  for ident in self.ids:
   r=self.app.tag_records[int(ident)];tags=[t for t in split_tags(r['draft']) if self.app.matches_tag_category(t)]
   chips,h=layout_chips(c,[(t,None) for t in tags],available,True);rowheight=max(142*s,h+16*s)
   self.tops.append(y);self.rows.append((ident,y,rowheight,chips));y+=rowheight
  self.total_height=max(1,y);c.configure(scrollregion=(0,0,width,self.total_height));self.relayout=False
 def see(self,ident):
  if self.relayout:self.make_layout()
  row=next((r for r in self.rows if r[0]==str(ident)),None)
  if row:
   top=self.canvas.canvasy(0);bottom=top+self.canvas.winfo_height();y=row[1]
   if y<top or y+min(row[2],self.canvas.winfo_height())>bottom:self.canvas.yview_moveto(y/self.total_height)
  self.schedule()
 def draw(self):
  self.pending=None;c=self.canvas
  if self.app.tag_inline_editor:self.app.cancel_inline_tag_edit()
  if self.relayout:self.make_layout()
  c.delete('all');s,f=metrics(c);width=max(280,c.winfo_width());top=c.canvasy(0);bottom=top+c.winfo_height()+142*s;first=max(0,bisect_right(self.tops,top)-1)
  self.hits=[];self.visible_ids=[];self.photos=[];selected=set(self.app.tag_image_list.selection())
  for ident,y,h,chips in self.rows[first:]:
   if y>bottom:break
   self.visible_ids.append(ident);record=self.app.tag_records[int(ident)]
   if ident in selected:
    c.create_rectangle(0,y,width,y+h,fill='#25263b',outline='');c.create_rectangle(0,y,3*s,y+h,fill=theme.BLUE,outline='')
   c.create_line(0,y+h,width,y+h,fill=theme.LINE)
   name=Path(record['images'][0] if record['images'] else record['text_path']).name
   display=name
   while f.measure(display)>112*s and len(display)>5:display=display[:-1]
   if display!=name:display=display[:-1]+'…'
   c.create_text(82*s,y+14*s,text=display,anchor='nw',font=f,fill=theme.TEXT)
   count=len(split_tags(record['draft']));dirty=record['draft']!=record['state']['text']
   c.create_text(82*s,y+43*s,text=f'{count} tags'+(' · unsaved' if dirty else ''),anchor='nw',font=f,fill=theme.BLUE if dirty else theme.MUTED)
   photo=self.app.tag_image_list.thumbnail(record['images'][0],72*s,112*s) if record['images'] else None
   if photo:c.create_image(41*s,y+71*s,image=photo);self.photos.append(photo)
   else:c.create_text(41*s,y+71*s,text='TXT',font=f,fill=theme.MUTED)
   self.hits.append(((4*s,y+8*s,78*s,y+130*s),'select',ident,None))
   rounded(c,83*s,y+69*s,112*s,31*s,theme.FIELD,radius=6*s)
   c.create_text(139*s,y+84*s,text='Copy view tags',font=f,fill=theme.TEXT)
   self.hits.append(((83*s,y+69*s,195*s,y+100*s),'copy',ident,None))
   for chip in chips:
    bounds=draw_chip(c,chip,self.tag_x,y+8*s,True,self.app.tag_selected_chip==(int(ident),chip[0]))
    self.hits.append((bounds,'tag',ident,chip[0]))
   if not chips:c.create_text(self.tag_x,y+20*s,text='No tags in this filter' if self.app.tag_category.get()!='All' else 'No caption tags',anchor='w',font=f,fill=theme.MUTED)
  if not self.ids:c.create_text(width/2,65*s,text='Open a folder to view image captions',font=('Segoe UI',10),fill=theme.MUTED)
 def hit(self,event):
  x=self.canvas.canvasx(event.x);y=self.canvas.canvasy(event.y)
  return next((r for r in self.hits if r[0][0]<=x<=r[0][2] and r[0][1]<=y<=r[0][3]),None)
 def clicked(self,event):
  hit=self.hit(event)
  if not hit:return 'break'
  bounds,kind,ident,tag=hit;index=int(ident);s,_=metrics(self.canvas)
  if kind=='select':self.app.tag_image_list.selection_set(ident)
  elif kind=='copy':
   text=', '.join(t for t in split_tags(self.app.tag_records[index]['draft']) if self.app.matches_tag_category(t))
   self.app.root.clipboard_clear();self.app.root.clipboard_append(text)
  elif self.canvas.canvasx(event.x)>=bounds[2]-12*s:self.app.remove_one_tag(index,tag)
  else:self.app.inline_tag_edit(index,tag,event)
  return 'break'
 def context(self,event):
  hit=self.hit(event)
  if hit and hit[1]=='tag':self.app.tag_category_menu(hit[3],event)
  return 'break'
