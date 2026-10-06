"""Brazilian Portuguese UI translations; model data and paths are not translated."""
TRANSLATIONS = {}
DATA = r"""
Inspect, review, then organize|Inspecione, confira e organize
Review destinations and approve items before moving files.|Confira os destinos e aprove os itens antes de mover arquivos.
Scan folder|Pasta a verificar
Destination models folder|Pasta models de destino
Browse…|Procurar…
Online lookup: hashes; filenames for HF search|Consulta online: hashes; nomes de arquivos para pesquisa no HF
Combined (Civitai + HF)|Combinada (Civitai + HF)
Scan all|Verificar tudo
Stop scan|Parar verificação
Scan new / changed|Verificar novos / alterados
Reset scan cache|Limpar cache de verificação
Compatibility candidates|Candidatos compatíveis
Preview|Prévia
Find duplicates|Encontrar duplicados
Check workflow references|Verificar referências dos fluxos
Search other sources…|Pesquisar outras fontes…
Identification results|Resultados da identificação
Diagnostics / support…|Diagnóstico / suporte…
Combined: Civitai + HF. Other sites open in your browser.|Combinada: Civitai + HF. Outros sites abrem no navegador.
Approve selected|Aprovar selecionados
Reject selected|Rejeitar selecionados
Mark pending|Marcar como pendente
Edit destination / links…|Editar destino / links…
Verify HF repository…|Verificar repositório HF…
All|Todos
Proposed moves|Movimentações propostas
Needs review / errors|Revisão necessária / erros
Unidentified models|Modelos não identificados
Approved|Aprovado
Rejected|Rejeitado
Pending|Pendente
Unchanged|Sem alteração
Applied|Aplicado
Decision|Decisão
Model / file|Modelo / arquivo
Type|Tipo
Family|Família
Evidence|Evidência
Current location|Local atual
Destination|Destino
Export list…|Exportar lista…
Create source TXT|Criar TXT da origem
Undo from history…|Desfazer pelo histórico…
Guide|Guia
Apply approved only…|Aplicar apenas os aprovados…
Source hash verified|Hash da origem confirmado
Previously reviewed rule|Regra conferida anteriormente
Inferred structure / review|Estrutura inferida / revisar
Network failure / retry|Falha de rede / tentar novamente
Error / cannot verify|Erro / não foi possível verificar
Existing location retained|Local existente mantido
Source matched|Origem encontrada
Structure inferred|Estrutura inferida
Network failure|Falha de rede
Needs review|Precisa de revisão
Working|Processando
Selection|Seleção
Completed|Concluído
Review required|Revisão necessária
Saved|Salvo
Choose a destination|Escolha um destino
Choose folder…|Escolher pasta…
Choose destination|Escolher destino
Check destination|Verificar destino
Missing folder|Pasta não encontrada
Rescan|Verificar novamente
Rescan required|Nova verificação necessária
Confirm undo|Confirmar restauração
Restored|Restaurado
Confirm moves|Confirmar movimentações
Approval required|Aprovação necessária
Items not approved|Itens não aprovados
Cannot edit|Não foi possível editar
Checkpoint candidates|Checkpoints candidatos
SHA256 duplicate detection|Detecção de duplicados por SHA256
Select ComfyUI workflows folder|Selecione a pasta de fluxos do ComfyUI
Review results|Conferir resultados
Repair references|Corrigir referências
Select workflows to repair|Selecione os fluxos a corrigir
Repair selected JSON only|Corrigir apenas o JSON selecionado
Workflow repair complete|Correção do fluxo concluída
Source TXT|TXT da origem
Search sources in browser|Pesquisar fontes no navegador
Diagnostics and support log|Diagnóstico e registro de suporte
Diagnostic log|Registro de diagnóstico
Save diagnostic log… (no auto-send)|Salvar registro de diagnóstico… (sem envio automático)
Scan complete: identification results|Verificação concluída: identificação
Show unidentified models only|Mostrar apenas modelos não identificados
None|Nenhum
Undecided|Não decidido
Unknown|Desconhecido
No matches|Nenhum resultado
Scan complete: |Verificação concluída: 
Stopped: |Interrompido: 
Evidence: |Evidência: 
Source: |Origem: 
Current location: |Local atual: 
Additional links: |Links adicionais: 
Proposed type: |Tipo proposto: 
Move history|Histórico de movimentações
Language|Idioma
Check for updates|Verificar atualizações
Check updates at startup (optional)|Verificar atualizações ao iniciar (opcional)
Offline mode (block all network requests)|Modo offline (bloquear toda comunicação)
Update / support settings|Configurações de atualização / suporte
Open support page|Abrir página de suporte
Publisher not configured|Distribuidor não configurado
Save settings|Salvar configurações
Export publisher settings|Exportar configurações de distribuição
Update available|Atualização disponível
Up to date|Atualizado
Open release page|Abrir página da versão
Close|Fechar
Save support log|Salvar registro de suporte
Support|Suporte
Overview|Visão geral
Offline and privacy|Modo offline e privacidade
Updates|Atualizações
Identification and organization|Identificação e organização
Reports|Relatórios
Save|Salvar
Cancel|Cancelar
Public model preview (memory only)|Prévia pública do modelo (somente na memória)
Please wait until the current operation finishes.|Aguarde a conclusão da operação atual.
Choose existing scan and destination folders.|Escolha pastas existentes para verificação e destino.
Discard pending approvals and rescan?|Descartar aprovações pendentes e verificar novamente?
Select one item to edit.|Selecione um item para editar.
Select one LoRA.|Selecione uma LoRA.
Select one model.|Selecione um modelo.
Select one model file to verify.|Selecione um arquivo de modelo para verificar.
Destination inside models (new folders allowed)|Destino dentro de models (novas pastas permitidas)
Optional hardlink folders, relative to models, separated by ;|Pastas opcionais de links físicos, relativas a models, separadas por ;
Optional source URL (manual, not proof of a hash match)|URL opcional da origem (manual, não comprova correspondência do hash)
Use destination (no move yet)|Usar destino (sem mover ainda)
Undo these moves? Stop if files changed or destinations conflict.|Desfazer movimentações? Interromper se os arquivos mudaram ou houver conflitos.
Create TXT with triggers, public descriptions and metadata? Existing TXT is preserved.|Criar TXT com palavras de ativação, descrições públicas e metadados? O TXT existente será preservado.
Reset scan and lookup caches? Models, move history and manual rules remain. The next scan recalculates hashes.|Limpar caches? Modelos, histórico e regras manuais serão mantidos. A próxima verificação recalculará os hashes.
Scan cache reset.|Cache de verificação limpo.
Scan stopped. No models were moved.|Verificação interrompida. Nenhum modelo foi movido.
Rescan errors or already applied items before editing.|Verifique novamente os itens com erros ou já aplicados antes de editar.
Rescan after changing the destination root.|Verifique novamente após alterar a pasta de destino.
Select items and approve them before applying moves.|Selecione e aprove os itens antes de movê-los.
Review this JSON and share it with the publisher if needed.|Confira este JSON e compartilhe com o distribuidor se necessário.
Folder names alone do not prove identity. A source hash match does not guarantee compatibility.|Nomes de pastas não comprovam identidade. Hashes iguais não garantem compatibilidade.
Identification results for this scan; skipped cached items are excluded.|Resultados desta verificação; itens ignorados por já estarem no cache não aparecem.
No items were scanned this time.|Nenhum item foi verificado desta vez.
These buttons open websites. Names alone never trigger automatic classification.|Estes botões abrem sites. Nomes sozinhos nunca determinam a classificação automática.
Model name to search. Add a verified page URL via Edit destination / links.|Nome do modelo para pesquisa. Adicione a URL confirmada em Editar destino / links.
Model repository URL (SHA256 check against main):|URL do repositório do modelo (verificação SHA256 na branch main):
Destination was not changed automatically. Review and select it.|O destino não foi alterado automaticamente. Confira e selecione.
You can undo from history. Continue?|É possível desfazer pelo histórico. Continuar?
Configure a publisher destination. Logs are never sent automatically.|Configure o endereço do distribuidor. Registros nunca são enviados automaticamente.
Network access is disabled in offline mode.|O acesso à rede está desativado no modo offline.
Language saved. Restart the app to apply.|Idioma salvo. Reinicie o aplicativo para aplicar.
Update checks need internet. Updates are not installed automatically.|Verificar atualizações exige internet. Elas não são instaladas automaticamente.
Choose folders, then scan. Ctrl / Shift selects multiple items.|Escolha as pastas e verifique. Ctrl / Shift seleciona vários itens.
Unchanged items need no move. Set missing destinations using Edit destination.|Itens sem alteração não precisam ser movidos. Defina destinos ausentes em Editar destino.
User-provided source URL (unverified)|URL da origem fornecida pelo usuário (não verificada)
Hardlinks to directories are not supported.|Links físicos para pastas não são suportados.
Hardlink destinations must stay inside models.|Os destinos de links físicos devem permanecer dentro de models.
Destination must stay inside models.|O destino deve permanecer dentro de models.
Destination already exists.|O destino já existe.
Wait for completion or stop the current scan before closing.|Aguarde a conclusão ou interrompa a verificação antes de fechar.
Organization complete. Refresh the ComfyUI model list and reselect models if needed.|Organização concluída. Atualize a lista do ComfyUI e selecione novamente os modelos se necessário.
Enter an HTTPS or HTTP source URL.|Informe uma URL HTTPS ou HTTP da origem.
Not selected|Não selecionado
User specified|Definido pelo usuário
Hugging Face verification|Verificação no Hugging Face
SHA256 match|SHA256 correspondente
Only HTTPS images are supported.|Somente imagens HTTPS são suportadas.
Preview image is too large.|A imagem de prévia é grande demais.
No safe public preview is available. Check the source URL in the TXT.|Nenhuma prévia pública adequada está disponível. Confira a URL da origem no TXT.
Folder|Pasta
Models|Modelos
Results|Resultados
Tools|Ferramentas
Working…|Processando…
Update readable TXT|Atualizar TXT legível
Select one model in Models, then load its preview.|Selecione um modelo em Modelos para carregar sua prévia.
Compatibility|Compatibilidade
Approve move|Aprovar movimentação
Do not move|Não mover
Leave pending|Deixar pendente
Scan this folder|Verificar esta pasta
Current scan results|Resultados da verificação atual
Copy|Copiar
Paste|Colar
Cut|Recortar
Select all|Selecionar tudo
TXT fields (basic identity is always included)|Campos do TXT (identificação básica sempre incluída)
Training captions|Legendas para treinamento
Text editor|Editor de texto
Images and training TXT|Imagens e TXT de treinamento
Model source TXT|TXT da origem do modelo
Image folder|Pasta de imagens
PixAI model folder|Pasta do modelo PixAI
Subfolders|Subpastas
Start ComfyUI if needed|Iniciar ComfyUI se necessário
Skip existing TXT|Ignorar TXT existentes
Recaption existing TXT (backup on save)|Refazer TXT existentes (backup ao salvar)
Install bridge node|Instalar nó de integração
Check connection|Verificar conexão
Analyze and review changes|Analisar e conferir alterações
Load image/TXT list|Carregar lista de imagens/TXT
Save current TXT|Salvar TXT atual
Prepend|Adicionar no início
Append|Adicionar no final
Remove|Remover
Replace|Substituir
Wrap in < >|Envolver com < >
Exact tag|Tag exata
Whole word|Palavra inteira
Preview changes|Prévia das alterações
Save these changes|Salvar estas alterações
Checkpoint|Checkpoint
Checkpoint folder|Pasta de checkpoints
LoRA folder|Pasta de LoRAs
Scan selected folders|Verificar pastas selecionadas
Refresh scanned models|Atualizar modelos verificados
Assessment|Avaliação
Choose a LoRA. Green: same family; yellow: related SDXL families; gray: unrelated or unknown. Results are not guaranteed.|Escolha uma LoRA. Verde: mesma família; amarelo: famílias SDXL relacionadas; cinza: sem relação ou desconhecida. Resultados não são garantidos.
Candidates come from this PC's scan history and current results. New PCs start empty. Drives are not searched automatically.|Os candidatos vêm do histórico deste PC e dos resultados atuais. Outros PCs começam sem dados. Unidades não são pesquisadas automaticamente.
No candidates. Select folders and scan them.|Nenhum candidato. Selecione pastas e verifique.
Select existing checkpoint/LoRA folders.|Selecione pastas existentes de checkpoints/LoRAs.
Compatibility scan complete. No models moved.|Verificação de compatibilidade concluída. Nenhum modelo movido.
Same family; pair untested|Mesma família; combinação não testada
Related SDXL family; medium (untested)|Família SDXL relacionada; média (não testada)
Different family; no known compatibility|Família diferente; sem compatibilidade conhecida
Unknown family|Família desconhecida
Click a row to record your assessment|Clique em uma linha para registrar sua avaliação
Automatic assessment|Avaliação automática
Worked in my test (green)|Funcionou no meu teste (verde)
Needs adjustment (yellow)|Precisa de ajustes (amarelo)
Did not work (gray)|Não funcionou (cinza)
User assessment|Avaliação do usuário
Notes|Observações
Save assessment|Salvar avaliação
Copy current path|Copiar caminho atual
Copy destination path|Copiar caminho de destino
Open current folder|Abrir pasta atual
Open destination folder|Abrir pasta de destino
Open source page|Abrir página da origem
Destination does not exist yet.|O destino ainda não existe.
Review appears only when moves or links are proposed.|A revisão aparece apenas quando movimentações ou links são propostos.
Review proposed moves…|Conferir movimentações propostas…
Select a model to show its public preview.|Selecione um modelo para mostrar sua prévia pública.
Loading…|Carregando…
No general-audience preview in the public API.|Não há prévia para público geral na API pública.
Cannot download previews offline.|Não é possível baixar prévias no modo offline.
ComfyUI URL (this PC)|URL do ComfyUI (este PC)
ComfyUI launcher|Inicializador do ComfyUI
ComfyUI folder (contains main.py)|Pasta do ComfyUI (contém main.py)
PixAI thresholds (0–1)|Limiares do PixAI (0–1)
Export API workflow|Exportar fluxo de API
API workflow exported|Fluxo de API exportado
Stop waiting (do not save TXT)|Parar espera (não salvar TXT)
Caption settings saved.|Configurações de legendas salvas.
Check ComfyUI connection|Verificar conexão com ComfyUI
Bridge node installed|Nó de integração instalado
Installation failed|Falha na instalação
Check settings|Verificar configurações
Thresholds must be between 0 and 1.|Os limiares devem estar entre 0 e 1.
Select the PixAI folder containing tagger_pipeline.py.|Selecione a pasta PixAI que contém tagger_pipeline.py.
No matching images. Check folder and existing-TXT settings.|Nenhuma imagem encontrada. Confira a pasta e as opções de TXT existentes.
Start image analysis|Iniciar análise de imagens
Analysis preparation canceled.|Preparação da análise cancelada.
Edit image-name training TXT, including captions from other apps. Saving updates the original TXT.|Edite o TXT de treinamento com o nome da imagem, inclusive legendas de outros aplicativos. Salvar atualiza o TXT original.
Model source TXT documents a model file: source URL, family, trigger words and selected metadata. It is not a training caption. Scan and select models in Models before creating or updating these TXT files.|O TXT da origem documenta o modelo: URL, família, palavras de ativação e metadados selecionados. Não é uma legenda de treinamento. Verifique e selecione modelos em Modelos antes de criar ou atualizar esses TXT.
Undo caption changes…|Desfazer alterações das legendas…
Unsaved edits are checked before switching images or closing.|Alterações não salvas são verificadas antes de trocar imagens ou fechar.
Unsaved changes|Alterações não salvas
Unsaved TXT|TXT não salvo
Save changes? Yes: save; No: discard; Cancel: go back.|Salvar alterações? Sim: salvar; Não: descartar; Cancelar: voltar.
Image / TXT|Imagem / TXT
Select an image|Selecione uma imagem
Not created|Não criado
Exists|Existe
Multiple images with the same name|Várias imagens com o mesmo nome
No matching image|Nenhuma imagem correspondente
Batch-edit selected TXT (review before saving)|Editar TXT selecionados em lote (conferir antes de salvar)
Target word / words to add|Palavra alvo / palavras a adicionar
Replacement|Substituição
Use < > when required by your embedding configuration. Ordinary LoRA trigger words do not require these brackets.|Use < > quando sua configuração de embedding exigir. Palavras de ativação comuns de LoRA não precisam desses símbolos.
Select an existing image/TXT folder.|Selecione uma pasta existente de imagens/TXT.
Cannot read TXT|Não foi possível ler o TXT
Cannot save|Não foi possível salvar
Select TXT to edit with Ctrl/Shift or Select all.|Selecione TXT para editar com Ctrl/Shift ou Selecionar tudo.
No changes to selected TXT.|Nenhuma alteração nos TXT selecionados.
Saving updates the original TXT. Backups go to the app's caption-backups folder.|Salvar atualiza o TXT original. Backups ficam na pasta caption-backups do aplicativo.
Confirm TXT save|Confirmar gravação dos TXT
TXT saved|TXT salvo
Restore TXT|Restaurar TXT
TXT restored|TXT restaurado
Undo selected changes? Later edits will block restoration.|Desfazer alterações selecionadas? Edições posteriores impedirão a restauração.
Use public APIs (normally enabled)|Usar APIs públicas (normalmente ativado)
When off, uses file structure, embedded metadata and cached information. Uncached authors, sources and descriptions may be unavailable. No AI is run on your GPU.|Quando desativado, usa estrutura, metadados incorporados e cache. Autores, fontes e descrições fora do cache podem faltar. Nenhuma IA é executada na sua GPU.
Wait for the operation to finish.|Aguarde a conclusão da operação.
Confirm|Confirmar
Review moves and new folders|Conferir movimentações e novas pastas
Yes (approve)|Sim (aprovar)
No|Não
Review the rest later|Conferir o restante depois
Yes: include; No: skip; Pending: decide later. No files are moved yet.|Sim: incluir; Não: ignorar; Pendente: decidir depois. Nenhum arquivo é movido ainda.
No proposed moves|Nenhuma movimentação proposta
No moves were approved.|Nenhuma movimentação aprovada.
Online source lookup|Consulta online da origem
Adapter tensors detected|Tensores de adaptador detectados
Matched (cached)|Correspondência (cache)
Matched|Correspondência encontrada
Not matched (offline)|Sem correspondência (offline)
Verified placement for identical SHA256|Local confirmado para SHA256 idêntico
Diffusion model with VAE/text encoder|Modelo de difusão com VAE/codificador de texto
Standalone diffusion model layers detected|Camadas de modelo de difusão independente detectadas
Embedding tensors detected|Tensores de embedding detectados
Cannot identify type from structure alone|Não é possível identificar o tipo apenas pela estrutura
Trigger words|Palavras de ativação
Description|Descrição
Public metadata|Metadados públicos
Lookup results|Resultados da consulta
File metadata|Metadados do arquivo
[Reason for proposal]|[Motivo da proposta]
[New folders]|[Novas pastas]
[Current location]|[Local atual]
[Destination]|[Destino]
[Additional hard links]|[Links físicos adicionais]
Update selected model source TXT. Existing app-generated TXT is backed up in app data. Handwritten TXT is unchanged. Restoring old moves may stop if TXT has changed.|Atualizar TXT da origem dos modelos selecionados. TXT gerados pelo aplicativo são copiados para backup nos dados do aplicativo. TXT manuais não são alterados. Restaurar movimentações antigas pode falhar se o TXT mudou.
Initial setup|Configuração inicial
Find running ComfyUI|Encontrar ComfyUI em execução
Open ComfyUI|Abrir ComfyUI
Check model folder|Verificar pasta do modelo
Save ComfyUI template|Salvar modelo de fluxo ComfyUI
Model folder verified.|Pasta do modelo verificada.
Select a folder.|Selecione uma pasta.
Multiple candidates found. Select the intended folder.|Várias opções encontradas. Selecione a pasta desejada.
ComfyUI not found. Select the folder containing main.py.|ComfyUI não encontrado. Selecione a pasta com main.py.
PixAI not found. Select the folder containing tagger_pipeline.py.|PixAI não encontrado. Selecione a pasta com tagger_pipeline.py.
Warning before changing file locations|Aviso antes de alterar locais dos arquivos
Do not show this warning again (final confirmation remains)|Não mostrar este aviso novamente (confirmação final mantida)
Yes (continue)|Sim (continuar)
No (cancel)|Não (cancelar)
History / Restore|Histórico / Restaurar
Restore previous locations. If several changes were made, undo the newest history first.|Restaure os locais anteriores. Se houve várias alterações, desfaça primeiro as mais recentes.
Refresh history|Atualizar histórico
Undo selected history|Desfazer histórico selecionado
Open history JSON…|Abrir JSON do histórico…
Show warning before moves|Mostrar aviso antes de mover
Execution date|Data da execução
Operations|Operações
Status|Status
History location:|Local do histórico:
Incomplete; review required|Incompleto; revisão necessária
History file:|Arquivo do histórico:
Before → After|Antes → Depois
Folders retained (not empty or changed):|Pastas mantidas (não vazias ou alteradas):
This history cannot be restored.|Este histórico não pode ser restaurado.
Select a history entry to undo.|Selecione um registro do histórico para desfazer.
This history is already restored or unreadable.|Este histórico já foi restaurado ou não pode ser lido.
Restore the locations in this history? Changes or original-path conflicts stop restoration. Folders created by this run are removed only if empty.|Restaurar os locais deste histórico? Alterações ou conflitos nos caminhos originais interrompem a restauração. Pastas criadas nesta execução só são removidas se estiverem vazias.
Model inspection|Inspeção de modelos
Training data|Dados de treinamento
Past scans, captions and exported files|Verificações anteriores, legendas e arquivos exportados
Date|Data
Result|Resultado
Saved model scan (cache)|Verificação de modelos salva (cache)
Details and past logs are in Results. Models have not been moved.|Detalhes e registros anteriores ficam em Resultados. Os modelos não foram movidos.
View details in Results.|Veja os detalhes em Resultados.
Caption analysis / edit result|Resultado da análise / edição de legendas
Combined scan = automatic Civitai + HF lookup.|Verificação combinada = consulta automática no Civitai + HF.
Browser|Navegador
Desktop application|Aplicativo de desktop
Template format|Formato do modelo de fluxo
Combined|Integrado
Expanded|Dividido em etapas
Open|Abrir
Save an image analysis workflow to create LoRA training TXT. Add Embedding words in Text editor. Run the workflow in ComfyUI.|Salve um fluxo de análise de imagens para criar TXT de treinamento LoRA. Adicione palavras de Embedding no Editor de texto. Execute o fluxo no ComfyUI.
Estimates whether a LoRA can be loaded with a checkpoint. Source families are compared: green for the same family, yellow for related SDXL families, gray for unknown or different families. Actual loader success and generation results are not guaranteed.|Estima se uma LoRA pode ser carregada com um checkpoint. Compara famílias: verde para a mesma, amarelo para famílias SDXL relacionadas e cinza para desconhecidas ou diferentes. Não garante carregamento nem qualidade dos resultados.
Image to Text model folder|Pasta do modelo de análise Image to Text
Model|Modelo
Model settings|Configurações do modelo
CL Tagger threshold|Limiar do CL Tagger
Taggerine threshold|Limiar do Taggerine
JoyCaption instruction|Instrução do JoyCaption
JoyCaption max tokens|Máximo de tokens do JoyCaption
Only the settings for the selected model apply.|Somente as configurações do modelo selecionado se aplicam.
Save matching TXT in ComfyUI (skip existing TXT)|Salvar TXT correspondente no ComfyUI (ignorar TXT existentes)
Save ComfyUI workflow template|Salvar modelo de fluxo do ComfyUI
Save required custom nodes|Salvar nós personalizados necessários
Workflow preview|Prévia do fluxo
Combined: fewer nodes. Expanded: each stage is visible. Both export an editable ComfyUI workflow JSON, not an API request.|Integrado: menos nós. Dividido: cada etapa fica visível. Ambos exportam um fluxo JSON editável do ComfyUI, não uma requisição de API.
Copy the exported custom nodes folder into ComfyUI/custom_nodes, install its requirements in the ComfyUI Python environment, then restart ComfyUI. Drag the workflow JSON onto the canvas. Model weights are separate.|Copie a pasta de nós exportados para ComfyUI/custom_nodes, instale as dependências no Python do ComfyUI e reinicie o ComfyUI. Arraste o JSON do fluxo para a tela. Os pesos dos modelos são separados.
Paths, model, thresholds and template options are saved automatically on this PC.|Caminhos, modelo, limiares e opções do fluxo são salvos automaticamente neste PC.
Support & Updates|Suporte e atualizações
"""
DATA += "\n search| pesquisar\n (search on site)| (pesquisar no site)\n items will be moved. Required folders and source TXT will also be created.| itens serão movidos. Pastas necessárias e TXT da origem também serão criados.\n files will be backed up and repaired. Complete model moves first.| arquivos terão backup e serão corrigidos. Conclua primeiro a movimentação dos modelos.\n source TXT files created. Existing TXT preserved.| TXT da origem criados. TXT existentes preservados.\n items. No models moved yet.| itens. Nenhum modelo foi movido ainda.\nApproved moves applied. History: |Movimentações aprovadas aplicadas. Histórico: \n moves undone. Please rescan.| movimentações desfeitas. Verifique novamente.\nList saved: |Lista salva: \nphysical_copies counts independent files; 1 means hardlinks only. extra_bytes estimates redundant copy size. Nothing is deleted.|physical_copies conta arquivos independentes; 1 significa apenas links físicos. extra_bytes estima o espaço de cópias redundantes. Nada é excluído.\nNo affected supported loader references found. Unsupported custom nodes and embedding prompts are not automatically repaired.|Nenhuma referência afetada de carregador suportado encontrada. Nós não suportados e prompts de embedding não são corrigidos automaticamente.\nOnly scanned, existing models are listed. The same SDXL family does not guarantee results. Check the author's source instructions.|Somente modelos existentes já verificados são listados. A mesma família SDXL não garante resultados. Consulte as instruções do autor.\nOnly supported model files and packages are counted. Unsupported formats such as .obj/.fbx/.glb are excluded. Unidentified items stay put until you choose a destination and approve.|Somente arquivos e pacotes suportados são contados. Formatos como .obj/.fbx/.glb são excluídos. Itens não identificados permanecem no local até você escolher e aprovar um destino.\nOriginal JSON backups:|Backups dos JSON originais:\nFetching source information |Obtendo informações da origem \n items| itens\nScan history and current results / LoRA: |Histórico e resultados atuais / LoRA: \n — Selected folders only; blank fields include all scan history.| — Apenas pastas selecionadas; campos vazios incluem todo o histórico.\nCould not load preview: |Não foi possível carregar a prévia: \nCreate image captions for LoRA/embedding training with local ComfyUI + PixAI. Review and save image-name TXT here. This does not train models or generate images.|Crie legendas de imagens para treinamento LoRA/embedding com ComfyUI local + PixAI. Confira e salve os TXT aqui. Não treina modelos nem gera imagens.\nTag order: quality / meta / rating → character → copyright → style → subject count → general. TXT is saved beside the image with the same base name.|Ordem das tags: qualidade / meta / classificação → personagem → obra → estilo → quantidade de pessoas → gerais. O TXT fica ao lado da imagem com o mesmo nome base.\nSaved / |Salvo / \nCannot display image: |Não foi possível mostrar a imagem: \nTXT change preview — |Prévia das alterações de TXT — \n TXT files will be created/updated. Continue? Images stay unchanged.| TXT serão criados/atualizados. Continuar? As imagens não serão alteradas.\nComfyUI API JSON returning analysis results, without a save node. Requires the bridge node.|JSON de API do ComfyUI que retorna resultados sem nó de gravação. Exige o nó de integração.\nRestart ComfyUI. Existing workflows are unchanged.|Reinicie o ComfyUI. Fluxos existentes não são alterados.\nPixAI GPU inference is checked when analysis runs.|A inferência PixAI na GPU é verificada durante a análise.\nConnection and bridge node verified.|Conexão e nó de integração verificados.\nDifferent image extensions share a name and collide on TXT: |Imagens com extensões diferentes compartilham o nome e geram conflito no TXT: \nImage changed during analysis: |Imagem alterada durante a análise: \n images will be analyzed by PixAI in local ComfyUI using local model Python code. Review results before saving TXT. Start?| imagens serão analisadas pelo PixAI no ComfyUI local usando o código Python do modelo. Confira antes de salvar TXT. Iniciar?\n1. Choose the ComfyUI folder and install the bridge node. Restart ComfyUI.|1. Escolha a pasta do ComfyUI e instale o nó de integração. Reinicie o ComfyUI.\n2. Set the launcher and connection URL. If using ComfyUI Desktop, start its server inside the app.|2. Defina o inicializador e a URL de conexão. No ComfyUI Desktop, inicie o servidor dentro do aplicativo.\n3. Choose the PixAI folder containing tagger_pipeline.py and your image folder.|3. Escolha a pasta PixAI com tagger_pipeline.py e sua pasta de imagens.\n4. After analysis, review changes and save TXT. Existing TXT is skipped by default.|4. Após a análise, confira as alterações e salve os TXT. Por padrão, TXT existentes são ignorados.\nSet paths on each PC. Model weights and GPU runtimes are not bundled.|Defina os caminhos em cada PC. Pesos de modelos e ambientes de GPU não estão incluídos.\nTXT from other applications can be edited in Text editor. Analysis currently uses ComfyUI only.|TXT de outros aplicativos podem ser editados no Editor de texto. A análise utiliza apenas ComfyUI.\nStop cancels waiting; a running ComfyUI job may continue, but this app will not save TXT.|Parar cancela a espera; uma tarefa do ComfyUI pode continuar, mas este aplicativo não salvará TXT.\nExplicit local ComfyUI operations remain available in offline mode.|Operações explícitas do ComfyUI local continuam disponíveis no modo offline.\nIf ComfyUI is already running, connect using its URL. No launcher path is needed.|Se o ComfyUI já estiver em execução, conecte pela URL. Não é necessário caminho do inicializador.\nShow initial setup / optional auto-start|Mostrar configuração inicial / início automático opcional\nFirst use: install bridge / Optional: auto-start|Primeiro uso: instalar integração / Opcional: início automático\nComfyUI installation folder (parent folder accepted)|Pasta de instalação do ComfyUI (pasta superior aceita)\nComfyUI launcher (optional: a file, not a folder)|Inicializador do ComfyUI (opcional: arquivo, não pasta)\nSelect the installation folder; the app checks its children for ComfyUI. Restart ComfyUI after installing the bridge.|Selecione a pasta de instalação; o aplicativo procura ComfyUI nas subpastas. Reinicie após instalar a integração.\nCould not connect. Start ComfyUI and paste its browser URL. Discovery checks your URL and ports 8188 and 8000.|Não foi possível conectar. Inicie o ComfyUI e cole a URL do navegador. A busca verifica sua URL e as portas 8188 e 8000.\nMultiple ComfyUI servers found. Paste the one you want and check the connection.|Vários servidores ComfyUI encontrados. Cole a URL desejada e verifique a conexão.\nConnected; bridge available. Select images and a model, then analyze.|Conectado; integração disponível. Selecione imagens e um modelo e analise.\nConnected to ComfyUI. Open initial setup, install the bridge, then restart ComfyUI.|Conectado ao ComfyUI. Abra a configuração inicial, instale a integração e reinicie o ComfyUI.\nTemplate saved. Drag the JSON onto ComfyUI. To review and save paired TXT, run analysis from this app.|Fluxo salvo. Arraste o JSON para o ComfyUI. Para conferir e salvar TXT correspondentes, execute a análise neste aplicativo.\nUsual workflow (ComfyUI already running)|Fluxo usual (ComfyUI já em execução)\n1. Start ComfyUI normally. Find running ComfyUI, or paste its browser URL.|1. Inicie o ComfyUI normalmente. Localize a instância em execução ou cole sua URL.\n2. Check connection and bridge. Choose image and PixAI folders. A parent model folder is accepted when exactly one model is found.|2. Verifique a conexão e a integração. Escolha as pastas de imagens e PixAI. Uma pasta superior é aceita quando apenas um modelo é encontrado.\n3. Analyze and review changes sends the job to ComfyUI. No manual workflow import is needed. Review results, then save image-name TXT.|3. Analisar e conferir alterações envia a tarefa ao ComfyUI. Não é preciso importar o fluxo manualmente. Confira e salve os TXT.\nFirst use only: if the bridge is missing, open initial setup and select the installation folder. The app checks two levels below it for main.py. Install the bridge and restart ComfyUI.|Somente no primeiro uso: se faltar integração, abra a configuração inicial e selecione a instalação. O aplicativo busca main.py em dois níveis de subpastas. Instale e reinicie o ComfyUI.\nTemplate: save a JSON workflow to drag onto ComfyUI. It contains the current image list, model and thresholds. Running it displays captions but does not save TXT automatically.|Fluxo: salve um JSON para arrastar ao ComfyUI. Inclui imagens, modelo e limiares atuais. Ao executar, mostra legendas sem salvar TXT automaticamente.\nLauncher is optional. Choose an .exe / .bat / .cmd / .lnk only for auto-start, not a directory.|O inicializador é opcional. Escolha .exe / .bat / .cmd / .lnk apenas para início automático, não uma pasta.\nOn another PC, choose that PC's paths. Images and models are read by local ComfyUI, not uploaded.|Em outro PC, escolha os caminhos daquele computador. Imagens e modelos são lidos pelo ComfyUI local, sem upload.\nComfy Desktop application (EXE, optional)|Aplicativo Comfy Desktop (EXE, opcional)\nThe UI launch target and analysis URL are separate settings. Select the same ComfyUI instance in Desktop. Drag the saved template JSON onto its canvas.|O aplicativo a abrir e a URL de análise são configurações separadas. Selecione a mesma instância no Desktop. Arraste o JSON salvo para a tela.\nThe expanded template requires the updated bridge. Both use the same PixAI model.|O fluxo dividido exige a integração atualizada. Ambos usam o mesmo modelo PixAI.\nSelect Desktop application|Selecionar aplicativo de desktop\nSelect the application to open. The analysis URL is not changed.|Selecione o aplicativo a abrir. A URL de análise não é alterada.\nChoose another EXE…|Escolher outro EXE…\nDesktop application requested. Check its selected ComfyUI instance and API URL.|Aplicativo solicitado. Confira a instância ComfyUI e a URL de API selecionadas.\nExpanded: update the bridge and restart ComfyUI.|Dividido: atualize a integração e reinicie o ComfyUI.\n"
DATA += '\nInspect all supported models without moving them. Cached results may be reused.|Verifique todos os modelos suportados sem movê-los. Resultados em cache podem ser reutilizados.\nInspect only models added or changed since the last scan.|Verifique apenas modelos adicionados ou alterados desde a última verificação.\nClear lookup caches to recheck models. Model files and undo history remain.|Limpe o cache para verificar novamente. Modelos e histórico de restauração são mantidos.\nCancel the scan. An active request may finish or time out first.|Cancele a verificação. Uma requisição em andamento pode terminar ou atingir o tempo limite antes.\nCompare the selected LoRA with scanned checkpoint families. This is not a compatibility guarantee.|Compare a LoRA selecionada com as famílias dos checkpoints verificados. Não garante compatibilidade.\nFetch a public image marked safe and display it in memory. Internet required.|Baixe uma imagem pública marcada como segura e exiba na memória. Requer internet.\nCompare full-file SHA256 hashes, distinguish hardlinks, and never auto-delete.|Compare SHA256 dos arquivos completos, diferencie links físicos e nunca exclua automaticamente.\nFind loader references affected by approved moves. Repair selected JSON with backups.|Localize referências afetadas por movimentações aprovadas. Corrija JSON selecionados com backup.\nMark selected items for execution. This button does not move files.|Marque itens para execução. Este botão não move arquivos.\nExclude selected items from this move operation.|Exclua os itens selecionados desta movimentação.\nClear approval or rejection and return items to pending.|Remova aprovação ou rejeição e volte os itens para pendentes.\nChoose a destination inside models, optional hardlinks and a source URL.|Escolha um destino dentro de models, links físicos opcionais e uma URL da origem.\nVerify SHA256 against main in a specified Hugging Face repository.|Verifique SHA256 na branch main de um repositório Hugging Face especificado.\nSave source, triggers and metadata beside the model. Existing TXT files are preserved.|Salve origem, palavras de ativação e metadados ao lado do modelo. TXT existentes são preservados.\nAfter confirmation, move approved models and create required folders.|Após confirmação, mova modelos aprovados e crie as pastas necessárias.\nRestore original locations from move history. Stop on modifications or conflicts.|Restaure os locais originais pelo histórico. Interrompa se houver alterações ou conflitos.\nExport scan results to CSV. Review local paths before sharing.|Exporte resultados para CSV. Confira caminhos locais antes de compartilhar.\nReview unidentified, inferred, failed and verified results with evidence.|Confira resultados não identificados, inferidos, com falhas e confirmados e suas evidências.\nReview and save diagnostics without personal paths or model names. No automatic upload.|Confira e salve diagnósticos sem caminhos pessoais nem nomes de modelos. Sem envio automático.\nOpen source websites in your browser, separately from automatic hash verification.|Abra sites de origem no navegador, separadamente da verificação automática por hash.\nEnter or edit this value. Folder fields also support Browse.|Digite ou edite o valor. Campos de pasta também aceitam Procurar.\nChoose an option. Selection alone does not move models.|Escolha uma opção. A seleção sozinha não move modelos.\nOpen the guide, updates, support and privacy settings.|Abra o guia, atualizações, suporte e configurações de privacidade.\nClick to begin. Operations that move or modify files show a confirmation.|Clique para iniciar. Operações que movem ou alteram arquivos exibem uma confirmação.\nInspect supported models in this folder and its subfolders.|Verifique modelos suportados nesta pasta e nas subpastas.\nDestination root. Proposed locations are restricted to this folder.|Raiz de destino. Locais propostos ficam restritos a esta pasta.\nApproval, rejection or pending state. Only approved items are applied.|Estado de aprovação, rejeição ou pendente. Somente itens aprovados são aplicados.\nModel filename. Folder packages are handled as one unit.|Nome do arquivo do modelo. Pacotes de pasta são tratados como uma unidade.\nRole such as LoRA or embedding. Distinguish unknown or inferred types.|Função como LoRA ou embedding. Diferencie tipos desconhecidos ou inferidos.\nBase model family from the source. Same family does not guarantee compatibility.|Família do modelo base informada pela origem. A mesma família não garante compatibilidade.\nSource match, reviewed rule, structural inference or unknown evidence.|Correspondência da origem, regra conferida, inferência de estrutura ou evidência desconhecida.\nFile location when scanned.|Local do arquivo no momento da verificação.\nProposed destination. Editable before applying.|Destino proposto. Pode ser editado antes de aplicar.\n'
for line in DATA.splitlines():
    if '|' in line:
        source, target = line.split('|', 1)
        TRANSLATIONS[source] = target

TRANSLATIONS['This operation changes the locations of models and related data, and creates folders or hard links. ComfyUI and existing workflows may need updated references.\n\nBefore any change, the original paths, destinations and affected file state are recorded in history. To undo, open the rightmost History / Restore tab, select the date, and click Undo selected history.\n\nThis is a placement record, not a copy of the model contents. Restoration stops if moved files were edited or deleted, or if another file occupies the original path.\n\nContinue?'] = 'Esta operação altera os locais de modelos e dados relacionados e cria pastas ou links físicos. As referências no ComfyUI e nos fluxos existentes podem precisar de atualização.\n\nAntes de qualquer alteração, os caminhos originais, destinos e estado dos arquivos são registrados no histórico. Para desfazer, abra Histórico / Restaurar, selecione a data e clique em Desfazer histórico selecionado.\n\nEste registro guarda os locais, não uma cópia do conteúdo dos modelos. A restauração é interrompida se os arquivos foram editados ou excluídos ou se o caminho original já está ocupado.\n\nContinuar?'

def register(catalog, languages):
    languages['pt-BR'] = 'Português (Brasil)'
    for value in catalog['en'].values():
        if '\n' in value and value not in TRANSLATIONS and all(line in TRANSLATIONS for line in value.splitlines()):
            TRANSLATIONS[value] = '\n'.join(TRANSLATIONS[line] for line in value.splitlines())
    catalog['pt-BR'] = {**catalog.get('pt-BR',{}), **{key: TRANSLATIONS[value] for key, value in catalog['en'].items() if value in TRANSLATIONS}}
    # English UI literals are also localized; About and Image to Text stay English.
    catalog['pt-BR'].update(TRANSLATIONS)
