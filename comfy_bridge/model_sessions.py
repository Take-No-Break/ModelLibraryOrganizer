import gc
import importlib.util
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image
from safetensors.torch import load_file
import torch
from transformers import AutoProcessor, LlavaForConditionalGeneration, StoppingCriteria, StoppingCriteriaList

import comfy.model_management as mm
from .tag_order import format_pixai_tags


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CheckInterrupt(StoppingCriteria):
    def __call__(self, input_ids, scores, **kwargs):
        mm.throw_exception_if_processing_interrupted()
        return False


class CaptionSession:
    def __init__(self, selection):
        self.selection = selection
        self.backend = selection['backend']
        self.pipeline = self.model = self.processor = self.module = self.vocab = None
        self.target = mm.get_torch_device() if selection['device'] == 'auto' else torch.device('cpu')

    def __enter__(self):
        mm.unload_all_models()
        mm.soft_empty_cache()
        path = Path(self.selection['path'])
        if self.backend == 'pixai':
            self.module = load_module(path / 'tagger_pipeline.py', 'selected_pixai_pipeline')
            self.model = self.module.ViTDetCls.from_pretrained(str(path), local_files_only=True).to(device=self.target).eval()
            size = json.loads((path / 'preprocessor_config.json').read_text())['size']
            self.pipeline = self.module.TaggerPipeline(model=self.model, image_processor=self.module.RescalePadProcessor(size=size), device=self.target)
        elif self.backend == 'cl_tagger':
            import onnxruntime as ort
            options = ort.SessionOptions()
            options.intra_op_num_threads = 4
            providers = ['CPUExecutionProvider']
            # ONNX Runtime's CUDA provider cannot run on an AMD/ROCm GPU.
            if self.target.type == 'cuda' and not torch.version.hip and 'CUDAExecutionProvider' in ort.get_available_providers():
                providers.insert(0, 'CUDAExecutionProvider')
            self.pipeline = ort.InferenceSession(str(path / 'model.onnx'), sess_options=options, providers=providers)
            self.vocab = json.loads((path / 'model_vocabulary.json').read_text(encoding='utf-8'))
            if self.pipeline.get_outputs()[0].shape[-1] != self.vocab['num_tags']:
                raise ValueError('CL Tagger model and vocabulary have different tag counts.')
        elif self.backend == 'taggerine':
            from accelerate import init_empty_weights
            self.module = load_module(path / 'inference_tagger_standalone.py', 'selected_taggerine')
            self.vocab = json.loads((path / 'tagger_vocab_with_categories_and_alias_updated.json').read_text(encoding='utf-8'))
            state = load_file(str(path / 'tagger_proto.safetensors'), device='cpu')
            backbone, head = self.module._split_and_clean_state_dict(state)
            with init_empty_weights():
                self.model = self.module.DINOv3Tagger()
                self.model.head, head_state = self.module._build_head_from_checkpoint(head, self.module.FEATURE_DIM, len(self.vocab['idx2tag']))
            self.model.backbone.load_state_dict(backbone, strict=True, assign=True)
            self.model.head.load_state_dict(head_state, strict=True, assign=True)
            dtype = torch.bfloat16 if self.target.type == 'cuda' and mm.supports_dtype(self.target, torch.bfloat16) else torch.float32
            self.model.backbone.to(device=self.target, dtype=dtype)
            self.model.head.to(device=self.target, dtype=torch.float32)
            self.model.eval()
        elif self.backend == 'joycaption':
            self.processor = AutoProcessor.from_pretrained(str(path), local_files_only=True, backend='pil')
            load_args = {'local_files_only': True, 'dtype': torch.bfloat16, 'attn_implementation': 'sdpa'}
            if self.target.type == 'cuda':
                free = int(mm.get_free_memory(self.target))
                load_args.update(device_map='auto', max_memory={self.target.index or 0: max(0, free - 2 * 1024**3), 'cpu': '20GiB'})
            else:
                load_args['device_map'] = {'': str(self.target)}
            self.model = LlavaForConditionalGeneration.from_pretrained(str(path), **load_args).eval()
        else:
            raise ValueError('Unsupported caption backend: ' + self.backend)
        return self

    def caption(self, image, threshold, prompt, max_tokens):
        mm.throw_exception_if_processing_interrupted()
        if not self.selection.get('explicit_threshold', False):
            threshold = threshold if threshold > 0 else self.selection.get('threshold', 0.5)
        if self.backend == 'pixai':
            results = self.pipeline(image, threshold={'general': threshold})['results']
            return format_pixai_tags(results)
        if self.backend == 'cl_tagger':
            pixels = np.asarray(image.resize((384, 384), Image.Resampling.BICUBIC), dtype=np.float32)
            pixels = ((pixels / 255.0 - 0.5) / 0.5).transpose(2, 0, 1)[None]
            logits = self.pipeline.run(['logits'], {'pixel_values': pixels})[0][0]
            scores = 1.0 / (1.0 + np.exp(-np.clip(logits, -80, 80)))
            ordered = np.flatnonzero(scores >= threshold)
            ordered = ordered[np.argsort(-scores[ordered])]
            return ', '.join(self.vocab['idx_to_tag'][str(i)] for i in ordered)
        if self.backend == 'taggerine':
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            buffer.seek(0)
            pixels = self.module.preprocess_image(buffer, max_size=512).to(self.target)
            scores = torch.sigmoid(self.model(pixels)[0].float())
            indices = (scores >= threshold).nonzero(as_tuple=True)[0]
            indices = indices[scores[indices].argsort(descending=True)].tolist()
            return ', '.join(self.vocab['idx2tag'][i] for i in indices)
        conversation = [{'role': 'system', 'content': 'You are a helpful image captioner.'}, {'role': 'user', 'content': prompt}]
        formatted = self.processor.apply_chat_template(conversation, tokenize=False, add_generation_prompt=True)
        inputs = self.processor(text=[formatted], images=[image], return_tensors='pt')
        target = self.model.get_input_embeddings().weight.device
        inputs = inputs.to(target)
        inputs['pixel_values'] = inputs['pixel_values'].to(torch.bfloat16)
        generated = self.model.generate(**inputs, max_new_tokens=max_tokens, do_sample=False, use_cache=True,
                                        stopping_criteria=StoppingCriteriaList([CheckInterrupt()]))[0]
        tokens = generated[inputs['input_ids'].shape[1]:]
        eos = self.model.generation_config.eos_token_id
        eos = eos if isinstance(eos, list) else [eos]
        if len(tokens) >= max_tokens and tokens[-1].item() not in eos:
            raise RuntimeError('Caption reached max_tokens. Increase max_tokens before saving.')
        return self.processor.tokenizer.decode(tokens, skip_special_tokens=True, clean_up_tokenization_spaces=False).strip()

    def __exit__(self, *_):
        if self.backend == 'taggerine' and self.module is not None:
            self.module._patch_coords_cached.cache_clear()
        self.pipeline = self.model = self.processor = self.module = self.vocab = None
        gc.collect()
        mm.soft_empty_cache()
