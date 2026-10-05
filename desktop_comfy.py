"""Open a user-selected local Desktop UI independently of the API server URL."""
import os,subprocess
from pathlib import Path

def find_desktop_apps():
 roots=[Path(os.environ.get('LOCALAPPDATA',str(Path.home())))/'Programs',Path(os.environ.get('PROGRAMFILES',r'C:\Program Files'))]
 found=[]
 for root in roots:
  if not root.is_dir():continue
  for folder in root.iterdir():
   if not folder.is_dir() or 'comfy' not in folder.name.casefold():continue
   for app in folder.glob('*.exe'):
    if 'comfy' in app.stem.casefold() and 'uninstall' not in app.stem.casefold():found.append(str(app.resolve()))
 return sorted(set(found))

def open_desktop(path):
 app=Path(path).resolve(strict=True)
 if not app.is_file() or app.suffix.casefold()!='.exe':raise ValueError('Select the Comfy Desktop / ComfyUI application EXE, not its Python launcher.')
 return subprocess.Popen([str(app)],cwd=str(app.parent),shell=False)
