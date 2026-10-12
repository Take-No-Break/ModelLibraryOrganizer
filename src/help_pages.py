"""Short About, task-based in-app help, and readable support summaries."""
import json
import tkinter as tk
import i18n,network
from i18n import ttk,LocalizedText,tr,filedialog,messagebox
from responsive_controls import ControlFlow
from core import atomic_json
from support import VERSION

ABOUT={
 'ja':'手持ちのAIモデルを確認・整理し、学習用テキストを準備するWindowsアプリです。\n\n公開APIの情報、ファイル構造、メタデータを使ってモデルを識別します。ファイル移動は確認・承認後に実行します。\n\nモデルの学習や画像生成そのものは行いません。モデル本体とComfyUIは別途必要です。詳しい操作は隣の「How to use」をご覧ください。',
 'en':'Inspect and organize local AI models, and prepare training captions on Windows.\n\nIdentification uses public APIs, file structure and metadata. File moves require review and approval.\n\nThe app does not train models or generate images. Model weights and ComfyUI are separate. See How to use for step-by-step instructions.',
 'zh-CN':'在 Windows 上查看和整理本地 AI 模型，并准备训练文本。\n\n通过公开 API、文件结构和元数据识别模型。文件移动需要审核和批准。\n\n应用不直接训练模型或生成图片。模型权重和 ComfyUI 需另行安装。具体步骤请看 How to use。',
 'zh-TW':'在 Windows 上查看與整理本機 AI 模型，並準備訓練文字。\n\n透過公開 API、檔案結構與中繼資料辨識模型。移動檔案前須確認與核准。\n\n應用程式不直接訓練模型或產生圖片。模型權重與 ComfyUI 須另外安裝。操作步驟請看 How to use。',
 'pt-BR':'Confira e organize modelos de IA locais e prepare legendas de treinamento no Windows.\n\nA identificação usa APIs públicas, estrutura dos arquivos e metadados. As movimentações exigem revisão e aprovação.\n\nO aplicativo não treina modelos nem gera imagens. Os pesos e o ComfyUI são separados. Consulte How to use para instruções.',
 'es':'Revisa y organiza modelos locales de IA y prepara textos de entrenamiento en Windows.\n\nLa identificación usa API públicas, estructura y metadatos. Los movimientos requieren revisión y aprobación.\n\nNo entrena modelos ni genera imágenes. Los pesos y ComfyUI se instalan aparte. Consulta How to use.',
 'de':'Lokale KI-Modelle unter Windows prüfen, ordnen und Trainingstexte vorbereiten.\n\nDie Erkennung nutzt öffentliche APIs, Dateistruktur und Metadaten. Dateien werden erst nach Prüfung und Freigabe verschoben.\n\nDie App trainiert keine Modelle und erzeugt keine Bilder. Modellgewichte und ComfyUI sind separat. Anleitungen stehen unter How to use.',
 'th':'ตรวจสอบและจัดระเบียบโมเดล AI ในเครื่อง พร้อมเตรียมข้อความฝึกบน Windows\n\nระบุโมเดลด้วย API สาธารณะ โครงสร้างไฟล์และเมทาดาทา การย้ายไฟล์ต้องตรวจสอบและอนุมัติก่อน\n\nแอปไม่ฝึกโมเดลหรือสร้างภาพ ต้องติดตั้งโมเดลและ ComfyUI แยกต่างหาก ดูขั้นตอนใน How to use'
}
EN={
 'Models':'1. Choose a scan folder and the destination models root (for example ComfyUI/models, not models/loras).\n2. Scan all identifies files without moving them. Choose Model type → Purpose → Base model family, or Provider → Creator → Model type → Base model family. Purpose depends on source metadata.\n3. Review the proposed folders and approve, reject or defer items.\n4. Review and organize proposed moves applies approved changes and records move history.\n\nModel type means LoRA, checkpoint, VAE, etc. Base model family means Pony, Illustrious, Anima, etc. Identification confidence is a status, not a probability; Evidence explains the supporting information.',
 'Model inspection':'1. Preview: scan a folder, then filter by model type, base model family or filename. The filename heading sorts A–Z.\n2. Select a model to read trigger words, source descriptions and available general-audience images. Previous / Next image changes the preview. Drag pane dividers to resize.\n3. Check updates, copy trigger words, compare version descriptions (green additions / red removals), or browse Authors. Authors lists scanned local files, not every online upload.\n4. Compatibility compares LoRA → Checkpoint or Checkpoint → LoRA. Save your own pair assessment after testing.\n\nFamily comparisons do not guarantee loading or generation. Find models used in image needs PNG generation metadata: supported names/hashes or a ComfyUI prompt graph. It cannot infer models from pixels. Training metadata tag counts are frequencies, not prompt weights.',
 'Training data':'1. Image to Text: choose an image folder, a supported adapter, its complete model folder and settings.\n2. Install / update custom nodes in the ComfyUI instance you actually use. Install dependencies with its Python, restart ComfyUI, and check the local connection. Changing paths or template format does not require reinstalling unchanged nodes.\n3. Run in ComfyUI, or export Combined / Expanded workflow JSON and open it there. Workflow JSON is the graph; required custom nodes are the code. Outputs are image hardlinks and matching TXT inside an adapter-named image subfolder.\n4. Edit Text or Tag editor edits individual/batch captions with review, backups and conflict checks. Source TXT documents models; it is not an image caption.\n\nSupported adapters: PixAI, JoyCaption, CL Tagger, Taggerine. An arbitrary safetensors architecture needs its own compatible adapter. PixAI loads Python code from the selected model folder inside ComfyUI: use trusted bundles only. Hardlinks share image contents with the original. This app does not train models.',
 'Tools':'Find duplicates: choose a scan folder in Models, then compare full SHA-256. Reports distinguish hardlinks from independent copies. Nothing is automatically deleted.\n\nCheck workflow references: after approved model relocation, choose your workflows folder. Review supported loader filename/path changes, select JSON files and confirm repair. Original JSON is backed up. Unsupported custom nodes are not automatically fixed; this does not run a workflow.\n\nIdentification results: summarizes the current scan, identified model types/families and supporting evidence. It does not perform a new scan or move files.\n\nDiagnostics / Support: shows recent connection/error status and lets you save a local diagnostic log. Open Discord for help and attach the log yourself if needed. Nothing is uploaded automatically.\n\nPublic API lookup off stops new source identification; Fully offline in About also stops external previews and update requests. Explicit local ComfyUI actions remain available.',
 'History / Restore':'1. Scans save original-path inventories; approved file moves separately record move journals.\n2. Open History / Restore and choose a record or open its JSON.\n3. Restore this layout returns eligible files to recorded paths. Previously restored move journals can be checked again.\n4. Review confirmation. Missing journals, changed files and conflicts can prevent restoration.\n\nA scan inventory without linked move history cannot restore files. History is not a model-content backup. Only open histories you trust. Results stores previous operation reports.'
}
JA={
 'Models':'1. 調査するフォルダと整理先のmodelsルートを選びます（ComfyUI/modelsなど。models/lorasは避けます）。\n2. 全件調査は識別だけで移動しません。「モデル種類 → 用途 → ベースモデル系統」か「配布元 → 作者 → モデル種類 → ベースモデル系統」を選びます。用途は取得情報に応じます。\n3. 作成予定のフォルダや移動先を確認し、承認・拒否・保留を選びます。\n4. 「移動案を確認して整理」で承認した案を実行し、移動履歴を保存します。\n\nモデル種類はLoRA・Checkpoint・VAEなどの役割、ベースモデル系統はPony・Illustrious・Animaなどの系列です。識別の確かさは照合済み・推定などの状態で確率ではありません。根拠は判断を支える情報です。',
 'Model inspection':'1. プレビューでフォルダを調査し、モデル種類・ベースモデル系統・ファイル名で絞り込みます。ファイル名はA–Z順です。\n2. モデルを選び、トリガーワード、配布元の説明、取得できた一般向け画像を確認します。「前の画像／次の画像」で切り替え、境界線で表示領域を調整できます。\n3. 更新確認、トリガーワードのコピー、バージョンの説明比較（追加は緑・削除は赤）、作者別一覧を使えます。作者別一覧は調査済みの手持ちファイルのみです。\n4. 互換性はLoRAからCheckpoint、または逆方向に比較できます。自分でテストした結果を組み合わせごとに保存できます。\n\n系統比較は動作・生成品質の保証ではありません。「画像から使用モデルを探す」はモデル名・ハッシュや対応するComfyUI生成情報を含むPNGが必要です。見た目だけでは判別できません。学習メタデータのタグ数値は出現回数で、プロンプトの重みではありません。',
 'Training data':'1. Image to Textで画像フォルダ、対応アダプター、その完全なモデルフォルダと設定を選びます。\n2. 使用するComfyUIのcustom_nodesへ「カスタムノードを導入・更新」します。そのPythonで依存関係を導入し、ComfyUIを再起動して接続確認します。パスや一体型／分解型の変更だけでは再導入は不要です。\n3. ComfyUIへ実行を送るか、ワークフローJSONを書き出してComfyUIで開きます。JSONはノード図、カスタムノードは動作するコードです。画像フォルダ内のアダプター名フォルダへ画像ハードリンクと同名TXTを保存します。\n4. Edit TextやTag editorで個別・一括編集し、変更確認後に保存します。バックアップと競合確認があります。配布元TXTはモデルの情報メモで画像キャプションとは別です。\n\n対応はPixAI・JoyCaption・CL Tagger・Taggerineです。任意のsafetensorsが使えるわけではありません。PixAIは選択したモデル内のPythonをComfyUIで実行するため、信頼できるモデル一式を使ってください。画像ハードリンクは元画像と同じ実体です。本アプリはモデルを学習しません。',
 'Tools':'重複を検出：モデル一覧で選んだ調査フォルダのSHA-256を比較します。ハードリンクと別コピーを区別します。自動削除はしません。\n\nワークフロー参照を確認：承認したモデル移動で変わるローダーのファイル名・パスを、選択したworkflowsフォルダ内で確認します。対応するJSONだけ選び、確認後に修正します。元JSONはバックアップします。未対応のカスタムノードは自動修正しません。ワークフローを実行する機能ではありません。\n\n識別結果：今回の調査で識別したモデル種類・系統・根拠をまとめます。新しい調査やファイル移動は行いません。\n\n通信診断・サポートログ：最近の通信・エラー状況を確認し、必要なら診断ログを保存します。Discordで相談し、必要なログは自分で添付してください。自動送信はしません。\n\n公開API照合をオフにすると新しい配布元調査を止めます。Aboutの完全オフラインは外部プレビュー・更新への通信も止めます。明示的なローカルComfyUI実行は利用できます。',
 'History / Restore':'1. 調査時に元の配置一覧、移動時に別の移動履歴を保存します。\n2. 履歴・復元で記録を選ぶかJSONを開きます。\n3. 「この配置へ戻す」で復元可能なファイルを戻します。復元済みの移動履歴も現在の記録済みパスから再確認できます。\n4. 確認画面を確認します。移動履歴の欠落、変更されたファイル、パス競合は復元を止めます。\n\n関連する移動履歴がない調査JSONだけでは復元できません。履歴はモデル本体のバックアップではありません。信頼できる履歴だけを開いてください。調査結果では以前の操作レポートを確認できます。'
}

def text_panel(parent,text):
 frame=ttk.Frame(parent);frame.pack(fill='both',expand=True)
 box=LocalizedText(frame,wrap='word',height=12);box.pack(side='left',fill='both',expand=True)
 scroll=ttk.Scrollbar(frame,command=box.yview);scroll.pack(side='right',fill='y');box.configure(yscrollcommand=scroll.set)
 box.insert('1.0',text);box.configure(state='disabled');return box

def build_help(app):
 page=app.pages['help']
 for child in page.winfo_children():child.destroy()
 ttk.Label(page,text='Model Library Organizer '+VERSION,font=('Yu Gothic UI',14,'bold')).pack(anchor='w',pady=8)
 text_panel(page,ABOUT.get(i18n.LANG,ABOUT['en'])+'\n\nMIT license · Windows\nIndependent of ComfyUI, Civitai and model authors.')
 offline=tk.BooleanVar(value=network.OFFLINE)
 def toggle():
  network.OFFLINE=offline.get();app.preferences['offline']=offline.get();app.save_preferences()
  if offline.get():app.online.set(False)
 ttk.Checkbutton(page,text='完全オフライン（すべての通信を停止）',variable=offline,command=toggle).pack(anchor='w',pady=5)
 auto=tk.BooleanVar(value=app.preferences.get('auto_updates',False))
 def auto_change():app.preferences['auto_updates']=auto.get();app.save_preferences()
 ttk.Checkbutton(page,text='起動時に更新を確認（任意）',variable=auto,command=auto_change).pack(anchor='w',pady=4)
 controls=ControlFlow(page);controls.pack(fill='x',pady=8)
 for label,fn in [('How to use',lambda:app.select_page(app.pages['howto'])),('GitHub repository',app.open_repository),('Discord support',app.open_support),('更新を確認',app.check_updates),('更新・サポート設定',app.publisher_settings)]:ttk.Button(controls,text=label,command=fn).pack(side='left',padx=3)
 page=app.pages['howto']
 for child in page.winfo_children():child.destroy()
 tabs=ttk.Notebook(page);tabs.pack(fill='both',expand=True)
 from help_pages_locales import GUIDES
 guide=JA if i18n.LANG=='ja' else dict(zip(EN,GUIDES[i18n.LANG])) if i18n.LANG in GUIDES else EN
 for title,body in guide.items():
  frame=ttk.Frame(tabs,padding=8);tabs.add(frame,text=title)
  text_panel(frame,body)

def diagnostics_page(app,report):
 win=app.open_panel('results','通信診断・サポートログ')
 jp=i18n.LANG=='ja'
 ttk.Label(win,text='問題がある場合はDiscordでご相談ください。ログは自動送信しません。' if jp else 'For help, contact us on Discord. Logs are never uploaded automatically.',wraplength=580).pack(anchor='w',padx=12,pady=12)
 errors=report.get('errors',[]);requests=report.get('network',[])
 summary=('アプリのバージョン: ' if jp else 'App version: ')+report['app_version']+'\n'
 summary+=('記録済みエラー: ' if jp else 'Recorded errors: ')+str(len(errors))+'\n'
 if errors:summary+=('最新のエラー: ' if jp else 'Latest error: ')+errors[-1].get('exception','Unknown')+' / '+errors[-1].get('context','')+'\n'
 summary+=('最近の通信記録: ' if jp else 'Recent connection records: ')+str(len(requests))+'\n'
 if requests:summary+=requests[-1]['host']+' / '+requests[-1]['status']+'\n'
 summary+=('\n記録がないことは、すべての機能に問題がないという意味ではありません。必要に応じてログを保存して相談時に添付してください。' if jp else '\nAn empty log does not prove every feature works. Save the log and attach it yourself if requested.')
 box=text_panel(win,summary)
 def show_details():box.configure(state='normal');box.delete('1.0','end');box.insert('1.0',json.dumps(report,ensure_ascii=False,indent=2));box.configure(state='disabled')
 def export():
  path=filedialog.asksaveasfilename(parent=win,defaultextension='.json',initialfile='model-organizer-support.json')
  if path:atomic_json(path,report);messagebox.showinfo('保存完了','必要な場合、このJSONを配布者に送ってください。',parent=win)
 controls=ControlFlow(win,align='right');controls.pack(fill='x',padx=10,pady=10)
 ttk.Button(controls,text='診断ログを保存…（自動送信なし）',command=export).pack(side='left',padx=4)
 ttk.Button(controls,text='詳細ログ' if jp else 'Detailed log',command=show_details).pack(side='left',padx=4)
 ttk.Button(controls,text='Discord support',command=app.open_support).pack(side='right',padx=4)
