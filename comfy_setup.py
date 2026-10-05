"""Small, local-only setup helpers; no disk-wide search and no server startup."""
import json
from pathlib import Path
from comfy_client import ComfyClient,NODE,base_url

def resolve_folder(value,kind):
    if not str(value).strip():raise ValueError('フォルダーを選択してください。')
    root=Path(value).resolve(strict=True)
    if root.is_file():root=root.parent
    def matches(p):
        return ((p/'main.py').is_file() and (p/'custom_nodes').is_dir()) if kind=='comfy' else (p/'tagger_pipeline.py').is_file()
    if matches(root):return str(root)
    candidates=[]
    # Inspect only children and grandchildren of the selected directory.
    for child in root.iterdir():
        if not child.is_dir() or child.is_symlink() or child.is_junction() or child.name.startswith('.'):continue
        if matches(child):candidates.append(child);continue
        for sub in child.iterdir():
            if sub.is_dir() and not sub.is_symlink() and not sub.is_junction() and matches(sub):candidates.append(sub)
    if len(candidates)==1:return str(candidates[0])
    if candidates:raise ValueError('複数の候補があります。使用するフォルダーを選択してください。\n'+'\n'.join(map(str,candidates)))
    raise ValueError('ComfyUI本体が見つかりません。main.pyが入ったフォルダーを選択してください。' if kind=='comfy' else 'PixAIモデルが見つかりません。tagger_pipeline.pyが入ったフォルダーを選択してください。')

def probe_running(url):
    client=ComfyClient(url)
    stats=client.request('/system_stats',timeout=2)
    if not isinstance(stats,dict) or not isinstance(stats.get('system'),dict):raise ValueError('Not a ComfyUI server.')
    info=client.request('/object_info/'+NODE,timeout=3)
    return {'url':client.url,'bridge':isinstance(info,dict) and NODE in info}

def find_running(configured,stop):
    urls=list(dict.fromkeys([base_url(configured),'http://127.0.0.1:8188','http://127.0.0.1:8000']))
    found=[]
    for url in urls:
        if stop.is_set():break
        try:found.append(probe_running(url))
        except (OSError,RuntimeError,ValueError):continue
    return found

def build_ui_workflow(images,model_path,thresholds,device='auto'):
    keys=['general','character','style','copyright','meta','rating']
    values=[json.dumps(images,ensure_ascii=False,indent=2),model_path,device]+[float(thresholds[k]) for k in keys]
    if any(not 0<=v<=1 for v in values[3:]):raise ValueError('Thresholds must be between 0 and 1.')
    return {'last_node_id':3,'last_link_id':1,'nodes':[
        {'id':1,'type':NODE,'pos':[40,70],'size':[550,490],'flags':{},'order':0,'mode':0,'inputs':[],
         'outputs':[{'name':'STRING','type':'STRING','links':[1],'slot_index':0}],
         'properties':{'Node name for S&R':NODE},'widgets_values':values,'title':'1. PixAI - image list and model'},
        {'id':2,'type':'PreviewAny','pos':[650,70],'size':[560,490],'flags':{},'order':1,'mode':0,
         'inputs':[{'name':'source','type':'*','link':1}], 'outputs':[{'name':'STRING','type':'STRING','links':None}],
         'properties':{'Node name for S&R':'PreviewAny'},'widgets_values':[],'title':'2. Captions (JSON preview)'},
        {'id':3,'type':'Note','pos':[40,610],'size':[1170,230],'flags':{},'order':2,'mode':0,'properties':{},
         'widgets_values':['Install the Organizer bridge node once, then restart ComfyUI. Drag this JSON onto the ComfyUI canvas or use Open.\n'
             'This template contains the image list at export time. Export again after adding images, or edit image_paths_json (a JSON array of full image paths).\n'
             'Set model_path to the PixAI folder containing tagger_pipeline.py. Thresholds are editable. Run to preview captions.\n'
             'This workflow does NOT write image TXT files. To review and save paired TXT, use Analyze and review changes in Model Library Organizer, connected to this ComfyUI server.\n'
             'PreviewAny is the built-in Preview as Text node; update ComfyUI if it is missing. Model weights and the GPU runtime are not included.'],
         'title':'How to use / no file writes'}],
        'links':[[1,1,0,2,0,'STRING']],'groups':[],'config':{},'extra':{},'version':0.4}
