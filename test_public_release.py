import tempfile,unittest,tkinter as tk,json,threading
from pathlib import Path
from unittest.mock import patch
from app import App
from core import Engine
from comfy_client import ComfyClient

class ReleaseTests(unittest.TestCase):
 def test_high_dpi_window_size_and_system_awareness(self):
  from display import scaled_window_size,enable_dpi
  from unittest.mock import Mock
  root=Mock();root.winfo_fpixels.return_value=192
  self.assertEqual(scaled_window_size(root,1320,860),(2640,1720))
  root.winfo_fpixels.return_value=96
  self.assertEqual(scaled_window_size(root,1320,860),(1320,860))
  with patch('ctypes.windll') as libraries,patch('display.sys.platform','win32'):
   libraries.user32.SetProcessDpiAwarenessContext.return_value=True
   enable_dpi()
   self.assertEqual(__import__('ctypes').c_ssize_t(libraries.user32.SetProcessDpiAwarenessContext.call_args.args[0].value).value,-2)
 def test_unwanted_source_search_button_removed(self):
  with tempfile.TemporaryDirectory() as folder:
   root=tk.Tk();root.withdraw()
   try:
    app=App(root,Path(folder));root.update()
    def children(widget):
     for child in widget.winfo_children():
      yield child
      yield from children(child)
    labels=[str(w.cget('text')) for w in children(app.pages['tools']) if 'text' in w.keys()]
    self.assertFalse(any('SeaArt' in text for text in labels))
   finally:root.update_idletasks();root.destroy()
 def test_completion_popup_keeps_tab_and_persists_history(self):
  with tempfile.TemporaryDirectory() as folder:
   root=tk.Tk();root.withdraw()
   try:
    app=App(root,Path(folder));root.update()
    self.assertEqual(app.tabs.tabs()[0],str(app.page_hosts['results']))
    app.select_page(app.pages['captions']);before=app.current_page()
    with patch('result_ui.messagebox.showinfo') as popup:app.show_text('API export complete','workflow.json')
    popup.assert_called_once();self.assertEqual(app.current_page(),before)
    self.assertEqual(len(list((Path(folder)/'operation-results').glob('*.json'))),1)
    app.refresh_results();self.assertTrue(any(r['text']=='workflow.json' for r in app.result_records.values()))
    app.record_result('Second result','captions saved');self.assertEqual(len(app.result_records),2)
   finally:root.update_idletasks();root.destroy()
 def test_caption_review_is_popup_without_navigation(self):
  with tempfile.TemporaryDirectory() as folder:
   root=tk.Tk();root.withdraw()
   try:
    app=App(root,Path(folder));root.update();app.select_page(app.pages['captions'])
    before=app.current_page()
    app.show_caption_plan([{'path':'sample.txt','before_text':'old','after_text':'new'}])
    self.assertEqual(app.current_page(),before)
    self.assertTrue(any(isinstance(w,tk.Toplevel) for w in root.winfo_children()))
    self.assertTrue(any('BEFORE\nold\nAFTER\nnew' in r['text'] for r in app.result_records.values()))
   finally:root.update_idletasks();root.destroy()
 def test_grouped_navigation_and_percentage(self):
  with tempfile.TemporaryDirectory() as folder:
   root=tk.Tk();root.withdraw()
   try:
    app=App(root,Path(folder));root.update()
    self.assertEqual(len(app.tabs.tabs()),7)
    app.select_page(app.pages['preview']);self.assertEqual(app.current_page(),str(app.pages['preview']))
    app.select_page(app.pages['texts']);self.assertEqual(app.current_page(),str(app.pages['texts']))
    self.assertEqual(app.tabs.tab(app.page_hosts['help'],'text'),'About')
    app.set_progress(17,100);self.assertEqual(app.progress_label.get(),'17%')
    self.assertEqual(float(app.progress['value']),17)
    self.assertEqual(str(app.progress['mode']),'determinate')
   finally:root.update_idletasks();root.destroy()
 def test_scan_counts_completed_files(self):
  with tempfile.TemporaryDirectory() as folder:
   base=Path(folder);source=base/'models';source.mkdir()
   for n in range(3):(source/f'{n}.safetensors').write_bytes(b'not-a-model')
   events=[];Engine(base/'data').scan(source,source,online=False,progress=lambda a,b:events.append((a,b)))
   self.assertEqual(events,[(0,3),(1,3),(2,3),(3,3)])
 def test_comfy_receives_matching_progress_only(self):
  client=ComfyClient('http://127.0.0.1:8188');events=[]
  class Socket:
   def recv(self):
    import websocket
    if self.frames:return json.dumps(self.frames.pop(0))
    raise websocket.WebSocketTimeoutException()
   frames=[{'type':'progress','data':{'prompt_id':'other','node':'1','value':9,'max':10}}, {'type':'progress','data':{'prompt_id':'job','node':'1','value':2,'max':4}}]
  with patch.object(client,'request',side_effect=[{'prompt_id':'job'},{'job':{'outputs':{'1':{'text':['[]']}}}}]):
   self.assertEqual(client._wait_prompt({},threading.Event(),lambda _:None,lambda _:None,lambda a,b:events.append((a,b)),'client',Socket()),[])
  self.assertEqual(events,[(2,4)])
