import csv
import json
import os
import queue
import sys
import threading
import traceback
import webbrowser
from pathlib import Path
import tkinter as tk
from i18n import ttk, filedialog, messagebox, simpledialog, LocalizedText, LocalizedToplevel, ChoiceVar, StatusVar, Tooltip, tr, set_language
from core import Engine, Cancelled, CATEGORIES, atomic_json, read_json

DATA=Path(os.environ.get('LOCALAPPDATA',str(Path.home())))/'ModelLibraryOrganizer'

from feature_ui import FeatureUI
from support_ui import SupportUI
from support import record_error
from panels import Panels
from dataset_editor import DatasetEditor
from caption_ui import CaptionUI
from restore_ui import RestoreUI
from result_ui import ResultUI
import network

class App(Panels,CaptionUI,DatasetEditor,SupportUI,FeatureUI,RestoreUI,ResultUI):
    def __init__(self,root,data=DATA):
        self.root=root;self.engine=Engine(data);self.rows=[];self.events=queue.Queue();self.stop=threading.Event();self.busy=False
        seed=read_json(Path(getattr(sys,'_MEIPASS',Path(__file__).parent))/'seed_registry.json',{})
        if not self.engine.cache.get('seed_imported'):
            for k in ['models','choices']:
                for sha,v in seed.get(k,{}).items():self.engine.cache[k].setdefault(sha,v)
            self.engine.cache['seed_imported']=True;self.engine.save()
        set_language((read_json(self.engine.data/'preferences.json',{}) or {}).get('language','ja'))
        self.settings=read_json(Path(data)/'settings.json',{})
        from display import scaled_window_size
        width,height=scaled_window_size(root,1320,860);minimum=scaled_window_size(root,760,480)
        root.title('Model Library Organizer');root.geometry(f'{width}x{height}');root.minsize(*minimum)
        from display import configure_fonts
        configure_fonts(root)
        style=ttk.Style();style.theme_use('clam');style.configure('.',font=('Yu Gothic UI',11));style.configure('TNotebook.Tab',padding=(10,7));style.configure('Treeview',rowheight=scaled_window_size(root,29,29)[0],font=('Yu Gothic UI',10));style.configure('TButton',padding=(10,6));style.configure('TLabel',font=('Yu Gothic UI',10))
        outer=ttk.Frame(root,padding=8);outer.pack(fill='both',expand=True)
        shell=outer
        self.tabs=ttk.Notebook(shell);self.tabs.pack(fill='both',expand=True)
        self.pages={};self.page_notebooks={};self.page_hosts={}
        from scroll_pages import ScrollablePage,scroll_wheel
        root.bind_all('<MouseWheel>',scroll_wheel)
        groups=[('results','調査結果',[('results','調査結果')]),('models','モデル一覧',[('models','モデル一覧')]),('inspect','モデル確認',[('preview','プレビュー'),('compatibility','互換性')]),('training','学習データ',[('captions','Image to Text'),('texts','テキスト編集')]),('tools','ツール',[('tools','ツール')]),('help','About',[('help','About')]),('restore','履歴・復元',[('restore','履歴・復元')])]
        for group,title,children in groups:
            parent=ttk.Frame(self.tabs,padding=4);self.tabs.add(parent,text=tr(title))
            if len(children)==1:
                host=ScrollablePage(parent);host.pack(fill='both',expand=True);key=children[0][0];self.pages[key]=host.body;self.page_hosts[key]=parent
            else:
                notebook=ttk.Notebook(parent);notebook.pack(fill='both',expand=True)
                for key,label in children:
                    host=ScrollablePage(notebook);notebook.add(host,text=tr(label));self.pages[key]=host.body;self.page_hosts[key]=host
                    self.page_notebooks[key]=(parent,notebook)
        outer=self.pages['models']
        fields=ttk.Frame(outer);fields.pack(fill='x');fields.columnconfigure(1,weight=1)
        self.scan_dir=tk.StringVar(value=self.settings.get('scan_root',''))
        self.target_dir=tk.StringVar(value=self.settings.get('target_root',''))
        for n,(label,var) in enumerate([('調査するフォルダー',self.scan_dir),('整理先の models フォルダー',self.target_dir)]):
            ttk.Label(fields,text=label).grid(row=n,column=0,sticky='w',pady=4)
            ttk.Entry(fields,textvariable=var,tooltip=__import__('tips').TIPS[label]).grid(row=n,column=1,sticky='ew',padx=10)
            ttk.Button(fields,text='選択…',command=lambda v=var:self.choose_root(v)).grid(row=n,column=2)
        bar=ttk.Frame(outer);bar.pack(fill='x',pady=10)
        self.online=tk.BooleanVar(value=True)
        connection=ttk.LabelFrame(self.pages['tools'],text='配布元のオンライン照合',padding=8);connection.pack(fill='x',pady=8)
        ttk.Checkbutton(connection,text='公開APIで照合（通常はオン）',variable=self.online).pack(anchor='w')
        ttk.Label(connection,text='オフ：ファイル構造・内部メタデータ・取得済み情報から判定します。未取得の作者・配布元・説明などは分からない場合があります。GPUでAIを動かす機能ではありません。',wraplength=1050).pack(anchor='w')
        self.host=ChoiceVar(value='まとめて調査（Civitai + HF）')
        ttk.Combobox(bar,textvariable=self.host,values=['まとめて調査（Civitai + HF）','https://civitai.red','https://civitai.com','Hugging Face'],state='readonly',width=23).pack(side='left',padx=8)
        ttk.Button(bar,text='全件調査',command=self.scan).pack(side='right');ttk.Button(bar,text='調査を停止',command=self.stop.set).pack(side='right',padx=6)
        self.add_features(self.pages['tools'])
        self.add_sources_ui(self.pages['tools'])
        ttk.Label(outer,text='移動やリンク追加の提案がある場合だけ、変更内容を確認する画面が開きます。').pack(anchor='w',pady=4)
        actions=ttk.Frame(outer);actions.pack(fill='x',pady=(0,8))
        for label,fn in [('保存先・リンクを変更…',self.edit),('プレビュー',self.preview),('新規・変更分を調査',lambda:self.scan(True)),('調査履歴リセット',self.reset_scan)]:
            ttk.Button(actions,text=label,command=fn).pack(side='left',padx=(0,5))
        self.filter=ChoiceVar(value='すべて');combo=ttk.Combobox(actions,textvariable=self.filter,values=['すべて','移動案のみ','要確認・エラー','判別できなかったモデル','承認','拒否'],state='readonly',width=16);combo.pack(side='right');combo.bind('<<ComboboxSelected>>',lambda _:self.render())
        body=ttk.Frame(outer);body.pack(fill='both',expand=True);body.rowconfigure(0,weight=1);body.columnconfigure(0,weight=1)
        columns=('decision','name','kind','family','confidence','source','destination')
        self.table=ttk.Treeview(body,columns=columns,show='headings',selectmode='extended')
        for c,t,w in zip(columns,['判断','モデル／ファイル','種類','系統','根拠の確かさ','現在の場所','移動先'],[75,225,80,90,120,235,235]):
            self.table.heading(c,text=t);self.table.column(c,width=w,minwidth=70,stretch=True)
        self.table.grid(row=0,column=0,sticky='nsew')
        from tips import TIPS
        column_help=[TIPS[x] for x in ['判断','モデル／ファイル','種類','系統','根拠の確かさ','現在の場所','移動先']]
        tip=Tooltip(self.table,column_help[0]);tip.column=None
        def column_hint(event):
            col=self.table.identify_column(event.x)
            cell=(col,self.table.identify_row(event.y))
            if cell!=tip.column:
                tip.column=cell;tip.hide()
                if col.startswith('#') and col[1:].isdigit() and 1<=int(col[1:])<=len(column_help):
                    tip.text=column_help[int(col[1:])-1]
                    if cell[1]:tip.text=str(self.table.item(cell[1],'values')[int(col[1:])-1])+'\n'+tip.text
                    tip.schedule()
        self.table.bind('<Motion>',column_hint,add='+')
        y=ttk.Scrollbar(body,command=self.table.yview);y.grid(row=0,column=1,sticky='ns');x=ttk.Scrollbar(body,orient='horizontal',command=self.table.xview);x.grid(row=1,column=0,sticky='ew');self.table.configure(yscrollcommand=y.set,xscrollcommand=x.set)
        self.table.tag_configure('approved',background='#ddf5e4');self.table.tag_configure('error',background='#ffe7e5');self.table.tag_configure('keep',foreground='#666666')
        self.table.bind('<<TreeviewSelect>>',self.details);self.table.bind('<Double-1>',lambda _:self.edit())
        self.table.bind('<Control-a>',lambda e:self.table.selection_set(self.table.get_children()))
        self.detail=LocalizedText(outer,height=7,wrap='word',font=('Yu Gothic UI',10),background='#f4f6f8');self.detail.pack(fill='x',pady=8)
        bottom=ttk.Frame(outer);bottom.pack(fill='x')
        self.notes_button=ttk.Button(bottom,text='配布元TXTを作成',command=self.enhanced_notes)
        ttk.Button(bottom,text='移動案を確認して整理…',command=self.review_and_apply).pack(side='right')
        self.status=StatusVar(value='まずフォルダーを選んで「調査開始」。Ctrl / Shiftで複数選択できます。');None
        footer=ttk.Frame(shell);footer.pack(side='bottom',fill='x',pady=(10,0),before=self.tabs)
        self.progress=ttk.Progressbar(footer,mode='determinate',maximum=100,length=165);self.progress.pack(side='left',padx=(0,6))
        self.progress_label=tk.StringVar(value='0%');ttk.Label(footer,textvariable=self.progress_label,width=5).pack(side='left',padx=(0,10))
        ttk.Label(footer,textvariable=self.status,wraplength=1050).pack(side='left',fill='x',expand=True)
        self.init_panels()
        self.init_captions()
        self.install_interactions()
        self.setup_support(shell)
        self.init_restore()
        self.init_results()
        self.help_center();self.select_page(self.pages['models'])
        self.tabs.bind('<<NotebookTabChanged>>',self.reset_model_filter)
        root.after(100,self.poll);root.protocol('WM_DELETE_WINDOW',self.close)

    def reset_model_filter(self,event=None):
        if self.current_page()==str(self.pages['models']):self.filter.set('すべて');self.render()
        elif self.current_page()==str(self.pages['restore']):self.refresh_restore()

    def ready(self):
        if getattr(self,'review_active',False):return False
        if self.busy:messagebox.showinfo('処理中','処理が終わるまでお待ちください。');return False
        return True
    def choose_root(self,var):
        if not self.ready():return
        p=filedialog.askdirectory(initialdir=var.get() or str(Path.home()))
        if p:var.set(p)
    def selected(self):return [self.rows[int(i)] for i in self.table.selection()]
    def current_page(self):
        selected=self.tabs.select()
        for key,(parent,notebook) in self.page_notebooks.items():
            if selected==str(parent):selected=notebook.select();break
        return next((str(self.pages[k]) for k,h in self.page_hosts.items() if str(h)==selected),selected)
    def select_page(self,page):
        key=next((k for k,v in self.pages.items() if str(v)==str(page)),None)
        if key in self.page_notebooks:
            parent,notebook=self.page_notebooks[key];self.tabs.select(parent);notebook.select(self.page_hosts[key])
        else:self.tabs.select(self.page_hosts.get(key,page))
    def set_progress(self,completed,total):
        value=max(0,min(100,100*completed/total)) if total else 0
        self.progress.configure(value=value);self.progress_label.set(f'{value:.0f}%')
    def report_progress(self,completed,total):self.events.put(('progress',(completed,total)))
    def work(self,fn,event):
        self.busy=True;self.set_progress(0,1);self.status.set("処理中…");self.root.update_idletasks()
        if hasattr(self,'editor'):self.editor.configure(state='disabled')
        def worker():
            try:
                result=fn();self.events.put(('progress',(1,1)));self.events.put((event,result))
            except Cancelled:self.events.put(('error','調査を停止しました。モデルは移動していません。'))
            except Exception as e:
                record_error(self.engine.data,e,event)
                self.events.put(('error',str(e)))
            finally:self.events.put(('idle',None))
        threading.Thread(target=worker,daemon=True).start()
    def scan(self,only_new=False):
        if not self.ready():return
        if not Path(self.scan_dir.get()).is_dir() or not Path(self.target_dir.get()).is_dir() or not self.scan_dir.get() or not self.target_dir.get():
            messagebox.showerror('フォルダー未指定','存在する調査元とmodelsフォルダーを選択してください。');return
        if any(r['decision']=='承認' for r in self.rows) and not messagebox.askyesno('再調査','未実行の承認を取り消して再調査しますか？'):return
        if not messagebox.askyesno('調査前の配置記録','調査前の全ファイル・フォルダーの場所をJSONに記録します。調査だけでは移動しません。\n\n整理を実行するとファイル・モデルの場所やフォルダーが変わります。実行前に変更履歴も保存し、履歴・復元から元の配置へ戻せます。\n\nこの記録は内容のバックアップではありません。変更・削除されたファイルは復元できない場合があります。\n\n調査を開始しますか？'):return
        self.scan_source=str(Path(self.scan_dir.get()).resolve());self.scan_target=str(Path(self.target_dir.get()).resolve())
        atomic_json(self.engine.data/'settings.json',{'scan_root':self.scan_source,'target_root':self.scan_target,'host':self.host.get()})
        self.stop.clear();online=self.online.get() and not network.OFFLINE;host=self.host.get();self.rows=[];self.filter.set('すべて');self.render()
        self.work(lambda:self.engine.scan(self.scan_source,self.scan_target,online,host,self.stop,lambda s:self.events.put(('status',s)),only_new=only_new,progress=self.report_progress),'scanned')
    def poll(self):
        try:
            while True:
                kind,value=self.events.get_nowait()
                if kind=='idle':
                    self.busy=False;self.status.set('処理完了' if self.status.get()=='処理中…' else self.status.get())
                    if hasattr(self,'editor'):self.editor.configure(state='normal')
                elif kind in ['report','preview','workflow','notes_done','duplicates']:self.feature_event(kind,value)
                elif kind=='dataset_rows':self.receive_dataset(value)
                elif kind=='dataset_auto':self.receive_auto_dataset(value)
                elif kind=='caption_prepared':pass
                elif kind=='caption_plan':self.show_caption_plan(value)
                elif kind=='caption_saved':self.captions_saved(value)
                elif kind=='caption_connections':self.caption_connections(value)
                elif kind=='compat_scanned':self.populate_compatibility();self.status.set(value);self.notify_result('互換性の調査完了',value)
                elif kind=='gallery_rows':self.set_gallery_rows(value)
                elif kind=='gallery_image':self.gallery_image(value)
                elif kind=='release':self.release_result(value)
                elif kind=='progress':self.set_progress(*value)
                elif kind=='status':self.status.set(value)
                elif kind=='error':self.status.set('処理を停止: '+value);self.show_text('確認が必要です',value)
                elif kind=='scanned':self.rows=value;self.render();self.set_gallery_rows(value,select=False);self.status.set(f'調査完了: {len(value)}項目。モデルの移動はまだ行っていません。');self.identification_report();self.root.after(150,self.review_moves)
                elif kind=='applied':self.refresh_restore();self.render();self.show_text('完了','承認した項目を整理しました。\n履歴: '+str(value));self.status.set('整理完了。ComfyUIのモデル一覧を更新し、必要ならモデルを選び直してください。')
                elif kind=='undone':self.rows=[];self.render();self.refresh_restore();self.notify_result('復元完了',f'{value}件の移動を元に戻しました。再調査してください。')
                elif kind=='hf':self.render();self.details();self.notify_result('SHA256一致',value+'\n保存先は自動変更していません。確認して選択してください。')
        except queue.Empty:pass
        self.root.after(100,self.poll)
    def render(self):
        if self.rows:self.notes_button.pack(side='left',padx=(0,5))
        else:self.notes_button.pack_forget()
        selected=self.table.selection();self.table.delete(*self.table.get_children())
        for i,r in enumerate(self.rows):
            f=self.filter.get()
            if f=='移動案のみ' and (not r['destination'] or r['decision']=='変更なし'):continue
            from features import identification_status
            if f=='要確認・エラー' and identification_status(r) in ['配布元照合済み','確認済み分類ルール']:continue
            if f=='判別できなかったモデル' and identification_status(r)!='判別できなかったモデル':continue
            if f in ['承認','拒否'] and r['decision']!=f:continue
            tag='error' if r['blocked'] else 'approved' if r['decision']=='承認' else 'keep' if r['decision']=='変更なし' else ''
            self.table.insert('', 'end',iid=str(i),values=(r['decision'],Path(r['source']).name+(' [フォルダー]' if r['bundle'] else ''),r['kind'],r['family'],r['confidence'],self.short_path(r['source'],self.scan_dir.get()),self.short_path(r['destination'],self.target_dir.get()) or '保存先を選択してください'),tags=(tag,))
        for i in selected:
            if self.table.exists(i):self.table.selection_add(i)
    def details(self,*_):
        rows=self.selected();self.detail.configure(state='normal');self.detail.delete('1.0','end')
        if rows:
            r=rows[0];self.detail.insert('end',f"{r['title']}\n根拠: {r['evidence']}\n配布元: {r['url'] or '未特定'}\n現在地: {r['source']}\n移動先: {r['destination'] or '未選択'}\n追加リンク: {', '.join(r['links']) or 'なし'}")
        self.linked_text(self.detail,self.detail.get('1.0','end-1c'))
    def decide(self,value):
        if not self.ready():return
        failures=[]
        for r in self.selected():
            if value=='承認' and (r['blocked'] or not r['destination'] or r['decision'] in ['変更なし','実行済み']):failures.append(Path(r['source']).name);continue
            if r['decision']!='実行済み':r['decision']=value
        self.render()
        if failures:messagebox.showinfo('承認しなかった項目', '\n'.join(failures[:8])+'\n変更なしの項目は移動不要です。未指定の保存先は「保存先を変更」で設定してください。')
    def edit(self):
        if not self.ready():return
        rows=self.selected()
        if len(rows)!=1:messagebox.showinfo('選択','編集する項目を1つ選択してください。');return
        r=rows[0]
        if r['blocked'] or r['decision']=='実行済み':messagebox.showinfo('編集不可','エラー項目／実行済み項目は再調査してください。');return
        win=LocalizedToplevel(self.root);win.title('移動先を選択');win.geometry('830x470');win.transient(self.root);win.grab_set()
        panel=ttk.Frame(win,padding=18);panel.pack(fill='both',expand=True)
        ttk.Label(panel,text=Path(r['source']).name,wraplength=780).pack(anchor='w')
        dest=tk.StringVar(value=str(Path(r['destination']).parent) if r['destination'] else self.scan_target)
        ttk.Label(panel,text='保存先フォルダー（models内。未作成のフォルダー名も入力可能）').pack(anchor='w',pady=(15,2))
        ttk.Entry(panel,textvariable=dest).pack(fill='x')
        def browse():
            p=filedialog.askdirectory(parent=win,initialdir=self.scan_target)
            if p:dest.set(p)
        ttk.Button(panel,text='フォルダーを選択…',command=browse).pack(anchor='w',pady=4)
        kind=tk.StringVar(value=r['kind']);combo=ttk.Combobox(panel,textvariable=kind,values=CATEGORIES,state='readonly');combo.pack(anchor='w')
        combo.bind('<<ComboboxSelected>>',lambda _:dest.set(str(Path(self.scan_target)/kind.get())))
        ttk.Label(panel,text='追加ハードリンク先フォルダー（任意。modelsからの相対パスを ; 区切り）').pack(anchor='w',pady=(12,2))
        links=tk.StringVar(value='; '.join(str(Path(x).parent.relative_to(Path(self.scan_target))) for x in r['links']))
        ttk.Entry(panel,textvariable=links).pack(fill='x')
        ttk.Label(panel,text='配布元URL（任意・手動入力。ハッシュ一致の証明にはなりません）').pack(anchor='w',pady=(12,2))
        url=tk.StringVar(value=r['url']);ttk.Entry(panel,textvariable=url).pack(fill='x')
        def save():
            try:
                root=Path(self.scan_target);d=Path(dest.get()).resolve()/Path(r['source']).name
                if not d.is_relative_to(root) or d==root:raise ValueError('保存先はmodels内を指定してください')
                hs=[]
                for val in links.get().split(';'):
                    if val.strip():
                        h=(root/val.strip()/Path(r['source']).name).resolve()
                        if not h.is_relative_to(root):raise ValueError('リンク先はmodels内を指定してください')
                        hs.append(str(h))
                if r['bundle'] and hs:raise ValueError('フォルダーのハードリンクは作成できません')
                if d.exists() and d!=Path(r['source']):raise ValueError('保存先は既に存在します')
                if url.get() and not url.get().startswith(('https://','http://')):raise ValueError('配布元URLはhttps:// または http://で入力してください')
                if url.get()!=r['url']:r['evidence']+=' / 配布元URLはユーザー指定（未照合）';r['confidence']='ユーザー指定'
                r['url']=url.get()
                r.update(destination=str(d),links=hs,kind=d.relative_to(root).parts[0],decision='保留' if d!=Path(r['source']) or hs else '変更なし')
                self.render();self.details();win.destroy();self.root.after(100,lambda:self.review_moves(rows=[r]))
            except Exception as e:messagebox.showerror('保存先の確認',str(e),parent=win)
        ttk.Button(panel,text='この保存先に設定（まだ移動しません）',command=save).pack(anchor='e',pady=15)
    def apply(self):
        if not self.ready():return
        if not hasattr(self,'scan_target') or str(Path(self.target_dir.get()).resolve())!=self.scan_target:messagebox.showerror('再調査が必要です','整理先を変更した場合は、もう一度調査してください。');return
        approved=[r for r in self.rows if r['decision']=='承認']
        if not approved:messagebox.showinfo('移動対象なし','確認画面で「はい」を選んだ移動案はありません。');return
        if not self.confirm_move_warning():return
        preview='\n\n'.join(f"{r['source']}\n → {r['destination']}" for r in approved[:5])
        if not messagebox.askyesno('移動の最終確認',f'{len(approved)}項目を移動します。必要なフォルダーと配布元TXTも作成します。\n\n{preview}\n\n履歴から元に戻せます。実行しますか？'):return
        host=self.host.get();online=self.online.get() and not network.OFFLINE
        def run():
            self.enrich_rows(approved,host,online)
            return self.engine.execute(self.rows,self.scan_target,progress=self.report_progress)
        self.work(run,'applied')
    def hf(self):
        if network.OFFLINE:messagebox.showinfo("オフライン・プライバシー","ネットワーク通信はオフライン設定で無効です。");return
        if not self.ready():return
        rows=self.selected()
        if len(rows)!=1 or not rows[0]['sha']:messagebox.showinfo('選択','照合する単一ファイルを1つ選択してください。');return
        url=simpledialog.askstring('Hugging Face照合','配布元のモデルリポジトリURL（mainのファイルとSHA256照合）:',parent=self.root)
        if url:self.work(lambda:self.engine.hf_match(rows[0],url),'hf')
    def export(self):
        if not self.ready() or not self.rows:return
        p=filedialog.asksaveasfilename(defaultextension='.csv',filetypes=[('CSV','*.csv')],initialfile='model-library.csv')
        if p:
            with open(p,'w',encoding='utf-8-sig',newline='') as f:
                cols=['decision','title','source','destination','kind','family','confidence','url','evidence','sha','links'];w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');w.writeheader();w.writerows(self.rows)
            self.status.set('一覧保存: '+p);self.notify_result('一覧保存完了',p)
    def undo(self):
        if not self.ready():return
        self.refresh_restore();self.select_page(self.pages['restore'])
    def help(self):
        self.help_center()
    def close(self):
        if self.busy:messagebox.showinfo('処理中','処理の完了を待ってください。調査は「調査を停止」で中止できます。');return
        if hasattr(self,'editor_guard') and not self.editor_guard():return
        self.save_training_settings()
        for timer in self.root.tk.splitlist(self.root.tk.call('after','info')):self.root.after_cancel(timer)
        self.root.destroy()

def main():
    from display import enable_dpi
    enable_dpi()
    root=tk.Tk();app=App(root)
    app.table.bind('<Control-a>',lambda e:app.table.selection_set(app.table.get_children()))
    if '--smoke-test' in sys.argv:
        root.update();root.after(300,root.destroy)
    root.mainloop()

if __name__=='__main__':main()
