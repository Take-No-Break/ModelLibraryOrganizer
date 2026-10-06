import json, os, struct, tempfile, threading, unittest
from pathlib import Path
from unittest.mock import patch
from core import Engine, header, infer, snapshot, enumerate_units, digest, atomic_json

def model(path,keys):
    path.parent.mkdir(parents=True,exist_ok=True)
    h={k:{'dtype':'F32','shape':[1],'data_offsets':[i*4,(i+1)*4]} for i,k in enumerate(keys)}
    b=json.dumps(h).encode();path.write_bytes(struct.pack('<Q',len(b))+b+b'\0'*4*len(keys));return path

class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.base=Path(self.temp.name);self.root=self.base/'models';self.root.mkdir();self.e=Engine(self.base/'state')
    def tearDown(self):self.temp.cleanup()
    def scan(self):return self.e.scan(self.root,self.root,online=False)
    def test_detection(self):
        for keys,expected in [(['lora_unet_a.lora_down.weight'],'loras'),(['clip_l','clip_g'],'embeddings'),(['controlnet_cond_embedding.conv_in.weight'],'controlnet'),(['encoder.conv_in.weight','decoder.conv_out.weight'],'vae'),(['net.blocks.0.weight'],'diffusion_models'),(['blocks.0.attn.wq.weight_scale','blocks.0.mod.lin'],'diffusion_models'),(['model.diffusion_model.x','first_stage_model.x'],'checkpoints'),(['text_model.embeddings.x'],'text_encoders')]:
            p=model(self.root/'x.safetensors',keys);h,m=header(p);self.assertEqual(infer(h,m,p.name)[0],expected)
    def test_specialized_roles(self):
        cases=[(['redux_down.weight','redux_up.weight'],'style_models'),
               (['controlnet_blocks.0.y_rms.weight','img_in.weight'],'model_patches'),
               (['controlnet_blocks.0.weight'],'controlnet'),
               (['vision_model.x','language_model.model.layers.0.x'],'Image_to_txt_models'),
               (['vision_model.x'],'clip_vision'),
               (['weight'],'')]
        for keys,expected in cases:
            self.assertEqual(infer(dict.fromkeys(keys),{},'style.onnx')[0],expected)
    def test_image_package_and_vision_encoder(self):
        for folder,arch,expected in [('caption','LlavaForConditionalGeneration','Image_to_txt_models'),('encoder','CLIPVisionModel','')]:
            p=model(self.root/folder/'model.safetensors',['weight'])
            (p.parent/'config.json').write_text(json.dumps({'architectures':[arch]}))
        rows=self.scan()
        self.assertEqual(next(r for r in rows if r['title']=='caption')['kind'],'Image_to_txt_models')
        self.assertEqual(next(r for r in rows if r['title']=='encoder')['kind'],'')
    def test_bad_header_blocked(self):
        (self.root/'bad.safetensors').write_bytes(b'version https://git-lfs.github.com/spec/v1\n')
        r=self.scan()[0];self.assertTrue(r['blocked']);self.assertEqual(r['decision'],'保留')
    def test_unapproved_unchanged(self):
        p=model(self.root/'x.safetensors',['clip_l']);rows=self.scan()
        with self.assertRaises(ValueError):self.e.execute(rows,self.root)
        self.assertTrue(p.exists())
    def test_move_link_note_rollback(self):
        p=model(self.root/'x.safetensors',['clip_l']);before=digest(p);r=self.scan()[0];r['decision']='承認';r['url']='https://huggingface.co/test/model'
        link=self.root/'embeddings'/'Multi'/'x.safetensors';r['links']=[str(link)]
        log=self.e.execute([r],self.root);d=Path(r['destination'])
        self.assertTrue(os.path.samefile(d,link));self.assertEqual(digest(d),before);self.assertFalse(p.exists())
        note=d.with_name(d.name+'.source.txt');self.assertIn(r['url'],note.read_text(encoding='utf-8-sig'))
        self.e.rollback(log);self.assertEqual(digest(p),before);self.assertFalse(link.exists());self.assertFalse(note.exists())
    def test_collision_preflight(self):
        p=model(self.root/'x.safetensors',['clip_l']);r=self.scan()[0];r['decision']='承認';d=Path(r['destination']);d.parent.mkdir();d.write_bytes(b'existing')
        with self.assertRaises(FileExistsError):self.e.execute([r],self.root)
        self.assertTrue(p.exists());self.assertEqual(d.read_bytes(),b'existing')
    def test_modified_input(self):
        p=model(self.root/'x.safetensors',['clip_l']);r=self.scan()[0];r['decision']='承認';p.write_bytes(b'modified')
        with self.assertRaises(ValueError):self.e.execute([r],self.root)
    def test_bundle_atomic(self):
        b=self.root/'download';model(b/'unet'/'model.safetensors',['input_blocks.0.weight']);(b/'model_index.json').write_text('{}')
        rows=self.scan();self.assertEqual(len(rows),1);r=rows[0];self.assertTrue(r['bundle']);r['decision']='承認'
        log=self.e.execute(rows,self.root);self.assertTrue((Path(r['destination'])/'unet'/'model.safetensors').exists());self.e.rollback(log);self.assertTrue(b.exists())
    def test_directory_escape(self):
        model(self.root/'x.safetensors',['clip_l']);r=self.scan()[0];r.update(decision='承認',destination=str(self.base/'escape.safetensors'))
        with self.assertRaises(ValueError):self.e.execute([r],self.root)
    def test_api_error_not_notfound(self):
        p=model(self.root/'x.safetensors',['unrecognized.weight'])
        with patch('core.api_lookup',return_value=(None,'通信失敗 (HTTP 429)')):
            r=self.e.scan(self.root,self.root)[0]
        self.assertEqual(r['confidence'],'通信失敗');self.assertEqual(r['destination'],'');self.assertTrue(p.exists())
    def test_sharded_onnx_not_split(self):
        d=self.root/'bundle';d.mkdir();(d/'a.onnx').write_bytes(b'a');(d/'b.onnx').write_bytes(b'b');(d/'b.onnx.data').write_bytes(b'data')
        self.assertEqual(enumerate_units(self.root,threading.Event()),[(d,True)])
    def test_existing_source_note_moves_back(self):
        p=model(self.root/'x.safetensors',['clip_l']);note=p.with_name(p.name+'.source.txt');note.write_text('my note')
        r=self.scan()[0];r['decision']='承認';log=self.e.execute([r],self.root)
        d=Path(r['destination']).with_name(p.name+'.source.txt');self.assertEqual(d.read_text(),'my note');self.assertFalse(note.exists())
        self.e.rollback(log);self.assertEqual(note.read_text(),'my note')
    def test_rollback_stops_on_edited_note(self):
        model(self.root/'x.safetensors',['clip_l']);r=self.scan()[0];r['decision']='承認';log=self.e.execute([r],self.root)
        d=Path(r['destination']);d.with_name(d.name+'.source.txt').write_text('edited')
        with self.assertRaises(ValueError):self.e.rollback(log)
        self.assertTrue(d.exists())
    def test_diffusion_overrides_historical_checkpoint(self):
        p=model(self.root/'x.safetensors',['net.blocks.0.weight']);sha=digest(p)
        self.e.cache['choices'][sha]={'relative':'checkpoints/Anime/Anima','family':'Anima'}
        r=self.scan()[0];self.assertEqual(r['kind'],'diffusion_models');self.assertIn('diffusion_models',r['destination'])
    def test_hf_exact_hash_required(self):
        p=model(self.root/'x.safetensors',['clip_l']);r=self.scan()[0]
        with patch('core.fetch_json',return_value={'siblings':[{'rfilename':'x','lfs':{'sha256':r['sha']}}]}):
            self.assertEqual(self.e.hf_match(r,'https://huggingface.co/test/model'),'x')
        with patch('core.fetch_json',return_value={'siblings':[]}):
            with self.assertRaises(ValueError):self.e.hf_match(r,'https://huggingface.co/test/model')
    def test_link_without_move(self):
        p=model(self.root/'embeddings'/'x.safetensors',['clip_l']);r=self.scan()[0]
        h=self.root/'embeddings'/'Multi'/'x.safetensors';r.update(decision='承認',links=[str(h)])
        log=self.e.execute([r],self.root);self.assertTrue(os.path.samefile(p,h));self.e.rollback(log)
        self.assertTrue(p.exists());self.assertFalse(h.exists())

if __name__=='__main__':unittest.main()
