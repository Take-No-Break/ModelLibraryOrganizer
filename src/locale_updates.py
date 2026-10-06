"""Full UI translations, separate from model metadata and user captions."""
ROWS='''チェックポイント|Checkpoint|Checkpoint
チェックポイントのフォルダー|Checkpoint folder|Carpeta de checkpoints
LoRAのフォルダー|LoRA folder|Carpeta de LoRA
指定フォルダーを追加調査|Scan selected folders|Analizar carpetas seleccionadas
調査済みモデルから一覧を更新|Refresh scanned models|Actualizar modelos analizados
判定|Assessment|Evaluación
LoRAを選ぶと、配布元の系統とチェックポイント候補を表示します。実際の生成結果を保証するものではありません。|Choose a LoRA. Green: same family; yellow: related SDXL families; gray: unrelated or unknown. Results are not guaranteed.|Seleccione un LoRA. Verde: misma familia; amarillo: familias SDXL relacionadas; gris: sin relación conocida. Los resultados no están garantizados.
候補はこのPCの調査履歴と今回の結果のみです。未調査のPCでは空です。全ドライブを自動探索しません。|Candidates come from this PC's scan history and current results. New PCs start empty. Drives are not searched automatically.|Los candidatos proceden del historial de este PC y los resultados actuales. En un PC nuevo la lista está vacía. No se buscan unidades automáticamente.
このPCの調査履歴＋今回の結果 / LoRA: |Scan history and current results / LoRA: |Historial y resultados actuales / LoRA: 
 — 入力したフォルダー内に候補を限定します。空欄では過去の調査全体です。| — Selected folders only; blank fields include all scan history.| — Solo carpetas seleccionadas; los campos vacíos incluyen todo el historial.
未調査または候補なし。フォルダーを指定して追加調査してください。|No candidates. Select folders and scan them.|Sin candidatos. Seleccione carpetas y analícelas.
存在するチェックポイント／LoRAフォルダーを選択してください。|Select existing checkpoint/LoRA folders.|Seleccione carpetas existentes de checkpoints/LoRA.
互換性用の追加調査完了。モデルは移動していません。|Compatibility scan complete. No models moved.|Análisis de compatibilidad completado. No se movieron modelos.
同じ系統・組み合わせ未検証|Same family; pair untested|Misma familia; combinación sin probar
SDXL派生・互換性は中（未検証）|Related SDXL family; medium (untested)|Familia SDXL relacionada; media (sin probar)
異なる系統・対応関係なし／未確認|Different family; no known compatibility|Familia diferente; sin compatibilidad conocida
系統未確認|Unknown family|Familia desconocida
行をクリックして、この組み合わせの評価を記録|Click a row to record your assessment|Haga clic en una fila para registrar su evaluación
自動判定|Automatic assessment|Evaluación automática
使用できた（緑）|Worked in my test (green)|Funcionó en mi prueba (verde)
要調整（黄）|Needs adjustment (yellow)|Requiere ajustes (amarillo)
使用不可（灰）|Did not work (gray)|No funcionó (gris)
手動評価|User assessment|Evaluación del usuario
メモ|Notes|Notas
評価を保存|Save assessment|Guardar evaluación
現在の場所をコピー|Copy current path|Copiar ruta actual
移動先をコピー|Copy destination path|Copiar ruta de destino
現在の場所のフォルダーを開く|Open current folder|Abrir carpeta actual
移動先のフォルダーを開く|Open destination folder|Abrir carpeta de destino
配布元を開く|Open source page|Abrir página de origen
この保存先はまだ作成されていません。|Destination does not exist yet.|El destino todavía no existe.
移動やリンク追加の提案がある場合だけ、変更内容を確認する画面が開きます。|Review appears only when moves or links are proposed.|La revisión aparece solo si se proponen traslados o enlaces.
移動案を確認して整理…|Review proposed moves…|Revisar traslados propuestos…
モデルを選ぶと公開画像を表示します。|Select a model to show its public preview.|Seleccione un modelo para ver su imagen pública.
読み込み中…|Loading…|Cargando…
公開APIに一般向け画像がありません。|No general-audience preview in the public API.|La API pública no ofrece una imagen para todos los públicos.
オフラインでは画像を取得できません。|Cannot download previews offline.|No se pueden descargar imágenes sin conexión.
画像を取得できません: |Could not load preview: |No se pudo cargar la imagen: 
LoRA・Embedding学習用のキャプションを作成します。画像生成・モデル学習は行いません。解析はローカルComfyUI＋PixAI、TXTの確認と保存はこのアプリで行います。|Create image captions for LoRA/embedding training with local ComfyUI + PixAI. Review and save image-name TXT here. This does not train models or generate images.|Cree descripciones para entrenar LoRA/embeddings con ComfyUI local + PixAI. Revise y guarde aquí los TXT con el nombre de cada imagen. No entrena modelos ni genera imágenes.
ComfyUI接続先（このPC）|ComfyUI URL (this PC)|URL de ComfyUI (este PC)
ComfyUI起動ファイル|ComfyUI launcher|Archivo de inicio de ComfyUI
ComfyUIフォルダー（main.pyのある場所）|ComfyUI folder (contains main.py)|Carpeta de ComfyUI (contiene main.py)
PixAI 閾値（0〜1）|PixAI thresholds (0–1)|Umbrales PixAI (0–1)
タグ順：quality / meta / rating → character → copyright → style → 人数 → general。保存先は画像と同じフォルダー・同じ名前の.txtです。|Tag order: quality / meta / rating → character → copyright → style → subject count → general. TXT is saved beside the image with the same base name.|Orden: quality / meta / rating → character → copyright → style → número de sujetos → general. El TXT se guarda junto a la imagen con el mismo nombre base.
APIワークフローを書き出す|Export API workflow|Exportar flujo API
APIワークフローを書き出しました|API workflow exported|Flujo API exportado
結果待ちを停止（TXTは保存しない）|Stop waiting (do not save TXT)|Dejar de esperar (no guardar TXT)
キャプション設定を保存しました。|Caption settings saved.|Configuración de descripciones guardada.
ComfyUI接続確認|Check ComfyUI connection|Comprobar conexión con ComfyUI
連携ノードを設置しました|Bridge node installed|Nodo de conexión instalado
設置できません|Installation failed|Error de instalación
設定を確認|Check settings|Revisar configuración
閾値は0〜1です。|Thresholds must be between 0 and 1.|Los umbrales deben estar entre 0 y 1.
PixAIのtagger_pipeline.pyがあるフォルダーを選択してください。|Select the PixAI folder containing tagger_pipeline.py.|Seleccione la carpeta PixAI que contiene tagger_pipeline.py.
対象画像がありません。フォルダーと既存TXTの設定を確認してください。|No matching images. Check folder and existing-TXT settings.|No hay imágenes válidas. Revise la carpeta y la opción de TXT existentes.
画像解析を開始|Start image analysis|Iniciar análisis de imágenes
解析準備を中止しました。|Analysis preparation canceled.|Preparación del análisis cancelada.
画像と同名の学習用TXTを編集します。他のソフトで作ったTXTも利用できます。保存すると元のTXTが更新されます。|Edit image-name training TXT, including captions from other apps. Saving updates the original TXT.|Edite los TXT de entrenamiento con el nombre de las imágenes, incluidos los de otras aplicaciones. Al guardar se actualiza el TXT original.
これはモデルの配布元TXTの設定です。画像と同名の学習用キャプションとは別です。モデル一覧で対象を選んでから操作してください。|Model source TXT documents a model file: source URL, family, trigger words and selected metadata. It is not a training caption. Scan and select models in Models before creating or updating these TXT files.|El TXT de origen documenta un modelo: URL, familia, palabras de activación y metadatos. No es una descripción para entrenamiento. Analice y seleccione modelos en Modelos antes de crear o actualizar estos TXT.
TXT変更を元に戻す…|Undo caption changes…|Deshacer cambios de descripciones…
未保存の変更は、一覧切替・終了時に確認します。|Unsaved edits are checked before switching images or closing.|Se comprobarán los cambios sin guardar antes de cambiar de imagen o cerrar.
未保存の変更あり|Unsaved changes|Cambios sin guardar
未保存のTXT|Unsaved TXT|TXT sin guardar
変更を保存しますか？ はい＝保存、いいえ＝破棄、キャンセル＝戻る。|Save changes? Yes: save; No: discard; Cancel: go back.|¿Guardar cambios? Sí: guardar; No: descartar; Cancelar: volver.
画像／TXT|Image / TXT|Imagen / TXT
画像を選択|Select an image|Seleccione una imagen
未作成|Not created|No creado
あり|Exists|Existe
同名画像が複数|Multiple images with the same name|Varias imágenes con el mismo nombre
対応する画像なし|No matching image|Sin imagen correspondiente
選択したTXTを一括編集（変更プレビュー後に保存）|Batch-edit selected TXT (review before saving)|Editar TXT en lote (revisar antes de guardar)
対象の語／追加する語|Target word / words to add|Palabra objetivo / palabras para añadir
置換後|Replacement|Reemplazo
< >はEmbeddingの設定と一致させる場合などに使用。LoRAの普通のトリガーワードに必須ではありません。|Use < > when required by your embedding configuration. Ordinary LoRA trigger words do not require these brackets.|Use < > cuando lo requiera su embedding. Las palabras de activación normales de LoRA no necesitan estos signos.
存在する画像・TXTフォルダーを選択してください。|Select an existing image/TXT folder.|Seleccione una carpeta existente de imágenes/TXT.
TXTを読み込めません|Cannot read TXT|No se puede leer el TXT
保存できません|Cannot save|No se puede guardar
保存済み / |Saved / |Guardado / 
画像を表示できません: |Cannot display image: |No se puede mostrar la imagen: 
一括編集するTXTを選択してください。Ctrl/Shiftまたは「すべて選択」が使えます。|Select TXT to edit with Ctrl/Shift or Select all.|Seleccione los TXT con Ctrl/Mayús o Seleccionar todo.
対象のTXTに変更はありません。|No changes to selected TXT.|No hay cambios en los TXT seleccionados.
TXT変更プレビュー — |TXT change preview — |Vista previa de cambios TXT — 
保存すると元のTXTを変更します。既存TXTはアプリ内caption-backupsにバックアップします。|Saving updates the original TXT. Backups go to the app's caption-backups folder.|Al guardar se actualiza el TXT original. Las copias se guardan en caption-backups de la aplicación.
TXT保存の確認|Confirm TXT save|Confirmar guardado de TXT
個のTXTを作成／更新しますか？ 画像は変更しません。| TXT files will be created/updated. Continue? Images stay unchanged.| archivos TXT se crearán/actualizarán. ¿Continuar? Las imágenes no cambian.
TXT保存完了|TXT saved|TXT guardado
TXT復元|Restore TXT|Restaurar TXT
TXT復元完了|TXT restored|TXT restaurado
選択した変更を元に戻しますか？ 後から編集されたTXTがあれば停止します。|Undo selected changes? Later edits will block restoration.|¿Deshacer cambios? Las ediciones posteriores bloquearán la restauración.
公開APIで照合（通常はオン）|Use public APIs (normally enabled)|Usar API públicas (normalmente activado)
オフ：ファイル構造・内部メタデータ・取得済み情報から判定します。未取得の作者・配布元・説明などは分からない場合があります。GPUでAIを動かす機能ではありません。|When off, uses file structure, embedded metadata and cached information. Uncached authors, sources and descriptions may be unavailable. No AI is run on your GPU.|Si se desactiva, usa la estructura del archivo, metadatos e información almacenada. Los autores, fuentes y descripciones no almacenados pueden faltar. No ejecuta IA en la GPU.
処理完了|Completed|Completado
処理の完了を待ってください。|Wait for the operation to finish.|Espere a que termine la operación.
確認|Confirm|Confirmar
移動・フォルダー作成の確認|Review moves and new folders|Revisar traslados y carpetas nuevas
はい（賛成）|Yes (approve)|Sí (aprobar)
いいえ|No|No
残りは後で確認|Review the rest later|Revisar el resto más tarde
はい＝実行対象にする／いいえ＝今回は移動しない／保留＝後で判断。ここではまだ移動しません。|Yes: include; No: skip; Pending: decide later. No files are moved yet.|Sí: incluir; No: omitir; Pendiente: decidir después. Todavía no se mueven archivos.
移動対象なし|No proposed moves|Sin traslados propuestos
確認画面で「はい」を選んだ移動案はありません。|No moves were approved.|No se aprobaron traslados.
配布元のオンライン照合|Online source lookup|Consulta de origen en línea'''

def install(catalog):
    for line in (ROWS+'\n'+EXTRA).splitlines():
        ja,en,es=line.split('|');catalog['en'][ja]=en;catalog['es'][ja]=es

EXTRA='''adapterテンソルを検出|Adapter tensors detected|Tensores adaptadores detectados
照合済み（キャッシュ）|Matched (cached)|Coincidencia (caché)
照合済み|Matched|Coincidencia
未照合（オフライン）|Not matched (offline)|Sin cotejar (sin conexión)
同一SHA256の確認済み配置|Verified placement for identical SHA256|Ubicación verificada para SHA256 idéntico
拡散モデルとVAE／テキストエンコーダーを同梱|Diffusion model with VAE/text encoder|Modelo de difusión con VAE/codificador de texto
単独の拡散モデル層を検出|Standalone diffusion model layers detected|Capas de difusión independientes detectadas
少数の埋め込みテンソルを検出|Embedding tensors detected|Tensores de embedding detectados
内部構造だけでは種類を確定できません|Cannot identify type from structure alone|No se puede identificar el tipo solo por la estructura
Trigger words|Trigger words|Palabras de activación
Description|Description|Descripción
Public metadata|Public metadata|Metadatos públicos
Lookup results|Lookup results|Resultados de búsqueda
File metadata|File metadata|Metadatos del archivo
【提案の理由】|[Reason for proposal]|[Motivo de la propuesta]
【新しく作成するフォルダー】|[New folders]|[Carpetas nuevas]
【現在の場所】|[Current location]|[Ubicación actual]
【移動先】|[Destination]|[Destino]
【追加ハードリンク】|[Additional hard links]|[Enlaces físicos adicionales]
履歴から元に戻せます。実行しますか？|You can undo from history. Continue?|Puede deshacerlo desde el historial. ¿Continuar?
根拠: |Evidence: |Evidencia: 
現在地: |Current location: |Ubicación actual: 
追加リンク: |Additional links: |Enlaces adicionales: 
配布元URLはユーザー指定（未照合）|User-provided source URL (unverified)|URL indicada por el usuario (sin verificar)
保存先は自動変更していません。確認して選択してください。|Destination was not changed automatically. Review and select it.|El destino no se cambió automáticamente. Revíselo y selecciónelo.
変更なしの項目は移動不要です。未指定の保存先は「保存先を変更」で設定してください。|Unchanged items need no move. Set missing destinations using Edit destination.|Los elementos sin cambios no necesitan traslado. Configure los destinos que faltan con Editar destino.
ComfyUIのAPI用JSONです。保存ノードは含まず、解析結果を返します。連携ノードが必要です。|ComfyUI API JSON returning analysis results, without a save node. Requires the bridge node.|JSON API de ComfyUI que devuelve resultados sin nodo de guardado. Requiere el nodo de conexión.
ComfyUIを起動し直してください。既存ワークフローは変更していません。|Restart ComfyUI. Existing workflows are unchanged.|Reinicie ComfyUI. Los flujos existentes no han cambiado.
PixAIのGPU推論は解析実行時に確認します。|PixAI GPU inference is checked when analysis runs.|La inferencia GPU de PixAI se comprueba al ejecutar el análisis.
接続と連携ノードを確認しました。|Connection and bridge node verified.|Conexión y nodo verificados.
同名で拡張子が違う画像があり、TXTが衝突します: |Different image extensions share a name and collide on TXT: |Imágenes con el mismo nombre y distinta extensión comparten el TXT: 
画像が解析中に変更されました: |Image changed during analysis: |La imagen cambió durante el análisis: 
枚をローカルComfyUIのPixAIで解析します。モデルのローカルPythonコードを利用します。解析後に変更内容を確認してからTXTを保存できます。開始しますか？| images will be analyzed by PixAI in local ComfyUI using local model Python code. Review results before saving TXT. Start?| imágenes se analizarán con PixAI en ComfyUI local mediante el código Python del modelo. Revise los resultados antes de guardar TXT. ¿Iniciar?
選択したモデルの配布元TXTを更新します。既存のアプリ生成TXTはアプリのデータフォルダーへバックアップします。手書きTXTは変更しません。更新したTXTがある移動履歴の復元は、安全確認で停止する場合があります。|Update selected model source TXT. Existing app-generated TXT is backed up in app data. Handwritten TXT is unchanged. Restoring old moves may stop if TXT has changed.|Actualizar TXT de origen seleccionados. Se guardan copias de los TXT creados por la app en sus datos. No se modifican TXT manuales. La restauración de traslados anteriores puede detenerse si el TXT ha cambiado.
項目を移動します。必要なフォルダーと配布元TXTも作成します。| items will be moved. Required folders and source TXT will also be created.| elementos se moverán. También se crearán las carpetas y los TXT de origen necesarios.'''

HELP_KEY='初回設定\n1. ComfyUIフォルダーを選び「連携ノードを設置」。ComfyUIを起動し直します。\n2. 起動ファイルと接続先URLを指定します。Desktopアプリだけ開いた場合は、その中でComfyUIを起動してください。\n3. PixAIモデルフォルダー（tagger_pipeline.pyのある場所）と画像フォルダーを選択します。\n4. 解析後、TXTの変更前後を確認して保存します。既存TXTは初期設定ではスキップします。\n他のPCでは、そのPCのパスを指定してください。重みやGPU環境は本アプリに含まれません。\n他のアプリで生成したTXTは「テキスト編集」で使えます。解析APIは今回はComfyUI専用です。\n停止ボタンは待機を中止します。すでにComfyUIで実行中の解析は続く場合がありますが、本アプリはTXTを保存しません。\n完全オフライン設定中も、明示的に実行する同一PC内のComfyUI連携は利用できます。'
HELP_EN='Initial setup\n1. Choose the ComfyUI folder and install the bridge node. Restart ComfyUI.\n2. Set the launcher and connection URL. If using ComfyUI Desktop, start its server inside the app.\n3. Choose the PixAI folder containing tagger_pipeline.py and your image folder.\n4. After analysis, review changes and save TXT. Existing TXT is skipped by default.\nSet paths on each PC. Model weights and GPU runtimes are not bundled.\nTXT from other applications can be edited in Text editor. Analysis currently uses ComfyUI only.\nStop cancels waiting; a running ComfyUI job may continue, but this app will not save TXT.\nExplicit local ComfyUI operations remain available in offline mode.'
HELP_ES='Configuración inicial\n1. Seleccione la carpeta de ComfyUI e instale el nodo de conexión. Reinicie ComfyUI.\n2. Configure el archivo de inicio y la URL. Si usa ComfyUI Desktop, inicie el servidor desde esa aplicación.\n3. Seleccione la carpeta PixAI que contiene tagger_pipeline.py y la carpeta de imágenes.\n4. Tras el análisis, revise los cambios y guarde los TXT. Por defecto se omiten los TXT existentes.\nConfigure las rutas en cada PC. No se incluyen los pesos ni el entorno GPU.\nPuede editar TXT de otras aplicaciones en Editor de texto. El análisis solo usa ComfyUI por ahora.\nDetener cancela la espera; una tarea de ComfyUI puede continuar, pero esta aplicación no guardará TXT.\nLas operaciones locales de ComfyUI iniciadas explícitamente siguen disponibles sin conexión.'
