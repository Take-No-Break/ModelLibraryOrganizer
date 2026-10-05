"""Visible PixAI stages; no writes to training files."""
import json,math

def build_split_workflow(images,model_path,thresholds,device='auto'):
 keys=['general','character','style','copyright','meta','rating']
 values=[float(thresholds[k]) for k in keys]
 if any(not math.isfinite(v) or not 0<=v<=1 for v in values):raise ValueError('Thresholds must be between 0 and 1.')
 nodes=[];links=[]
 def node(ident,kind,title,pos,inputs,outputs,widgets,size=(360,150)):
  result={'id':ident,'type':kind,'title':title,'pos':list(pos),'size':list(size),'flags':{},'order':ident-1,'mode':0,'inputs':[{'name':name,'type':typ,'link':None} for name,typ in inputs], 'outputs':[{'name':name,'type':typ,'links':[],'slot_index':i} for i,(name,typ) in enumerate(outputs)],'properties':{'Node name for S&R':kind},'widgets_values':widgets}
  nodes.append(result);return result
 node(1,'OrganizerImagePaths','1. Images / editable image list',(30,60),[],[('image_paths','ORGANIZER_IMAGE_PATHS')],[json.dumps(images,ensure_ascii=False,indent=2)],(450,320))
 node(2,'OrganizerPixAIModel','2. PixAI model / load once',(30,420),[],[('pixai_model','ORGANIZER_PIXAI_MODEL')],[model_path,device],(450,145))
 node(3,'OrganizerPixAIAnalyze','3. Analyze / all tag scores',(550,80),[('image_paths','ORGANIZER_IMAGE_PATHS'),('pixai_model','ORGANIZER_PIXAI_MODEL')],[('all_scores','ORGANIZER_PIXAI_SCORES')],[])
 node(4,'OrganizerPixAIThresholds','4. Threshold settings',(550,350),[],[('thresholds','ORGANIZER_PIXAI_THRESHOLDS')],values,(360,250))
 node(5,'OrganizerPixAISelect','5. Select tags by threshold',(990,80),[('all_scores','ORGANIZER_PIXAI_SCORES'),('thresholds','ORGANIZER_PIXAI_THRESHOLDS')],[('selected_categories','ORGANIZER_PIXAI_TAGS')],[])
 node(6,'OrganizerPixAIFormat','6. Tag order / build captions',(1420,80),[('selected_categories','ORGANIZER_PIXAI_TAGS')],[('caption_json','STRING'),('category_scores_json','STRING')],[])
 node(7,'PreviewAny','7. Captions / JSON',(1840,50),[('source','*')],[('STRING','STRING')],[],(530,380))
 node(8,'PreviewAny','8. Category scores / JSON',(1840,480),[('source','*')],[('STRING','STRING')],[],(530,380))
 def connect(source,slot,target,input_slot,typ):
  ident=len(links)+1;links.append([ident,source,slot,target,input_slot,typ]);nodes[source-1]['outputs'][slot]['links'].append(ident);nodes[target-1]['inputs'][input_slot]['link']=ident
 connect(1,0,3,0,'ORGANIZER_IMAGE_PATHS');connect(2,0,3,1,'ORGANIZER_PIXAI_MODEL')
 connect(3,0,5,0,'ORGANIZER_PIXAI_SCORES');connect(4,0,5,1,'ORGANIZER_PIXAI_THRESHOLDS');connect(5,0,6,0,'ORGANIZER_PIXAI_TAGS');connect(6,0,7,0,'STRING');connect(6,1,8,0,'STRING')
 nodes.append({'id':9,'type':'Note','title':'Stages / no file writes','pos':[30,680],'size':[1690,230],'flags':{},'order':8,'mode':0,'properties':{},'widgets_values':['Update the Organizer bridge and restart this ComfyUI instance before opening this workflow.\n'
 '1: edit image_paths_json; 2: choose PixAI folder and device; 3: infer raw scores; 4: six independent thresholds; 5: filter scores; 6: order categories; 7/8: inspect results.\n'
 'When image paths, image timestamps and model files are unchanged and ComfyUI retains its cache, changing thresholds only reruns tag selection and formatting. Model weights are held on CPU between runs; GPU weights are released after analysis.\n'
 'Caption order: quality / meta / rating → character → copyright → style → subject counts → general.\n'
 'This workflow does NOT write image TXT files. Use Analyze and review changes in Model Library Organizer to review and save paired TXT. Opening the Desktop app does not import this workflow automatically: drag this saved JSON onto its canvas.']})
 return {'last_node_id':9,'last_link_id':len(links),'nodes':nodes,'links':links,'groups':[],'config':{},'extra':{},'version':.4}
