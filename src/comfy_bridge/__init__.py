"""ComfyUI extension shipped with Model Library Organizer. Returns captions; never writes user files."""
import json,gc,importlib.util
from pathlib import Path

class OrganizerPixAICaptionBatch:
 @classmethod
 def INPUT_TYPES(cls):
  fields={'image_paths_json':('STRING',{'default':'[]','multiline':True}),'model_path':('STRING',{'default':''}),'device':(['auto','cpu'],)}
  for key,value in {'general':.17,'character':.27,'style':.15,'copyright':.24,'meta':.17,'rating':.41}.items():fields[key+'_threshold']=('FLOAT',{'default':value,'min':0.,'max':1.,'step':.01,'precision':2})
  return {'required':fields}
 RETURN_TYPES=('STRING',)
 FUNCTION='caption'
 OUTPUT_NODE=True
 CATEGORY='Model Library Organizer'
 @classmethod
 def IS_CHANGED(cls,**kwargs):return float('nan')
 def caption(self,image_paths_json,model_path,device,**thresholds):
  from .backend import image_paths,ModelHandle,analyze,select_tags,format_records
  handle=ModelHandle(model_path,device)
  try:
   records=select_tags(analyze(image_paths(image_paths_json),handle),{k.removesuffix('_threshold'):v for k,v in thresholds.items()})
   text=format_records(records)
   return {'ui':{'text':[text]},'result':(text,)}
  finally:
   del handle;gc.collect()

NODE_CLASS_MAPPINGS={'OrganizerPixAICaptionBatch':OrganizerPixAICaptionBatch}
NODE_DISPLAY_NAME_MAPPINGS={'OrganizerPixAICaptionBatch':'Organizer - PixAI Caption Batch (no file writes)'}

from .stages import CLASSES,NAMES
NODE_CLASS_MAPPINGS.update(CLASSES)
NODE_DISPLAY_NAME_MAPPINGS.update(NAMES)

from .other_models import CLASSES as OTHER_CLASSES
from .save_text import OrganizerSaveCaptionTXT
NODE_CLASS_MAPPINGS.update(OTHER_CLASSES)
NODE_CLASS_MAPPINGS["OrganizerSaveCaptionTXT"]=OrganizerSaveCaptionTXT
