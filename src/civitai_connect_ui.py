"""Experimental Civitai connection dialog."""
import queue,threading,tkinter as tk
from i18n import ttk,LocalizedToplevel,tr
from core import read_json,atomic_json
import civitai_auth,network
def show(app):
 window=LocalizedToplevel(app.root);window.title('Civitai connection (experimental)');window.transient(app.root)
 window.geometry('700x440')
 ttk.Label(window,text='Sign in through your browser. Previews remain general-audience only.\nCredentials are held in memory and cleared when the app closes.',wraplength=620).pack(anchor='w',padx=12,pady=12)
 config=app.engine.data/'civitai-oauth-client.json'
 client=tk.StringVar(value=(read_json(config,{}) or {}).get('client_id',''))
 from locales import CATALOG
 CATALOG['en']['取得場所：Civitaiのアカウント設定 → OAuth Apps → 新規アプリを登録（Public）→ 発行されたClient IDをコピー。\nこの番号は開発者が一度登録するアプリの識別番号です。ユーザーのログインIDやパスワードではありません。\n下の「OAuth app settings」で設定ページを開けます。']='Where to find it: Civitai account settings → OAuth Apps → Register a new app (Public) → Copy the issued Client ID.\nThis identifies the app registered once by its developer; it is not your login ID or password.\nUse OAuth app settings below to open the settings page.'
 ttk.Label(window,text='取得場所：Civitaiのアカウント設定 → OAuth Apps → 新規アプリを登録（Public）→ 発行されたClient IDをコピー。\nこの番号は開発者が一度登録するアプリの識別番号です。ユーザーのログインIDやパスワードではありません。\n下の「OAuth app settings」で設定ページを開けます。',wraplength=660).pack(anchor='w',padx=12,pady=8)
 ttk.Label(window,text='Public OAuth Client ID').pack(anchor='w',padx=12)
 ttk.Entry(window,textvariable=client).pack(fill='x',padx=12)
 callback_bar=ttk.Frame(window);callback_bar.pack(fill='x',padx=12,pady=(8,0))
 ttk.Label(callback_bar,text='Register callback (This is your PC): '+civitai_auth.REDIRECT,wraplength=560).pack(side='left',fill='x',expand=True)
 def copy_callback():
  window.clipboard_clear();window.clipboard_append(civitai_auth.REDIRECT)
 ttk.Button(callback_bar,text='Copy',command=copy_callback).pack(side='right',padx=(8,0))
 ttk.Label(window,text='Permissions: UserRead, ModelsRead, MediaRead',wraplength=660).pack(anchor='w',padx=12,pady=(4,8))
 status=tk.StringVar(value='Connected' if civitai_auth.bearer() else 'Not connected')
 ttk.Label(window,textvariable=status,wraplength=620).pack(anchor='w',padx=12,pady=6)
 events=queue.Queue()
 def poll():
  if not window.winfo_exists():return
  try:
   ok,message=events.get_nowait();status.set(message);button.configure(state='normal')
  except queue.Empty:pass
  window.after(100,poll)
 def connect():
  if network.OFFLINE or not app.online.get():status.set('Enable online API lookup before connecting.');return
  value=client.get().strip()
  if not value:status.set('Enter the Client ID from Civitai account settings → OAuth Apps.');return
  atomic_json(config,{'client_id':value})
  button.configure(state='disabled');status.set('Waiting for browser authorization (3 minute timeout)…')
  threading.Thread(target=civitai_auth.login,args=(value,lambda ok,msg:events.put((ok,msg))),daemon=True).start()
 def disconnect():
  civitai_auth.clear();status.set('Disconnected locally. Revoke consent in Civitai Connected Apps if needed.')
 bar=ttk.Frame(window);bar.pack(fill='x',padx=12)
 button=ttk.Button(bar,text='Connect with Civitai',command=connect);button.pack(side='left')
 ttk.Button(bar,text='Disconnect',command=disconnect).pack(side='left',padx=6)
 ttk.Button(bar,text='OAuth app settings',command=lambda:app.open_external('https://civitai.com/user/account')).pack(side='left')
 poll()
