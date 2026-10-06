import json,webbrowser,time
from pathlib import Path
import tkinter as tk
import i18n,network
from i18n import ttk,messagebox,filedialog,LocalizedToplevel,LocalizedText,Tooltip,tr
from core import atomic_json,read_json
from support import VERSION,load_publisher,valid_repo,check_release,support_report,record_error
from guide import GUIDE

class SupportUI:
 def setup_support(self,outer):
    self.preferences=read_json(self.engine.data/'preferences.json',{}) or {}
    self.publisher=load_publisher(self.engine.data)
    network.OFFLINE=bool(self.preferences.get('offline',False))
    if network.OFFLINE:self.online.set(False)
    head=self.operation_header;head.pack(fill='x',before=self.tabs,pady=(0,3))
    self.operation_progress.pack_forget()
    version=ttk.Label(head,text='v'+VERSION,font=('Yu Gothic UI',9));version.grid(row=0,column=0,sticky='w')
    controls=ttk.Frame(head);controls.grid(row=0,column=2,sticky='e')
    self.language=tk.StringVar(value=i18n.LANGS[i18n.LANG])
    choose=ttk.Combobox(controls,values=list(i18n.LANGS.values()),textvariable=self.language,state='readonly',width=15,font=('Yu Gothic UI',9));choose.pack(side='right');choose.bind('<<ComboboxSelected>>',self.change_language)
    ttk.Label(controls,text='言語',font=('Yu Gothic UI',9)).pack(side='right',padx=5)
    self.appearance=tk.StringVar(value='Classic' if self.preferences.get('theme','classic')=='classic' else 'Dark')
    appearance=ttk.Combobox(controls,values=['Dark','Classic'],textvariable=self.appearance,state='readonly',width=8,font=('Yu Gothic UI',9))
    appearance.pack(side='right',padx=5);appearance.bind('<<ComboboxSelected>>',self.change_appearance)
    self.operation_progress.pack_forget();head.columnconfigure(1,weight=1)
    def fit_header(event=None):
        compact=head.winfo_width()<version.winfo_reqwidth()+controls.winfo_reqwidth()+self.operation_progress.winfo_reqwidth()+30
        controls.grid_configure(row=0,column=2,sticky='e')
        self.operation_progress.grid(row=1 if compact else 0,column=0 if compact else 1,columnspan=3 if compact else 1,sticky='e',pady=(2,0) if compact else 0)
    head.bind('<Configure>',fit_header,add='+');self.root.after_idle(fit_header)
    self.root.report_callback_exception=self.callback_error
    if self.preferences.get('auto_updates') and not network.OFFLINE and self.publisher.get('github_repository'):
        self.root.after(1800,lambda:self.check_updates(True))
 def change_appearance(self,event=None):
    old=self.preferences.get('theme','classic')
    mode='classic' if self.appearance.get()=='Classic' else 'dark'
    if not self.ready() or not self.editor_guard() or not self.tag_guard():
        self.appearance.set('Classic' if old=='classic' else 'Dark');return
    self.preferences['theme']=mode;self.preferences.pop('theme_color',None);self.save_preferences()
    self.change_language()
 def save_preferences(self):atomic_json(self.engine.data/'preferences.json',self.preferences)
 def change_language(self,event=None):
    code=next(k for k,v in i18n.LANGS.items() if v==self.language.get())
    if not self.ready() or not self.editor_guard() or not self.tag_guard():self.language.set(i18n.LANGS[i18n.LANG]);return
    root=self.root;data=self.engine.data;geometry=root.geometry()
    page=next((k for k,v in self.pages.items() if str(v)==self.current_page()),'models')
    rows=self.rows;dataset=self.dataset_rows;dataset_path=self.dataset_path.get()
    state={k:v.get() for k,v in vars(self).items() if isinstance(v,tk.Variable) and k not in ('language','appearance','theme_color','filter','status','header_status','editor_status','compat_origin','cap_connection')}
    groups={k:{name:v.get() for name,v in getattr(self,k).items()} for k in ('cap_thresholds','compat_roots')}
    context={k:getattr(self,k) for k in ['scan_source','scan_target'] if hasattr(self,k)}
    self.save_training_settings()
    self.preferences['language']=code;self.save_preferences()
    for timer in root.tk.splitlist(root.tk.call('after','info')):root.after_cancel(timer)
    for child in root.winfo_children():child.destroy()
    self.__init__(root,data)
    root.geometry(geometry)
    for k,v in state.items():getattr(self,k).set(v)
    for k,values in groups.items():
        for name,value in values.items():getattr(self,k)[name].set(value)
    for k,v in context.items():setattr(self,k,v)
    self.rows=rows;self.render();self.set_gallery_rows(rows,select=False)
    self.dataset_path.set(dataset_path);self.receive_dataset(dataset)
    self.update_template_view()
    self.populate_compatibility();self.select_page(self.pages[page])
 def callback_error(self,kind,value,tb):
    try:record_error(self.engine.data,value.with_traceback(tb),'ui_callback')
    except Exception:pass
    messagebox.showerror('確認が必要です',kind.__name__+'\n'+tr('通信診断・サポートログ'))
 def check_updates(self,automatic=False):
    if self.busy:
        if automatic:self.root.after(3000,lambda:self.check_updates(True))
        return
    if network.OFFLINE:
        if not automatic:messagebox.showinfo('更新','ネットワーク通信はオフライン設定で無効です。')
        return
    repo=self.publisher.get('github_repository','')
    if not repo:
        if not automatic:messagebox.showinfo('公開先未設定','公開先を設定してください。ログは自動送信されません。')
        return
    self.work(lambda:{**check_release(repo),'automatic':automatic},'release')
 def release_result(self,data):
    self.preferences['last_update_check']=time.time();self.save_preferences()
    if data['automatic'] and (not data['newer'] or self.preferences.get('notified_version')==data['latest']):return
    self.preferences['notified_version']=data['latest'];self.save_preferences()
    self.record_result('更新があります' if data['newer'] else '最新版です',f"{data['current']} → {data['latest']}\n{data['url']}\n{data['notes']}")
    win=self.open_panel('results','更新があります' if data['newer'] else '最新版です')
    ttk.Label(win,text=f"{data['current']} → {data['latest']}").pack(pady=10)
    box=LocalizedText(win,wrap='word');box.pack(fill='both',expand=True,padx=12);box.insert('1.0',data['notes']);box.configure(state='disabled')
    ttk.Button(win,text='リリースページを開く',command=lambda:self.open_external(data['url'])).pack(pady=8)
 def open_external(self,url):
    if network.OFFLINE:messagebox.showinfo('オフライン・プライバシー','ネットワーク通信はオフライン設定で無効です。');return
    if not str(url).startswith('https://'):raise ValueError('HTTPS URL required.')
    webbrowser.open(url)
 def help_center(self):
    win=self.open_panel('help','About')
    tabs=ttk.Notebook(win);tabs.pack(fill='both',expand=True,padx=12,pady=12)
    titles=['概要','識別と整理','オフライン・プライバシー','Support & Updates']
    for idx,title in enumerate(titles):
        frame=ttk.Frame(tabs,padding=12);tabs.add(frame,text=tr(title))
        body=LocalizedText(frame,wrap='word',height=12);body.pack(fill='both',expand=True);body.insert('1.0',GUIDE[i18n.LANG][idx]+('\n\n'+GUIDE[i18n.LANG][4] if idx==3 else ''));body.configure(state='disabled')
        if idx==2:
            offline=tk.BooleanVar(value=network.OFFLINE)
            def toggle(v=offline):
                network.OFFLINE=v.get();self.preferences['offline']=v.get();self.save_preferences()
                if v.get():self.online.set(False)
            ttk.Checkbutton(frame,text='完全オフライン（すべての通信を停止）',variable=offline,command=toggle,tooltip='ネットワーク通信はオフライン設定で無効です。').pack(anchor='w',pady=8)
        if idx==3:
            ttk.Button(frame,text='通信診断・サポートログ…',command=self.network_report).pack(side='left',padx=5)
            ttk.Button(frame,text='問い合わせページを開く',command=self.open_support).pack(side='left',padx=5)
        if idx==3:
            ttk.Button(frame,text='GitHub repository',command=self.open_repository).pack(side='left',padx=5)
            repo=self.publisher.get('github_repository','')
            if repo:
                link=ttk.Label(frame,text='https://github.com/'+valid_repo(repo),foreground=__import__('tag_theme').BLUE,cursor='hand2');link.pack(anchor='w',pady=5);link.bind('<Button-1>',lambda event:self.open_repository())
            auto=tk.BooleanVar(value=self.preferences.get('auto_updates',False))
            def toggle_auto(v=auto):self.preferences['auto_updates']=v.get();self.save_preferences()
            ttk.Checkbutton(frame,text='起動時に更新を確認（任意）',variable=auto,command=toggle_auto,tooltip='最新版の確認にはインターネット接続が必要です。自動インストールはしません。').pack(anchor='w',pady=8)
            ttk.Button(frame,text='更新を確認',command=self.check_updates).pack(side='left',padx=5)
            ttk.Button(frame,text='更新・サポート設定',command=self.publisher_settings).pack(side='left',padx=5)
    about=ttk.Frame(tabs,padding=12);tabs.add(about,text='About')
    tabs.select(about)
    body=tk.Text(about,wrap='word');body.pack(fill='both',expand=True)
    body.insert('1.0',f'''Model Library Organizer {VERSION}

A desktop utility for inspecting and organizing local AI model libraries.

Identify models using file structure, embedded metadata, SHA256 hashes and available public source information. Review proposed destinations and hard links before applying file changes. Unidentified files remain visible for review.

Compatibility colors are estimates: green indicates the same family, yellow indicates related SDXL families, and gray indicates no known relationship or insufficient information. Successful loading does not guarantee useful results. You can record a separate assessment for each LoRA/checkpoint pair after testing it.

Image to Text exports editable ComfyUI workflow templates for supported image analysis models. The app can submit analysis to an already running local ComfyUI server, or export a workflow to run there. It does not launch or restart ComfyUI. Current outputs use an adapter-named image subfolder containing original-image hardlinks and matching TXT. The text editor supports individual and batch caption edits. Model source TXT instead documents model identity, source links, family, trigger words and other selected metadata; it is not a training caption.

Model weights, ComfyUI and a GPU runtime are not bundled. Choose folders on each computer; the app does not search every drive. Preview images are shown inside the app, not written beside your models.

Online lookup can send model hashes and search names to source services. Offline mode disables external requests; workflow template creation and text editing remain available. Diagnostic reports are not uploaded automatically. Updates and support links depend on the distributor's configured publication address.

Source lookup limits: Combined scanning automatically checks Civitai and Hugging Face. Civitai uses SHA256 lookup; Hugging Face searches up to five filename-based candidates on their main branch, then verifies file SHA256. It is not a global hash index. SeaArt's published interfaces do not provide a verified public reverse-SHA256 lookup for this app; SeaArt-only downloads can remain unidentified. Tensor.Art supports website hash searches: enter @sha256 followed by the file's SHA256 in its search box (https://tensor.art/updates). An automatic public reverse-hash API has not been verified for this app, so it does not automatically query Tensor.Art. The lookup report distinguishes these limitations from requests actually made. Check the original download page and add its URL manually. A matching filename alone is not proof. Safetensors is a file format, not a distribution website.

Scan and restoration: Every scan first saves a JSON inventory of original file/folder paths under scan-history. Scanning does not move files. Applying approved changes separately writes a move journal under history before the first change and links it to that inventory. Select the inventory or open its JSON in History / Restore to inspect it; restore uses the linked move journals. Inventory is not a file-content backup, and it cannot undo edits/deletions or changes made outside this app.

Source descriptions and model names retain their original language. Exported model information uses English field labels. This application is independent of ComfyUI, Civitai, Hugging Face and the model authors.

Folder organization: Starting a scan offers the existing type/category layout or provider / creator / type / family. Creator mode uses verified source metadata; Hugging Face namespaces may be organizations. Unknown creators or types stay in place for review. Already organized libraries can be scanned again to propose the other layout. The destination models root remains user-selected. Provider-first layouts can require corresponding ComfyUI model-search configuration. Only empty former source folders are removed after approved moves; installed files, independent duplicate copies and existing hard-link aliases are not deleted. Empty-folder changes are recorded with the move history. Recognized ComfyUI workflow JSON files are included; arbitrary JSON settings are not treated as workflows.

Create source TXT fills in missing model information files. A scan alone does not create these TXT files. Applying organization creates a TXT if missing and moves an existing source TXT with its model. The button skips existing TXT rather than creating extra copies or overwriting edits. Update readable TXT is a separate explicit operation with backup.

Tag editor statistics count how many caption TXT files contain each comma-separated tag, counting a tag once per file. The denominator includes existing TXT, including empty files, and new captions with pending edits; images without a TXT and without edits are excluded. This is dataset usage frequency, not rating/tag confidence from an AI model. Source-information .source.txt files are excluded. Tag editor shares the folder and frequency statistics. Scroll the left-hand image thumbnails and select them with Ctrl/Shift. Compact rounded tags can be sorted by count/name, searched and filtered by category; clicking a statistics tag filters the images containing it. Category filters show matching tags, not image recognition: local keyword rules assign categories, and right-click offers manual overrides. Click an image's tag to edit it, then Enter to apply or Esc to cancel; × removes it from that image. Bulk Insert, Remove, Remove unwanted, Delete category and Delete all tags use the Selected / Filtered / All scope. Registering an unwanted tag alone does not remove existing tags; it excludes that exact tag from future Bulk Insert, and Remove unwanted stages explicit removal. Save all changes opens a before/after review, then updates original TXT with conflict checks and caption-backups. Images are never edited. No auto-tagging or model inference is performed by these tabs.
''');body.configure(state='disabled')
 def publisher_settings(self):
    win=self.open_panel('help','更新・サポート設定')
    ttk.Label(win,text='GitHub: owner/repository').pack(anchor='w',padx=16,pady=10)
    repo=tk.StringVar(value=self.publisher.get('github_repository',''));ttk.Entry(win,textvariable=repo,width=95).pack(padx=16,fill='x')
    ttk.Label(win,text='Support URL (HTTPS) — optional; default: GitHub Issues').pack(anchor='w',padx=16,pady=10)
    url=tk.StringVar(value=self.publisher.get('support_url',''));ttk.Entry(win,textvariable=url,width=95).pack(padx=16,fill='x')
    def config():
        r=valid_repo(repo.get()) if repo.get().strip() else ''
        u=url.get().strip()
        from urllib.parse import urlparse
        if u:
            parsed=urlparse(u)
            if parsed.scheme!='https' or not parsed.netloc or parsed.username or parsed.password:raise ValueError('Use an HTTPS support page without embedded credentials.')
        return {'github_repository':r,'support_url':u}
    def save(export=False):
        try:
            c=config()
            if export:
                path=filedialog.asksaveasfilename(parent=win,initialfile='publisher.json',defaultextension='.json')
                if path:atomic_json(path,c)
            else:
                atomic_json(self.engine.data/'publisher-settings.json',c);self.publisher=c;self.help_center()
        except Exception as e:messagebox.showerror('確認が必要です',str(e),parent=win)
    ttk.Button(win,text='設定を保存',command=save).pack(pady=12)
    ttk.Button(win,text='配布用設定を書き出す',command=lambda:save(True)).pack()
 def open_repository(self):
    repo=self.publisher.get('github_repository','')
    if not repo:self.publisher_settings();return
    self.open_external('https://github.com/'+valid_repo(repo))
 def open_support(self):
    url=self.publisher.get('support_url','');repo=self.publisher.get('github_repository','')
    if not url and repo:url='https://github.com/'+valid_repo(repo)+'/issues/new/choose'
    if not url:messagebox.showinfo('公開先未設定','公開先を設定してください。ログは自動送信されません。');return
    self.open_external(url)
 def network_report(self):
    report=support_report(self.engine.data)
    win=self.open_panel('results','通信診断・サポートログ')
    box=LocalizedText(win,wrap='word');box.pack(fill='both',expand=True,padx=12,pady=12)
    box.insert('1.0',GUIDE[i18n.LANG][3]+'\n\n'+json.dumps(report,ensure_ascii=False,indent=2));box.configure(state='disabled')
    def export():
        p=filedialog.asksaveasfilename(parent=win,defaultextension='.json',initialfile='model-organizer-support.json')
        if p:atomic_json(p,report);messagebox.showinfo('保存完了','必要な場合、このJSONを配布者に送ってください。',parent=win)
    ttk.Button(win,text='診断ログを保存…（自動送信なし）',command=export).pack(side='left',padx=12,pady=10)
    ttk.Button(win,text='問い合わせページを開く',command=self.open_support).pack(side='left',padx=12,pady=10)

