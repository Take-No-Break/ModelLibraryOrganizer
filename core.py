"""Model Library Organizer. No tensor deserialization or remote code execution."""
import hashlib
import json
import os
import re
import struct
import threading
import time
import uuid
import urllib.request
import urllib.error
from pathlib import Path

EXTS={'.safetensors','.sft','.ckpt','.pt','.pth','.bin','.onnx','.gguf','.pt2'}
CATEGORIES=['checkpoints','loras','embeddings','workflows','diffusion_models','diffusers','vae','vae_approx',
 'text_encoders','clip','clip_vision','controlnet','background_removal','upscale_models',
 'latent_upscale_models','style_models','model_patches','audio_encoders','detection','sams',
 'ultralytics','frame_interpolation','geometry_estimation','optical_flow','gligen',
 'hypernetworks','classifiers','photomaker','Image_to_txt_models','Img2txtModels','onnx','unet','configs','Not Found']
API_TYPES={'Checkpoint':'checkpoints','LORA':'loras','LoCon':'loras','TextualInversion':'embeddings',
 'Controlnet':'controlnet','VAE':'vae','Upscaler':'upscale_models','Hypernetwork':'hypernetworks'}

def declared_category(meta):
    # Only an explicit ComfyUI role, never arbitrary repository tags or filenames.
    value=str(meta.get('comfyui.model_type',meta.get('comfyui_model_type',''))).strip()
    if value=='Img2txtModels':return 'Image_to_txt_models'
    return value if value in CATEGORIES and value not in {'Not Found','configs'} else ''

class Cancelled(Exception): pass

def atomic_json(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(tmp,path)

def read_json(path, default=None):
    try:return json.loads(Path(path).read_text(encoding='utf-8-sig'))
    except (OSError,ValueError):return default

def stamp(p):
    s=Path(p).stat()
    return [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns]

def snapshot(p):
    p=Path(p)
    if p.is_file():return {'':stamp(p)[:4]}
    return {str(x.relative_to(p)):stamp(x)[:4] for x in sorted(p.rglob('*')) if x.is_file()}

def has_link(p):
    return p.is_symlink() or (hasattr(p,'is_junction') and p.is_junction())

def safe_tree(p):
    if has_link(p):return False
    if p.is_dir():
        for root,dirs,files in os.walk(p,followlinks=False):
            if any(has_link(Path(root)/n) for n in dirs+files):return False
    return True

def digest(p,stop=None):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        while b:=f.read(8*1024*1024):
            if stop and stop.is_set():raise Cancelled()
            h.update(b)
    return h.hexdigest()

def header(p):
    with Path(p).open('rb') as f:
        b=f.read(8)
        if len(b)!=8:raise ValueError('ファイルが短すぎます')
        n=struct.unpack('<Q',b)[0]
        if not 2<=n<=32*1024*1024 or n+8>Path(p).stat().st_size:
            raise ValueError('Safetensorsヘッダー不正（未完了ダウンロード・Git LFSポインター等）')
        h=json.loads(f.read(n))
    if not isinstance(h,dict):raise ValueError('Safetensorsヘッダー不正')
    meta=h.pop('__metadata__',{})
    payload=Path(p).stat().st_size-n-8
    for value in h.values():
        if not isinstance(value,dict) or 'shape' not in value or 'data_offsets' not in value:raise ValueError('テンソル情報不正')
        a,b=value['data_offsets']
        if not 0<=a<=b<=payload:raise ValueError('テンソルデータ範囲不正')
    return h,meta

def infer(h,meta,name):
    keys=list(h); lower=' '.join(keys).lower(); title=str(meta.get('modelspec.architecture','')).lower()
    if any(s in lower for s in ['lora_down','lora_up','lora_a.','lora_b.','lokr_','hada_w']):return 'loras','adapterテンソルを検出'
    if keys and len(keys)<=16 and (set(keys)<={'clip_l','clip_g','emb_params'} or 'emb_params' in keys or any(k.startswith('string_to_param') for k in keys)):
        return 'embeddings','少数の埋め込みテンソルを検出'
    if {'redux_down.weight','redux_up.weight'} <= set(keys) or ('style_embedding' in keys and any('transformer' in k for k in keys)):
        return 'style_models','ComfyUI StyleAdapter／Redux専用層を検出'
    patch_pairs=[('controlnet_blocks.0.y_rms.weight','img_in.weight'),
                 ('control_img_in.weight','control_blocks.0.img_mlp.out.weight'),
                 ('audio_proj.proj1.weight','blocks.0.audio_cross_attn.proj.weight')]
    if any(set(pair)<=set(keys) for pair in patch_pairs) or any(k in keys for k in (
            'lllite_conditioning1.conv1.weight','feature_embedder.mid_layer_norm.bias',
            'control_all_x_embedder.2-1.weight','controlnet_patch_embedding.weight')):
        return 'model_patches','ComfyUI ModelPatchLoader専用層を検出'
    if 'multi_modal_projector' in lower or 'language_model.model.' in lower:
        return 'Image_to_txt_models','マルチモーダル言語モデル層を検出'
    if any(s in lower for s in ['controlnet_cond_embedding','controlnet_down_blocks','control_model.zero_convs','controlnet_blocks','controlnet_x_embedder']):return 'controlnet','ControlNet専用層を検出'
    diffusion=any(s in lower for s in ['model.diffusion_model.','diffusion_model.','double_blocks.','joint_blocks.','net.blocks.','input_blocks.','down_blocks.0.attentions']) or (
        any(k.startswith('blocks.0.attn.wq.') for k in keys) and 'blocks.0.mod.lin' in keys)
    if diffusion and any(s in lower for s in ['first_stage_model.','cond_stage_model.','conditioner.embedders.']):return 'checkpoints','拡散モデルとVAE／テキストエンコーダーを同梱'
    if diffusion:return 'diffusion_models','単独の拡散モデル層を検出'
    if 'encoder.conv_in.weight' in keys and 'decoder.conv_out.weight' in keys:return 'vae','VAEのencoder／decoder層を検出'
    if any(k.startswith(('vision_model.','visual.','model.vision_model.')) for k in keys):return 'clip_vision','画像エンコーダー層を検出'
    if any(k.startswith(('text_model.','transformer.text_model.')) for k in keys) or ('shared.weight' in keys and 'encoder.block.0.layer.0.SelfAttention.q.weight' in keys):return 'text_encoders','テキストエンコーダー専用層を検出'
    if 'model.embed_tokens.weight' in keys and any(k.startswith('model.layers.') for k in keys):return 'text_encoders','言語モデル層。用途は配布情報と照合が必要'
    if any('rdb1.conv1' in k.lower() or 'rrdb_trunk.' in k.lower() for k in keys):return 'upscale_models','RRDBアップスケーラー層を検出'
    if 'birefnet' in name.lower() and any(k.startswith('bb.layers.') for k in keys):return 'background_removal','BiRefNet名とbackbone構造（推定）'
    if 'lora' in title:return 'loras','modelspec.architecture（自己申告情報）'
    if declared_category(meta):return declared_category(meta),'明示的なComfyUI種類メタデータ（自己申告・要確認）'
    return '', '内部構造だけでは種類を確定できません'

def enumerate_units(root,stop):
    units=[]
    def walk(p):
        if stop.is_set():raise Cancelled()
        if not safe_shallow(p):return
        files=list(p.iterdir())
        weights=[f for f in files if f.is_file() and f.suffix.lower() in EXTS]
        bundle=(p/'model_index.json').exists() or any(p.glob('*.safetensors.index.json')) or any(p.glob('*.bin.index.json')) or (
            bool(weights) and any((p/n).exists() for n in ['config.json','model_metadata.json','tagger_vocab.json'])) or any(
            f.suffix.lower()=='.onnx' and f.with_name(f.name+'.data').exists() for f in weights)
        if bundle:
            units.append((p,True));return
        for f in sorted(files):
            if has_link(f):continue
            if f.is_dir():
                if f.name not in {'.cache','.git','__pycache__','.organizer'}:walk(f)
            elif f.suffix.lower() in EXTS:
                units.append((f,False))
            elif f.suffix.lower()=='.json':
                from organization import is_workflow
                if is_workflow(f):units.append((f,False))
    walk(Path(root));return units

def safe_shallow(p):return not has_link(p)

def fetch_json(url):
    from network import request_json
    return request_json(url)

def api_lookup(sha,host):
    try:
        d=fetch_json(host+'/api/v1/model-versions/by-hash/'+sha)
        files=d.get('files',[])
        if not any(f.get('hashes',{}).get('SHA256','').lower()==sha for f in files):
            return None,'照合失敗: APIのファイルSHA256が一致しません'
        return {'kind':API_TYPES.get(d.get('model',{}).get('type'),'') ,
          'family':d.get('baseModel',''), 'title':d.get('model',{}).get('name',''),
          'source':f"{host}/models/{d['modelId']}?modelVersionId={d['id']}",
          'model_id':d['modelId'],'description':d.get('description') or ''},'照合済み'
    except urllib.error.HTTPError as e:
        return None,'配布元未特定 (404)' if e.code==404 else f'通信失敗 (HTTP {e.code})'
    except Exception as e:return None,'通信失敗: '+str(e)

def slug(s):
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]','_',s).strip(' .')[:80] or 'Unknown'

def family_name(s):
    return {'Krea 2':'Krea2','SDXL 1.0':'SDXL','ZImageBase':'Z-Image','ZImageTurbo':'Z-Image','SD 1.5':'SD1.5'}.get(s,slug(s)) if s else ''

class Engine:
    def __init__(self,data_dir):
        self.data=Path(data_dir);self.data.mkdir(parents=True,exist_ok=True)
        self.cache=read_json(self.data/'cache.json',{'hashes':{},'models':{},'choices':{}})
        for k in ['hashes','models','choices']:self.cache.setdefault(k,{})
    def save(self):atomic_json(self.data/'cache.json',self.cache)
    def sha(self,p,stop):
        key=str(p.resolve());s=stamp(p);c=self.cache['hashes'].get(key)
        if c and c['stamp']==s:return c['sha']
        for cached in self.cache['hashes'].values():
            if cached['stamp']==s:
                self.cache['hashes'][key]={'stamp':s,'sha':cached['sha']}
                return cached['sha']
        sha=digest(p,stop)
        if stamp(p)!=s:raise ValueError('調査中にファイルが変更されました')
        self.cache['hashes'][key]={'stamp':s,'sha':sha};return sha
    def scan(self,scan_root,target_root,online=True,host='https://civitai.red',stop=None,notify=lambda x:None,only_new=False,progress=lambda completed,total:None,layout='category'):
        stop=stop or threading.Event();source_root=Path(scan_root).resolve();target_root=Path(target_root).resolve()
        from scan_history import capture
        notify('調査前の配置をJSONに記録しています…')
        capture(self,source_root,target_root,stop)
        units=enumerate_units(source_root,stop);result=[];progress(0,len(units))
        seen=self.cache.setdefault('seen',{});catalog=self.cache.setdefault('catalog',{})
        for n,(p,bundle) in enumerate(units,1):
            if stop.is_set():raise Cancelled()
            identity=str(p.resolve());fingerprint={'files':snapshot(p),'online':online,'host':host,'target':str(target_root),'layout':layout,'classification_version':2}
            if only_new and seen.get(identity)==fingerprint:
                progress(n,len(units));continue
            notify(f'{n}/{len(units)} 調査: {p.name}')
            row={'source':str(p.resolve()),'destination':'','links':[],'sha':'','kind':'','family':'',
                 'title':p.name,'evidence':'','url':'','confidence':'要確認','decision':'保留','bundle':bundle,'blocked':False,'layout':layout,'scan_root':str(source_root)}
            try:
                if not safe_tree(p):raise ValueError('シンボリックリンク／ジャンクションを含むため移動対象外')
                row['snapshot']=snapshot(p)
                note=p.with_name(p.name+'.source.txt')
                row['source_note_snapshot']=snapshot(note) if note.exists() else None
                current=p.relative_to(target_root).parts[0] if p.is_relative_to(target_root) and p!=target_root else ''
                if bundle:
                    config=read_json(p/'config.json',{}) or {};arch=str(config.get('architectures','')).lower()
                    kind='diffusers' if (p/'model_index.json').exists() else 'Image_to_txt_models' if any(x in arch for x in ['mlama','llava','qwen2vl','qwen2_5vl','idefics','pixai','tagger']) or (p/'tagger_vocab.json').exists() else ''
                    row.update(kind=kind or (current if current in CATEGORIES else ''),evidence='設定・重み・分割ファイルをまとめたパッケージ。個別ファイルには分解しません。')
                    if current in CATEGORIES:row['destination']=str(p);row['confidence']='配置維持'
                    elif kind:row['destination']=str(target_root/kind/p.name)
                else:
                    h={};meta={}
                    if p.suffix.lower() in {'.safetensors','.sft'}:h,meta=header(p)
                    row['metadata']=meta
                    inferred,why=infer(h,meta,p.name)
                    if p.suffix.lower()=='.json':inferred,why='workflows','Recognized ComfyUI workflow JSON'
                    sha=self.sha(p,stop);row['sha']=sha
                    saved=self.cache['choices'].get(sha)
                    if not saved or saved.get('layout','category')!=layout:
                        saved=self.cache.get('layout_choices',{}).get(layout,{}).get(sha)
                    info=self.cache['models'].get(sha)
                    if host in ('まとめて調査（Civitai + HF）','Hugging Face'):info=self.cache.setdefault('lookups',{}).get(host,{}).get(sha)
                    status='照合済み（キャッシュ）' if info else '未照合（オフライン）'
                    if not info and online:
                        if host in ('まとめて調査（Civitai + HF）','Hugging Face'):
                            from providers import lookup
                            info,status=lookup(sha,p.name,host,stop)
                        else:info,status=api_lookup(sha,host)
                        if info:
                            # Text/tags only; do not download or store sample images.
                            try:
                                from urllib.parse import urlparse
                                origin=urlparse(info['source'])
                                card=fetch_json(origin.scheme+'://'+origin.netloc+'/api/v1/models/'+str(info['model_id']))
                                info['tags']=card.get('tags',[]);info['author']=card.get('creator',{}).get('username')
                            except Exception:pass
                            self.cache['models'][sha]=info
                            if host in ('まとめて調査（Civitai + HF）','Hugging Face') and '通信失敗' not in status:self.cache.setdefault('lookups',{}).setdefault(host,{})[sha]=info
                    if info:
                        row['author']=info.get('author') or self.cache.get('details',{}).get(sha,{}).get('author')
                        if layout=='creator' and not row['author'] and info.get('model_id') and online:
                            try:
                                from urllib.parse import urlparse
                                origin=urlparse(info['source'])
                                if origin.hostname in ('civitai.red','civitai.com'):
                                    card=fetch_json(origin.scheme+'://'+origin.netloc+'/api/v1/models/'+str(info['model_id']))
                                    row['author']=info['author']=card.get('creator',{}).get('username')
                            except Exception as exc:row['evidence']='Creator lookup failed: '+str(exc)
                        row['source_checks']=info.get('source_checks',[])
                        row['matched_sources']=info.get('matched_sources',[info.get('source','')])
                        if info.get('details'):
                            row['info']=info['details'];self.cache.setdefault('details',{})[sha]=info['details']
                    kind=(info or {}).get('kind') or inferred
                    if kind=='Img2txtModels':kind='Image_to_txt_models'
                    reason=[why,status]
                    conflict=False
                    if inferred=='diffusion_models' and kind=='checkpoints':kind=inferred;reason.append('公開分類はCheckpointですが、実体は単独の拡散モデルです')
                    elif inferred and kind and inferred!=kind:conflict=True;reason.append('公開情報と内部構造の種類が異なるため要確認')
                    row.update(kind=kind,family=family_name((info or {}).get('family','')),title=(info or {}).get('title') or p.stem,url=(info or {}).get('source',''))
                    if saved:
                        relative=Path(saved['relative'])
                        if relative.is_absolute() or '..' in relative.parts:raise ValueError('保存済みルールのパス不正')
                        if relative.parts and relative.parts[0]=='Img2txtModels':
                            relative=Path('Image_to_txt_models',*relative.parts[1:])
                        dest=target_root/relative/p.name
                        # Prefer actual tensor role over historical checkpoint placement.
                        if inferred=='diffusion_models' and relative.parts[0]=='checkpoints':
                            dest=target_root/'diffusion_models'/Path(*relative.parts[1:])/p.name
                            reason.append('過去の配置ルールを単独拡散モデルの種類に修正')
                        row.update(destination=str(dest),links=[str(target_root/Path(x)/p.name) for x in saved.get('links',[])],confidence='確認済みルール')
                        row['url']=saved.get('url') or row['url'];reason.append('同一SHA256の確認済み配置')
                        row['family']=saved.get('family') or row['family']
                        row['kind']=saved.get('kind') or str(dest.relative_to(target_root).parts[0])
                        if row['kind']=='Img2txtModels':row['kind']='Image_to_txt_models'
                    elif kind:
                        dest=target_root/kind/p.name
                        if kind in {'checkpoints','loras'} and info:
                            tags={str(x).lower() for x in info.get('tags',[])}
                            purpose='Character' if tags & {'character','characters'} else 'Copyright(Style)' if tags & {'style','artstyle','artist'} else ''
                            if kind=='checkpoints':purpose='Realistic' if tags & {'photorealistic','realism','realistic'} else 'Anime' if 'anime' in tags else ''
                            if purpose:dest=target_root/kind/purpose/(row['family'] or 'Unknown')/p.name
                            elif row['family']:dest=target_root/kind/row['family']/p.name
                        aliases={'clip':'text_encoders','unet':'diffusion_models'}
                        if aliases.get(current,current)==kind:dest=p
                        row['destination']=str(dest)
                        row['confidence']='配布元一致' if info and not conflict else '構造推定'
                    elif current in CATEGORIES:
                        row.update(destination=str(p),confidence='配置維持',kind=current)
                    if conflict:row['confidence']='要確認'
                    if status.startswith('通信失敗'):row['confidence']='通信失敗'
                    row['evidence']+=' / '+' / '.join(reason)
                from organization import apply_layout
                if row.get('sha') and not row.get('author'):
                    row['author']=self.cache.get('details',{}).get(row['sha'],{}).get('author')
                apply_layout(row,target_root,layout)
                if row['destination'] and Path(row['destination'])==p:row['decision']='変更なし'
                if row['destination'] and Path(row['destination']).exists() and Path(row['destination'])!=p:
                    if p.is_file() and os.path.samefile(p,row['destination']):row['decision']='変更なし';row['evidence']+=' / 既存ハードリンク'
                    else:row['blocked']=True;row['evidence']+=' / 保存先が既に存在します'
                if snapshot(p)!=row['snapshot']:raise ValueError('調査中にファイルが変更されました')
            except Cancelled:raise
            except Exception as e:row.update(blocked=True,confidence='エラー',evidence=str(e))
            result.append(row)
            catalog[identity]=row
            if not row['blocked'] and '通信失敗' not in row['evidence']:seen[identity]=fingerprint
            else:seen.pop(identity,None)
            progress(n,len(units))
            if n%10==0:self.save()
        if layout=='creator':
            destinations={}
            for row in result:
                if row.get('blocked') or not row.get('destination') or row['destination']==row['source']:continue
                key=os.path.normcase(row['destination']);other=destinations.get(key)
                if other:
                    if Path(row['source']).is_file() and Path(other['source']).is_file() and os.path.samefile(row['source'],other['source']):
                        row.update(destination=row['source'],links=[],decision='変更なし')
                        row['evidence']+=' / Existing hard-link alias retained; no file deleted.'
                    else:
                        row['blocked']=True;row['confidence']='要確認';row['evidence']+=' / Multiple files propose the same destination; choose another destination.'
                else:destinations[key]=row
        self.save();return result

    def hf_match(self,row,url):
        from urllib.parse import urlparse
        u=urlparse(url)
        if u.hostname not in {'huggingface.co','www.huggingface.co'}:raise ValueError('Hugging FaceのURLを入力してください')
        parts=u.path.strip('/').split('/')
        if len(parts)<2:raise ValueError('モデルリポジトリのURLが必要です')
        repo='/'.join(parts[:2]);data=fetch_json('https://huggingface.co/api/models/'+repo+'?blobs=true')
        matches=[s for s in data.get('siblings',[]) if s.get('lfs',{}).get('sha256','').lower()==row['sha']]
        if not row['sha'] or not matches:raise ValueError('このリポジトリのmainに一致するSHA256がありません。移動先は変更していません。')
        row['url']='https://huggingface.co/'+repo;row['evidence']+=' / HF SHA256一致: '+matches[0]['rfilename']
        row['title']=repo;row['confidence']='配布元一致'
        row['info']={'status':'HF SHA256一致','repository':repo,'triggers':[], 'card_data':data.get('cardData',{}),'tags':data.get('tags',[]),'matched_file':matches[0],'last_modified':data.get('lastModified')}
        self.cache.setdefault('details',{})[row['sha']]=row['info'];self.save()
        return matches[0]['rfilename']

    def execute(self,rows,target_root,progress=lambda completed,total:None):
        root=Path(target_root).resolve();chosen=[r for r in rows if r['decision']=='承認']
        if not chosen:raise ValueError('承認された移動がありません')
        ops=[];occupied=set();sources=[]
        for r in chosen:
            s=Path(r['source']).resolve();d=Path(r['destination']).resolve()
            if r.get('blocked'):raise ValueError('エラーがある項目は実行できません: '+s.name)
            if not r['destination'] or not d.is_relative_to(root) or d==root:raise ValueError('保存先は指定したmodelsフォルダー内にしてください')
            if s==d and not r.get('links'):raise ValueError('移動元と先が同じです: '+s.name)
            if s!=d and d.is_relative_to(s):raise ValueError('フォルダー自身の内部へ移動できません')
            if not safe_tree(s) or snapshot(s)!=r['snapshot']:raise ValueError('調査後に変更されています。再調査してください: '+s.name)
            if s.stat().st_dev!=root.stat().st_dev:raise ValueError('この版の移動は同じドライブ内のみ対応します: '+s.name)
            old_note=s.with_name(s.name+'.source.txt');new_note=d.with_name(d.name+'.source.txt')
            if old_note.exists():
                if snapshot(old_note)!=r.get('source_note_snapshot'):raise ValueError('配布元TXTが調査後に変更されています')
                if s!=d and new_note.exists():raise FileExistsError('保存先の配布元TXTが既に存在します: '+str(new_note))
            paths=[d]+[Path(x).resolve() for x in r.get('links',[])]
            for p in paths:
                if not p.is_relative_to(root) or p==root:raise ValueError('リンク先がmodels外です')
                key=os.path.normcase(str(p))
                if key in occupied:raise ValueError('複数の項目で保存先が重複しています: '+str(p))
                occupied.add(key)
                if p.exists():
                    if p==d and s==d:continue
                    if p!=d and s.is_file() and os.path.samefile(s,p):continue
                    raise FileExistsError('既存ファイルを上書きしません: '+str(p))
                if p!=d and s.is_dir():raise ValueError('フォルダーパッケージのハードリンクは非対応です')
            sources.append(s);ops.append((r,s,d,paths[1:]))
        for s in sources:
            if any(s!=other and s.is_relative_to(other) for other in sources):raise ValueError('移動元が入れ子です')
        logdir=self.data/'history';logdir.mkdir(exist_ok=True)
        journal=logdir/(time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6]+'.json')
        # Persist the complete affected-path plan before the first filesystem change.
        before=[]
        for r,s,d,links in ops:
            note=s.with_name(s.name+'.source.txt')
            folders={}
            for target in [d,*links]:
                parent=target.parent
                while parent.is_relative_to(root):
                    folders[str(parent)]={'exists':parent.exists(),'identity':stamp(parent)[:2] if parent.exists() else None}
                    if parent==root:break
                    parent=parent.parent
            before.append({'source':str(s),'destination':str(d),'links':[str(h) for h in links],
                'folders_before':folders,
                'source_snapshot':snapshot(s),'sha256':r.get('sha',''),
                'source_note':{'path':str(note),'snapshot':snapshot(note)} if note.exists() else None,
                'targets_before':[{'path':str(p),'exists':p.exists(),'snapshot':snapshot(p) if p.exists() else None} for p in [d,*links]]})
        record={'version':2,'created_at':time.strftime('%Y-%m-%d %H:%M:%S'),'root':str(root),
                'scope':'Affected model paths and source TXT only; not a content backup.',
                'before_state':before,'created_dirs':[],'complete':False,'ops':[],
                'cleanup_root':str(Path(ops[0][0].get('scan_root',root)).resolve()),'layout':ops[0][0].get('layout','category')}
        atomic_json(journal,record)
        from scan_history import link
        record['scan_snapshot']=link(self,journal)
        atomic_json(journal,record)
        def make_parents(parent):
            missing=[];p=parent
            while not p.exists():
                if not p.is_relative_to(root) or p==root:raise ValueError('Folder creation outside models root')
                missing.append(p);p=p.parent
            for p in reversed(missing):
                try:p.mkdir()
                except FileExistsError:
                    if not p.is_dir() or has_link(p):raise
                    continue
                record['created_dirs'].append({'path':str(p),'identity':stamp(p)[:2]})
                atomic_json(journal,record)
        try:
            progress(0,len(ops))
            for completed,(r,s,d,links) in enumerate(ops,1):
                # Recheck immediately before each rename; never overwrite.
                if (s!=d and d.exists()) or snapshot(s)!=r['snapshot']:raise ValueError('実行前の変更または保存先の競合')
                op={'source':str(s),'destination':str(d),'snapshot':r['snapshot'],'links':[],'notes':[],'done':False,'no_move':s==d}
                old_note=s.with_name(s.name+'.source.txt');new_note=d.with_name(d.name+'.source.txt')
                if s!=d and old_note.exists():op['moved_note']={'source':str(old_note),'destination':str(new_note),'snapshot':snapshot(old_note)}
                record['ops'].append(op);atomic_json(journal,record)
                make_parents(d.parent)
                if s!=d:s.rename(d)
                op['done']=True;atomic_json(journal,record)
                if snapshot(d)!=r['snapshot']:raise ValueError('移動後のファイル検証に失敗')
                if op.get('moved_note'):old_note.rename(new_note)
                for h in links:
                    if h.exists() and os.path.samefile(d,h):continue
                    op['links'].append(str(h));atomic_json(journal,record)
                    make_parents(h.parent);os.link(d,h)
                    if not os.path.samefile(d,h):raise ValueError('リンク検証失敗')
                for location in [d,*links]:
                    self.write_note(r,location,op,lambda:atomic_json(journal,record))
                if r['sha']:
                    previous=self.cache['choices'].get(r['sha'])
                    layouts=self.cache.setdefault('layout_choices',{})
                    if previous:layouts.setdefault(previous.get('layout','category'),{})[r['sha']]=previous
                    self.cache['choices'][r['sha']]={'relative':str(d.parent.relative_to(root)),
                       'links':[str(h.parent.relative_to(root)) for h in links], 'url':r['url'],'family':r['family'],
                       'layout':r.get('layout','category'),'kind':r['kind']}
                    layouts.setdefault(r.get('layout','category'),{})[r['sha']]=self.cache['choices'][r['sha']]
                    self.cache['hashes'][str(d)]={'stamp':stamp(d),'sha':r['sha']}
                r['decision']='実行済み';progress(completed,len(ops))
            if record['layout']=='creator':
                from organization import cleanup_empty_sources
                cleanup_empty_sources(record,journal,lambda:atomic_json(journal,record))
            record['complete']=True;atomic_json(journal,record);self.save()
        except Exception as e:
            record['error']=str(e);atomic_json(journal,record)
            raise RuntimeError(f'{e}\n途中までの履歴: {journal}\n「履歴から元に戻す」で復元できます。') from e
        return journal

    def rollback(self,journal):
        j=read_json(journal)
        if not j or j.get('restored'):raise ValueError('復元できる履歴ではありません')
        root=Path(j['root']).resolve();ops=[]
        for op in reversed(j['ops']):
            s=Path(op['source']).resolve();d=Path(op['destination']).resolve()
            if not d.is_relative_to(root):raise ValueError('履歴の保存先不正')
            if s.exists() and not d.exists():continue
            if (s!=d and s.exists()) or not d.exists() or snapshot(d)!=op['snapshot']:raise ValueError('移動後の変更／元パス競合があります。復元を中止: '+str(d))
            for name in op['links']:
                h=Path(name).resolve()
                if not h.is_relative_to(root):raise ValueError('履歴のリンク先不正')
                if h.exists() and not os.path.samefile(d,h):raise ValueError('リンク先が置き換わっています')
            for note in op.get('notes',[]):
                p=Path(note['path']).resolve()
                if not p.is_relative_to(root):raise ValueError('履歴のTXTパス不正')
                if p.exists() and digest(p)!=note['sha']:raise ValueError('配布元TXTが編集されています。復元を中止')
            if note:=op.get('moved_note'):
                ns=Path(note['source']);nd=Path(note['destination'])
                if nd.exists() and (ns.exists() or snapshot(nd)!=note['snapshot']):raise ValueError('移動した配布元TXTが変更されています')
                if not nd.exists() and not ns.exists():raise ValueError('配布元TXTが見つかりません')
            ops.append((op,s,d))
        for op,s,d in ops:
            for note in op.get('notes',[]):
                if Path(note['path']).exists():Path(note['path']).unlink()
            for name in op['links']:
                if Path(name).exists():Path(name).unlink()
            s.parent.mkdir(parents=True,exist_ok=True)
            if s!=d:d.rename(s)
            if note:=op.get('moved_note'):
                if Path(note['destination']).exists():Path(note['destination']).rename(note['source'])
            op['restored']=True;atomic_json(journal,j)
        # Remove only directories created by this run, still identical and empty.
        retained=[]
        for item in reversed(j.get('created_dirs',[])):
            p=Path(item['path'])
            if not p.exists():continue
            if not p.resolve().is_relative_to(root) or p.resolve()==root or has_link(p) or stamp(p)[:2]!=item['identity']:
                retained.append(str(p));continue
            try:p.rmdir()
            except OSError:retained.append(str(p))
        j['retained_dirs']=retained;j['restored_at']=time.strftime('%Y-%m-%d %H:%M:%S')
        j['restored']=True;atomic_json(journal,j)
        # Remembered routing could immediately propose the undone move; clear matching rules.
        affected={op['destination'] for op in j['ops']}
        for p in affected:
            c=self.cache['hashes'].get(p)
            if c:
                self.cache['choices'].pop(c['sha'],None)
                for rules in self.cache.get('layout_choices',{}).values():
                    rule=rules.get(c['sha'])
                    if rule and str(root/Path(rule['relative'])/Path(p).name)==p:rules.pop(c['sha'],None)
        self.save();return len(ops)

    @staticmethod
    def note_content(row):
        from note_format import note_content
        return note_content(row)

    def write_note(self,row,location,op=None,flush=lambda:None):
        location=Path(location)
        # Package note is a sibling, so the package snapshot stays unchanged.
        p=location.with_name(location.name+'.source.txt')
        content=self.note_content(row).encode('utf-8-sig')
        if p.exists():return False  # Never overwrite existing user notes.
        if op is not None:
            op.setdefault('notes',[]).append({'path':str(p),'sha':hashlib.sha256(content).hexdigest()});flush()
        with p.open('xb') as f:f.write(content)
        return True
