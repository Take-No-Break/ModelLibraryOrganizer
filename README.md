# Model Library Organizer

**Windows preview · v1.0.32 · MIT license**

Downloaded too many models to remember what they are, where they came from, or where they belong? Model Library Organizer helps inspect a ComfyUI model collection, identify sources, review folder layouts, and organize files. It also prepares Image to Text workflows and lets you edit training captions.

[Download the Windows preview](https://github.com/Take-No-Break/ModelLibraryOrganizer/releases/tag/v1.0.32) · [Report an issue](https://github.com/Take-No-Break/ModelLibraryOrganizer/issues)

## What you can do

| Area | Features |
| --- | --- |
| Models | Recursively scan supported files; calculate full SHA-256; match public sources; inspect model types and families; review unidentified files. |
| Organization | Choose type/category or provider → creator → type → family layouts; review moves and hardlinks; create required folders when approved changes run. |
| Model inspection | View available descriptions, trigger words, source links and preview images inside the app; resize preview panes. |
| Compatibility | Select one LoRA and compare its family with all identified checkpoint/diffusion models in the chosen folder; record manual results for individual pairs. |
| Source TXT | Create readable model information files with available trigger words, source, type, family and hash; choose optional fields or update existing generated notes with backups. |
| Image to Text | Export Combined or Expanded ComfyUI workflows, install/update required custom nodes, or run against a local ComfyUI server. |
| Edit Text | Inspect image/TXT pairs or standalone TXT; edit individual captions or bulk prepend, append, remove, replace and wrap text. |
| Tag editor | Browse image thumbnails and compact tags; search, filter, sort tag counts, select tags, insert/remove tags in bulk and save reviewed edits. |
| Results and recovery | Review saved operation results, detect duplicates by SHA-256, inspect move history, restore eligible changes and repair supported workflow references. |
| Appearance and support | Dark/Classic themes, resizable panels, progress display, multilingual guides, local diagnostic reports and optional update checks. |

The app prepares training data; it does not train LoRA/Embedding models or generate images itself.

## Install on Windows

1. Download and extract the entire **Windows-x64-Preview.zip** from Releases.
2. Run `Install.cmd`, or launch `ModelLibraryOrganizer.exe` directly. Keep `_internal` beside the EXE.
3. Select your own folders. Model weights, personal paths, histories and ComfyUI are not included.

`Uninstall.cmd` is included. It removes recorded application files while leaving model libraries and user data. **The uninstaller has not been executed or tested.** This preview has local tests and packaged startup verification; a separate-PC or virtual-machine test is not claimed.

## Organize a model library

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

SeaArt and Tensor.Art are not automatically queried: this app has no verified reverse-hash API integration for them. Add a known source URL manually. A source match does not prove runtime compatibility.

### Compatibility

Choose checkpoint and LoRA folders and scan them, then select a LoRA. The table compares it with every identified checkpoint/diffusion model within the selected checkpoint folder, including subfolders:

- **Green:** same known family.
- **Yellow:** related SDXL families.
- **Gray:** different or unknown families.

These are metadata-based estimates, not actual loading or generation tests. Record successful use, required adjustments or failure separately for each pair. A new computer needs its own folder selection and scans; the app does not know where another user's checkpoints are stored.

### Model source TXT

After scanning, **Create source TXT** writes `model-name.safetensors.source.txt` beside the model. With no selection, it uses eligible list items, excluding errors and rejected items. It includes available identity information and published trigger words; optional sections include descriptions and metadata. Field labels are always English. Descriptions retain their source language.

Creation skips existing files. **Update readable TXT** rebuilds the same generated note with an original backup in application data. Neither action changes model weights. These model information notes are separate from image training captions.

## Image to Text

Supported adapters: **PixAI, JoyCaption, CL Tagger and Taggerine**. Choose the appropriate complete model folder, not just an arbitrary `.safetensors` file. Weights and model dependencies must be installed separately; arbitrary Image to Text models are not supported automatically.

### Set up custom nodes

1. Open **Install / update custom nodes** in Image to Text.
2. Detect or browse to the `custom_nodes` directory of the ComfyUI instance you actually use.
3. Install the bundle and restart ComfyUI. Install missing requirements with that instance's Python environment when necessary.
4. Check the connection to your running local ComfyUI server, usually `http://127.0.0.1:8188`.

The bundle is shared by all supported adapters and Combined/Expanded templates. Changing image paths, supported model selection or template format does not require reinstalling it. Update it when the app's node implementation changes or install it separately for another ComfyUI instance. The app does not automatically launch or restart ComfyUI.

For manual ZIP setup, extract the node package so `__init__.py` is directly inside:

```text
ComfyUI/custom_nodes/model_library_organizer_bridge/__init__.py
```

Do not leave it nested inside another ZIP extraction folder. See [node setup details](comfy_bridge/README.md).

### Run or export

Select the image folder, adapter/model folder and relevant thresholds or prompt settings.

- **Run in ComfyUI and save:** submits analysis to the running local server, then saves completed captions and image hardlinks.
- **Save ComfyUI Workflow Template:** exports the visual graph for opening in ComfyUI. Combined uses fewer nodes; Expanded exposes individual processing steps.
- **Save Required Custom Nodes:** exports the implementation package for manual setup, not another workflow.

For exported templates, enable **Save matching TXT in ComfyUI** before export when you want files saved. Exporting alone does not run analysis or create captions.

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

## Edit Text and Tag editor

Open a dataset folder to view images and matching captions. Select an image or TXT to edit its text. Bulk changes can add prefixes/suffixes, remove or replace text, or wrap selected terms in `< >`. Review changes before saving; originals are backed up. External file changes prevent overwriting stale content.

The Tag editor provides a thumbnail sidebar, compact clickable tags, tag-count sorting, search, category filters, bulk insertion and unwanted-tag removal. Changes remain unsaved until saved. Tag counts reflect caption occurrence, not inference confidence scores.

Caption requirements depend on your trainer and settings. Wrapping a word in `< >` does not train an Embedding by itself; match the token/placeholder settings of your training software.

## Results, history and restore

Results stores operation reports for later review. SHA-256 duplicate checks distinguish identical content from filenames; multiple hardlinks can refer to one underlying file.

A scan-history JSON records the original inventory. **An inventory without a linked move journal cannot restore locations.** Actual organization operations write recovery journals before moving files. Open or select an eligible record in **History / Restore** to undo recorded changes, starting with the newest operation.

Changed/deleted files or destination conflicts can block restoration. History is not a backup of model contents and cannot undo unrelated external changes. Supported workflow-reference repair can adjust changed relative model paths and backs up original workflow JSON; not every custom node is supported.

## Languages and appearance

Interface/guide languages: Japanese, English, Spanish, Simplified Chinese, Traditional Chinese, Brazilian Portuguese, German and Thai. Some technical setup messages remain English. **About** and **Image to Text** retain their English names. Choose **Dark** or nostalgic gray **Classic** in appearance settings.

## Offline mode and privacy

Fully offline mode blocks external public API, preview-image and update requests. Local scans, cached data, organization, TXT editing, workflow export and separately running local ComfyUI remain available. Disabling public API lookup alone stops new source searches; it does not disable other online features.

Lookup sends hashes and, for Hugging Face search, filenames. It does not upload model weights or dataset images. Public preview images are displayed in memory. Logs stay on the device and are never submitted automatically.

Use **About → Support & Updates** to review/save a diagnostic report and open the repository or Issues. Review attachments before posting to public Issues. Optional update checks read GitHub Releases and open a newer stable release page; they do not install or execute updates. Startup checks are off by default. Preview releases are not advertised by stable update checks.

## Develop and contribute

```powershell
python -m pip install -r requirements.txt
python run_tests.py
python -m pip install pyinstaller==6.22.3
python -m PyInstaller --noconfirm ModelLibraryOrganizer.spec
```

Windows CI uses Python 3.12. The prepared local Windows preview was built using Python 3.14.5. Test file organization on disposable data. See [Contributing](CONTRIBUTING.md), [Security](SECURITY.md) and [release preparation](RELEASE_PREPARATION.md).

## License and acknowledgments

Application source is provided under the [MIT license](LICENSE). Contributions and improvements are welcome; MIT does not require contributors to submit modifications upstream. Model weights and third-party dependencies retain their own licenses and notices.

The Tag editor interface was developed with [unaya-git/TagFilter](https://github.com/unaya-git/TagFilter) as a design reference. This acknowledgment does not imply endorsement or affiliation.
