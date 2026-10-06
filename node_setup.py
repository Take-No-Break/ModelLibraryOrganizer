"""Discover a few local ComfyUI locations and install the bundled extension."""
import os,json,shutil,subprocess,uuid
from pathlib import Path

def node_directory(value):
 p=Path(value).resolve(strict=True)
 if not p.is_dir():raise ValueError('Choose a folder.')
 if p.name.casefold()=='custom_nodes':return p
 if (p/'custom_nodes').is_dir():return p/'custom_nodes'
 if (p/'ComfyUI'/'custom_nodes').is_dir():return p/'ComfyUI'/'custom_nodes'
 raise ValueError('Choose your actual ComfyUI folder or its custom_nodes folder.')

def candidates(saved=''):
 paths=[saved] if saved else []
 appdata=Path(os.environ.get('APPDATA',Path.home()/'AppData/Roaming'))
 for name in ('ComfyUI','Comfy Desktop'):
  try:
   data=json.loads((appdata/name/'config.json').read_text(encoding='utf-8'))
   paths.extend(data[k] for k in ('basePath','installPath') if isinstance(data.get(k),str))
  except (OSError,ValueError):pass
 if os.name=='nt':
  try:
   command="Get-CimInstance Win32_Process -Filter \"Name = 'python.exe'\" | Where-Object { $_.CommandLine -like '*ComfyUI*main.py*' } | Select-Object -ExpandProperty ExecutablePath | ConvertTo-Json -Compress"
   result=subprocess.run(['powershell','-NoProfile','-Command',command],capture_output=True,text=True,timeout=10,creationflags=subprocess.CREATE_NO_WINDOW)
   exes=json.loads(result.stdout or '[]');exes=[exes] if isinstance(exes,str) else exes
   for exe in exes:
    paths=[str(p) for p in Path(exe).parents]+paths
  except (OSError,ValueError,subprocess.TimeoutExpired):pass
 found=[]
 for path in paths:
  try:
   directory=node_directory(path)
   if str(directory) not in found:found.append(str(directory))
  except (OSError,ValueError):pass
 return found

def install(value,bundle):
 directory=node_directory(value);target=directory/'model_library_organizer_bridge';bundle=Path(bundle)
 files=[p for p in bundle.iterdir() if p.is_file() and p.suffix in ('.py','.txt','.md')]
 if not any(p.name=='__init__.py' for p in files):raise ValueError('Bundled nodes are missing.')
 if target.is_symlink() or (hasattr(target,'is_junction') and target.is_junction()):raise ValueError('Cannot install through a directory link.')
 if target.exists() and not (target/'.organizer-bridge').exists():
  if any(not (target/p.name).is_file() or (target/p.name).read_bytes()!=p.read_bytes() for p in files):raise ValueError('An unmanaged folder already exists at the destination. It was not overwritten.')
 target.mkdir(exist_ok=True)
 for source in files:
  destination=target/source.name
  if destination.is_symlink():raise ValueError('A linked file exists at the destination.')
  if destination.exists() and destination.read_bytes()!=source.read_bytes():shutil.copy2(destination,target/(source.name+'.'+uuid.uuid4().hex[:8]+'.bak'))
  shutil.copy2(source,destination)
 (target/'.organizer-bridge').write_text('Model Library Organizer bridge\n',encoding='utf-8')
 return str(target)
