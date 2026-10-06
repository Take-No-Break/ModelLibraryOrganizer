from pathlib import Path
from urllib.parse import quote
from core import api_lookup,fetch_json,Cancelled
AUTO='まとめて調査（Civitai + HF）'
HF='Hugging Face'

def hf_lookup(sha,name,stop=None):
    # Bounded name-based candidate discovery, then exact file SHA256 verification.
    query=Path(name).stem[:120]
    candidates=fetch_json('https://huggingface.co/api/models?search='+quote(query,safe='')+'&limit=5')
    if not isinstance(candidates,list):raise ValueError('HF検索応答形式が変更されています')
    for item in candidates:
        if stop and stop.is_set():raise Cancelled()
        repo=item.get('id','')
        if not repo:continue
        data=fetch_json('https://huggingface.co/api/models/'+quote(repo,safe='/')+'?blobs=true')
        matches=[f for f in data.get('siblings',[]) if f.get('lfs',{}).get('sha256','').lower()==sha.lower()]
        if matches:
            details={'status':'HF SHA256一致','repository':repo,'triggers':[],'card_data':data.get('cardData',{}),'tags':data.get('tags',[]),'matched_file':matches[0],'last_modified':data.get('lastModified')}
            return {'kind':'','family':'','title':repo,'source':'https://huggingface.co/'+repo,'tags':data.get('tags',[]),'details':details},'HF SHA256一致'
    return None,'HF: 候補内でハッシュ一致なし（名前検索の上位5件・mainのみ）'

def lookup(sha,name,mode,stop=None):
    matches=[];checks=[]
    if mode==AUTO:
        info,status=api_lookup(sha,'https://civitai.red');checks.append({'site':'Civitai.red','result':status})
        if info:matches.append(info)
        else:
            if stop and stop.is_set():raise Cancelled()
            info,status=api_lookup(sha,'https://civitai.com');checks.append({'site':'Civitai.com','result':status})
            if info:matches.append(info)
    if stop and stop.is_set():raise Cancelled()
    try:
        info,status=hf_lookup(sha,name,stop);checks.append({'site':'Hugging Face','result':status})
        if info:matches.append(info)
    except Cancelled:raise
    except Exception as e:checks.append({'site':'Hugging Face','result':'通信失敗: '+str(e)})
    if mode==AUTO:
        checks.append({'site':'SeaArt','result':'自動SHA256逆引き非対応（公開エンドポイント未確認）'})
        checks.append({'site':'Tensor.Art','result':'Web検索は @sha256 + ハッシュ値に対応。自動照合APIは未確認・未実行'})
    if matches:
        result=dict(matches[0]);result['source_checks']=checks;result['matched_sources']=[x['source'] for x in matches]
        return result,'照合済み / '+str(checks)
    errors=any('通信失敗' in x['result'] for x in checks)
    return None,('通信失敗 / ' if errors else '配布元未特定 / ')+str(checks)
