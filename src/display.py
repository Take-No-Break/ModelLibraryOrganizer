"""Windows DPI setup and consistent readable Tk fonts."""
import sys
from tkinter import font

def center_popup(window,parent):
    window.update_idletasks()
    width=window.winfo_width();height=window.winfo_height()
    x=parent.winfo_rootx()+(parent.winfo_width()-width)//2
    y=parent.winfo_rooty()+(parent.winfo_height()-height)//2
    window.geometry(f'{width}x{height}{x:+d}{y:+d}')

def enable_dpi():
    if sys.platform != 'win32': return
    import ctypes
    try:
        # Tk 8.6 does not rescale all existing widgets on WM_DPICHANGED.
        # System awareness lets Windows scale the complete window when it moves
        # to a monitor with a different display scale, rather than keeping it tiny.
        if ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-2)): return
    except (AttributeError, OSError): pass
    try: ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError): pass

def scaled_window_size(root,width,height):
    scale=max(1,float(root.winfo_fpixels('1i'))/96)
    return round(width*scale),round(height*scale)

def configure_fonts(root):
    families=set(font.families(root))
    family='Yu Gothic UI' if 'Yu Gothic UI' in families else 'Segoe UI'
    for name in ('TkDefaultFont','TkTextFont','TkMenuFont','TkHeadingFont','TkCaptionFont','TkSmallCaptionFont','TkIconFont','TkTooltipFont'):
        font.nametofont(name,root=root).configure(family=family,size=11)
    root.option_add('*Text.Font','TkTextFont')
    root.option_add('*Entry.Font','TkTextFont')
    return family


def highlight_folder_paths(widget,paths):
    """Display each proposed/created directory in green without changing its text."""
    import tag_theme
    color='#8dd59f' if tag_theme.MODE=='dark' else '#19713a'
    widget.tag_configure('new_folders',foreground=color)
    for path in paths:
        start='1.0'
        while True:
            found=widget.search(str(path),start,stopindex='end',exact=True)
            if not found:break
            end=found+' + '+str(len(str(path)))+' chars'
            widget.tag_add('new_folders',found,end);start=end
    widget.tag_raise('new_folders')
