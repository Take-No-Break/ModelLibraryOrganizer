"""Shared selectable application palette and compact navigation."""
import tkinter as tk
from tkinter import ttk
import tag_theme as colors

def configure_theme(root,mode="dark"):
 colors.set_mode(mode)
 root.configure(background=colors.BG)
 for option,value in [('Background',colors.BG),('Foreground',colors.TEXT),('insertBackground',colors.TEXT),('selectBackground',colors.SELECT),('selectForeground','#ffffff')]:root.option_add('*'+option,value)
 style=ttk.Style(root);style.theme_use('clam')
 style.configure('.',background=colors.BG,foreground=colors.TEXT,font=('Yu Gothic UI',10),bordercolor=colors.LINE,lightcolor=colors.LINE,darkcolor=colors.LINE,troughcolor=colors.PANEL)
 for name in ('TFrame','TLabel','TLabelframe','TLabelframe.Label'):style.configure(name,background=colors.BG,foreground=colors.TEXT)
 style.configure('TNotebook',background=colors.BG,borderwidth=0,tabmargins=(0,0,0,0))
 style.configure('TNotebook.Tab',font=('Yu Gothic UI',9),padding=(8,3),background=colors.PANEL,foreground=colors.MUTED)
 style.map('TNotebook.Tab',background=[('selected',colors.FIELD),('active',colors.HOVER)],foreground=[('selected',colors.TEXT),('active',colors.TEXT)])
 style.configure('TButton',padding=(8,4),background=colors.FIELD,foreground=colors.TEXT)
 style.map('TButton',background=[('active',colors.HOVER),('disabled',colors.PANEL)],foreground=[('disabled',colors.MUTED)])
 for name in ('TEntry','TCombobox','TSpinbox'):
  style.configure(name,fieldbackground=colors.FIELD,background=colors.FIELD,foreground=colors.TEXT,arrowcolor=colors.TEXT,insertcolor=colors.TEXT)
  style.map(name,fieldbackground=[('readonly',colors.FIELD),('disabled',colors.PANEL)],foreground=[('readonly',colors.TEXT),('disabled',colors.MUTED)],selectbackground=[('readonly',colors.FIELD)],selectforeground=[('readonly',colors.TEXT)])
 for name in ('TCheckbutton','TRadiobutton'):
  style.configure(name,background=colors.BG,foreground=colors.TEXT,indicatorbackground=colors.FIELD,indicatorforeground=colors.BLUE)
  style.map(name,background=[('active',colors.PANEL)],foreground=[('active',colors.TEXT)])
 style.configure('Treeview',background=colors.BG,fieldbackground=colors.BG,foreground=colors.TEXT,font=('Yu Gothic UI',10))
 style.configure('Treeview.Heading',background=colors.PANEL,foreground=colors.TEXT)
 style.map('Treeview',background=[('selected',colors.SELECT)],foreground=[('selected',colors.TEXT)])
 for name in ('Vertical.TScrollbar','Horizontal.TScrollbar'):
  style.configure(name,background=colors.FIELD,troughcolor=colors.BG,arrowcolor=colors.MUTED)
  style.map(name,background=[('active',colors.HOVER),('pressed',colors.SELECT)])
 style.configure('Horizontal.TProgressbar',background=colors.BLUE,troughcolor=colors.FIELD,bordercolor=colors.LINE)

def recolor_existing(parent):
 if colors.MODE=="classic":
  return
 # Some older text panes specify light colors explicitly rather than using ttk.
 for widget in parent.winfo_children():
  if widget.winfo_class() in ('Text','Canvas','Frame','Label','Entry','Listbox','Toplevel','TLabel'):
   for name,target in [('background',colors.PANEL if widget.winfo_class()=='Text' else colors.BG),('foreground',colors.TEXT),('insertbackground',colors.TEXT)]:
    try:
     rgb=widget.winfo_rgb(widget.cget(name));light=sum(rgb)/3>38000;dark=sum(rgb)/3<18000
     if name=='foreground' and str(widget.cget(name)) in ('#175fa6','#1265bd'):widget.configure(foreground=colors.BLUE)
     elif name=='background' and light or name!='background' and dark:widget.configure(**{name:target})
    except tk.TclError:pass
  if widget.winfo_class()=='Treeview':
   for tag in widget.tk.splitlist(widget.tk.call(widget._w,'tag','names')):
    old=str(widget.tag_configure(tag,'background'))
    mapped={'#ddf5e4':'#263e38','#e4f4e6':'#263e38','#ffe7e5':'#49303c','#fff2d8':'#443b2a','#e5e5e5':'#303344'}
    if old in mapped:widget.tag_configure(tag,background=mapped[old],foreground=colors.TEXT)
  recolor_existing(widget)
