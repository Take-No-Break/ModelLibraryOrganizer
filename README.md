# Model Library Organizer 1.0.32 — Windows preview

A model library organizer for ComfyUI: inspect downloaded models, review destinations, organize files and prepare image captions.

## Install

Extract the entire Windows ZIP. Run Install.cmd or use ModelLibraryOrganizer.exe directly; keep _internal beside the EXE. Uninstall.cmd removes recorded application files and leaves model libraries and user data.

## Usage

GETTING STARTED
1. Choose the scan folder and destination models folder, then Scan all. Subfolders are included. Before scanning, original file and folder paths are recorded in scan-history JSON. Scanning does not move files.
2. Choose organization by type/category or provider / creator / type / family. Review identification and destinations. Answer Yes, No or Later for proposed moves and hard links. No changes are applied at this stage.
3. Review and organize proposed moves opens final confirmation. Only approved proposals are applied. Required folders are created then. Models already at the right destination need no move.

CONTROLS AND DISPLAY
Use Ctrl/Shift to select multiple items. Hover over a button for about 0.6 seconds for help. Table locations are relative to the selected folder; right-click to copy the full path or open its folder. Select a model in Preview to see its description and public images. Click a source URL to open it. The upper-right progress bar shows 0–100% and status. Dark / Classic are saved for the next launch.

MODEL SOURCE TXT
After scanning, Create source TXT writes model-name.safetensors.source.txt beside the model. With nothing selected, the list is used, excluding errors and rejected items. It records type, family, source, SHA256, trigger words, author description and other available information. Missing information cannot be included. Choose optional fields in Model source TXT. Field names are always English; author descriptions stay in their original language. Creation does not overwrite existing TXT. Update readable TXT rebuilds the same file and backs up the original in application data. Model weights are not updated.

IDENTIFICATION AND COMPATIBILITY
Supported files are enumerated and their full SHA256 calculated. Identical contents have the same hash even with different filenames. Unchanged files use cached results. Civitai is checked through its public hash API. Hugging Face searches filename candidates and verifies public SHA256; a matching name alone is not verification. Source metadata, classification rules, tensor names/shapes and embedded metadata help identify type and family. Unidentified models remain visible for review.
SeaArt and Tensor.Art have no automatic reverse-hash API verified for this app and are not queried automatically. Add the original page manually. Tensor.Art website search accepts @sha256 followed by a hash. Even a verified hash does not guarantee runtime success.
Compatibility compares LoRA and checkpoint source families: green for the same family, yellow for related SDXL families, gray for unknown or different families. It does not guarantee loading or output quality. Candidates come from this computer's scan history and current results. On a new PC, select checkpoint/LoRA folders and scan them. The app does not search every drive.

IMAGE TO TEXT AND EDIT TEXT
Select the image folder, analysis model and thresholds, check the connection, then run. A folder named after the model type is created inside the image folder, containing image hardlinks and matching TXT. Original images stay in place; existing TXT is not overwritten.
Use Install / update custom nodes, choose the actual ComfyUI/custom_nodes folder, confirm and install. Restart ComfyUI, then check connection. Model weights and dependencies are separate. Combined and Expanded share nodes. ZIP remains available for manual setup. Both direct execution and exported workflows can save into the automatic model-type output folder.
Edit Text displays and edits training TXT with the same name as an image, and can also edit TXT without an image. Multiple-selection prepend, append, remove, replace and wrapping in < > are reviewed before saving. Brackets alone do not train an Embedding; match OneTrainer placeholder settings. External changes stop overwriting. Supported original encodings are preserved and originals are backed up in caption-backups. Training TXT and model source TXT serve different purposes.

HISTORY AND WORKFLOW REFERENCES
Before moving, a history journal is saved and linked to the pre-scan inventory. Select a record or open its JSON in History / Restore to undo linked moves. Undo newest changes first. Edited/deleted files or path conflicts stop restoration. This is not a model-content backup or a general undo of external actions. Only unused empty folders are removed, never their files. Hiding the warning does not skip the journal or final confirmation. Workflow references repair changed ComfyUI relative paths for supported standard loaders and back up original JSON; not every custom node is supported.

OFFLINE AND PRIVACY
Fully offline mode blocks external requests for public APIs, updates and public preview images. Local scans, cached information, organization, template export, TXT editing and log saving remain available.
Turning off public API lookup stops only new source searches. Use fully offline mode to stop preview and update requests too. Public API lookup is normally enabled.
Online lookup sends hashes and filenames for HF search, not model weights or images. Previews are displayed in memory and are not saved beside models. Internal structure can suggest type/family but cannot recover unrecorded authors, source pages or trigger words. Previously collected information can be reused. Local scanning does not run an LLM or image generation AI.

SUPPORT AND DIAGNOSTICS
Diagnostic logs stay on the device and are never sent automatically. Support reports omit personal paths, model names, credentials and detailed exception messages. Review and save a report in About → Support & Updates, then share it yourself when needed. GitHub Issues are public; inspect attachments before posting. Reports can be saved without a configured support destination. You do not need to attach models, images or private files to a support request.

UPDATES AND PUBLICATION
GitHub repository in About → Support & Updates opens the project. Update checks read public GitHub Releases. Startup checks are off by default; manual checks are available. Offline mode cannot detect new releases. A newer version offers its release page, never automatic installation or execution.
Distributors include publisher.json beside the EXE and publish a stable tag and ZIP in GitHub Releases. Posting source alone does not produce an update notification. Extract the entire ZIP and keep _internal beside the EXE. Models, personal paths and histories are excluded from distribution packages.

## License and reference

MIT license. Tag editor interface reference: [unaya-git/TagFilter](https://github.com/unaya-git/TagFilter). Model licenses are separate.

## Support and updates

[Project repository](https://github.com/Take-No-Break/ModelLibraryOrganizer). Reports stay local until you choose to share them. This preview is prepared locally; no release has been published by this preparation.
