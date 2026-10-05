"""Shared PixAI stages. Import torch only inside the ComfyUI execution process."""
import gc,importlib.util,json,math,threading
from pathlib import Path
from .tag_order import format_pixai_tags

KEYS=('general','character','style','copyright','meta','rating')
DEFAULTS=dict(zip(KEYS,(.17,.27,.15,.24,.17,.41)))

def image_paths(value):
 paths=json.loads(value) if isinstance(value,str) else value
 if not isinstance(paths,list) or not 1<=len(paths)<=10000:raise ValueError('Expected 1–10000 image paths.')
 out=[]
 for name in paths:
  if not isinstance(name,str):raise ValueError('Image paths must be strings.')
  path=Path(name).resolve(strict=True)
  if not path.is_file() or path.suffix.lower() not in ('.png','.jpg','.jpeg','.webp','.bmp','.tif','.tiff'):raise ValueError('Unsupported image: '+name)
  out.append(str(path))
 return out

def limits(values):
 result={key:float(values[key]) for key in KEYS}
 if any(not math.isfinite(v) or not 0<=v<=1 for v in result.values()):raise ValueError('Thresholds must be finite numbers between 0 and 1.')
 return result

class ModelHandle:
 def __init__(self,path,device):
  if device not in ('auto','cpu'):raise ValueError('Unsupported device.')
  root=Path(path).resolve(strict=True)
  if not (root/'tagger_pipeline.py').is_file():raise ValueError('Select the PixAI folder containing tagger_pipeline.py.')
  spec=importlib.util.spec_from_file_location('organizer_pixai_pipeline',root/'tagger_pipeline.py')
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  self.model=module.ViTDetCls.from_pretrained(str(root),local_files_only=True).to('cpu').eval()
  size=json.loads((root/'preprocessor_config.json').read_text(encoding='utf-8'))['size']
  self.processor=module.RescalePadProcessor(size=size);self.device=device;self.lock=threading.RLock()

def analyze(paths,handle):
 import torch
 from PIL import Image,ImageOps
 import comfy.model_management as mm
 from comfy.utils import ProgressBar
 paths=image_paths(paths);progress=ProgressBar(len(paths));records=[]
 with handle.lock:
  target=mm.get_torch_device() if handle.device=='auto' else torch.device('cpu')
  mm.unload_all_models()
  try:
   handle.model.to(target)
   with torch.inference_mode():
    for index,path in enumerate(paths):
     mm.throw_exception_if_processing_interrupted()
     with Image.open(path) as source:image=ImageOps.exif_transpose(source).convert('RGB')
     pixels=handle.processor(image)['pixel_values'].to(device=target,dtype=handle.model.dtype)
     scores=handle.model(pixels).sigmoid()[0].detach().to('cpu').clone()
     records.append({'image':path,'scores':scores});progress.update_absolute(index+1)
   return {'tags':handle.model.config.tags,'splits':handle.model.config.tags_split,'items':records}
  finally:
   handle.model.to('cpu');gc.collect();mm.soft_empty_cache()

def select_tags(raw,thresholds):
 thresholds=limits(thresholds);records=[]
 for record in raw['items']:
  results={};start=0;scores=record['scores']
  for category,count in raw['splits']:
   cutoff=thresholds.get(category,.2)
   if hasattr(scores,'dtype'):
    indices=(scores[start:start+count]>cutoff).nonzero().flatten().tolist()
   else:indices=[i for i in range(count) if float(scores[start+i])>cutoff]
   results[category]={raw['tags'][start+i]:float(scores[start+i]) for i in indices}
   start+=count
  if start!=len(scores) or start!=len(raw['tags']):raise ValueError('PixAI tag dimensions do not match.')
  records.append({'image':record['image'],'results':results})
 return records

def format_records(records):
 output=[]
 for record in records:
  caption=format_pixai_tags(record['results'])
  if not caption.strip():raise ValueError('Empty caption: '+record['image'])
  output.append({'image':record['image'],'caption':caption})
 return json.dumps(output,ensure_ascii=False)
