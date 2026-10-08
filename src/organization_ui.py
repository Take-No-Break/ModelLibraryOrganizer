import tkinter as tk
from i18n import ttk,LocalizedToplevel,LocalizedText
from locales import CATALOG

LABELS={
 'フォルダーの整理方法':'Folder organization',
 'どの方法でフォルダーを整理しますか？':'How would you like to organize the folders?',
 '1. 種類・カテゴリー別（既存の方法）':'1. By type and category (existing method)',
 '2. 配布サイト・投稿者別':'2. By provider and creator',
 '続ける':'Continue','キャンセル':'Cancel',
}
CATALOG['en'].update(LABELS)
EXISTING='1. 種類 → 用途 → 系統\n\nまずloras・checkpoints・embeddingsなどの種類で整理します。配布元の情報がある場合は用途（LoRA：Character、Copyright(Style)／チェックポイント：Anime、Realistic）、次にIllustrious・Anima・Ponyなどの系統で分けます。用途が不明な階層は省略します。Poseの自動分類には現在対応していません。確認済みの配置や、正しく配置されたファイルは維持する場合があります。\n\nmodels / loras / Character / Illustrious / model.safetensors\nmodels / checkpoints / Anime / Anima / model.safetensors\nmodels / embeddings / model.safetensors'
CREATOR='2. 配布サイト → 投稿者 → 種類 → 系統\nmodels / Civitai / creator_name / loras / Illustrious / model.safetensors\nmodels / Hugging Face / account_or_organization / embeddings / SDXL / model.safetensors\n\n整理済みのモデルも移動を提案します。投稿者や種類が不明なものは元の場所に残します。HFは組織名の場合もあります。ComfyUIのモデル検索先設定が必要になる場合があります。空になった旧フォルダーだけを削除し、ファイルは削除しません。配布元TXTはモデルと一緒に移動します。'
CATALOG['en'][EXISTING]='1. Existing method\nmodels / loras / Character / Illustrious / model.safetensors\n\nKeeps previously confirmed category placements.'
CATALOG['en'][CREATOR]='2. Provider → Creator → Model type → Base model family\nmodels / Civitai / creator_name / loras / Illustrious / model.safetensors\nmodels / Hugging Face / account_or_organization / embeddings / SDXL / model.safetensors\n\nAlready organized models can be proposed for relocation. Unknown creators/types remain in their current location. HF namespaces can be organizations. ComfyUI model search paths may need adjustment for this hierarchy. Only empty former folders are removed; files are never deleted. Generated source TXT moves with its model.'

def choose_layout(app):
    import organization_text
    win=LocalizedToplevel(app.root);win.title('フォルダーの整理方法');win.transient(app.root);win.grab_set();win.geometry('720x500')
    result=[None];choice=tk.StringVar(value=app.preferences.get('organization_layout','category'))
    ttk.Label(win,text='どの方法でフォルダーを整理しますか？',padding=12).pack(anchor='w')
    ttk.Radiobutton(win,text='1. 種類・カテゴリー別（既存の方法）',variable=choice,value='category').pack(anchor='w',padx=15,pady=6)
    ttk.Radiobutton(win,text='2. 配布サイト・投稿者別',variable=choice,value='creator').pack(anchor='w',padx=15,pady=6)
    preview=LocalizedText(win,height=12,wrap='word');preview.pack(fill='both',expand=True,padx=15,pady=8)
    def show(*_):
        text=EXISTING if choice.get()=='category' else CREATOR
        preview.configure(state='normal');preview.delete('1.0','end');preview.insert('1.0',text);preview.configure(state='disabled')
    choice.trace_add('write',show);show()
    bar=ttk.Frame(win);bar.pack(fill='x',padx=15,pady=10)
    def finish(accepted):
        if accepted:result[0]=choice.get()
        win.destroy()
    ttk.Button(bar,text='続ける',command=lambda:finish(True)).pack(side='right',padx=4)
    ttk.Button(bar,text='キャンセル',command=lambda:finish(False)).pack(side='right',padx=4)
    win.protocol('WM_DELETE_WINDOW',lambda:finish(False))
    from display import center_popup
    center_popup(win,app.root)
    app.root.wait_window(win)
    return result[0]
