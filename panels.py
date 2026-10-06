from pathlib import Path
import uuid
from i18n import ttk,LocalizedText,messagebox,tr
from PIL import ImageTk
from note_format import plain

from gallery import Gallery

class Panels(Gallery):
    def open_panel(self,key,title):
        if key=='results':
            from i18n import LocalizedToplevel
            page=LocalizedToplevel(self.root);page.title(title);page.geometry('1000x680');page.transient(self.root)
            return page
        page=self.pages[key]
        for child in page.winfo_children():child.destroy()
        ttk.Label(page,text=title,font=('Yu Gothic UI',14,'bold')).pack(anchor='w',pady=8)
        self.select_page(page)
        return page
    def init_panels(self):
        tabs=ttk.Notebook(self.pages['texts']);tabs.pack(fill='both',expand=True)
        for key,title in [('caption_texts','画像・学習用TXT'),('source_texts','モデルの配布元TXT')]:
            frame=ttk.Frame(tabs,padding=6);tabs.add(frame,text=tr(title));self.pages[key]=frame
        page=self.pages['tools']
        import tkinter as tk
        from core import read_json,atomic_json
        from note_format import note_content
        options=read_json(self.engine.data/'note-options.json',{'sections':['triggers','description','public','lookup','metadata']})
        self.note_sections=list(options['sections'])
        self.engine.note_content=lambda row:note_content(row,self.note_sections)
        page=self.pages['source_texts']
        ttk.Label(page,text='これはモデルの配布元TXTの設定です。画像と同名の学習用キャプションとは別です。モデル一覧で対象を選んでから操作してください。',wraplength=1000).pack(anchor='w',pady=10)
        ttk.Button(page,text='配布元TXTを作成',command=self.enhanced_notes).pack(anchor='w',pady=5)
        ttk.Button(page,text='TXTを読みやすく更新',command=self.refresh_notes).pack(anchor='w',pady=5)
        group=ttk.LabelFrame(page,text='TXTに含める情報（基本情報は常に記載）',padding=8);group.pack(fill='x',pady=8)
        self.note_vars={}
        def save_options():
            self.note_sections=[k for k,v in self.note_vars.items() if v.get()]
            atomic_json(self.engine.data/'note-options.json',{'sections':self.note_sections})
        for key,label in [('triggers','Trigger words'),('description','Description'),('public','Public metadata'),('lookup','Lookup results'),('metadata','File metadata')]:
            var=tk.BooleanVar(value=key in self.note_sections);self.note_vars[key]=var
            ttk.Checkbutton(group,text=label,variable=var,command=save_options).pack(side='left',padx=5)
        self.init_gallery()
        self.init_compatibility()
        ttk.Button(self.pages['results'],text='識別結果',command=self.identification_report).pack(anchor='w')
    def show_preview(self,value):
        image,row,info=value
        self.display_gallery(row,info,image)
    def refresh_notes(self):
        if not self.ready():return
        rows=[dict(r) for r in self.selected() if not r.get('blocked')]
        if not rows:messagebox.showinfo('選択','モデルを1つ選択してください。');return
        if not messagebox.askyesno('TXTを読みやすく更新','選択したモデルの配布元TXTを更新します。既存のアプリ生成TXTはアプリのデータフォルダーへバックアップします。手書きTXTは変更しません。更新したTXTがある移動履歴の復元は、安全確認で停止する場合があります。'):return
        host=self.host.get();online=self.online.get() and not __import__('network').OFFLINE
        def run():
            from core import atomic_json
            self.enrich_rows(rows,host,online)
            backup=self.engine.data/'note-backups'/uuid.uuid4().hex;records=[];count=0
            for row in rows:
                locations=[row.get('destination'),*row.get('links',[])] if row.get('decision')=='実行済み' else [row['source']]
                for location in locations:
                    if not location or not Path(location).exists():continue
                    path=Path(location).with_name(Path(location).name+'.source.txt')
                    raw=path.read_bytes() if path.exists() else None
                    if raw is not None:
                        if not raw.decode('utf-8-sig',errors='replace').startswith(('Model Library Organizer — 配布元情報','Model Library Organizer — Source information')):continue
                        backup.mkdir(parents=True,exist_ok=True)
                        saved=backup/(str(len(records))+'.txt');saved.write_bytes(raw)
                        records.append({'original':str(path),'backup':str(saved)})
                        atomic_json(backup/'manifest.json',records)
                        if path.read_bytes()!=raw:raise ValueError('TXT changed during update: '+str(path))
                    temporary=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
                    temporary.write_text(self.engine.note_content(row),encoding='utf-8-sig');temporary.replace(path);count+=1
            return ('完了',str(count)+' TXT\nBackup: '+str(backup) if records else str(count)+' TXT')
        self.work(run,'report')

    @staticmethod
    def actionable(row):
        return not row.get('blocked') and bool(row.get('destination')) and row.get('decision') not in ('変更なし','実行済み') and (Path(row['source'])!=Path(row['destination']) or bool(row.get('links')))
    def review_and_apply(self):
        if not self.ready():return
        chosen=self.selected()
        self.review_moves(done=self.apply,rows=chosen if chosen else None)
    def review_moves(self,done=None,rows=None):
        if self.busy or getattr(self,'review_active',False):return
        proposals=[r for r in (rows if rows is not None else self.rows) if self.actionable(r) and (rows is not None or r.get('decision')=='保留')]
        if not proposals:
            if done:done()
            return
        import tkinter as tk
        from i18n import LocalizedToplevel,LocalizedText
        self.review_active=True
        win=LocalizedToplevel(self.root);win.title('移動・フォルダー作成の確認');win.geometry('850x560');win.transient(self.root);win.grab_set()
        panel=ttk.Frame(win,padding=16);panel.pack(fill='both',expand=True)
        heading=ttk.Label(panel,text='');heading.pack(anchor='w',pady=8)
        text=LocalizedText(panel,wrap='word',height=17);text.pack(fill='both',expand=True)
        ttk.Label(panel,text='はい＝実行対象にする／いいえ＝今回は移動しない／保留＝後で判断。ここではまだ移動しません。',wraplength=790).pack(anchor='w',pady=8)
        controls=ttk.Frame(panel);controls.pack(fill='x');position=[0]
        def finish(execute=False):
            self.review_active=False;win.destroy();self.render()
            if execute and done:done()
        def show():
            r=proposals[position[0]];heading.configure(text=f"{position[0]+1} / {len(proposals)} — {Path(r['source']).name}")
            folders=[]
            for target in [r['destination'],*r.get('links',[])]:
                parent=Path(target).parent
                while not parent.exists() and parent!=parent.parent:
                    if str(parent) not in folders:folders.append(str(parent))
                    parent=parent.parent
            body='【提案の理由】\n'+r.get('evidence','')+'\n\n【現在の場所】\n'+r['source']+'\n\n【移動先】\n'+r['destination']+'\n\n【追加ハードリンク】\n'+('\n'.join(r.get('links',[])) or 'なし')+'\n\n【新しく作成するフォルダー】\n'+('\n'.join(folders) or 'なし')
            self.linked_text(text,body)
            from display import highlight_folder_paths
            highlight_folder_paths(text,folders)
        def answer(value):
            proposals[position[0]]['decision']=value;position[0]+=1
            if position[0]>=len(proposals):finish(True)
            else:show()
        for label,value in [('はい（賛成）','承認'),('いいえ','拒否'),('保留','保留')]:ttk.Button(controls,text=label,command=lambda v=value:answer(v)).pack(side='left',padx=5)
        ttk.Button(controls,text='残りは後で確認',command=finish).pack(side='right')
        win.protocol('WM_DELETE_WINDOW',finish);show()
