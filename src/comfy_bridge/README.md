# Organizer Image to Text nodes

## Installation

Recommended: use **Install / update custom nodes** in Model Library Organizer, select the actual ComfyUI instance's `custom_nodes` directory, install and restart ComfyUI.

For manual setup, copy this package so its entry file is at:

```text
ComfyUI/custom_nodes/model_library_organizer_bridge/__init__.py
```

Install this package's `requirements.txt` with the Python interpreter used by that ComfyUI instance, then restart it. A compatible torch/GPU runtime and model weights must be installed separately. Model-specific dependencies can also be required by the model author's inference script.

## Supported adapters

- PixAI: complete bundle containing `tagger_pipeline.py`.
- JoyCaption: Llava-compatible weights, configuration, processor and tokenizer.
- CL Tagger: `model.onnx` and `model_vocabulary.json`.
- Taggerine: `inference_tagger_standalone.py` and `tagger_proto.safetensors`.

Arbitrary caption models are not supported automatically. Combined and Expanded workflows share this package. Reinstall only for another ComfyUI instance or update when node code changes, not whenever you change input paths or a supported model.

## Workflow and output

Open the exported visual workflow JSON in ComfyUI. Paths belong to the computer running ComfyUI. Enable TXT saving before export if desired; saving is off by default.

Current templates provide an output folder such as `Images/PixAI`. The save node creates original-image hardlinks and matching TXT there. Existing TXT is skipped. Hardlinks must be on the same filesystem volume. Exporting alone creates no captions.

Legacy workflows with a blank output folder save TXT beside source images. Update nodes, restart ComfyUI and export a new workflow for the subfolder layout.
