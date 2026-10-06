import subprocess,sys,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ENV=dict(os.environ, PYTHONPATH=os.pathsep.join([str(ROOT/"src"),str(ROOT/"tests")]))
MODULES='test_node_setup test_caption_output test_tag_editor test_organization test_scan_history test_pt_br test_core test_features test_providers test_support test_ui_changes test_dataset test_dataset_ui test_release17 test_comfy_setup test_restore test_public_release test_split_caption test_template_only test_release_cleanup'.split()
def main():
 MODULES.append('test_gallery_filters')
 MODULES.append('test_callback_errors')
 for module in MODULES:
  run=subprocess.run([sys.executable,'-X','utf8','-m','unittest','-q',module],cwd=ROOT,env=ENV,capture_output=True,text=True,encoding='utf-8')
  print(module+(': PASS' if run.returncode==0 else ': FAIL'),flush=True)
  if run.returncode:print(run.stdout+run.stderr);return run.returncode
 print('All checks passed.');return 0
if __name__=='__main__':raise SystemExit(main())
