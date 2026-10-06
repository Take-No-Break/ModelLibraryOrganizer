"""Readable duplicate reports, including legacy saved JSON reports."""
import json
from pathlib import Path
from i18n import tr

def size(value):
    for unit in ['B','KiB','MiB','GiB','TiB']:
        if value<1024 or unit=='TiB':return f'{value:.1f} {unit}'
        value/=1024

def parse(text):
    # Legacy records used a short introduction followed by a JSON array.
    for i,c in enumerate(text):
        if c!='[':continue
        try:groups=json.loads(text[i:])
        except ValueError:continue
        if isinstance(groups,list) and all(isinstance(g,dict) and 'files' in g and 'physical_copies' in g for g in groups):return groups
    return None

def format_report(groups):
    copies=sum(g['physical_copies']>1 for g in groups)
    links=len(groups)-copies
    lines=[tr('同じ内容のファイル：')+str(len(groups))+tr('組'),
           tr('重複コピー：')+str(copies)+tr('組')+' / '+tr('ハードリンクのみ：')+str(links)+tr('組'),
           tr('重複コピーの容量：')+size(sum(g['extra_bytes'] for g in groups)),
           tr('ファイルは削除・移動していません。'),
           tr('ハードリンクは同じ実体を別のパスから参照します。容量の重複ではありません。'), '']
    for i,g in enumerate(groups,1):
        state=tr('ハードリンクのみ（追加容量なし）') if g['physical_copies']==1 else tr('独立した重複コピーあり')
        lines.extend([f'{i}. {state}',tr('表示パス数：')+str(len(g['files']))+' / '+tr('実体数：')+str(g['physical_copies']),
                      tr('余分に使用する容量：')+size(g['extra_bytes'])])
        identities={}
        for file in g['files']:
            key=tuple(file.get('identity',[file['path']]))
            identities.setdefault(key,len(identities)+1)
            lines.append('  '+tr('実体')+str(identities[key])+' — '+file['path'])
        lines.extend(['  SHA256: '+g['sha256'],''])
    return '\n'.join(lines)
