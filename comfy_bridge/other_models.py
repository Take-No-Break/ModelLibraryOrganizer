import json
from pathlib import Path
from .backend import image_paths

BACKENDS={'JoyCaption':'joycaption','CL Tagger':'cl_tagger','Taggerine':'taggerine'}
PROMPT='Describe the visible subject, clothing, pose, composition, background and art style in English. Return only the caption.'
CATEGORY='Model Library Organizer / Image to Text'

def selection(backend,model_path,device):
 if backend not in BACKENDS or device not in ('auto','cpu'):raise ValueError('Unsupported model backend or device.')
 path=Path(model_path).resolve(strict=True)
 if not path.is_dir():raise ValueError('Select the model folder.')
 return {'backend':BACKENDS[backend],'path':str(path),'device':device,'explicit_threshold':True}

def options(cl_threshold=.55,taggerine_threshold=.4,joy_prompt=PROMPT,joy_max_tokens=512):
 import math
 if any(not math.isfinite(float(v)) or not 0<=float(v)<=1 for v in (cl_threshold,taggerine_threshold)):raise ValueError('Thresholds must be between 0 and 1.')
 if not 1<=int(joy_max_tokens)<=4096:raise ValueError('Invalid maximum token count.')
 return dict(cl_threshold=float(cl_threshold),taggerine_threshold=float(taggerine_threshold),joy_prompt=joy_prompt,joy_max_tokens=int(joy_max_tokens))

def infer(paths,model,settings):
 from PIL import Image,ImageOps
 from comfy.utils import ProgressBar
 from .model_sessions import CaptionSession
 paths=image_paths(paths);out=[];progress=ProgressBar(len(paths))
 with CaptionSession(model) as session:
  cutoff=settings['cl_threshold'] if model['backend']=='cl_tagger' else settings['taggerine_threshold'] if model['backend']=='taggerine' else 0
  for index,path in enumerate(paths):
   with Image.open(path) as source:image=ImageOps.exif_transpose(source).convert('RGB')
   caption=session.caption(image,cutoff,settings['joy_prompt'],settings['joy_max_tokens'])
   if not isinstance(caption,str) or not caption.strip():raise ValueError('Empty caption: '+path)
   out.append({'image':path,'caption':caption.strip()});progress.update_absolute(index+1)
 return out

class OrganizerCaptionModel:
 @classmethod
 def INPUT_TYPES(cls):return {'required':{'backend':(list(BACKENDS),),'model_path':('STRING',{'default':''}),'device':(['auto','cpu'],)}}
 RETURN_TYPES=('ORGANIZER_OTHER_MODEL',);RETURN_NAMES=('caption_model',);FUNCTION='load';CATEGORY=CATEGORY
 def load(self,backend,model_path,device):return (selection(backend,model_path,device),)

class OrganizerCaptionSettings:
 @classmethod
 def INPUT_TYPES(cls):return {'required':{'cl_threshold':('FLOAT',{'default':.55,'min':0.,'max':1.,'step':.01,'precision':2}),'taggerine_threshold':('FLOAT',{'default':.4,'min':0.,'max':1.,'step':.01,'precision':2}),'joy_prompt':('STRING',{'default':PROMPT,'multiline':True}),'joy_max_tokens':('INT',{'default':512,'min':1,'max':4096})}}
 RETURN_TYPES=('ORGANIZER_OTHER_SETTINGS',);RETURN_NAMES=('settings',);FUNCTION='configure';CATEGORY=CATEGORY
 def configure(self,**kwargs):return (options(**kwargs),)

class OrganizerCaptionAnalyze:
 @classmethod
 def INPUT_TYPES(cls):return {'required':{'image_paths':('ORGANIZER_IMAGE_PATHS',),'caption_model':('ORGANIZER_OTHER_MODEL',),'settings':('ORGANIZER_OTHER_SETTINGS',)}}
 RETURN_TYPES=('ORGANIZER_OTHER_CAPTIONS',);RETURN_NAMES=('captions',);FUNCTION='run';CATEGORY=CATEGORY
 @classmethod
 def IS_CHANGED(cls,**kwargs):return float('nan')
 def run(self,image_paths,caption_model,settings):return (infer(image_paths,caption_model,settings),)

class OrganizerCaptionFormat:
 @classmethod
 def INPUT_TYPES(cls):return {'required':{'captions':('ORGANIZER_OTHER_CAPTIONS',)}}
 RETURN_TYPES=('STRING',);RETURN_NAMES=('caption_json',);FUNCTION='format';CATEGORY=CATEGORY
 def format(self,captions):return (json.dumps(captions,ensure_ascii=False),)

class OrganizerCaptionBatch:
 @classmethod
 def INPUT_TYPES(cls):
  return {'required':{'image_paths_json':('STRING',{'default':'[]','multiline':True}),**OrganizerCaptionModel.INPUT_TYPES()['required'],**OrganizerCaptionSettings.INPUT_TYPES()['required']}}
 RETURN_TYPES=('STRING',);RETURN_NAMES=('caption_json',);FUNCTION='run';CATEGORY=CATEGORY;OUTPUT_NODE=True
 @classmethod
 def IS_CHANGED(cls,**kwargs):return float('nan')
 def run(self,image_paths_json,backend,model_path,device,**kwargs):
  text=json.dumps(infer(image_paths_json,selection(backend,model_path,device),options(**kwargs)),ensure_ascii=False)
  return {'ui':{'text':[text]},'result':(text,)}

CLASSES={cls.__name__:cls for cls in (OrganizerCaptionModel,OrganizerCaptionSettings,OrganizerCaptionAnalyze,OrganizerCaptionFormat,OrganizerCaptionBatch)}
