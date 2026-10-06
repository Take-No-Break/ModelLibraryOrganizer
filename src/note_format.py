from pathlib import Path
from html.parser import HTMLParser
import re

class PlainDescription(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.parts=[];self.hidden=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'):self.hidden+=1
        if not self.hidden and tag in ('p','div','br','li','h1','h2','h3','h4','tr'):self.parts.append('\n')
    def handle_endtag(self,tag):
        if tag in ('script','style'):self.hidden=max(0,self.hidden-1)
        if not self.hidden and tag in ('p','div','li','h1','h2','h3','h4','tr'):self.parts.append('\n')
    def handle_data(self,data):
        if not self.hidden:self.parts.append(data)

def plain(value):
    value=str(value or '')
    if not re.search(r'</?[a-zA-Z][^>]*>',value):return value
    parser=PlainDescription();parser.feed(value)
    return re.sub(r'\n[ \t]*\n+', '\n\n',''.join(parser.parts)).strip()

def readable(value,indent=''):
    if isinstance(value,dict):
        return '\n'.join(indent+str(k)+':\n'+readable(v,indent+'  ') for k,v in value.items() if k!='images')
    if isinstance(value,list):return '\n'.join(readable(v,indent) for v in value)
    return '\n'.join(indent+line for line in plain(value).splitlines())

def note_content(row,sections=None):
    info=row.get('info',{})
    lines=['Model Library Organizer — Source information','', 'Model: '+row.get('title',''),
      'Filename: '+Path(row['source']).name,'Source: '+(row.get('url') or 'Unknown'),
      'Type: '+row.get('kind',''),'Base model family: '+row.get('family',''),
      'Creator / organization: '+(row.get('author') or info.get('author') or 'Unknown'),
      'SHA256: '+row.get('sha',''),'Confidence: '+row.get('confidence',''),'Evidence: '+row.get('evidence',''),
      '', 'Trigger words: '+(', '.join(info.get('triggers',[])) or 'Not available / not retrieved'),
      '', '[Model description]',plain(info.get('model_description','')),
      '', '[Version description]',plain(info.get('description','')),
      '', '[Public metadata]',readable({k:v for k,v in info.items() if k not in ('model_description','description','images','triggers')}),
      '', '[Lookup results]',readable({'matched_sources':row.get('matched_sources',[]),'source_checks':row.get('source_checks',[])}),
      '', '[File metadata]',readable(row.get('metadata',{})),
      '', 'A shared model family does not guarantee compatibility or results with every checkpoint.','']
    if sections is not None:
        sections=set(sections)|{'triggers'}
        markers={'Trigger words: ':'triggers','[Model description]':'description','[Version description]':'description','[Public metadata]':'public','[Lookup results]':'lookup','[File metadata]':'metadata'}
        enabled=True;filtered=[]
        for line in lines:
            for marker,key in markers.items():
                if line.startswith(marker):enabled=key in sections;break
            if line.startswith('A shared model family'):enabled=True
            if enabled:filtered.append(line)
        lines=filtered
    return '\n'.join(lines)
