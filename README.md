# Model Library Organizer

**Windows · v1.0.0 · MIT license**

**English** · [日本語](README.JP.md) · [简体中文](README.ZH.md)

[Download for Windows](https://github.com/Take-No-Break/ModelLibraryOrganizer/releases/tag/v1.0.0) · [Interface preview](#organize-a-model-library) · [Report an issue](https://github.com/Take-No-Break/ModelLibraryOrganizer/issues)

Browse your downloaded LoRA and checkpoint models, see available preview images, and retrieve published trigger words and descriptions through public APIs without opening each source website. Model Library Organizer also identifies and organizes files, creates model source notes, prepares Image to Text workflows, and edits training captions and tags.

## What you can do

| Area | Features |
| --- | --- |
| [Models](#organize-a-model-library) | Recursively scan supported files; calculate full SHA-256; match public sources; inspect model types and families; review unidentified files. |
| [Organization](#organize-a-model-library) | Choose type/category or provider → creator → type → family layouts; review moves and hardlinks; create required folders when approved changes run. |
| [Model inspection](#preview-a-model) | View available descriptions, trigger words, source links and preview images inside the app; resize preview panes. |
| [Compatibility](#compatibility) | Select one LoRA and compare its family with all identified checkpoint/diffusion models in the chosen folder; record manual results for individual pairs. |
| [Source TXT](#model-source-txt) | Create readable model information files with available trigger words, source, type, family and hash; choose optional fields or update existing generated notes with backups. |
| [Image to Text](#image-to-text) | Export Combined or Expanded ComfyUI workflows, install/update required custom nodes, or run against a local ComfyUI server. |
| [Edit Text](#edit-text) | Inspect image/TXT pairs or standalone TXT; edit individual captions or bulk prepend, append, remove, replace and wrap text. |
| [Tag editor](#tag-editor) | Browse image thumbnails and compact tags; search, filter, sort tag counts, select tags, insert/remove tags in bulk and save reviewed edits. |
| [Results and recovery](#results-history-and-restore) | Review saved operation results, detect duplicates by SHA-256, inspect move history, restore eligible changes and repair supported workflow references. |

**LoRA / Checkpoint training preparation:** Image to Text, Edit Text and Tag editor prepare and edit dataset captions. Source TXT documents downloaded models. The app prepares training data; it does not train LoRA/Embedding models or generate images itself.

Use an AI assistant to guide you through this repository or README: [Complete control reference](docs/CONTROLS.md).

## Install on Windows

1. Download and extract the entire **Windows-x64.zip** from Releases.
2. Run `Install.cmd`, or launch `ModelLibraryOrganizer.exe` directly. Keep `_internal` beside the EXE.
3. Select your own folders. Model weights, personal paths, histories and ComfyUI are not included.

`Uninstall.cmd` is included. It removes recorded application files while leaving model libraries and user data. **The uninstaller has not been executed or tested.** This release has local tests and packaged startup verification; a separate-PC or virtual-machine test is not claimed.

## Organize a model library

![Models: file types, families and proposed destinations](docs/screenshots/models.jpg)


1. Choose a **scan folder** containing downloaded models. Subfolders are included.
2. Choose the destination **models folder**, such as `ComfyUI/models` or your configured shared models directory. Select the actual models directory, rather than the ComfyUI application root.
3. Click **Scan all**, choose a layout and review the proposals. Scanning records an inventory of original paths but does not move files.
4. Approve, reject or defer proposed changes, then use **Review and organize proposed moves**. The final confirmation explains the changes; a move journal is saved before execution.

Example layouts (additional purpose folders may appear when metadata is available):

```text
models/loras/Character/Pony/example.safetensors
models/Civitai/ExampleCreator/loras/Pony/example.safetensors
```

Family folders are derived from returned source metadata, not a fixed set of bundled folders. A newly reported family can produce a new folder proposal. The folder is created only when approved changes execute. Unknown families are not guessed: proposals may use a type folder or `Unknown`, or remain for review. Correctly placed files can retain their existing locations.

Files are not deleted to clean up a layout. Only eligible empty source folders are removed. Conflicting destinations are flagged for review.

### How identification works

The app calculates the full SHA-256 of each supported file. Civitai lookup uses its public hash API. Hugging Face lookup searches filename candidates and verifies public SHA-256; a matching filename alone is not a verified match. Cached results, tensor names/shapes and embedded metadata also help identify file roles.

Recognized roles include LoRA, checkpoints, VAE, Embeddings, supported ControlNet structures, style adapters, model patches and supported caption-model bundles. Existing ComfyUI categories can be preserved, but support for a folder name does not mean every possible model in it can be identified. Reliable per-file tensor structure takes priority over the overall category of a distribution page. Unidentified or conflicting files remain available for review.

SeaArt and Tensor.Art are not automatically queried: this app has no verified reverse-hash API integration for them. Models whose source cannot be identified may need review or organization under `Not Found`. They are not automatically moved there solely because a source lookup failed; existing recognized types and locations can be preserved, and you can choose a destination manually. Add a known source URL manually. A source match does not prove runtime compatibility.

### Preview a model

![Preview: model list, source information and image](docs/screenshots/preview.jpg)

1. Open **Model inspection → Preview** after scanning.
2. Select a LoRA, checkpoint or another identified model in the list.
3. Read available trigger words, type, family and source descriptions below the list.
4. View the preview image on the right. Open the source link only when you need the original page.

Published metadata must be available from a supported source; unavailable trigger words or images are not invented.

### Compatibility

1. Open **Model inspection → Compatibility** and choose checkpoint and LoRA folders.
2. Scan those folders, then select one LoRA.
3. Compare it with all identified checkpoints: **green** = same family, **yellow** = related SDXL families, **gray** = different or unknown.
4. Click a row to record your own loading/generation test result.

Colors are metadata estimates, not generation tests or guarantees. Each computer needs its own folder selection and scans.

### Model source TXT

1. Scan the models, then select the models you want to document.
2. Open **Text editor → Model source TXT** to choose optional fields. Identity and available published trigger words are always included.
3. Click **Create source TXT** to create missing `model-name.safetensors.source.txt` notes beside the models.
4. Use **Update readable TXT** only to rebuild existing app-generated notes with backups.

With no selection, creation uses eligible list items. Existing notes are skipped. Labels are English; descriptions retain their source language. These notes document models, not image training captions. Model weights are unchanged.

## LoRA / Checkpoint training data preparation

Create and edit image captions for LoRA or checkpoint training datasets. Image to Text prepares captions, while Edit Text and Tag editor let you adjust trigger words and other text for your trainer. The app prepares data; it does not train models. Model source TXT is a separate information note about downloaded models.

### Image to Text

The adapters currently implemented in this project are **PixAI, JoyCaption, CL Tagger and Taggerine**; this is not a list of every Image to Text model available. Select your model directory in **Image to Text model folder**, then select the matching adapter in **Model**. Use a complete model bundle with the files required by that adapter. A standalone or arbitrary `.safetensors` file is not sufficient. Other architectures need a compatible adapter implementation and may fail to load. Threshold settings are adapter-specific and may not apply to a different model. Weights and model dependencies must be installed separately.

![Image to Text: model settings and workflow preview](docs/screenshots/image-to-text.jpg)

### Set up custom nodes once

1. Click **Install / update custom nodes**.
2. Click **Detect**, or browse to the `custom_nodes` folder of the ComfyUI instance you use.
3. Click **Install / update**, install any missing dependencies with ComfyUI's Python, and restart ComfyUI.
4. Enter the running local ComfyUI URL and click **Check connection**.

The same node bundle works with all four supported adapters and both template formats. Changing paths, model selection or template format does not require reinstalling it. Update it when node code changes. The app does not start or restart ComfyUI.

Manual ZIP setup: extract **Save required custom nodes** so the entry file is at `ComfyUI/custom_nodes/model_library_organizer_bridge/__init__.py`. For step-by-step troubleshooting, see [custom-node setup](docs/CONTROLS.md#custom-node-setup).

### Run or export

1. Choose the image folder, model adapter and complete model folder.
2. Set the relevant thresholds or prompt. Check the automatic save location.
3. For direct execution, click **Check connection**, then **Run in ComfyUI and save image hardlinks + TXT**.
4. Alternatively, choose **Combined** or **Expanded**, enable **Save matching TXT in ComfyUI** if needed, and click **Save ComfyUI workflow template**. Open that JSON in ComfyUI and run it there.

**Workflow template** = editable visual graph. **Required custom nodes** = code that makes those nodes work. Exporting either file alone does not analyze images or save captions.

Outputs go into an adapter-named subfolder inside the selected image folder:

```text
Images/
├─ example.png              # original image
└─ PixAI/
   ├─ example.png           # hardlink to the original image
   └─ example.txt           # generated caption
```

Other adapters use `JoyCaption`, `CL-Tagger` or `Taggerine`. Original images stay in place. Hardlinks require the same filesystem volume; editing a hardlinked image affects the same underlying file. Existing captions are skipped and conflicting images are protected. Recursive scans exclude these generated output folders.

Old exported workflows with an empty output setting may write TXT beside the original images. Update the custom nodes, restart ComfyUI and export a new template to use the subfolder layout.

## Edit Text

![Text editor: image list, preview and editable caption](docs/screenshots/text-editor.jpg)

1. Choose a dataset folder; its image/TXT list loads automatically.
2. Select an image/TXT pair, preview the image and edit the caption on the right.
3. For batch edits, select several files and choose wrap, prepend, append, remove or replace, then **Preview changes**.
4. Save the current TXT or approve the batch review. Originals are backed up; conflicting external edits block saving.

### Tag editor

![Tag editor: thumbnails, tag statistics and caption tags](docs/screenshots/tag-editor.jpg)

1. Click **Open Folder** and browse the thumbnails on the left.
2. Sort tag counts, search or select a tag to filter matching images.
3. Click caption tags to edit them, or use bulk insertion/removal with the **Selected / Filtered / All** scope.
4. Click **Save All**, review the changes and confirm saving.

Counts show how many caption files use a tag, not AI confidence. Category filters use local keyword rules. Edits remain pending until saved. Wrapping a term in `< >` does not train an Embedding; match your trainer's token settings.

## Results, history and restore

1. Open **Results** and select a report to revisit scans, exports or caption changes.
2. Use **History / Restore** to inspect recorded file moves.
3. Select an eligible history record, or open its JSON, then choose **Restore this layout**.
4. Restore the newest operation first and review the confirmation.

**A scan inventory without a linked move journal cannot restore locations.** Changed/deleted files or path conflicts may block restoration. History is not a model-content backup and cannot undo external actions. [Tools and recovery details](docs/CONTROLS.md#tools) explain duplicate checks and workflow-reference repair.

## Offline mode and privacy

- **Online lookup:** sends hashes and HF search filenames, not model weights or dataset images.
- **Fully offline:** blocks external source, preview and update requests. Local tools, cached data and separately running local ComfyUI remain usable.
- **Reports and updates:** logs are never submitted automatically; review them before sharing. Update checks open release pages and never install updates.

See the [support controls](docs/CONTROLS.md#about-support-and-updates) for details.

## Develop and contribute

```powershell
python -m pip install -r requirements.txt
python scripts/run_tests.py
python -m pip install pyinstaller==6.22.3
python -m PyInstaller --noconfirm ModelLibraryOrganizer.spec
```

Windows CI uses Python 3.12. The prepared local Windows release was built using Python 3.14.5. Test file organization on disposable data. See [Contributing](CONTRIBUTING.md), [Security](SECURITY.md) and [release preparation](RELEASE_PREPARATION.md).

## License and acknowledgments

Application source is provided under the [MIT license](LICENSE). Contributions and improvements are welcome; MIT does not require contributors to submit modifications upstream. Model weights and third-party dependencies retain their own licenses and notices.

The Tag editor interface was developed with [unaya-git/TagFilter](https://github.com/unaya-git/TagFilter) as a design reference. This acknowledgment does not imply endorsement or affiliation.
