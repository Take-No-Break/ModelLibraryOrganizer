"""Regression: centering must not replace pending window dimensions with 1x1."""
import tkinter as tk
import unittest
from types import SimpleNamespace
from unittest.mock import patch,MagicMock
import i18n

class PopupSizeTests(unittest.TestCase):
 def test_pending_size_changes_only_position(self):
  from display import center_popup
  window=MagicMock();parent=MagicMock()
  window._requested_size=(720,500)
  window.winfo_width.return_value=1;window.winfo_height.return_value=1
  window.winfo_screenwidth.return_value=1920;window.winfo_screenheight.return_value=1080
  parent.winfo_width.return_value=1000;parent.winfo_height.return_value=800
  parent.winfo_rootx.return_value=100;parent.winfo_rooty.return_value=100
  with patch('display.tk.Wm.geometry') as geometry:center_popup(window,parent)
  geometry.assert_called_once_with(window,'+240+250')

 def test_scan_all_dialog_preserves_size_and_buttons(self):
  from organization_ui import choose_layout
  from i18n import LocalizedToplevel
  for language,scale in [('ja',1),('en',1.5),('en',2)]:
   with self.subTest(language=language,scale=scale):
    i18n.set_language(language)
    root=tk.Tk();root.attributes('-alpha',0);root.geometry('1000x750+50+50');root.update()
    observed=[]
    def hidden_window(*args,**kwargs):
     window=LocalizedToplevel(*args,**kwargs);window.attributes('-alpha',0);return window
    def inspect():
     window=next(w for w in root.winfo_children() if isinstance(w,tk.Toplevel))
     dimensions=window.winfo_width(),window.winfo_height()
     def walk(widget):
      for child in widget.winfo_children():yield child;yield from walk(child)
     buttons=[w for w in walk(window) if w.winfo_class()=='TButton']
     observed.append((dimensions,[(b.winfo_rooty()-window.winfo_rooty(),b.winfo_height()) for b in buttons],len(buttons)))
     window.destroy()
    root.after(100,inspect)
    try:
     with patch('organization_ui.LocalizedToplevel',side_effect=hidden_window),patch.object(LocalizedToplevel,'grab_set'),patch('display.scaled_window_size',side_effect=lambda widget,w,h:(round(w*scale),round(h*scale))):
      self.assertIsNone(choose_layout(SimpleNamespace(root=root,preferences={})))
     expected=(min(round(720*scale),max(320,root.winfo_screenwidth()-60)),min(round(500*scale),max(220,root.winfo_screenheight()-100)))
     self.assertEqual(observed[0][0],expected)
     self.assertEqual(observed[0][2],2)
     for y,height in observed[0][1]:self.assertGreaterEqual(y,0);self.assertLessEqual(y+height,expected[1])
    finally:
     for job in root.tk.splitlist(root.tk.call('after','info')):root.after_cancel(job)
     root.destroy();i18n.set_language('ja')

if __name__=='__main__':unittest.main()
