ROWS='''起動中のComfyUIを探す|Find running ComfyUI|Buscar ComfyUI en ejecución
ComfyUI画面を開く|Open ComfyUI|Abrir ComfyUI
モデルの場所を確認|Check model folder|Comprobar carpeta del modelo
ComfyUIが起動済みならURLだけで接続できます。起動ファイルの指定は不要です。|If ComfyUI is already running, connect using its URL. No launcher path is needed.|Si ComfyUI ya está en ejecución, conecte mediante su URL. No necesita indicar el archivo de inicio.
初回連携・自動起動の設定を表示|Show initial setup / optional auto-start|Mostrar configuración inicial / inicio automático opcional
初回のみ：連携ノードの設置／任意：自動起動|First use: install bridge / Optional: auto-start|Primer uso: instalar conexión / Opcional: inicio automático
ComfyUIのインストール先（親フォルダーでも可）|ComfyUI installation folder (parent folder accepted)|Carpeta de instalación de ComfyUI (se admite la carpeta superior)
ComfyUI起動ファイル（任意：フォルダーではありません）|ComfyUI launcher (optional: a file, not a folder)|Archivo de inicio de ComfyUI (opcional: archivo, no carpeta)
インストール先を選ぶと、下の階層からComfyUI本体を確認します。設置後はComfyUIを再起動してください。|Select the installation folder; the app checks its children for ComfyUI. Restart ComfyUI after installing the bridge.|Seleccione la carpeta de instalación; la app buscará ComfyUI en sus subcarpetas. Reinicie ComfyUI tras instalar el nodo.
ComfyUI用テンプレートを保存|Save ComfyUI template|Guardar plantilla de ComfyUI
モデルの場所を確認しました。|Model folder verified.|Carpeta del modelo verificada.
接続できませんでした。ComfyUIを起動し、ブラウザーに表示されたURLを貼り付けてください。確認するポートは指定URL・8188・8000です。|Could not connect. Start ComfyUI and paste its browser URL. Discovery checks your URL and ports 8188 and 8000.|No se pudo conectar. Inicie ComfyUI y pegue la URL del navegador. La búsqueda comprueba su URL y los puertos 8188 y 8000.
複数のComfyUIが見つかりました。使用するURLを貼り付けて接続を確認してください。|Multiple ComfyUI servers found. Paste the one you want and check the connection.|Se encontraron varios servidores ComfyUI. Pegue la URL deseada y compruebe la conexión.
接続できました。連携ノードも利用できます。画像とモデルを選び、解析へ進めます。|Connected; bridge available. Select images and a model, then analyze.|Conectado; nodo disponible. Seleccione imágenes y modelo para analizar.
ComfyUIに接続できました。初回連携の設定を開き、連携ノードを設置してComfyUIを再起動してください。|Connected to ComfyUI. Open initial setup, install the bridge, then restart ComfyUI.|Conectado a ComfyUI. Abra la configuración inicial, instale el nodo y reinicie ComfyUI.
テンプレートを保存しました。ComfyUI画面にJSONをドラッグしてください。TXT保存はこのアプリから解析した場合に確認できます。|Template saved. Drag the JSON onto ComfyUI. To review and save paired TXT, run analysis from this app.|Plantilla guardada. Arrastre el JSON a ComfyUI. Para revisar y guardar TXT, ejecute el análisis desde esta app.
フォルダーを選択してください。|Select a folder.|Seleccione una carpeta.
複数の候補があります。使用するフォルダーを選択してください。|Multiple candidates found. Select the intended folder.|Hay varios candidatos. Seleccione la carpeta deseada.
ComfyUI本体が見つかりません。main.pyが入ったフォルダーを選択してください。|ComfyUI not found. Select the folder containing main.py.|No se encontró ComfyUI. Seleccione la carpeta que contiene main.py.
PixAIモデルが見つかりません。tagger_pipeline.pyが入ったフォルダーを選択してください。|PixAI not found. Select the folder containing tagger_pipeline.py.|No se encontró PixAI. Seleccione la carpeta que contiene tagger_pipeline.py.'''
HELP_JA='''通常の使い方（ComfyUIが起動済み）
1. ComfyUIをいつも通り起動。「起動中のComfyUIを探す」を押すか、ブラウザーのURLを接続先に貼り付けます。
2. 接続と連携ノードを確認。画像フォルダーとPixAIモデルフォルダーを選びます。PixAIの親フォルダーでも候補が一つなら本体を検出します。
3. 「解析して変更を確認」でComfyUIへ解析を依頼します。ワークフローを手で貼り付ける必要はありません。結果を確認後、画像と同名のTXTを保存できます。
初回だけ：連携ノードがない場合は「初回連携…」を開き、ComfyUIのインストール先を選んで設置します。main.pyを自分で探す代わりに、選んだフォルダーの2階層下まで確認します。設置後はComfyUIの再起動が必要です。
テンプレート：「ComfyUI用テンプレートを保存」で、画面にドラッグできるJSONを作れます。書き出した時点の画像一覧・モデル・閾値が入ります。ComfyUIで実行すると結果を表示しますが、TXTを自動保存しません。
起動ファイルは任意です。自動起動を使う場合だけ.exe / .bat / .cmd / .lnkを選びます。フォルダーを指定する欄ではありません。
別のPCではそのPCのパスを指定してください。画像・モデルはアップロードされず、同じPCのComfyUIが読み込みます。'''
HELP_EN='''Usual workflow (ComfyUI already running)
1. Start ComfyUI normally. Find running ComfyUI, or paste its browser URL.
2. Check connection and bridge. Choose image and PixAI folders. A parent model folder is accepted when exactly one model is found.
3. Analyze and review changes sends the job to ComfyUI. No manual workflow import is needed. Review results, then save image-name TXT.
First use only: if the bridge is missing, open initial setup and select the installation folder. The app checks two levels below it for main.py. Install the bridge and restart ComfyUI.
Template: save a JSON workflow to drag onto ComfyUI. It contains the current image list, model and thresholds. Running it displays captions but does not save TXT automatically.
Launcher is optional. Choose an .exe / .bat / .cmd / .lnk only for auto-start, not a directory.
On another PC, choose that PC's paths. Images and models are read by local ComfyUI, not uploaded.'''
HELP_ES='''Uso habitual (ComfyUI ya en ejecución)
1. Inicie ComfyUI normalmente. Busque ComfyUI en ejecución o pegue la URL del navegador.
2. Compruebe la conexión y el nodo. Seleccione carpetas de imágenes y PixAI. Se admite la carpeta superior si hay un único modelo.
3. Analizar y revisar cambios envía la tarea a ComfyUI. No necesita importar un flujo manualmente. Revise los resultados y guarde los TXT con el nombre de cada imagen.
Solo el primer uso: si falta el nodo, abra la configuración inicial y seleccione la carpeta de instalación. La app busca main.py hasta dos niveles por debajo. Instale el nodo y reinicie ComfyUI.
Plantilla: guarde un flujo JSON para arrastrarlo a ComfyUI. Incluye la lista actual de imágenes, el modelo y los umbrales. Al ejecutarlo muestra descripciones, pero no guarda TXT automáticamente.
El archivo de inicio es opcional. Seleccione un .exe / .bat / .cmd / .lnk solo para inicio automático, no una carpeta.
En otro PC, elija sus rutas. ComfyUI local lee imágenes y modelos; no se suben a Internet.'''

def install(catalog):
 for row in ROWS.splitlines():
  ja,en,es=row.split('|');catalog['en'][ja]=en;catalog['es'][ja]=es
 catalog['en'][HELP_JA]=HELP_EN;catalog['es'][HELP_JA]=HELP_ES
