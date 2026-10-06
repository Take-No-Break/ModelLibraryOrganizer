"""Image to Text overview in every supported UI language."""
TEXT={
'ja':('画像フォルダーと解析モデル・閾値を選び、接続確認後に実行します。画像フォルダー内にモデル種類名のフォルダーを作り、元画像のハードリンクと同名TXTを保存します。元画像は移動せず、既存TXTは上書きしません。','接続確認','保存先（自動）'),
'en':('Select the image folder, analysis model and thresholds, check the connection, then run. A folder named after the model type is created inside the image folder, containing image hardlinks and matching TXT. Original images stay in place; existing TXT is not overwritten.','Check connection','Save location (automatic)'),
'es':('Seleccione la carpeta de imágenes, el modelo de análisis y los umbrales; compruebe la conexión y ejecute. Dentro de la carpeta de imágenes se crea una carpeta con el nombre del tipo de modelo, con enlaces físicos a las imágenes y archivos TXT del mismo nombre. Las imágenes originales no se mueven y los TXT existentes no se sobrescriben.','Comprobar conexión','Destino (automático)'),
'zh-CN':('选择图片文件夹、分析模型和阈值，确认连接后运行。程序会在图片文件夹内创建以模型类型命名的文件夹，保存原图的硬链接和同名TXT。原图不会移动，已有TXT不会被覆盖。','检查连接','保存位置（自动）'),
'zh-TW':('選擇圖片資料夾、分析模型和閾值，確認連線後執行。程式會在圖片資料夾內建立以模型類型命名的資料夾，儲存原圖的硬連結和同名TXT。原圖不會移動，既有TXT不會被覆寫。','檢查連線','儲存位置（自動）'),
'pt-BR':('Selecione a pasta de imagens, o modelo de análise e os limites; verifique a conexão e execute. Uma pasta com o nome do tipo de modelo será criada dentro da pasta de imagens, contendo links físicos das imagens e arquivos TXT com os mesmos nomes. As imagens originais não são movidas e os TXT existentes não são sobrescritos.','Verificar conexão','Destino (automático)'),
'de':('Wählen Sie den Bildordner, das Analysemodell und die Schwellenwerte, prüfen Sie die Verbindung und starten Sie. Im Bildordner wird ein nach dem Modelltyp benannter Ordner mit Hardlinks der Bilder und gleichnamigen TXT-Dateien erstellt. Originalbilder bleiben am ursprünglichen Ort; vorhandene TXT-Dateien werden nicht überschrieben.','Verbindung prüfen','Speicherort (automatisch)'),
'th':('เลือกโฟลเดอร์ภาพ โมเดลวิเคราะห์ และค่าเกณฑ์ ตรวจสอบการเชื่อมต่อแล้วเริ่มทำงาน ระบบจะสร้างโฟลเดอร์ตามชื่อประเภทโมเดลภายในโฟลเดอร์ภาพ เพื่อบันทึกฮาร์ดลิงก์ของภาพต้นฉบับและไฟล์ TXT ชื่อเดียวกัน ภาพต้นฉบับจะไม่ถูกย้าย และไฟล์ TXT ที่มีอยู่จะไม่ถูกเขียนทับ','ตรวจสอบการเชื่อมต่อ','ตำแหน่งบันทึก (อัตโนมัติ)')}

def labels(language):return TEXT.get(language,TEXT['en'])

RESTORE_NOTICE={
'ja':'移動履歴が付いていない調査JSONだけでは復元できません。調査JSONは元の配置を記録するものです。復元するには、整理を実行したときの変更履歴、またはその変更履歴が関連付いた調査JSONを選んでください。',
'en':'A scan JSON without linked move history cannot restore files. It only records the original layout. To restore, select the move history created when organization was executed, or a scan JSON linked to that history.',
'es':'Un JSON de análisis sin un historial de movimientos asociado no puede restaurar archivos. Solo registra la ubicación original. Para restaurar, seleccione el historial creado al ejecutar la organización o un JSON de análisis vinculado a ese historial.',
'zh-CN':'没有关联移动历史的扫描JSON无法恢复文件。它只记录原来的布局。要恢复，请选择执行整理时生成的变更历史，或已关联该变更历史的扫描JSON。',
'zh-TW':'沒有關聯移動歷史的掃描JSON無法還原檔案。它只記錄原本的配置。要還原，請選擇執行整理時產生的變更歷史，或已關聯該變更歷史的掃描JSON。',
'pt-BR':'Um JSON de análise sem histórico de movimentação vinculado não permite restaurar arquivos. Ele apenas registra a organização original. Para restaurar, selecione o histórico criado ao executar a organização ou um JSON de análise vinculado a esse histórico.',
'de':'Eine Scan-JSON ohne verknüpften Verschiebeverlauf kann Dateien nicht wiederherstellen. Sie dokumentiert nur die ursprünglichen Speicherorte. Wählen Sie zur Wiederherstellung den beim Organisieren erstellten Änderungsverlauf oder eine damit verknüpfte Scan-JSON.',
'th':'ไฟล์ JSON ของการตรวจสอบที่ไม่มีประวัติการย้ายเชื่อมโยงอยู่ ไม่สามารถคืนค่าไฟล์ได้ เพราะบันทึกเพียงตำแหน่งเดิม หากต้องการคืนค่า ให้เลือกประวัติการเปลี่ยนแปลงที่สร้างเมื่อจัดระเบียบจริง หรือ JSON ของการตรวจสอบที่เชื่อมโยงกับประวัตินั้น'}
