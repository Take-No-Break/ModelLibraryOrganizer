"""Loopback-only ComfyUI API transport. No inference dependencies in the organizer."""
import json,os,subprocess,time,uuid,urllib.request,urllib.error
from pathlib import Path
from urllib.parse import urlsplit
from core import Cancelled

NODE='OrganizerPixAICaptionBatch'
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError('Redirects are not allowed for local ComfyUI.')

def base_url(value):
 u=urlsplit(value.strip())
 if u.scheme!='http' or u.hostname not in ('127.0.0.1','localhost','::1') or u.username or u.password or u.query or u.fragment or u.path not in ('','/'):
  raise ValueError('Use a local ComfyUI HTTP address, e.g. http://127.0.0.1:8188')
 if u.port is not None and not 1<=u.port<=65535:raise ValueError('Invalid port.')
 return value.rstrip('/')

class ComfyClient:
 def __init__(self,url):self.url=base_url(url);self.opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
 def request(self,path,payload=None,timeout=10):
  raw=None if payload is None else json.dumps(payload).encode('utf-8')
  request=urllib.request.Request(self.url+path,data=raw,headers={'Content-Type':'application/json'})
  try:
   with self.opener.open(request,timeout=timeout) as response:data=response.read(32*1024*1024+1)
  except urllib.error.HTTPError as e:raise RuntimeError('ComfyUI HTTP '+str(e.code)+': '+e.read(4096).decode('utf-8',errors='replace'))
  if len(data)>32*1024*1024:raise ValueError('ComfyUI response too large.')
  return json.loads(data)
 def check(self):
  info=self.request('/object_info/'+NODE)
  if NODE not in info:raise ValueError('Organizer bridge node missing. Install the bundled node and restart ComfyUI.')
  return info
 def ensure(self,launcher='',auto_start=False,stop=None,status=lambda x:None):
  try:self.request('/system_stats',timeout=2)
  except (OSError,RuntimeError):
   if not auto_start:raise RuntimeError('ComfyUI is not running at '+self.url+'. Start ComfyUI or enable auto-start.')
   p=Path(launcher)
   if not p.is_file() or p.suffix.lower() not in ('.exe','.bat','.cmd','.lnk'):raise ValueError('Choose an existing ComfyUI launcher (.exe/.bat/.cmd/.lnk).')
   if p.suffix.lower()=='.lnk':os.startfile(str(p))
   elif p.suffix.lower() in ('.bat','.cmd'):
    command='"'+os.environ.get('COMSPEC','cmd.exe')+'" /d /s /c ""'+str(p.resolve())+'""'
    subprocess.Popen(command,cwd=str(p.parent),creationflags=subprocess.CREATE_NO_WINDOW)
   else:subprocess.Popen([str(p)],cwd=str(p.parent))
   for i in range(180):
    if stop and stop.is_set():raise Cancelled()
    status('ComfyUI起動待ち… '+str(i+1)+'s')
    try:self.request('/system_stats',timeout=1);break
    except (OSError,RuntimeError):time.sleep(1)
   else:raise RuntimeError('ComfyUI did not become ready. If the desktop launcher opened, start the installation there and check its port.')
  return self.check()
 def run(self,prompt,stop,status=lambda x:None,on_queued=lambda x:None,progress=None):
  client_id=str(uuid.uuid4());socket=None
  if progress is not None:
   try:
    import websocket
    socket=websocket.create_connection(self.url.replace('http://','ws://')+'/ws?clientId='+client_id,timeout=1,http_no_proxy=['localhost','127.0.0.1','::1'])
    socket.settimeout(.01)
   except Exception:socket=None
  try:
   return self._wait_prompt(prompt,stop,status,on_queued,progress,client_id,socket)
  finally:
   if socket is not None:socket.close()
 def _wait_prompt(self,prompt,stop,status,on_queued,progress,client_id,socket):
  response=self.request('/prompt',{'prompt':prompt,'client_id':client_id})
  if response.get('node_errors') or not response.get('prompt_id'):raise ValueError('ComfyUI rejected workflow: '+json.dumps(response,ensure_ascii=False))
  job=response['prompt_id'];on_queued(job);start=time.monotonic()
  while True:
   if stop.is_set():
    # Delete only this pending job. Never interrupt another user's active generation.
    self.request('/queue',{'delete':[job]})
    raise RuntimeError('結果待ちを停止しました。TXTは保存していません。実行中だった解析はComfyUI側で続く場合があります。Job: '+job)
   if socket is not None:
    import websocket
    try:
     for _ in range(100):
      raw=socket.recv()
      if not isinstance(raw,str):continue
      event=json.loads(raw);data=event.get('data',{})
      if event.get('type')=='progress' and data.get('prompt_id')==job and str(data.get('node'))=='1':
       if isinstance(data.get('value'),(int,float)) and isinstance(data.get('max'),(int,float)) and data['max']>0:progress(data['value'],data['max'])
    except (websocket.WebSocketTimeoutException,websocket.WebSocketConnectionClosedException,OSError,ValueError):pass
   history=self.request('/history/'+job)
   if job in history:
    item=history[job]
    if item.get('status',{}).get('status_str')=='error':raise RuntimeError('ComfyUI execution error: '+json.dumps(item.get('status',{}),ensure_ascii=False)[:4000])
    texts=item.get('outputs',{}).get('1',{}).get('text',[])
    if not texts:raise ValueError('ComfyUI returned no caption data. Check its console. Job: '+job)
    return json.loads(texts[0])
   status('ComfyUIで解析中／待機中… '+str(int(time.monotonic()-start))+'s / '+job[:8]);time.sleep(.6)
   if time.monotonic()-start>86400:raise TimeoutError('ComfyUI job exceeded 24 hours; check ComfyUI. Job: '+job)

def build_prompt(images,model_path,thresholds,device='auto'):
 return {'1':{'class_type':NODE,'inputs':{'image_paths_json':json.dumps(images,ensure_ascii=False),'model_path':model_path,'device':device,**{k+'_threshold':float(v) for k,v in thresholds.items()}}}}

def install_bridge(comfy_root,bundle):
 import shutil
 root=Path(comfy_root).resolve(strict=True)
 if not (root/'main.py').is_file() or not (root/'custom_nodes').is_dir():raise ValueError('Select the ComfyUI folder containing main.py and custom_nodes.')
 target=root/'custom_nodes'/'model_library_organizer_bridge'
 if target.exists() and not (target/'.organizer-bridge').exists():raise ValueError('Existing unmanaged bridge directory; refusing to overwrite.')
 target.mkdir(exist_ok=True)
 for name in ('__init__.py','tag_order.py','backend.py','stages.py','other_models.py','model_sessions.py','save_text.py','requirements.txt','README.md'):
  destination=target/name
  if destination.exists() and destination.read_bytes()!=(Path(bundle)/name).read_bytes():shutil.copy2(destination,destination.with_suffix('.py.bak'))
  shutil.copy2(Path(bundle)/name,destination)
 (target/'.organizer-bridge').write_text('Model Library Organizer bridge\n',encoding='utf-8')
 return str(target)
