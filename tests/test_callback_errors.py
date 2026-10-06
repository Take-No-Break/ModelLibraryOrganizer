import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from support_ui import SupportUI
from scroll_pages import scroll_wheel


class CallbackErrorTests(unittest.TestCase):
    def test_native_dialog_widget_is_ignored(self):
        self.assertIsNone(scroll_wheel(SimpleNamespace(widget='.!native_dialog', state=0, delta=120)))

    def test_repeated_callback_error_shows_one_explained_dialog(self):
        with tempfile.TemporaryDirectory() as folder:
            app=SimpleNamespace(engine=SimpleNamespace(data=Path(folder)),root=None)
            try:
                getattr('native-widget','winfo_class')
            except AttributeError as exc:
                with patch('support_ui.messagebox.showerror') as popup:
                    for _ in range(3):SupportUI.callback_error(app,type(exc),exc,exc.__traceback__)
                    self.assertEqual(popup.call_count,1)
                    self.assertIn('MLO-',popup.call_args.args[1])
                    self.assertIn('AttributeError',popup.call_args.args[1])
                    self.assertGreater(len(popup.call_args.args[1]),100)
