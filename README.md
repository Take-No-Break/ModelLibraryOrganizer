# Model Library Organizer 1.0.8 — Windows preview

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
