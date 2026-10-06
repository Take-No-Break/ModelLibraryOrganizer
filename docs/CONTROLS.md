# Complete control reference

Model Library Organizer **1.0.0**. [Return to the illustrated README](../README.md).

This guide describes the visible controls and dialogs, including what they change on disk. Button translations can differ; English names identify the equivalent action. AI assistants can follow these headings to explain a specific task. Do not infer that a proposed move, exported workflow or pending edit has already executed.

## Navigation and common controls

| Control | What it does |
| --- | --- |
| Results | Opens saved operation reports. |
| Models | Opens file identification and organization proposals. |
| Model inspection → Preview | Shows model information and available preview images. |
| Model inspection → Compatibility | Compares a selected LoRA with identified checkpoint candidates. |
| Training data → Image to Text | Configures local ComfyUI analysis and workflow/node exports. |
| Training data → Text editor | Opens image training captions or model source-note settings. |
| Training data → Tag editor | Opens thumbnail browsing and tag editing. |
| Tools | Opens duplicate and workflow-reference tools. |
| About | Opens overview, guides, privacy and support/update settings. |
| History / Restore | Opens scan inventories and move journals. |
| Language | Changes interface/guide language, after checking pending work and unsaved edits. |
| Dark / Classic | Changes the saved appearance. No other accent selector is provided. |
| Progress and status | Shows operation progress and completion/error status; hover over shortened status for more text. |
| Browse / folder entry | Chooses or enters the folder used by the adjacent feature. Paths belong to this computer. |
| Scrollbars / pane dividers | Scroll content or resize adjacent panes. |
| Ctrl / Shift selection | Selects multiple files/images where supported. |
| Text right-click menu | Copy, paste, cut or select all in editable text fields; read-only fields remain read-only. |
| Source URL | Opens the original page in a browser when available. |

## Models

### Scan and identify

1. Choose the downloaded-file **Scan folder**.
2. Choose the destination **models folder**, such as `ComfyUI/models` or a configured shared models root.
3. Choose the source and click **Scan all**.
4. Read the table, then inspect models or review proposed changes.

| Control | What it does |
| --- | --- |
| Scan folder | Root to enumerate recursively; it is not necessarily the destination. |
| Destination models folder | Root under which approved destinations and links must stay. |
| Source selector | Combined Civitai + HF lookup, a selected Civitai host, or Hugging Face lookup. |
| Public API lookup | Allows new public-source matching. Off uses local structure and cached metadata. Fully offline additionally blocks previews and updates. |
| Scan all | Records original paths, calculates hashes and proposes classification/destinations. Does not move models. |
| Stop scan | Requests cancellation of the current scan. |
| Scan new / changed | Uses incremental information to inspect new or changed files. |
| Reset scan cache | Resets incremental scan tracking so files are reconsidered; does not delete models. |
| Edit destination / links | Opens a proposal editor for one selected model. |
| Preview | Opens the selected model in Model inspection → Preview. |
| Filter | All, proposed moves, review/errors, unidentified, approved or rejected. Returning to Models resets it to All. |
| Model row | Selects a file and displays its details. Decision, type, family and evidence have different meanings. |
| Right-click row → Copy current location / destination | Copies the full path, even when the table shows a relative path. |
| Right-click row → Open folder | Opens that path's folder if it exists. A proposed new folder may not exist yet. |
| Right-click row → Open source | Opens its known distribution page. |
| Create source TXT | Creates missing model source notes for the selected models, or eligible list items if none selected. |
| Review proposed moves | Reviews actionable proposals, then proceeds to final execution confirmation. |

### Organization and confirmation dialogs

| Control | What it does |
| --- | --- |
| Type/category layout | Proposes model-type folders with available purpose/family subfolders. |
| Provider / creator / type / family layout | Proposes a source/creator hierarchy using available verified metadata. Unknown creators/types stay for review. ComfyUI search configuration may need to include the new layout. |
| Continue / Cancel in layout dialog | Starts the requested scan or cancels it. |
| Destination folder in editor | Sets the proposed folder inside the selected models root. |
| Type selector in editor | Sets the proposed role and its type folder. |
| Additional hardlink folders | Semicolon-separated relative folders for additional links inside the models root. |
| Set this destination | Saves the proposal only; does not move the file. |
| Yes / Approve in proposal review | Marks this move/link proposal as approved. |
| No in proposal review | Rejects this proposal for the current operation. |
| Later / Pending | Leaves the proposal undecided. |
| Review the rest later | Closes proposal review without executing the remaining proposals. |
| New folders shown in green | Identifies directories that approved execution would create. |
| Move-warning Yes / No | Continues toward execution or cancels it. |
| Do not show this warning again | Hides the preliminary warning; recovery journaling and final confirmation remain. |
| Final execution confirmation | Applies approved moves/links after a recovery journal is written. Cancel leaves files unchanged. |

Folder names are derived from metadata; new reported families can create new folder proposals. Scanning alone creates no organization folders. Empty old directories may be removed after recorded moves, but files inside them are not deleted.

## Model inspection

### Preview

| Control | What it does |
| --- | --- |
| Folder entry / Browse | Chooses a collection to inspect. |
| Scan this folder | Performs source identification for that folder. |
| Current scan results | Populates the preview list from the current Models results. |
| Model list | Selects a model; the family/type column distinguishes LoRA, checkpoint, VAE and other recognized roles. |
| Information pane | Displays available identity, published trigger words, descriptions and evidence. Unavailable fields are labeled accordingly. |
| Image pane | Shows an available general-audience source image; no image is saved beside the model. |
| Horizontal / vertical dividers | Resizes the list, information and image areas. |

API metadata can be missing, restricted or unavailable. No trigger words or preview images are fabricated.

### Compatibility

1. Choose checkpoint and LoRA folders and scan them.
2. Select one LoRA.
3. Read all identified checkpoint candidates and their automatic family estimates.
4. Select a checkpoint row to record your own test result.

| Control | What it does |
| --- | --- |
| Checkpoint folder / LoRA folder | Limits candidates to the selected folders, including subfolders. Blank entries use known scan history. |
| Scan selected folders | Performs an additional read-only identification scan for these folders. |
| Refresh scanned models | Rebuilds candidates from current results and this computer's saved catalog. |
| LoRA selector | Compares one LoRA against every available checkpoint/diffusion candidate. |
| Checkpoint row | Selects the pair whose assessment you want to record. |
| Automatic assessment | Uses known family metadata: same green, related SDXL yellow, different/unknown gray. |
| Worked / Needs adjustment / Failed | Records a manual pair-specific evaluation from your own experience. |
| Notes | Adds context to that evaluation. |
| Save assessment | Saves this pair's rating and note locally. No image generation test is run. |

## Model source TXT

Model information notes describe weights. Image training TXT describes images. These are separate features.

| Control | What it does |
| --- | --- |
| Model source TXT subtab | Opens note-generation settings. Select target models in Models first. |
| Create source TXT | Writes missing `model-filename.source.txt`; skips existing notes. Published trigger words and basic identity are always included when available. |
| Update readable TXT | Rebuilds selected app-generated notes with backups. Handwritten notes are not replaced; model weights are unchanged. |
| Description | Includes available source descriptions. |
| Public metadata | Includes available public model/version details. |
| Lookup results | Includes source-query/matching results. |
| File metadata | Includes available embedded file metadata. |

Options save locally. English field labels are used regardless of interface language. Information that the source/file does not contain cannot be recovered automatically.

## Image to Text

### Settings and actions

| Control | What it does |
| --- | --- |
| Image folder | Selects original images to analyze. |
| Image to Text model folder | Selects a complete bundle compatible with the chosen adapter. Weights alone may be insufficient. |
| Model selector | PixAI, JoyCaption, CL Tagger or Taggerine. Arbitrary other models are not automatically supported. |
| Auto / CPU | Chooses the adapter's device setting. GPU/runtime availability depends on ComfyUI. |
| Subfolders | Includes nested source images, excluding generated adapter output folders. |
| Save location (automatic) | Shows the adapter-named subfolder inside the image folder. It is not a manual output field. |
| Running ComfyUI URL | Local server address, usually `http://127.0.0.1:8188`. The app does not launch or restart the server. |
| Check connection | Checks the local server and whether required node classes are registered. |
| PixAI thresholds | Separate 0–1 thresholds for general, character, style, copyright, meta and rating tags. Apply only to PixAI. |
| CL Tagger / Taggerine threshold | Sets that adapter's inclusion threshold. |
| JoyCaption instruction / max tokens | Sets the requested description and response limit for JoyCaption. |
| Run in ComfyUI and save image hardlinks + TXT | Submits local analysis; saves complete returned captions and hardlinks after success. Existing TXT is skipped. |
| Save matching TXT in ComfyUI | Enables saving in exported templates. Direct app execution already saves successful outputs. |
| Combined / Expanded | Chooses a compact visual graph or a graph exposing individual stages. Both use the same node bundle. |
| Workflow preview | Shows the visual graph structure for the selected format. |
| Save ComfyUI workflow template | Saves an editable workflow JSON to open and execute in ComfyUI. Does not run analysis by itself. |
| Save required custom nodes | Saves a ZIP of node implementation files for manual installation. Not a model or workflow JSON. |
| Install / update custom nodes | Opens direct node setup for the actual ComfyUI instance. |

Paths, thresholds and template options save automatically on this computer. Only settings for the selected adapter apply. Output folders are `PixAI`, `JoyCaption`, `CL-Tagger` or `Taggerine`. They contain original-image hardlinks and same-name TXT. Hardlinks require the same filesystem volume and share the original image data; existing captions and conflicting image files are protected.

### Custom-node setup

1. Open **Install / update custom nodes**.
2. Click **Detect** and select the correct running installation, or **Browse** to `ComfyUI/custom_nodes`.
3. Click **Install / update**. Install missing requirements in that ComfyUI instance's Python environment if needed.
4. Restart ComfyUI and click **Check connection** in the app.

| Dialog control | What it does |
| --- | --- |
| Directory field / detected dropdown | Shows the selected ComfyUI root or custom_nodes directory. Confirm it belongs to the instance you use. |
| Detect | Lists candidates from saved settings and known/running installations; does not scan every drive. |
| Browse | Lets you select the actual directory manually. |
| Install / update | Copies the bundled nodes into `custom_nodes/model_library_organizer_bridge`; changed managed files are backed up. Does not install weights, pip dependencies or restart ComfyUI. |
| Close | Closes setup. |

For manual ZIP installation, ensure the entry file is directly at `ComfyUI/custom_nodes/model_library_organizer_bridge/__init__.py`, not inside another nested package directory. Install its `requirements.txt` with ComfyUI's own Python. See [package guidance](../comfy_bridge/README.md).

Changing images, a supported model or Combined/Expanded does not require another node installation. Update when node code changes, or install separately for another ComfyUI instance. A missing-node message usually means the wrong directory, nested extraction, an import/dependency error or a missing restart. Inspect ComfyUI's startup log; connection success alone does not establish that model weights can load.

## Edit Text

1. Choose a folder; the list loads automatically.
2. Select an image/TXT pair and edit the caption.
3. Save that caption, or choose multiple files and preview a bulk edit.
4. Approve reviewed changes; originals are backed up.

| Control | What it does |
| --- | --- |
| Images and training TXT subtab | Opens the caption editor. Also supports standalone TXT without an image. |
| Folder / Browse / Subfolders | Loads matching image/TXT entries; including subfolders is optional. |
| Select all | Selects every caption target in the list. |
| Image/TXT row | Loads its caption into the editor and previews the corresponding image. |
| Caption field | Edits the pending text; selecting another entry checks unsaved changes. |
| Save current TXT | Writes this caption with conflict checks and an original backup. |
| Undo caption changes | Selects a saved caption-change backup and attempts restoration with safety checks. Separate from model move history. |
| Wrap in < > | Wraps the matching term for trainer token/placeholder conventions. Does not train an Embedding. |
| Prepend / Append | Adds text at the beginning or end. |
| Remove | Removes matching terms. |
| Replace / Replacement field | Changes matching terms to the supplied replacement. |
| Target word / words to add | Supplies the operation's matching/insertion text. |
| Exact tag / Word boundary | Chooses comma-tag matching or word-boundary matching. |
| Preview changes | Opens before/after text for the selected targets. |
| Save these changes in review | Applies the displayed caption changes with backups and conflict checks. Closing the review does not save. |
| Unsaved-edit Yes / No / Cancel | Saves, discards pending editor content or cancels navigation. |

## Tag editor

| Control | What it does |
| --- | --- |
| Open Folder / path entry | Loads images and captions from a dataset. |
| Save All | Opens a before/after review of pending tag changes; originals update only after review confirmation. |
| Subfolders | Includes nested dataset entries. |
| Reload | Reloads captions from disk, checking pending changes first. |
| Select All | Selects all image entries. |
| Thumbnail sidebar | Selects images; Ctrl/Shift supports multiple selection. |
| Sidebar search | Filters entries by filename. |
| By count / By name | Sorts the statistics tags by caption-file frequency or name. |
| Find | Searches statistics tags. |
| Statistics tag | Filters images to captions containing that tag. The badge counts files, not AI confidence. |
| Delete Selected | Stages removal of the currently chosen statistics tag within the selected edit scope. |
| All / category buttons | Shows tags matching a local keyword category: Face, Body, Outfit, Pose, BG, Style, Expr, Chara, Title, Artist or Other. |
| Bulk Insert field / Insert | Stages tag addition within the selected scope, excluding registered unwanted tags. |
| Remove | Stages removal of entered tags within the selected scope. |
| Selected / Filtered / All | Limits bulk edits to selected images, currently filtered images or the whole loaded dataset. |
| Unwanted Tag / Register | Records an exact unwanted tag for future insert filtering. Registration alone does not remove existing caption tags. |
| Remove Unwanted | Stages removal of registered unwanted tags within the chosen scope. |
| Unwanted tag × | Unregisters that unwanted-tag rule. |
| Delete Category | Stages removal of tags in the selected category within the chosen scope. |
| Delete All Tags | Stages clearing captions within the chosen scope; does not delete images. |
| Caption tag | Opens inline editing. Enter applies to pending text; Escape cancels. |
| Caption tag × | Stages removal of that tag from that caption. |
| Right-click tag → Set category | Saves a local category override; it is not image recognition. |
| Copy view tags | Copies the displayed caption tags. |
| Clear filter | Clears the statistics-tag image filter. Other search/category settings are separate. |
| Yellow pane dividers | Adjusts sidebar width and upper/lower pane sizes. |

This tab edits existing captions; it does not auto-tag images or run inference. Model source `.source.txt` notes are excluded from training tag statistics. All destructive caption edits remain pending until explicit save.

## Results

| Control | What it does |
| --- | --- |
| Report row | Shows the stored report for that scan, export, caption operation or other completed action. |
| Identification results | Summarizes model roles, evidence and unresolved files from current scan results. |
| Duplicate-group row | Expands paths, physical copies and possible extra-copy space for that SHA-256 group. |
| Report URL | Opens a known linked page. |

Completion popups inform you of success without forcing a tab change. Reports are local and are different from recovery journals.

## Tools

| Control | What it does |
| --- | --- |
| Detect duplicates | Chooses a folder and groups identical contents by SHA-256. Distinguishes hardlinks from independent copies. Does not delete either. |
| Check workflow references | Chooses supported ComfyUI JSON workflows and reviews repairs for model paths changed by recorded moves. |
| Repair selected JSON only | Applies selected supported reference repairs with workflow backups. Custom nodes may use unsupported path conventions. |
| Identification results | Opens the current identification summary. |
| Network diagnostics / support logs | Opens a report for local review/export. Does not send it automatically. |

## History and restore

| Control | What it does |
| --- | --- |
| History row | Shows scan inventory or recorded move details and restore eligibility. |
| Open history JSON | Imports a scan inventory or move journal for inspection. |
| Restore this layout | Restores an eligible journal or linked moves after confirmation. Disabled when there are no restorable operations, required journals are missing or the record was already restored. |
| Show warning before moving | Restores or disables the preliminary move warning. Final confirmation and journaling remain. |
| Confirm restoration | Attempts recorded reversal; file changes or conflicts can block it. |

A scan inventory alone contains paths, not executed moves. It needs linked move journals to restore. Undo newest operations first. No model-content backup is created, and unrelated external changes cannot be undone.

## About, support and updates

| Control | What it does |
| --- | --- |
| Overview / Identification and organization / Offline and privacy / Support & Updates / About | Opens the corresponding guide section. |
| Fully offline | Blocks external API, preview and update requests; local tools and local ComfyUI remain available. Turning it on also disables new public API lookups. |
| Network diagnostics / support logs | Shows a sanitized local diagnostic report. |
| Save diagnostic log | Exports JSON for you to inspect/share yourself; no automatic upload. |
| Open support page | Opens repository Issues or the configured HTTPS support page. Does not submit a report. |
| GitHub repository | Opens the configured repository. |
| Check updates at startup | Enables optional startup checks; off by default. Does not install updates. |
| Check updates | Reads the newest stable GitHub Release when online. Drafts and previews are ignored. |
| Open release page | Opens an available release for manual review/download. |
| Update / support settings | Configures the repository and optional support URL. |
| Save settings in publisher dialog | Saves publication/support destinations for this computer. |
| Export distributor settings | Writes `publisher.json` to include beside the EXE when distributing the app. |

Public lookup sends hashes and HF search filenames, not weights or dataset images. Diagnostic exports omit sensitive path/model details, but inspect every attachment before posting publicly. Model lists and caches are not sanitized diagnostic reports.

## Installation scripts

1. Extract the whole Windows ZIP.
2. Run `Install.cmd`, or run the EXE with `_internal` beside it.
3. Choose your own model/dataset folders on that computer.
4. Use `Uninstall.cmd` only when you intend to remove recorded application files.

The uninstaller is included but has not been executed or tested. Model libraries and local user data are retained by its intended behavior. No separate-PC or VM verification is claimed.
