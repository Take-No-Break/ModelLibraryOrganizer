"""Save completed local captions with image hardlinks; never overwrite existing files."""
import os
from pathlib import Path

def output_folder(images, backend):
    names={'PixAI':'PixAI','JoyCaption':'JoyCaption','CL Tagger':'CL-Tagger','Taggerine':'Taggerine'}
    if backend not in names:raise ValueError('Unsupported model type.')
    return Path(images).resolve()/names[backend]

def collect_images(folder, recursive=False):
    from dataset_files import list_dataset
    outputs=[output_folder(folder,b) for b in ('PixAI','JoyCaption','CL Tagger','Taggerine')]
    return [str(p) for row in list_dataset(folder,recursive,include_text=False) for p in row['images']
            if not any(Path(p).resolve().is_relative_to(out) for out in outputs)]

def save_output(records, output, expected_images):
    expected={str(Path(p).resolve()) for p in expected_images}
    root=Path(output).resolve()
    if not records or not isinstance(records,list):raise ValueError('No caption records returned.')
    plans=[];seen=set()
    for record in records:
        source=Path(record['image']).resolve(strict=True)
        if str(source) not in expected:raise ValueError('Unexpected image returned by ComfyUI.')
        text=record.get('caption')
        if not isinstance(text,str) or not text.strip():raise ValueError('Empty caption returned.')
        key=source.stem.casefold()
        if key in seen:raise ValueError('Duplicate image names would overwrite captions: '+source.stem)
        seen.add(key);plans.append((source,root/source.name,root/(source.stem+'.txt'),text.strip()+'\n'))
    if {str(p[0]) for p in plans}!=expected:raise ValueError('ComfyUI did not return all images.')
    root.mkdir(parents=True,exist_ok=True)
    for source,image,txt,text in plans:
        if source.stat().st_dev!=root.stat().st_dev:raise ValueError('Image hardlinks require the output folder to be on the same drive as the images.')
        if image.exists() and not os.path.samefile(source,image):raise ValueError('Existing output image has different contents: '+str(image))
    saved=skipped=0
    for source,image,txt,text in plans:
        if txt.exists() or txt.is_symlink():skipped+=1;continue
        created=False
        try:
            if not image.exists():os.link(source,image);created=True
            with txt.open('xb') as stream:stream.write(text.encode('utf-8'))
        except Exception:
            if created:image.unlink()
            raise
        saved+=1
    return f'TXT saved: {saved}; existing TXT skipped: {skipped}. Image hardlinks and TXT: {root}'

def run_local(url,images,model_path,backend,thresholds,device,settings,output,stop,status,progress):
    from comfy_client import ComfyClient,build_prompt
    import json
    client=ComfyClient(url)
    node='OrganizerPixAICaptionBatch' if backend=='PixAI' else 'OrganizerCaptionBatch'
    if node not in client.request('/object_info/'+node):
        raise ValueError('Required Organizer nodes are missing in the running ComfyUI. Install in that instance and restart ComfyUI.')
    if backend=='PixAI':prompt=build_prompt(images,model_path,thresholds,device)
    else:
        prompt={'1':{'class_type':node,'inputs':{'image_paths_json':json.dumps(images),'backend':backend,'model_path':model_path,'device':device,'cl_threshold':settings[0],'taggerine_threshold':settings[1],'joy_prompt':settings[2],'joy_max_tokens':settings[3]}}}
    records=client.run(prompt,stop,status,progress=progress)
    if stop.is_set():raise ValueError('Cancelled before saving outputs.')
    return save_output(records,output,images)
