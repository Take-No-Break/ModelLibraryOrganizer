import json
from pathlib import Path
from .backend import image_paths,ModelHandle,analyze,limits,select_tags,format_records,DEFAULTS

CATEGORY='Model Library Organizer / PixAI stages'

class OrganizerImagePaths:
 @classmethod
 def INPUT_TYPES(cls):return {'required':{'image_paths_json':('STRING',{'default':'[]','multiline':True})}}
 RETURN_TYPES=('ORGANIZER_IMAGE_PATHS',);RETURN_NAMES=('image_paths',);FUNCTION='paths';CATEGORY=CATEGORY
 @classmethod
 def IS_CHANGED(cls,image_paths_json):
  return json.dumps([(name,Path(name).stat().st_size,Path(name).stat().st_mtime_ns) for name in image_paths(image_paths_json)])
 def paths(self,image_paths_json):return (image_paths(image_paths_json),)

class OrganizerPixAIModel:
 @classmethod
 def INPUT_TYPES(cls):return {'required':{'model_path':('STRING',{'default':''}),'device':(['auto','cpu'],)}}
 RETURN_TYPES=('ORGANIZER_PIXAI_MODEL',);RETURN_NAMES=('pixai_model',);FUNCTION='load';CATEGORY=CATEGORY
 @classmethod
 def IS_CHANGED(cls,model_path,device):
  root=Path(model_path)
  return json.dumps([(p.name,p.stat().st_size,p.stat().st_mtime_ns) for p in sorted(root.iterdir()) if p.is_file()])
 def load(self,model_path,device):return (ModelHandle(model_path,device),)

class OrganizerPixAIAnalyze:
 @classmethod
 def INPUT_TYPES(cls):return {'required':{'image_paths':('ORGANIZER_IMAGE_PATHS',),'pixai_model':('ORGANIZER_PIXAI_MODEL',)}}
 RETURN_TYPES=('ORGANIZER_PIXAI_SCORES',);RETURN_NAMES=('all_scores',);FUNCTION='run';CATEGORY=CATEGORY
 def run(self,image_paths,pixai_model):return (analyze(image_paths,pixai_model),)

class OrganizerPixAIThresholds:
 @classmethod
 def INPUT_TYPES(cls):return {'required':{key+'_threshold':('FLOAT',{'default':value,'min':0.,'max':1.,'step':.01,'precision':2}) for key,value in DEFAULTS.items()}}
 RETURN_TYPES=('ORGANIZER_PIXAI_THRESHOLDS',);RETURN_NAMES=('thresholds',);FUNCTION='configure';CATEGORY=CATEGORY
 def configure(self,**values):return (limits({key:values[key+'_threshold'] for key in DEFAULTS}),)

class OrganizerPixAISelect:
 @classmethod
 def INPUT_TYPES(cls):return {'required':{'all_scores':('ORGANIZER_PIXAI_SCORES',),'thresholds':('ORGANIZER_PIXAI_THRESHOLDS',)}}
 RETURN_TYPES=('ORGANIZER_PIXAI_TAGS',);RETURN_NAMES=('selected_categories',);FUNCTION='select';CATEGORY=CATEGORY
 def select(self,all_scores,thresholds):return (select_tags(all_scores,thresholds),)

class OrganizerPixAIFormat:
 @classmethod
 def INPUT_TYPES(cls):return {'required':{'selected_categories':('ORGANIZER_PIXAI_TAGS',)}}
 RETURN_TYPES=('STRING','STRING');RETURN_NAMES=('caption_json','category_scores_json');FUNCTION='format';CATEGORY=CATEGORY;OUTPUT_NODE=True
 def format(self,selected_categories):
  text=format_records(selected_categories);details=json.dumps(selected_categories,ensure_ascii=False)
  return {'ui':{'text':[text]},'result':(text,details)}

CLASSES={cls.__name__:cls for cls in (OrganizerImagePaths,OrganizerPixAIModel,OrganizerPixAIAnalyze,OrganizerPixAIThresholds,OrganizerPixAISelect,OrganizerPixAIFormat)}
NAMES=dict(zip(CLASSES,('1. Image paths','2. Load PixAI model','3. Analyze images / all scores','4. PixAI thresholds','5. Select category tags','6. Order tags / caption JSON')))
