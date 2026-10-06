import tkinter as tk
from tkinter import ttk

class ScrollablePage(ttk.Frame):
 def __init__(self,parent,padding=4):
  super().__init__(parent)
  self.canvas=tk.Canvas(self,highlightthickness=0,borderwidth=0,background=__import__('tag_theme').BG)
  y=ttk.Scrollbar(self,command=self.canvas.yview);x=ttk.Scrollbar(self,orient='horizontal',command=self.canvas.xview)
  self.y_scroll=y;self.x_scroll=x
  self.canvas.configure(yscrollcommand=y.set,xscrollcommand=x.set)
  self.canvas.grid(row=0,column=0,sticky='nsew');y.grid(row=0,column=1,sticky='ns');x.grid(row=1,column=0,sticky='ew')
  self.rowconfigure(0,weight=1);self.columnconfigure(0,weight=1)
  self.body=ttk.Frame(self.canvas,padding=padding);self.body._page_scroll=self
  self.window=self.canvas.create_window(0,0,anchor='nw',window=self.body)
  self.body.bind('<Configure>',self.resize);self.canvas.bind('<Configure>',self.resize)
 def resize(self,event=None):
  if self.body.winfo_reqwidth()>self.canvas.winfo_width()+1:self.x_scroll.grid()
  else:self.x_scroll.grid_remove()
  if self.body.winfo_reqheight()>self.canvas.winfo_height()+1:self.y_scroll.grid()
  else:self.y_scroll.grid_remove()
  width=max(self.canvas.winfo_width(),self.body.winfo_reqwidth());height=max(self.canvas.winfo_height(),self.body.winfo_reqheight())
  self.canvas.itemconfigure(self.window,width=width,height=height);self.canvas.configure(scrollregion=(0,0,width,height))

def scroll_wheel(event):
 widget=event.widget
 if widget.winfo_class() in ('Text','Treeview','Listbox','TCombobox'):return
 while widget is not None:
  page=getattr(widget,'_page_scroll',None)
  if page:
   (page.canvas.xview_scroll if event.state&1 else page.canvas.yview_scroll)(-int(event.delta/120),'units');return 'break'
  widget=getattr(widget,'master',None)
