# Model Library Organizer 1.0.22 — Windows preview

## Run or install

Extract the entire ZIP. Double-click `ModelLibraryOrganizer.exe` to run it directly.
Keep `_internal` beside the EXE. Python installation is not required.
Alternatively double-click `Install.cmd`: it installs under your LocalAppData Programs
folder and creates a desktop shortcut. Administrator access is not required.
This preview is unsigned; Windows may display an unknown-publisher message.

Select your own scan folder and destination models folder. No author's model paths,
model weights or personal classification database are included.

## Tabs

- Results: persistent operation history and past model/caption results. Completion notifications appear as popups without switching tabs.
- Models: scan and review proposed changes.
- Model inspection: preview and compatibility.
- Training data: Image to Text workflow templates and TXT editing.
- Tools: duplicate detection, workflow references, networking and maintenance.
- About: guide, privacy, Support & Updates.
- History / Restore: recorded file changes and restoration.

The progress bar counts completed files for scans, duplicate checks, moves and other file operations. Preparation or
operations without intermediate counts stay at 0% until they complete. Failure or
cancellation does not mark the operation as successfully completed.

## Image to Text templates

Choose PixAI, JoyCaption, CL Tagger or Taggerine, then select the image and model folders.
Save a Combined or Expanded ComfyUI workflow JSON. The diagram previews its structure.
Combined uses fewer nodes; Expanded separates model loading, settings and analysis.
Only the selected model's settings apply. Arbitrary model architectures are not supported.
Save required custom nodes as a ZIP, extract its folder into ComfyUI/custom_nodes,
install its requirements using ComfyUI's Python environment and restart ComfyUI.
Model weights and GPU/runtime dependencies are installed separately.
Drag the workflow JSON onto ComfyUI's canvas and run it there. This app does not connect,
start ComfyUI, submit API jobs or analyze images directly.
TXT saving in ComfyUI is opt-in; existing TXT files are skipped. Each new TXT uses its
image's folder and filename. Use Text editor to review/edit the captions afterward.
Selecting a valid image/TXT folder automatically loads the list. Unsaved edits are checked.
Pages scroll vertically and horizontally when the window is small.

## File changes

Review destination proposals before executing. A warning and final confirmation
precede changes. History records affected paths before changing files. Restoration
refuses conflicts or files changed since the operation. It is not a full model backup.

## Privacy and support

Online lookup sends model hashes and sometimes search names to Civitai/Hugging Face.
Model weights and training images are not uploaded. Diagnostics are not sent
automatically. The app no longer connects to or launches ComfyUI.
Support: https://github.com/Take-No-Break/ModelLibraryOrganizer/issues
No GitHub login is needed to run the app. Posting an issue requires a GitHub account.

For a friend's test: try startup with no saved settings, an offline scan of copied
sample files, preview and TXT editing, then a small move and restore using disposable
files. Do not start by reorganizing the only copy of a valuable library.

## Verification limits

Automated local tests and isolated fresh-settings EXE startup are tested. A second
computer or Windows VM is not yet verified. The development host does not have
VirtualBox or Windows Sandbox installed. The project uses the MIT license. Application source upload and a public binary
release are still pending. Third-party runtime licenses accompany this package.

## Verification of new adapters

All four template variants are checked against registered node input/output schemas.
PixAI inference was tested previously on the development GPU. Actual inference for
JoyCaption, CL Tagger and Taggerine is not verified in this release; their model-specific
requirements and supported model formats must match the supplied adapters.

## Saved settings and exports

Image to Text remembers paths, model, device, thresholds, instructions and template
options automatically on this PC. This does not overwrite a saved workflow JSON.
The separate API request export and manual settings-save button have been removed.
Combined Civitai/Hugging Face lookup is the default in Models. The separate single-file HF lookup button has been removed. Duplicate Preview/Compatibility buttons and the CSV
export button have been removed from Tools.
Compatibility is a checkpoint/LoRA loading estimate based on known architecture
families; this app does not load a checkpoint to test it or guarantee generation quality.

## License and contributions

Our project source is provided under the MIT license; see LICENSE. You may use,
modify and redistribute it, including commercially, while retaining the required
copyright and license notice. Third-party dependencies retain their own licenses.
Downloaded model weights are not covered by our license and are not bundled.

Improvements are welcome through GitHub issues and pull requests. Returning changes
upstream is encouraged, not required by MIT. See CONTRIBUTING.md.

## Project links

Repository: https://github.com/Take-No-Break/ModelLibraryOrganizer
Support: https://github.com/Take-No-Break/ModelLibraryOrganizer/issues

About / Support & Updates points to this repository.
Update checks require a published stable GitHub Release. Preview releases do not
trigger automatic stable-update notifications.
No GitHub account token is included in the package.

Brazilian Portuguese (Português (Brasil)) is available in the language selector.
About and Image to Text retain their English names.

## Build from source

Use Python 3.12 on Windows:

    python -m pip install -r requirements.txt pyinstaller==6.22.3
    python run_tests.py
    python -m PyInstaller --noconfirm ModelLibraryOrganizer.spec

Keep the entire dist/ModelLibraryOrganizer directory together. Include the runtime
license notices and the documents listed in RELEASE_PREPARATION.md when packaging.
GitHub Actions runs Windows tests, builds the EXE and checks fresh-settings startup.


## Scan records, restore and duplicate results (1.0.8)

Starting a full scan asks for confirmation and saves a read-only inventory of file
and folder locations under LocalAppData/ModelLibraryOrganizer/scan-history. A scan
does not move files. Applying approved changes writes a separate move journal
before the first change and links it to that inventory. If recording fails, the
operation stops. History / Restore automatically lists records and shows a restore
action only when recorded moves are available. Missing move journals are reported
as requiring review. Inventory JSON is not a backup of file contents and cannot
undo external edits or deletions. Undo the newest moves first.

Saved SHA256 duplicate reports display a table with file count, physical copy count,
extra storage and hard-link/copy status. Selecting a group shows its paths and hash.
Existing saved reports use the same presentation. Detection does not delete files.

Automatic source lookup checks Civitai (with .com fallback when .red has no match)
and bounded Hugging Face filename candidates verified by SHA256. Hugging Face is
not a global reverse-hash index. SeaArt has no verified public reverse-SHA256 API
for this app. Tensor.Art's website supports @sha256 followed by the hash:
https://tensor.art/updates . A public automatic reverse-hash API has not been
verified for Tensor.Art; no automatic Tensor.Art or SeaArt query is performed.
Reports show these limitations explicitly. Add known source URLs manually when
needed. Safetensors is a file format, not a source website.

This local Windows preview was built with Python 3.14.5. Source CI uses Python 3.12.
Neither an independent PC/VM test nor code signing is claimed.

## Preview classification (1.0.9)

Preview lists show base family / file type, for example Illustrious / LoRA or SDXL / Checkpoint. Recognized embeddings, Image to Text packages and other model types keep their own type labels. Unknown classification is displayed explicitly; this display change does not expand scanning to workflow JSON files or infer model identity from filenames.

## Organization layouts (1.0.10)

Starting Scan all (or a new-only scan) opens a layout selector:

1. Existing type/category/family placement.
2. Provider / creator / type / family, for example models/Civitai/Creator/loras/Illustrious/model.safetensors.

Scan an already organized library again to propose another layout. Each layout
remembers its routing separately. Review and approve proposals before applying.
Creator names come from source metadata; Hugging Face uses the repository account
or organization namespace. Unknown creators/types stay in place for review.
ComfyUI may require model-search configuration for provider-first hierarchies.

Existing model-name.source.txt moves with its model. Applying changes creates this
TXT only if absent. Create source TXT fills missing notes for scanned models without
moving them; existing TXT is skipped. It documents identity, source URL, creator,
family, trigger words and selected metadata, not image training captions.

Only empty former source ancestors are removed after approved creator-layout moves,
within the selected scan root. No model, unrelated file, duplicate copy or old
hard-link alias is deleted. Same-name destination conflicts require review. Folder
removal is journaled and source folders are recreated during restoration.
Recognized ComfyUI UI/API workflow JSON is scanned; arbitrary JSON settings are not.
Workflows whose creator is not known remain in place in creator mode.

## Tag rankings and Tag editor (1.0.11)

Training data now has two additional tabs beside Text editor:
- Tag rankings: ranks tags by the number of caption TXT files containing them,
  with count and percentage. Repetition within a file counts once. This is usage
  frequency, not an AI confidence score; 100 of 200 TXT files means 50%.
- Tag editor: previews the selected image and its clickable tags, filters images
  by tag, removes a tag with × and adds/removes tags across selected images.

Choose a dataset folder in either tab; they share its data. The folder loads
automatically. Ranking includes existing TXT (even empty files) and pending new
caption drafts. Images without TXT and without edits are excluded from the
denominator. Model source-information .source.txt files are excluded. Comma/newline
separated tags are recognized; bracketed prompt groups remain together. It does
not invent tags or split natural-language captions into individual words.

Edits are staged in memory. Save all changes opens a before/after review and only
then writes original TXT. Existing TXT encoding is preserved and backups go to
LocalAppData/ModelLibraryOrganizer/caption-backups. External TXT changes stop saving;
the Text editor's restore action can restore its backup manifest. Closing or
reloading checks unsaved edits. Image bytes are never written. There is no direct
model inference or automatic tagging in these tabs. The existing Image to Text
workflow exporter is unchanged.

## Compact thumbnail Tag editor (1.0.12)

- The left pane is a scrollable image thumbnail strip. Ctrl/Shift selects multiple
  images. Only visible thumbnails are decoded, with a bounded image cache.
- Statistics and image tags are small rounded chips. Statistics scroll through all
  tags, sort by count/name and support text search. Click a statistics chip to
  filter images containing that exact tag. Search filenames above the thumbnails.
- Category filters: All, Face, Body, Outfit, Pose, BG, Style, Expr, Chara, Title,
  Artist and Other. These filter tags using local keyword rules, not image
  recognition. Unknown names remain Other. Right-click a chip to set its category;
  category overrides are stored in app settings, not caption TXT.
- Click an image's chip to edit its text. Enter stages the change; Esc cancels it.
  The chip's × stages removal from that image.
- Bulk Insert / Remove accepts multiple comma-separated tags. Scope Selected means
  highlighted thumbnails; Filtered means all results currently in the thumbnail
  strip; All means the entire loaded dataset. Delete category, Delete all tags and
  Remove unwanted use the same scope. Whole-category/all-tag removal asks first.
- Unwanted Tag / Register stores exact tags in a persistent list; registration
  alone does not delete existing tags. Registered tags are excluded from Bulk
  Insert. Remove unwanted explicitly stages their removal from the chosen scope.
  The registry chip's × unregisters the tag without changing captions.

All caption edits remain drafts until Save all changes and the before/after review
are confirmed. Existing encoding, conflict checks and caption backups are retained.
Changing language, switching dataset folders or closing checks unsaved drafts.
The app does not modify images or run automatic tagging in this editor.

## Reference-style Tag editor (1.0.13)

The Tag editor now follows the supplied dataset-editor reference:
- Local dark theme, dense rounded tags and separate blue count badges.
- Scrollable large thumbnails on the left, tag statistics above the editing area,
  category pills and compact Bulk Insert / Unwanted Tag controls in between.
- Multiple image/caption rows below, each with its own thumbnail, filename, tag
  count, Copy view tags button and editable tags. Selecting a left thumbnail brings
  that image's row into view instead of replacing every other row.
- Click an image-row tag and press Enter to stage an edit; Escape cancels. Its ×
  removes that tag only from that image's draft. Category filters affect which tags
  are displayed in each row; clicking a statistics tag filters dataset images.
- Both image panes render only nearby visible rows and share a bounded thumbnail
  cache. Large datasets do not create a widget for every tag in every image.

Save All still opens the before/after review. TXT writes, encoding preservation,
conflict checks and backups follow the existing process. Other application tabs
retain their appearance. No image analysis or inference was added to the editor.

## Compact unified navigation (1.0.22)

The application now shares the Tag editor's dark palette, with compact navigation
tabs and smaller outer margins. Progress, percent and operation status appear in
the top header instead of occupying a separate footer. The status can be read in
full by hovering over it. Page scrollbars appear only when content overflows.

The window is resizable down to a smaller minimum. Its size is saved on normal
close in logical DPI units and restored within the current screen bounds.
Selected statistics tags and image-row tags are visibly highlighted in blue.
The tag filter is also shown beside Clear filter. File operations and caption
saving retain their existing confirmation, conflict checks and backups.

## Appearance (1.0.22)

Choose Dark or Classic in the top header. The choice is saved locally and restored on launch. Classic uses neutral light colors.

## Design reference

[TagFilter — LoRA Dataset Tag Editor](https://github.com/unaya-git/TagFilter), by unaya-git, was used as a visual reference for the Tag editor layout. This acknowledgement credits the design reference; it does not state that TagFilter source code was incorporated.

## Guide languages (1.0.22)

Detailed guides are provided in Japanese, English, Simplified Chinese, Traditional Chinese (Taiwan) and Brazilian Portuguese. Spanish, Thai and German currently display the full English guide with an explicit language notice.

## Uninstall

Close the application and run Uninstall.cmd from an installation made with Install.cmd. Type YES to confirm. Recorded application files and the matching desktop shortcut are removed; additional files, models, captions, settings and restoration history are preserved. Portable copies are removed manually. The uninstaller has not been executed or tested.
