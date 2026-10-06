"""Tag frequency means TXT document frequency, not model confidence."""
from pathlib import Path
from collections import Counter
from dataset_files import list_dataset,read_caption,make_change

def split_tags(text):
    # Preserve commas within common prompt/embedding bracket groups.
    tags=[];start=0;stack=[];closing={')':'(',']':'[','>':'<'}
    for i,char in enumerate(text):
        if char in '([<':stack.append(char)
        elif char in closing and stack and stack[-1]==closing[char]:stack.pop()
        elif char in ',\r\n' and not stack:
            tag=text[start:i].strip()
            if tag:tags.append(tag)
            start=i+1
    tag=text[start:].strip()
    if tag:tags.append(tag)
    return tags

def load_tags(folder,recursive=False):
    records=[]
    for item in list_dataset(folder,recursive):
        if Path(item['text_path']).name.lower().endswith('.source.txt'):continue
        state=read_caption(item['text_path'])
        records.append({**item,'state':state,'draft':state['text']})
    return records

def frequencies(records):
    usable=[r for r in records if r['state']['raw'] is not None or r['draft']!=r['state']['text']]
    counts=Counter(tag for record in usable for tag in set(split_tags(record['draft'])))
    return len(usable),sorted(counts.items(),key=lambda pair:(-pair[1],pair[0]))

def edit_tags(record,value,remove=False):
    requested=split_tags(value)
    if not requested:raise ValueError('Enter a non-empty tag.')
    original=split_tags(record['draft'])
    updated=[t for t in original if t not in requested] if remove else original+[t for t in dict.fromkeys(requested) if t not in original]
    if updated==original:return False
    record['draft']=', '.join(updated)+'\n' if updated else ''
    return True

def tag_changes(records):
    return [make_change(r['text_path'],r['draft'],r['state']) for r in records if r['draft']!=r['state']['text']]
