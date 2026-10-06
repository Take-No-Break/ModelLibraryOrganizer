"""Control rows that wrap within the available page width."""
import tkinter as tk

class ControlFlow(tk.Frame):
 def __init__(self,parent,align='left',**kwargs):
  super().__init__(parent,**kwargs);self.align=align;self.items=None;self.pending=None;self.scheduler=self._root()
  self.bind('<Configure>',self.schedule);self.scheduler.after_idle(self.reflow)
 def schedule(self,event=None):
  if self.pending:self.scheduler.after_cancel(self.pending)
  self.pending=self.scheduler.after_idle(self.reflow)
 def reflow(self):
  self.pending=None
  if self.items is None:
   left=[];right=[]
   for child in self.pack_slaves():
    (right if child.pack_info().get('side')=='right' else left).append(child)
   self.items=left+right[::-1]
   for child in self.items:child.pack_forget()
  available=max(1,self.winfo_width()-8);rows=[];row=[];used=0;height=0
  for child in self.items:
   width=min(available,child.winfo_reqwidth());h=child.winfo_reqheight()
   if row and used+width+6>available:
    rows.append((row,used,height));row=[];used=0;height=0
   row.append((child,width,h));used+=width+(6 if len(row)>1 else 0);height=max(height,h)
  if row:rows.append((row,used,height))
  y=3
  for row,used,height in rows:
   x=4+(available-used if self.align=='right' else 0)
   for child,width,h in row:
    child.place(x=x,y=y+(height-h)//2,width=width,height=h);x+=width+6
   y+=height+5
  requested=max(1,y)
  if self.winfo_reqheight()!=requested:self.configure(height=requested)
