import json,os
from pathlib import Path
from .backend import image_paths

class OrganizerSaveCaptionTXT:
 @classmethod
 def INPUT_TYPES(cls):return {'required':{'caption_json':('STRING',{'multiline':True,'forceInput':True}),'save_txt':('BOOLEAN',{'default':False}),'output_folder':('STRING',{'default':''})}}
 RETURN_TYPES=('STRING',);RETURN_NAMES=('save_report',);FUNCTION='save';CATEGORY='Model Library Organizer / Image to Text';OUTPUT_NODE=True
 @classmethod
 def IS_CHANGED(cls,**kwargs):return float('nan')
 def save(self,caption_json,save_txt,output_folder=''):
  if output_folder and save_txt:
   from .caption_output import save_output
   records=json.loads(caption_json)
   report=save_output(records,output_folder,[r['image'] for r in records])
   return {'ui':{'text':[report]},'result':(report,)}
  records=json.loads(caption_json)
  if not isinstance(records,list):raise ValueError('Expected caption records.')
  plan=[];seen=set()
  for record in records:
   path=Path(image_paths([record['image']])[0]).with_suffix('.txt');caption=record.get('caption')
   if not isinstance(caption,str) or not caption.strip():raise ValueError('Empty caption.')
   identity=os.path.normcase(str(path))
   if identity in seen:raise ValueError('Several images map to the same TXT: '+str(path))
   seen.add(identity);plan.append((path,caption.strip()+'\n'))
  saved=0;skipped=0
  if save_txt:
   for path,text in plan:
    # Never replace an existing caption or follow a TXT symlink.
    try:
     with path.open('xb') as stream:stream.write(text.encode('utf-8'))
     saved+=1
    except FileExistsError:skipped+=1
  report=f'TXT saved: {saved}; existing TXT skipped: {skipped}; captions: {len(plan)}. '+('Same folder and name as each image.' if save_txt else 'Saving is OFF; preview only.')
  return {'ui':{'text':[report]},'result':(report,)}
