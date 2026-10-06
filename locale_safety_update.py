"""Shared presentation strings for scan inventories and readable duplicate reports."""
ROWS = r"""
同じ内容のファイル：|Identical-content groups: |Grupos com conteúdo idêntico: 
組| groups| grupos
重複コピー：|Independent duplicate copies: |Cópias duplicadas independentes: 
ハードリンクのみ：|Hardlinks only: |Somente links físicos: 
重複コピーの容量：|Redundant copy space: |Espaço de cópias redundantes: 
ファイルは削除・移動していません。|No files were deleted or moved.|Nenhum arquivo foi excluído ou movido.
ハードリンクは同じ実体を別のパスから参照します。容量の重複ではありません。|Hardlinks reference the same physical file from different paths; they do not duplicate storage.|Links físicos referenciam o mesmo arquivo em caminhos diferentes, sem duplicar espaço.
ハードリンクのみ（追加容量なし）|Hardlinks only (no extra storage)|Somente links físicos (sem espaço extra)
独立した重複コピーあり|Independent duplicate copies|Cópias duplicadas independentes
表示パス数：|Visible paths: |Caminhos visíveis: 
表示パス数|Paths|Caminhos
実体数：|Physical files: |Arquivos físicos: 
実体数|Physical files|Arquivos físicos
余分に使用する容量：|Redundant storage: |Espaço redundante: 
実体|Physical file |Arquivo físico 
重複コピーの容量|Redundant space|Espaço redundante
詳細は調査結果の表で確認できます。|See the table in Results for details.|Veja os detalhes na tabela em Resultados.
調査前の配置記録|Pre-scan location inventory|Registro dos locais antes da verificação
調査前の配置記録（変更なし）|Pre-scan inventory (no changes)|Registro anterior (sem alterações)
変更履歴から復元可能|Restore available from move history|Restauração disponível pelo histórico
調査だけでは移動していません。整理を実行すると復元用の変更履歴が関連付けられます。|Scanning does not move files. Applied moves are linked to this inventory for restoration.|Verificar não move arquivos. Movimentações aplicadas são vinculadas a este registro para restauração.
関連する変更履歴：|Linked move journals: |Registros de movimentação vinculados: 
ファイル数：|Files: |Arquivos: 
フォルダー数：|Folders: |Pastas: 
記録件数|Recorded items|Itens registrados
この配置へ戻す…|Restore these locations…|Restaurar estes locais…
調査前の配置記録|Pre-scan location inventory|Registro dos locais antes da verificação
調査前の配置をJSONに記録しています…|Saving pre-scan locations to JSON…|Salvando os locais anteriores em JSON…
関連する移動履歴がありません。調査だけでは場所を変更していません。|No linked moves exist. Scanning did not change locations.|Não há movimentações vinculadas. A verificação não mudou os locais.
"""
SCAN_WARNING_JA='調査前の全ファイル・フォルダーの場所をJSONに記録します。調査だけでは移動しません。\n\n整理を実行するとファイル・モデルの場所やフォルダーが変わります。実行前に変更履歴も保存し、履歴・復元から元の配置へ戻せます。\n\nこの記録は内容のバックアップではありません。変更・削除されたファイルは復元できない場合があります。\n\n調査を開始しますか？'
SCAN_WARNING_EN='Original file and folder locations will be recorded in JSON before scanning. Scanning does not move files.\n\nApplying organization changes file/model locations and folders. A move journal is saved before changes, allowing restoration from History / Restore.\n\nThis is not a content backup. Edited or deleted files may not be recoverable.\n\nStart scanning?'
SCAN_WARNING_PT='Os locais originais de arquivos e pastas serão registrados em JSON antes da verificação. Verificar não move arquivos.\n\nAplicar a organização altera locais e pastas. Um registro é salvo antes de mudar arquivos, permitindo restauração em Histórico / Restaurar.\n\nNão é backup do conteúdo. Arquivos editados ou excluídos podem não ser recuperáveis.\n\nIniciar verificação?'

def install(catalog):
 for line in ROWS.splitlines():
  if not line:continue
  ja,en,pt=line.split('|')
  catalog['en'][ja]=en
  catalog['pt-BR'][ja]=pt;catalog['pt-BR'][en]=pt
 catalog['en'][SCAN_WARNING_JA]=SCAN_WARNING_EN
 catalog['pt-BR'][SCAN_WARNING_JA]=SCAN_WARNING_PT
