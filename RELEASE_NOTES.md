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
