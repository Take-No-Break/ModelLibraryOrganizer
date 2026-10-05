import hashlib, json, os, threading, time, uuid
from pathlib import Path
from urllib.parse import urlparse
from core import fetch_json, digest, stamp, EXTS, atomic_json, Cancelled


def enrich(engine,row,host,online=True):
    sha=row.get('sha');cache=engine.cache.setdefault('details',{})
    if host not in ('https://civitai.red','https://civitai.com'):
        origin=urlparse(row.get('url',''))
        host=(origin.scheme+'://'+origin.netloc) if origin.hostname in ('civitai.red','civitai.com') else 'https://civitai.red'
    if sha in cache:row['info']=cache[sha];return row['info']
    info={'status':'公開情報未取得','triggers':[]}
    if sha and online:
        try:
            v=fetch_json(host+'/api/v1/model-versions/by-hash/'+sha)
            if not any(f.get('hashes',{}).get('SHA256','').lower()==sha.lower() for f in v.get('files',[])):raise ValueError('SHA256不一致')
            info={'status':'SHA256一致','triggers':v.get('trainedWords',[]),'version':v.get('name'), 'version_id':v.get('id'),'base_model':v.get('baseModel'),'published':v.get('publishedAt'),'description':v.get('description'),'model':v.get('model'),'files':[{'name':f.get('name'),'hashes':f.get('hashes')} for f in v.get('files',[])],'images':v.get('images',[])}
            try:
                card=fetch_json(host+'/api/v1/models/'+str(v['modelId']))
                info['author']=card.get('creator',{}).get('username');info['tags']=card.get('tags',[]);info['model_description']=card.get('description')
                info['permissions']={k:card[k] for k in ['allowNoCredit','allowCommercialUse','allowDerivatives','allowDifferentLicense'] if k in card}
            except Exception as e:info['model_details_status']='取得失敗: '+str(e)
            cache[sha]=info;engine.save()
        except Exception as e:info['status']='取得失敗: '+str(e)
    row['info']=info;return info


def duplicates(root,stop=None,notify=lambda x:None,progress=lambda completed,total:None):
    stop=stop or threading.Event();groups={};files=[]
    for base,dirs,names in os.walk(root,followlinks=False):
        dirs[:]=[d for d in dirs if not Path(base,d).is_symlink() and not Path(base,d).is_junction()]
        files.extend(Path(base,n) for n in names if Path(n).suffix.lower() in EXTS and not Path(base,n).is_symlink())
    progress(0,len(files))
    for i,p in enumerate(files):
        if stop.is_set():raise Cancelled()
        notify(f'重複検出 SHA256 {i+1}/{len(files)}: {p.name}')
        before=stamp(p);sha=digest(p,stop)
        if stamp(p)!=before:raise ValueError('計算中に変更されました: '+str(p))
        groups.setdefault(sha,[]).append({'path':str(p),'identity':before[:2],'size':before[2]});progress(i+1,len(files))
    return [{'sha256':sha,'files':items,'physical_copies':len({tuple(x['identity']) for x in items}),'extra_bytes':(len({tuple(x['identity']) for x in items})-1)*items[0]['size']} for sha,items in groups.items() if len(items)>1]


def family_relation(a,b):
    a=(a or '').strip().casefold();b=(b or '').strip().casefold()
    unknown={'','unknown','not found','multi','不明'}
    if a in unknown or b in unknown:return 'unknown'
    if a==b:return 'same'
    sdxl={'sdxl','sdxl 1.0','pony','illustrious','noobai','animagine'}
    if a in sdxl and b in sdxl:return 'related'
    return 'different'

def pair_key(lora,checkpoint):
    def identity(row):
        return row.get('sha','').lower() or os.path.normcase(str(Path(row['source']).resolve()))
    return hashlib.sha256(json.dumps([identity(lora),identity(checkpoint)]).encode()).hexdigest()

def compatibility(row,catalog):
    result=[]
    for other in catalog:
        if other.get('kind') not in ('checkpoints','diffusion_models') or not Path(other['source']).exists():continue
        a=row.get('family','');b=other.get('family','')
        relation=family_relation(a,b)
        status={'same':'同じ系統・組み合わせ未検証','related':'SDXL派生・互換性は中（未検証）','different':'異なる系統・対応関係なし／未確認','unknown':'系統未確認'}[relation]
        result.append({'checkpoint':other['source'],'family':b,'assessment':status,'relation':relation,'pair_key':pair_key(row,other),'source':other.get('url','')})
    return result

# Explicit loader fields only. Never rewrite captions, prompts or arbitrary strings.
LOADERS={'CheckpointLoaderSimple':('checkpoints',[(0,'ckpt_name')]),'CheckpointLoader':('checkpoints',[(1,'ckpt_name')]),'LoraLoader':('loras',[(0,'lora_name')]),'LoraLoaderModelOnly':('loras',[(0,'lora_name')]),'UNETLoader':('diffusion_models',[(0,'unet_name')]),'VAELoader':('vae',[(0,'vae_name')]),'CLIPLoader':('text_encoders',[(0,'clip_name')]),'DualCLIPLoader':('text_encoders',[(0,'clip_name1'),(1,'clip_name2')]),'ControlNetLoader':('controlnet',[(0,'control_net_name')])}
ALIASES={'clip':'text_encoders','unet':'diffusion_models'}

def workflow_plan(folder,root,rows):
    root=Path(root).resolve();mapping={};plans=[]
    for r in rows:
        if r.get('decision') not in ('承認','実行済み') or not r.get('destination'):continue
        s=Path(r['source']).resolve();d=Path(r['destination']).resolve()
        if s==d or not s.is_relative_to(root) or not d.is_relative_to(root):continue
        sp=s.relative_to(root).parts;dp=d.relative_to(root).parts
        if ALIASES.get(sp[0],sp[0])!=ALIASES.get(dp[0],dp[0]):continue
        key=(ALIASES.get(sp[0],sp[0]),'/'.join(sp[1:]).casefold())
        mapping.setdefault(key,set()).add(('/'.join(dp[1:]),str(d)))
    for p in Path(folder).rglob('*.json'):
        if p.is_symlink():continue
        try:raw=p.read_bytes();doc=json.loads(raw.decode('utf-8-sig'))
        except (ValueError,OSError):continue
        changes=[]
        def visit(obj):
            if isinstance(obj,dict):
                typ=obj.get('type') or obj.get('class_type')
                if isinstance(typ,str) and typ in LOADERS:
                    kind,fields=LOADERS[typ]
                    for idx,name in fields:
                        container=obj.get('inputs') if obj.get('class_type') else obj.get('widgets_values')
                        key=name if obj.get('class_type') else idx
                        if not isinstance(container,(dict,list)):continue
                        try:old=container[key]
                        except (KeyError,IndexError):continue
                        if not isinstance(old,str):continue
                        choices=mapping.get((kind,old.replace('\\','/').casefold()),set())
                        if len(choices)==1:
                            new,dest=next(iter(choices));container[key]=new;changes.append({'old':old,'new':new,'destination':dest})
                for val in obj.values():visit(val)
            elif isinstance(obj,list):
                for val in obj:visit(val)
        visit(doc)
        if changes:plans.append({'path':str(p),'before':hashlib.sha256(raw).hexdigest(),'document':doc,'changes':changes})
    return plans


def repair_workflows(plans,backup_root):
    for plan in plans:
        if digest(Path(plan['path']))!=plan['before']:raise ValueError('確認後に編集されたワークフロー: '+plan['path'])
        if any(not Path(c['destination']).exists() for c in plan['changes']):raise ValueError('先に承認済みモデルの移動を実行してください。')
    backup=Path(backup_root)/(time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]);backup.mkdir(parents=True)
    manifest=[]
    for i,plan in enumerate(plans):
        p=Path(plan['path']);raw=p.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=plan['before']:raise ValueError('修正直前にファイルが変更されました')
        b=backup/(str(i)+'-'+p.name)
        with b.open('xb') as f:f.write(raw)
        manifest.append({'original':str(p),'backup':str(b),'sha256':plan['before']});atomic_json(backup/'manifest.json',manifest)
        atomic_json(p,plan['document'])
    return str(backup)

def identification_status(row):
    if row.get('blocked') or row.get('confidence')=='エラー':return 'エラー・確認不能'
    if row.get('confidence')=='通信失敗':return '通信失敗・再確認が必要'
    if row.get('confidence')=='確認済みルール' and row.get('kind') not in ('','Not Found'):return '確認済み分類ルール'
    if row.get('confidence')=='配布元一致' and row.get('kind') not in ('','Not Found'):return '配布元照合済み'
    if row.get('confidence')=='構造推定':return '構造からの推定・要確認'
    return '判別できなかったモデル'
