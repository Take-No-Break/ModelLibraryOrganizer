from pathlib import Path
import json
from comfy_setup import build_ui_workflow
from split_template import build_split_workflow

PROMPT='Describe the visible subject, clothing, pose, composition, background and art style in English. Return only the caption.'

def build_template(images,model_path,backend,expanded,thresholds,device='auto',settings=None,save_txt=False,output_folder=''):
 settings=settings or [.55,.4,PROMPT,512]
 if backend=='PixAI':
  graph=(build_split_workflow if expanded else build_ui_workflow)(images,model_path,thresholds,device)
  source=6 if expanded else 1
 else:
  nodes=[];links=[]
  def node(i,kind,title,inputs,outputs,widgets,x,y):
   n=dict(id=i,type=kind,title=title,pos=[x,y],size=[380,240],flags={},order=i-1,mode=0,properties={'Node name for S&R':kind},widgets_values=widgets,inputs=[dict(name=a,type=b,link=None) for a,b in inputs],outputs=[dict(name=a,type=b,links=[],slot_index=j) for j,(a,b) in enumerate(outputs)])
   nodes.append(n)
  def link(a,b,slot,typ):
   i=len(links)+1;links.append([i,a,0,b,slot,typ]);nodes[a-1]['outputs'][0]['links'].append(i);nodes[b-1]['inputs'][slot]['link']=i
  if expanded:
   node(1,'OrganizerImagePaths','Images',[],[('image_paths','ORGANIZER_IMAGE_PATHS')],[json.dumps(images,ensure_ascii=False)],30,30)
   node(2,'OrganizerCaptionModel','Model',[],[('caption_model','ORGANIZER_OTHER_MODEL')],[backend,model_path,device],30,350)
   node(3,'OrganizerCaptionSettings','Model settings',[],[('settings','ORGANIZER_OTHER_SETTINGS')],settings,450,350)
   node(4,'OrganizerCaptionAnalyze','Analyze images',[('image_paths','ORGANIZER_IMAGE_PATHS'),('caption_model','ORGANIZER_OTHER_MODEL'),('settings','ORGANIZER_OTHER_SETTINGS')],[('captions','ORGANIZER_OTHER_CAPTIONS')],[],880,30)
   node(5,'OrganizerCaptionFormat','Caption text',[('captions','ORGANIZER_OTHER_CAPTIONS')],[('caption_json','STRING')],[],1300,30)
   link(1,4,0,'ORGANIZER_IMAGE_PATHS');link(2,4,1,'ORGANIZER_OTHER_MODEL');link(3,4,2,'ORGANIZER_OTHER_SETTINGS');link(4,5,0,'ORGANIZER_OTHER_CAPTIONS');source=5
  else:
   node(1,'OrganizerCaptionBatch',backend+' / Image to Text',[],[('caption_json','STRING')],[json.dumps(images,ensure_ascii=False),backend,model_path,device,*settings],30,30);source=1
  graph=dict(nodes=nodes,links=links,groups=[],config={},extra={},version=.4)
 nodes=graph['nodes'];links=graph['links']
 for n in nodes:
  if n['type']=='Note':n['widgets_values']=['Install the exported Organizer nodes into ComfyUI/custom_nodes and restart ComfyUI. Drag this workflow JSON onto its canvas. Run it in ComfyUI. TXT saving is optional; existing TXT files are never overwritten. Model weights and runtime dependencies are not bundled.']
 i=max(n['id'] for n in nodes)+1;l=max((x[0] for x in links),default=0)+1
 src=next(n for n in nodes if n['id']==source);src['outputs'][0]['links'].append(l)
 nodes.append(dict(id=i,type='OrganizerSaveCaptionTXT',title='Save matching TXT / optional',pos=[1750 if expanded else 550,950 if expanded else 450],size=[410,140],flags={},order=i-1,mode=0,properties={'Node name for S&R':'OrganizerSaveCaptionTXT'},inputs=[dict(name='caption_json',type='STRING',link=l)],outputs=[dict(name='save_report',type='STRING',links=[],slot_index=0)],widgets_values=[bool(save_txt),str(output_folder)]))
 links.append([l,source,0,i,0,'STRING']);graph.update(last_node_id=i,last_link_id=l)
 return graph


def resolve_model_folder(folder,backend):
 if not folder.strip():return ''
 root=Path(folder).resolve(strict=True)
 if not root.is_dir():raise ValueError('Select a model folder.')
 markers={'PixAI':('tagger_pipeline.py',),'JoyCaption':('config.json','tokenizer_config.json'),'CL Tagger':('model.onnx','model_vocabulary.json'),'Taggerine':('inference_tagger_standalone.py','tagger_proto.safetensors')}[backend]
 candidates=[root]+[p for p in root.glob('*') if p.is_dir()]+[p for p in root.glob('*/*') if p.is_dir()]
 found=[p for p in candidates if all((p/name).is_file() for name in markers)]
 if root in found:return str(root)
 if len(found)==1:return str(found[0])
 raise ValueError('Select the specific '+backend+' model folder containing: '+', '.join(markers))
