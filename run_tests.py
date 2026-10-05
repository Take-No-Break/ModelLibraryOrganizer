import subprocess,sys
MODULES='test_pt_br test_core test_features test_providers test_support test_ui_changes test_dataset test_dataset_ui test_release17 test_comfy_setup test_restore test_public_release test_split_caption test_template_only test_release_cleanup'.split()
def main():
 for module in MODULES:
  run=subprocess.run([sys.executable,'-X','utf8','-m','unittest','-q',module],capture_output=True,text=True,encoding='utf-8')
  print(module+(': PASS' if run.returncode==0 else ': FAIL'),flush=True)
  if run.returncode:print(run.stdout+run.stderr);return run.returncode
 print('All checks passed.');return 0
if __name__=='__main__':raise SystemExit(main())
