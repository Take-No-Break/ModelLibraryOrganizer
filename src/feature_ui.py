import io,json,tkinter as tk,urllib.request
import network
from pathlib import Path
from i18n import tr,ttk,messagebox,filedialog,LocalizedText,LocalizedToplevel
from PIL import Image,ImageTk
from features import enrich,duplicates,compatibility,workflow_plan,repair_workflows

class FeatureUI:
    def add_features(self,parent):
        bar=ttk.Frame(parent);bar.pack(fill='x',pady=4)
        for label,fn in [('重複を検出',self.find_duplicates),('ワークフロー参照を確認',self.workflows)]:ttk.Button(bar,text=label,command=fn).pack(side='left',padx=2)
    def reset_scan(self):
        if self.ready() and messagebox.askyesno('調査履歴リセット','調査済み判定とハッシュキャッシュを消します。モデル・移動履歴・手動分類は残ります。次回は全件を再計算します。'):
            self.engine.cache['seen']={};self.engine.cache['hashes']={};self.engine.cache['details']={};self.engine.cache['models']={};self.engine.cache['lookups']={};self.engine.save();self.status.set('調査済み判定をリセットしました。')
    def show_text(self,title,text):
        self.notify_result(title,text)
    def feature_event(self,kind,value):
        if kind=='duplicates':
            from duplicate_report import format_report
            self.record_result('SHA256による重複検出',json.dumps(value,ensure_ascii=False))
            messagebox.showinfo('SHA256による重複検出',format_report(value).split('\n\n')[0]+'\n\n'+tr('詳細は調査結果の表で確認できます。'))
        elif kind=='report':self.show_text(value[0],value[1])
        elif kind=='preview':
            self.show_preview(value)
        elif kind=='workflow':self.workflow_dialog(value)
        elif kind=='notes_done':self.show_text('完了',f'{value}個の配布元TXTを作成しました。既存TXTは保護されています。')
    def compat(self):
        self.populate_compatibility()
        self.select_page(self.pages['compatibility'])
    def preview(self):
        rows=self.selected()
        self.set_gallery_rows(self.rows)
        if rows:self.choose_gallery_row(rows[0])
    def find_duplicates(self):
        if not self.ready():return
        folder=self.scan_dir.get()
        if not folder or not Path(folder).is_dir():return
        self.stop.clear()
        def run():
            found=duplicates(folder,self.stop,lambda s:self.events.put(('status',s)),progress=self.report_progress)
            return found
        self.work(run,'duplicates')
    def workflows(self):
        if not self.ready():return
        folder=filedialog.askdirectory(title='ComfyUIのworkflowsフォルダーを選択')
        if folder:
            root=self.target_dir.get();rows=list(self.rows)
            self.work(lambda:workflow_plan(folder,root,rows),'workflow')
    def workflow_dialog(self,plans):
        if not plans:messagebox.showinfo('確認結果','承認済み／実行済みの移動による、対応ローダーの参照変更は見つかりませんでした。未対応のカスタムノードや埋め込みプロンプトは自動修正しません。');return
        win=self.open_panel('results','修正するワークフローを選択')
        text=LocalizedText(win,height=18,wrap='word');text.pack(fill='both',expand=True);text.insert('1.0',json.dumps([{'path':p['path'],'changes':p['changes']} for p in plans],ensure_ascii=False,indent=2));text.configure(state='disabled')
        box=tk.Listbox(win,selectmode='extended',height=8);box.pack(fill='x')
        for p in plans:box.insert('end',p['path'])
        def apply():
            if not self.ready():return
            chosen=[plans[i] for i in box.curselection()]
            if not chosen:return
            if not messagebox.askyesno('参照修正',f'{len(chosen)}ファイルをバックアップして修正します。先にモデルの移動を完了してください。',parent=win):return
            self.work(lambda:('ワークフロー修正完了','元JSONのバックアップ:\n'+repair_workflows(chosen,self.engine.data/'workflow-backups')),'report')
        ttk.Button(win,text='選択したJSONだけ修正',command=apply).pack(pady=6)
    def enrich_rows(self,rows,host,online):
        for i,r in enumerate(rows):
            self.events.put(('status',f'配布元情報を取得 {i+1}/{len(rows)}'))
            enrich(self.engine,r,host,online)
    def enhanced_notes(self):
        if not self.ready():return
        rows=[r for r in (self.selected() or self.rows) if not r['blocked'] and r['decision']!='拒否']
        if not rows:return
        if not messagebox.askyesno('配布元TXT','トリガーワード・公開説明・メタデータを含むTXTを作成します。既存TXTは上書きしません。'):return
        host=self.host.get();online=self.online.get() and not network.OFFLINE
        def run():
            from core import snapshot
            self.enrich_rows(rows,host,online);count=0
            for r in rows:
                locations=[Path(r['destination']),*[Path(x) for x in r['links']]] if r['decision']=='実行済み' else [Path(r['source'])]
                for p in locations:
                    if p.exists():
                        count+=self.engine.write_note(r,p)
                        if str(p)==r['source']:r['source_note_snapshot']=snapshot(p.with_name(p.name+'.source.txt'))
            return count
        self.work(run,'notes_done')

    def add_sources_ui(self,parent):
        bar=ttk.Frame(parent);bar.pack(fill='x',pady=3)
        ttk.Button(bar,text='識別結果',command=self.identification_report).pack(side='left',padx=5)
        ttk.Button(bar,text='通信診断・サポートログ…',command=self.network_report).pack(side='left',padx=5)

    def external_sources(self):
        if not self.ready():return
        import webbrowser
        from urllib.parse import quote
        rows=self.selected()
        default=Path(rows[0]['source']).stem if rows else ''
        win=self.open_panel('results','配布元を検索（ブラウザー）')
        query=tk.StringVar(value=default)
        ttk.Label(win,text='検索するモデル名。ページで確認したURLは「保存先・リンクを変更」で登録できます。').pack(pady=12)
        ttk.Entry(win,textvariable=query,width=85).pack(padx=12)
        def open_site(site):
            q=quote(query.get().strip(),safe='')
            urls={'SeaArt':'https://www.seaart.ai/search/model/'+q,'Hugging Face':'https://huggingface.co/models?search='+q,'Tensor.Art':'https://tensor.art/'}
            self.open_external(urls[site])
        for site in ['SeaArt','Hugging Face','Tensor.Art']:ttk.Button(win,text=site+('（サイト内で検索）' if site=='Tensor.Art' else 'で検索'),command=lambda v=site:open_site(v)).pack(pady=5)
        ttk.Label(win,text='これらのボタンは検索ページを開きます。名前一致だけで自動分類しません。').pack()

    def identification_report(self):
        from features import identification_status
        from collections import Counter
        counts=Counter(identification_status(r) for r in self.rows)
        summary=' / '.join(f'{k}: {v}件' for k,v in counts.items()) or '今回の調査対象は0件です。'
        body=summary+'\n\n'+ '\n\n'.join(r['source']+'\n'+identification_status(r)+' / '+r.get('kind','')+' / '+r.get('family','')+'\n'+r.get('evidence','')+'\n'+r.get('url','') for r in self.rows)
        if inventory:=getattr(self.engine,'scan_snapshot',None):body=tr('調査前の配置記録')+'\n'+str(inventory)+'\n\n'+body
        self.record_result('調査完了：モデルの識別結果',body)
        messagebox.showinfo('調査完了',summary+'\n\n詳細と過去のログは「調査結果」で確認できます。モデルはまだ移動していません。',parent=self.root)
