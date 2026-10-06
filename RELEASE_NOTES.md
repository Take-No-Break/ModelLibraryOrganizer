# Windows preview 1.0.22

- Progress/status header fits narrow windows; long status is shortened with full text on hover.
- Proposed new folder paths are green in move review; created folder paths are green in history details.
- Fixed callback ownership when closing responsive controls.
- Existing scan classification tests and all 18 test modules passed. No real models moved.
- Uninstaller is included but has not been executed or tested. No GitHub push/release performed.

## 1.0.23: Model roles and Image to Text folder

Added conservative StyleAdapter/Redux and supported ModelPatchLoader tensor signatures. Multimodal language layers take priority over their vision encoder component. Recognized caption bundles stay intact and use Image_to_txt_models; generic CLIPVision bundles are not assumed to be caption models. Explicit comfyui.model_type metadata can propose other known model roles, but is self-reported. All 31 existing folder names are supported for preserving placement; this does not verify every model type. ONNX is a format, and repository tags do not establish per-file roles. Unknown models remain unchanged for review. Classification changes invalidate incremental scan fingerprints. No user models were moved.

## 1.0.24: Per-file classification correction

Reliable tensor structure takes priority over the distribution page category. A VAE bundled in a Checkpoint publication stays a VAE. Conflicting remembered routes are not reused; the corrected destination is proposed for review. Incremental scans revisit previous classifications. No real model files were moved.

## 1.0.25: Select a specific LoRA and Checkpoint

Compatibility now has separate LoRA and Checkpoint/diffusion model selectors. Select both files to display the assessment for that exact pair and save a pair-specific manual evaluation. Folder selection filters previously scanned models; use Scan selected folders for models not investigated yet. This comparison estimates compatibility from known families and does not load models or perform image generation. No files are moved.

## 1.0.26: One LoRA against every checkpoint

Select a LoRA to compare against all identified checkpoint/diffusion models in the selected folder, including subfolders. Choosing a folder starts a read-only compatibility scan when idle. The checkpoint selector was removed. Automatic family estimates remain untested; each row can separately record successful use, adjustments or failure. No generation test is performed and no models are moved.

## 1.0.27: Source triggers and setup help

Source TXT always includes published trigger words when available, even with older section preferences. Incomplete Civitai details caches are refreshed when online. Japanese and English help now explains ZIP extraction, correct custom_nodes placement, ComfyUI Python dependencies, restarting, workflow export, supported model changes and error diagnosis.

## 1.0.28: Run local Image to Text and save to a chosen folder

Select images, a supported model folder/type, thresholds, an output folder and the running ComfyUI URL. Run in ComfyUI and save creates image hardlinks and matching captions in the chosen output folder after successful inference. Hardlinks require the same drive. Existing TXT and differing images are protected. Required nodes must be installed directly in the custom_nodes directory of the actual running instance, then ComfyUI must be restarted. Workflow exports remain available. The app does not launch or restart ComfyUI automatically.

## 1.0.29: Automatic caption output and connection check

Image to Text saves under the selected image folder in a PixAI/JoyCaption/CL-Tagger/Taggerine subfolder. The separate output entry was removed; automatic save location is displayed. Check connection beside the ComfyUI URL verifies that the required nodes are loaded. Recursive runs exclude generated output folders. Exported templates also use the automatic output folder when TXT saving is enabled. The updated save node must be installed and ComfyUI restarted for new templates; direct app execution only needs the existing analysis nodes.
