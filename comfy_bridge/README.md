# Organizer Image to Text nodes
Copy this folder to ComfyUI/custom_nodes/model_library_organizer_bridge.
Install requirements.txt using the Python interpreter used by ComfyUI, then restart ComfyUI.
ComfyUI must already have a compatible torch/GPU runtime. Model weights are not included.
Supported folders: PixAI (tagger_pipeline.py), JoyCaption (Llava-compatible model, config, processor and tokenizer), CL Tagger (model.onnx and model_vocabulary.json), Taggerine (inference_tagger_standalone.py and tagger_proto.safetensors).
These adapters do not support arbitrary Image to Text models. Model-specific dependencies may also be required by the model author's inference script.
Drag the exported workflow JSON into ComfyUI. Paths refer to the computer running ComfyUI.
The Save matching TXT node is off by default. Enable it to create image-name TXT beside the original images. Existing TXT files are skipped, never overwritten.
