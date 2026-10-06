import json,sys,zipfile
from pathlib import Path
import tkinter as tk
from i18n import ttk,filedialog,messagebox,ChoiceVar,tr
from core import read_json,atomic_json
from dataset_files import list_dataset
from template_generator import build_template,PROMPT,resolve_model_folder

class CaptionUI:
 def init_captions(self):
  self.training_settings=read_json(self.engine.data/'training-settings.json',{}) or {};self.init_text_editor()
  page=self.pages['captions']
  import i18n
  from caption_labels import labels
  explanation,connection_label,location_label=labels(i18n.LANG)
  ttk.Label(page,text=explanation,wraplength=1000).pack(anchor='w',pady=6)
  panes=ttk.Panedwindow(page,orient='horizontal');panes.pack(fill='both',expand=True)
  left=ttk.Frame(panes);right=ttk.Frame(panes);panes.add(left,weight=3);panes.add(right,weight=1)
  self.cap_folder=tk.StringVar(value=self.training_settings.get('image_folder',''));self.cap_model=tk.StringVar(value=self.training_settings.get('model_path',''))
  self.cap_output=tk.StringVar();self.cap_url=tk.StringVar(value=self.training_settings.get('comfy_url','http://127.0.0.1:8188'))
  self.cap_backend=tk.StringVar(value=self.training_settings.get('backend','PixAI'));self.cap_template_mode=ChoiceVar(value=self.training_settings.get('template_mode','一体型'));self.cap_device=tk.StringVar(value='auto');self.cap_recursive=tk.BooleanVar(value=False);self.cap_save_txt=tk.BooleanVar(value=False)
  fields=ttk.Frame(left);fields.pack(fill='x');fields.columnconfigure(1,weight=1)
  for i,(label,var) in enumerate([('画像フォルダー',self.cap_folder),('Image to Text model folder',self.cap_model)]):
   ttk.Label(fields,text=label).grid(row=i,column=0,sticky='w');ttk.Entry(fields,textvariable=var,width=36).grid(row=i,column=1,sticky='ew',padx=4)
   ttk.Button(fields,text='選択…',command=lambda v=var:self.choose_root(v)).grid(row=i,column=2)
  ttk.Label(fields,text='Running ComfyUI URL').grid(row=3,column=0,sticky='w');ttk.Entry(fields,textvariable=self.cap_url,width=26).grid(row=3,column=1,sticky='ew')
  ttk.Button(fields,text=connection_label,command=self.check_caption_connection).grid(row=3,column=2)
  ttk.Label(fields,text=location_label).grid(row=2,column=0,sticky='w');ttk.Label(fields,textvariable=self.cap_output,wraplength=480).grid(row=2,column=1,columnspan=2,sticky='w')
  ttk.Button(left,text='Run in ComfyUI and save image hardlinks + TXT',command=self.run_caption_local).pack(anchor='w',pady=5)
  bar=ttk.Frame(left);bar.pack(fill='x',pady=8)
  ttk.Label(bar,text='Model').pack(side='left');combo=ttk.Combobox(bar,textvariable=self.cap_backend,values=['PixAI','JoyCaption','CL Tagger','Taggerine'],state='readonly',width=14);combo.pack(side='left');combo.bind('<<ComboboxSelected>>',lambda e:self.update_template_view())
  ttk.Combobox(bar,textvariable=self.cap_device,values=['auto','cpu'],state='readonly',width=7).pack(side='left',padx=5)
  ttk.Checkbutton(left,text='サブフォルダー',variable=self.cap_recursive).pack(anchor='w')
  self.cap_thresholds={};self.cap_threshold_frame=ttk.LabelFrame(left,text='PixAI thresholds (0–1)',padding=6)
  for i,(key,value) in enumerate(dict(general=.17,character=.27,style=.15,copyright=.24,meta=.17,rating=.41).items()):
   var=tk.StringVar(value=str(value));self.cap_thresholds[key]=var;ttk.Label(self.cap_threshold_frame,text=key).grid(row=i//3,column=(i%3)*2);ttk.Entry(self.cap_threshold_frame,textvariable=var,width=6).grid(row=i//3,column=(i%3)*2+1,padx=3,pady=4)
  self.cap_other_frame=ttk.LabelFrame(left,text='Model settings',padding=6);self.cap_cl=tk.StringVar(value='.55');self.cap_tag=tk.StringVar(value='.4');self.cap_joy=tk.StringVar(value=PROMPT);self.cap_tokens=tk.StringVar(value='512')
  for label,var in [('CL Tagger threshold',self.cap_cl),('Taggerine threshold',self.cap_tag),('JoyCaption instruction',self.cap_joy),('JoyCaption max tokens',self.cap_tokens)]:
   ttk.Label(self.cap_other_frame,text=label).pack(anchor='w');ttk.Entry(self.cap_other_frame,textvariable=var,width=52).pack(fill='x')
  ttk.Label(left,text='Only the settings for the selected model apply.',wraplength=520).pack(anchor='w',pady=5)
  ttk.Checkbutton(left,text='Save matching TXT in ComfyUI (skip existing TXT)',variable=self.cap_save_txt).pack(anchor='w',pady=5)
  ttk.Label(left,text='テンプレート形式').pack(anchor='w')
  combo=ttk.Combobox(left,textvariable=self.cap_template_mode,values=['一体型','分解版'],state='readonly',width=20);combo.pack(anchor='w');combo.bind('<<ComboboxSelected>>',lambda e:self.update_template_view())
  for label,fn in [('Save ComfyUI workflow template',self.export_caption_ui_workflow),('Save required custom nodes',self.export_caption_nodes)]:ttk.Button(left,text=label,command=fn).pack(anchor='w',pady=5)
  ttk.Label(right,text='Workflow preview').pack(anchor='w');self.cap_canvas=tk.Canvas(right,width=320,height=290,background='#202329',highlightthickness=0);self.cap_canvas.pack(anchor='nw');self.cap_canvas.bind('<Configure>',lambda e:self.draw_template_preview())
  ttk.Label(right,text='Combined: fewer nodes. Expanded: each stage is visible. Both export an editable ComfyUI workflow JSON, not an API request.',wraplength=320).pack(anchor='w',pady=8)
  ttk.Label(page,text='Copy the exported custom nodes folder into ComfyUI/custom_nodes, install its requirements in the ComfyUI Python environment, then restart ComfyUI. Drag the workflow JSON onto the canvas. Model weights are separate.',wraplength=1000).pack(anchor='w',pady=8)
  self.cap_settings_timer=None
  self.cap_settings_vars={'image_folder':self.cap_folder,'model_path':self.cap_model,'backend':self.cap_backend,'template_mode':self.cap_template_mode,'device':self.cap_device,'recursive':self.cap_recursive,'save_txt':self.cap_save_txt,'cl_threshold':self.cap_cl,'taggerine_threshold':self.cap_tag,'joy_prompt':self.cap_joy,'joy_tokens':self.cap_tokens}
  self.cap_settings_vars.update(comfy_url=self.cap_url)
  for key,var in self.cap_settings_vars.items():
   if key in self.training_settings:var.set(self.training_settings[key])
  for key,var in self.cap_thresholds.items():
   if key in self.training_settings.get('thresholds',{}):var.set(self.training_settings['thresholds'][key])
  for var in [*self.cap_settings_vars.values(),*self.cap_thresholds.values()]:var.trace_add('write',lambda *args:self.schedule_training_settings())
  for var in (self.cap_folder,self.cap_backend):var.trace_add('write',lambda *args:self.update_caption_output())
  self.update_caption_output()
  ttk.Label(left,text='Paths, model, thresholds and template options are saved automatically on this PC.',wraplength=520).pack(anchor='w',pady=5)
  self.update_template_view()
 def schedule_training_settings(self):
  if self.cap_settings_timer:self.root.after_cancel(self.cap_settings_timer)
  self.cap_settings_timer=self.root.after(500,self.save_training_settings)
 def update_template_view(self):
  self.cap_threshold_frame.pack_forget();self.cap_other_frame.pack_forget()
  (self.cap_threshold_frame if self.cap_backend.get()=='PixAI' else self.cap_other_frame).pack(fill='x',pady=6)
  self.draw_template_preview()
 def draw_template_preview(self):
  c=self.cap_canvas;c.delete('all');expanded=self.cap_template_mode.get()=='分解版'
  w=max(c.winfo_width(),300);h=max(c.winfo_height(),290)
  if not expanded:
   boxes=[('Analyze / '+self.cap_backend.get(),.5,.15),('Caption JSON',.28,.48),('Save TXT (optional)',.7,.78)];edges=[(0,1),(0,2)]
  elif self.cap_backend.get()=='PixAI':
   boxes=[('Images',.23,.08),('Model',.75,.08),('Analyze',.5,.26),('Thresholds',.23,.44),('Select tags',.75,.44),('Caption text',.5,.63),('Save TXT (optional)',.5,.84)];edges=[(0,2),(1,2),(2,4),(3,4),(4,5),(5,6)]
  else:
   boxes=[('Images',.23,.08),('Model',.75,.08),('Settings',.23,.3),('Analyze',.75,.3),('Caption text',.5,.56),('Save TXT (optional)',.5,.81)];edges=[(0,3),(1,3),(2,3),(3,4),(4,5)]
  bw=min(135,w*.44);bh=30
  for source,target in edges:
   _,sx,sy=boxes[source];_,tx,ty=boxes[target]
   c.create_line(sx*w,sy*h+bh/2,tx*w,ty*h-bh/2,fill='#8bc6aa',width=2,arrow='last')
  for name,x,y in boxes:
   x*=w;y*=h;c.create_rectangle(x-bw/2,y-bh/2,x+bw/2,y+bh/2,fill='#39434f',outline='#7b9ea6');c.create_text(x,y,text=name,fill='white',font=('Segoe UI',9),width=bw-6)
 def save_training_settings(self):
  if self.cap_settings_timer:self.root.after_cancel(self.cap_settings_timer);self.cap_settings_timer=None
  settings={key:var.get() for key,var in self.cap_settings_vars.items()}
  settings['thresholds']={key:var.get() for key,var in self.cap_thresholds.items()}
  atomic_json(self.engine.data/'training-settings.json',settings)
 def export_caption_ui_workflow(self):
  if not self.ready():return
  try:
   folder=self.cap_folder.get().strip();images=[]
   if folder:
    if not Path(folder).is_dir():raise ValueError('Select an existing image folder.')
    images=[p for row in list_dataset(folder,self.cap_recursive.get(),include_text=False) for p in row['images']]
   backend=self.cap_backend.get()
   thresholds={k:float(v.get()) for k,v in self.cap_thresholds.items()} if backend=='PixAI' else dict(general=.17,character=.27,style=.15,copyright=.24,meta=.17,rating=.41)
   settings=[float(self.cap_cl.get()) if backend=='CL Tagger' else .55,float(self.cap_tag.get()) if backend=='Taggerine' else .4,self.cap_joy.get() if backend=='JoyCaption' else PROMPT,int(self.cap_tokens.get()) if backend=='JoyCaption' else 512]
   if any(not 0<=v<=1 for v in settings[:2]) or not 1<=settings[3]<=4096:raise ValueError('Check threshold and token values.')
   backend=self.cap_backend.get();expanded=self.cap_template_mode.get()=='分解版'
   model_path=resolve_model_folder(self.cap_model.get(),backend)
   graph=build_template(images,model_path,backend,expanded,thresholds,self.cap_device.get(),settings,self.cap_save_txt.get(),self.cap_output.get())
   path=filedialog.asksaveasfilename(defaultextension='.json',initialfile=f'Image to Text - {backend} - {"Expanded" if expanded else "Combined"}.json',filetypes=[('ComfyUI workflow','*.json')])
   if path:atomic_json(Path(path),graph);self.notify_result('Save ComfyUI workflow template',path)
  except Exception as exc:messagebox.showerror('Export failed',str(exc))
 def update_caption_output(self):
  from caption_output import output_folder
  self.cap_output.set(str(output_folder(self.cap_folder.get(),self.cap_backend.get())) if self.cap_folder.get().strip() else '')
 def check_caption_connection(self):
  if not self.ready():return
  from comfy_client import ComfyClient
  url=self.cap_url.get();backend=self.cap_backend.get()
  def check():
   client=ComfyClient(url);node='OrganizerPixAICaptionBatch' if backend=='PixAI' else 'OrganizerCaptionBatch'
   info=client.request('/object_info/'+node)
   if node not in info:raise ValueError('Required custom nodes are missing. Install them in the running ComfyUI instance and restart it.')
   return ('ComfyUI connection','Connected: '+url+'\nRequired '+backend+' nodes are available. This checks the connection and nodes, not model inference.')
  self.work(check,'report')
 def run_caption_local(self):
  if not self.ready():return
  try:
   from caption_output import run_local
   from comfy_client import base_url
   folder=self.cap_folder.get().strip();output=self.cap_output.get().strip();backend=self.cap_backend.get()
   if not Path(folder).is_dir() or not output:raise ValueError('Select image and output folders.')
   from caption_output import output_folder
   from core import read_json
   output=str(output_folder(folder,backend))
   generated_roots={output_folder(folder,b) for b in ('PixAI','JoyCaption','CL Tagger','Taggerine')}
   images=[str(p) for row in list_dataset(folder,self.cap_recursive.get(),include_text=False) for p in row['images'] if not any(Path(p).resolve().is_relative_to(r) for r in generated_roots)]
   if not images:raise ValueError('No images in the selected folder.')
   if len({Path(p).stem.casefold() for p in images})!=len(images):raise ValueError('Duplicate image filenames: select folders with unique image names.')
   model=resolve_model_folder(self.cap_model.get(),backend);url=base_url(self.cap_url.get());device=self.cap_device.get()
   thresholds={k:float(v.get()) for k,v in self.cap_thresholds.items()}
   if any(not 0<=v<=1 for v in thresholds.values()):raise ValueError('Thresholds must be between 0 and 1.')
   settings=[float(self.cap_cl.get()),float(self.cap_tag.get()),self.cap_joy.get(),int(self.cap_tokens.get())]
   self.stop.clear()
   self.work(lambda:('Image to Text complete',run_local(url,images,model,backend,thresholds,device,settings,output,self.stop,lambda s:self.events.put(('status',s)),self.report_progress)),'report')
  except Exception as exc:messagebox.showerror('Image to Text',str(exc))
 def export_caption_nodes(self):
  path=filedialog.asksaveasfilename(defaultextension='.zip',initialfile='Organizer-Image-to-Text-Nodes.zip',filetypes=[('ZIP','*.zip')])
  if not path:return
  source=Path(getattr(sys,'_MEIPASS',Path(__file__).parent))/'comfy_bridge'
  with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as archive:
   for file in source.iterdir():
    if file.is_file() and file.suffix in ('.py','.txt','.md'):archive.write(file,'model_library_organizer_bridge/'+file.name)
  self.notify_result('Saved custom nodes',path)
