"""Dense dark layout based on the user's LoRA dataset editor reference."""
import tkinter as tk
from tkinter import ttk
from i18n import Tooltip
from tag_widgets import ThumbnailStrip,PillButton
from tag_rows import CaptionRows
from tag_categories import CATEGORIES
import tag_theme as theme

def build_editor(app):
 page=app.pages['tag_editor'];scale=max(1,page.winfo_fpixels('1i')/96)
 style=ttk.Style();style.configure('Tag.Vertical.TScrollbar',background=theme.FIELD,troughcolor=theme.BG,bordercolor=theme.BG,arrowcolor=theme.MUTED)
 style.configure('Tag.TCombobox',font=('Segoe UI',8),fieldbackground=theme.FIELD,background=theme.FIELD,foreground=theme.TEXT,arrowcolor=theme.TEXT,bordercolor=theme.LINE,padding=3)
 style.map('Tag.TCombobox',fieldbackground=[('readonly',theme.FIELD)],foreground=[('readonly',theme.TEXT)],selectbackground=[('readonly',theme.FIELD)],selectforeground=[('readonly',theme.TEXT)])
 base=tk.Frame(page,bg=theme.BG);base.pack(fill='both',expand=True);app.tag_editor_surface=base
 def frame(parent,bg=None):return tk.Frame(parent,bg=bg or parent.cget('bg'))
 def label(parent,text,muted=False):return tk.Label(parent,text=text,bg=parent.cget('bg'),fg=theme.MUTED if muted else theme.TEXT,font=('Segoe UI',8),anchor='w')
 def entry(parent,var,width=24):return tk.Entry(parent,textvariable=var,width=width,font=('Segoe UI',9),bg=theme.FIELD,fg=theme.TEXT,insertbackground=theme.TEXT,selectbackground=theme.SELECT,relief='flat',highlightthickness=1,highlightbackground=theme.FIELD,highlightcolor=theme.BLUE)
 def button(parent,text,action,side='left',small=False):
  b=PillButton(parent,text,action,small=small);b.pack(side=side,padx=3,pady=2);return b
 toolbar_host=frame(base,theme.PANEL);toolbar_host.pack(fill='x')
 toolbar=frame(toolbar_host,theme.PANEL);toolbar.pack(side='right');app.tag_toolbar=toolbar
 button(toolbar,'Open Folder',lambda:app.choose_root(app.tag_folder));button(toolbar,'Save All',app.preview_tag_save)
 path=entry(toolbar,app.tag_folder,26);path.pack(side='left',padx=8,ipady=3);app.tag_path_entry=path
 tk.Checkbutton(toolbar,text='Subfolders',variable=app.tag_recursive,bg=theme.PANEL,fg=theme.TEXT,selectcolor=theme.FIELD,activebackground=theme.PANEL,activeforeground=theme.TEXT,font=('Segoe UI',8),bd=0).pack(side='left')
 button(toolbar,'Reload',lambda:app.reload_tags(True));button(toolbar,'Select All',lambda:app.tag_image_list.selection_set(app.tag_image_list.get_children()))
 body=tk.PanedWindow(base,orient='horizontal',bg='#c6a348',sashwidth=6,sashrelief='flat',bd=0,opaqueresize=True);body.pack(fill='both',expand=True);app.tag_body_split=body
 left=frame(body);right=frame(body);body.add(left,minsize=120,width=round(200*scale));body.add(right,minsize=420,stretch='always')
 content=tk.PanedWindow(right,orient='vertical',bg='#c6a348',sashwidth=6,sashrelief='flat',bd=0,opaqueresize=True);content.pack(fill='both',expand=True);app.tag_content_split=content
 upper=frame(content);content.add(upper,minsize=150);lower=frame(content);content.add(lower,minsize=120,stretch='always')
 searchbar=frame(left);searchbar.pack(fill='x',padx=3,pady=3);entry(searchbar,app.tag_image_search,20).pack(fill='x',ipady=2)
 app.tag_image_list=ThumbnailStrip(left,lambda:app.tag_records);app.tag_image_list.pack(fill='both',expand=True);app.tag_image_list.bind('<<TreeviewSelect>>',app.select_tag_image)
 stats=frame(upper,theme.PANEL);stats.pack(fill='both',expand=True);stats_head=frame(stats);stats_head.pack(fill='x',padx=7,pady=(4,0))
 app.tag_stats=label(stats_head,'Tag Stats',True);app.tag_stats.pack(side='left')
 help_label=label(stats_head,'ⓘ  Ctrl / Shift: select images',True);help_label.pack(side='right')
 Tooltip(help_label,'Click a statistics tag to filter images. Category filters show tags. Right-click a tag to set its category. Edits are saved only after Save All and review.')
 sortbar=frame(stats);sortbar.pack(fill='x',padx=7)
 label(sortbar,'Sort:',True).pack(side='left');app.tag_sort_buttons={}
 for name in ('By count','By name'):
  b=button(sortbar,name,lambda n=name:app.change_tag_sort(n),small=True);app.tag_sort_buttons[name]=b
 button(sortbar,'Delete Selected',app.delete_filtered_tag,side='right',small=True)
 entry(sortbar,app.tag_cloud_search,18).pack(side='right',padx=6,ipady=1);label(sortbar,'Find:',True).pack(side='right')
 cloud=frame(stats);cloud.pack(fill='both',expand=True,padx=5,pady=4);app.tag_cloud=cloud
 app.tag_cloud_canvas=tk.Canvas(cloud,height=134*scale,bg=theme.PANEL,highlightthickness=0);app.tag_cloud_canvas.pack(side='left',fill='both',expand=True)
 scroll=ttk.Scrollbar(cloud,command=app.tag_cloud_canvas.yview,style='Tag.Vertical.TScrollbar');scroll.pack(side='right',fill='y');app.tag_cloud_canvas.configure(yscrollcommand=scroll.set)
 app.tag_cloud_canvas.bind('<Configure>',lambda _:app.draw_tag_cloud());app.tag_cloud_canvas.bind('<MouseWheel>',lambda e:(app.tag_cloud_canvas.yview_scroll(-int(e.delta/120),'units'),'break')[-1])
 filters=frame(lower,theme.PANEL);filters.pack(fill='x',pady=(1,0));label(filters,'Filter:',True).pack(side='left',padx=(7,2));app.tag_category_buttons={}
 for category in CATEGORIES:
  b=button(filters,category,lambda c=category:app.change_tag_category(c),small=True);app.tag_category_buttons[category]=b
 tools=frame(lower,theme.PANEL);tools.pack(fill='x',pady=(1,0))
 bulk=frame(tools);bulk.pack(fill='x',padx=7,pady=(3,0));label(bulk,'Bulk Insert:',True).pack(side='left')
 entry(bulk,app.tag_value,25).pack(side='left',padx=6,ipady=3);button(bulk,'Insert',lambda:app.bulk_tag_edit(False),small=True);button(bulk,'Remove',lambda:app.bulk_tag_edit(True),small=True)
 scope=ttk.Combobox(bulk,textvariable=app.tag_scope,values=['Selected','Filtered','All'],state='readonly',style='Tag.TCombobox',font=('Segoe UI',8),width=9);scope.pack(side='left',padx=6)
 Tooltip(scope,'Selected: highlighted images. Filtered: images currently shown. All: entire loaded dataset. This scope applies to bulk edits.')
 button(bulk,'Delete Category',lambda:app.clear_scoped_tags(True),side='right',small=True)
 unwanted=frame(tools);unwanted.pack(fill='x',padx=7);label(unwanted,'Unwanted Tag:',True).pack(side='left')
 entry(unwanted,app.tag_unwanted_value,23).pack(side='left',padx=6,ipady=3);button(unwanted,'Register',app.register_unwanted,small=True);button(unwanted,'Remove Unwanted',app.remove_unwanted,small=True)
 button(unwanted,'Delete All Tags',lambda:app.clear_scoped_tags(False),side='right',small=True)
 app.tag_unwanted_canvas=tk.Canvas(tools,height=25*scale,bg=theme.PANEL,highlightthickness=0);app.tag_unwanted_canvas.pack(fill='x',padx=5,pady=2);app.tag_unwanted_canvas.bind('<Configure>',lambda _:app.draw_unwanted())
 app.tag_rows=CaptionRows(lower,app);app.tag_rows.pack(fill='both',expand=True,pady=(4,0));app.tag_chip_canvas=app.tag_rows.canvas
 foot=frame(base,theme.PANEL);foot.pack(fill='x');app.tag_filter_label=label(foot,'All images');app.tag_filter_label.pack(side='left',padx=7)
 button(foot,'Clear filter',lambda:app.set_tag_filter(''),small=True)
 label(foot,'Click tag: edit  ·  Enter: apply  ·  Esc: cancel  ·  ×: remove',True).pack(side='right',padx=7)
 app.tag_refreshing=False
 app.resize_tag_editor(save=False)
