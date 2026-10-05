WARNING='この操作はモデルや関連データの保存場所を変更し、フォルダーやハードリンクを作成します。ComfyUIや既存ワークフローの参照先が変わる場合があります。\n\n変更する前に、対象の元パス・移動先・ファイル状態を履歴へ記録します。元に戻したい場合は、右端の「履歴・復元」タブで日時を選び、「選択した履歴を元に戻す」を押してください。\n\nこれは配置の記録であり、モデル本体のコピーではありません。移動後にファイルが編集・削除された場合や元の場所に別のファイルがある場合は、復元を停止します。\n\n続けますか？'
ROWS='''保存場所を変更する前の警告|Warning before changing file locations|Advertencia antes de cambiar ubicaciones
この警告を再度表示しない（最終確認は残ります）|Do not show this warning again (final confirmation remains)|No mostrar de nuevo esta advertencia (se mantiene la confirmación final)
はい（続ける）|Yes (continue)|Sí (continuar)
いいえ（中止）|No (cancel)|No (cancelar)
履歴・復元|History / Restore|Historial / Restaurar
変更前の保存場所へ戻します。複数回変更した場合は、新しい履歴から順に戻してください。|Restore previous locations. If several changes were made, undo the newest history first.|Restaure ubicaciones anteriores. Si hubo varios cambios, deshaga primero el historial más reciente.
履歴を更新|Refresh history|Actualizar historial
選択した履歴を元に戻す|Undo selected history|Deshacer historial seleccionado
履歴JSONを開く…|Open history JSON…|Abrir JSON de historial…
移動前の警告を表示|Show warning before moves|Mostrar advertencia antes de mover
実行日時|Execution date|Fecha de ejecución
変更件数|Operations|Operaciones
状態|Status|Estado
履歴の保存場所：|History location:|Ubicación del historial:
復元済み|Restored|Restaurado
実行完了|Completed|Completado
途中終了・確認が必要|Incomplete; review required|Incompleto; requiere revisión
履歴ファイル：|History file:|Archivo de historial:
変更前 → 変更後|Before → After|Antes → Después
空でない等の理由で残したフォルダー：|Folders retained (not empty or changed):|Carpetas conservadas (no vacías o modificadas):
復元できる履歴ではありません|This history cannot be restored.|Este historial no se puede restaurar.
元に戻す履歴を選択してください。|Select a history entry to undo.|Seleccione una entrada para deshacer.
この履歴は復元済み、または読み込めません。|This history is already restored or unreadable.|Este historial ya fue restaurado o no se puede leer.
選択した履歴の配置へ戻しますか？変更後のファイルや元パスに競合がある場合は停止します。今回作成したフォルダーは空の場合だけ削除します。|Restore the locations in this history? Changes or original-path conflicts stop restoration. Folders created by this run are removed only if empty.|¿Restaurar las ubicaciones de este historial? Los cambios o conflictos detendrán la restauración. Las carpetas creadas en esta ejecución se eliminan solo si están vacías.'''

def install(catalog):
 for row in ROWS.splitlines():
  ja,en,es=row.split('|');catalog['en'][ja]=en;catalog['es'][ja]=es
 catalog['en'][WARNING]='This operation changes the locations of models and related data, and creates folders or hard links. ComfyUI and existing workflows may need updated references.\n\nBefore any change, the original paths, destinations and affected file state are recorded in history. To undo, open the rightmost History / Restore tab, select the date, and click Undo selected history.\n\nThis is a placement record, not a copy of the model contents. Restoration stops if moved files were edited or deleted, or if another file occupies the original path.\n\nContinue?'
 catalog['es'][WARNING]='Esta operación cambia la ubicación de modelos y datos relacionados, y crea carpetas o enlaces físicos. Puede ser necesario actualizar las referencias de ComfyUI y de los flujos existentes.\n\nAntes de cambiar nada se registran las rutas originales, destinos y estado de los archivos afectados. Para deshacer, abra la pestaña Historial / Restaurar del extremo derecho, seleccione la fecha y pulse Deshacer historial seleccionado.\n\nEs un registro de ubicaciones, no una copia del contenido del modelo. La restauración se detiene si los archivos se editaron o eliminaron, o si otro archivo ocupa la ruta original.\n\n¿Continuar?'
