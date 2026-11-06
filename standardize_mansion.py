#!/usr/bin/env python3
"""Idempotent, dependency-free cleanup of an existing Mythra's Mansion checkout.
Run from the repository root. Creates no commits/pushes by itself.
"""
from pathlib import Path
from urllib.parse import urlsplit,unquote
from html.parser import HTMLParser
from collections import Counter
import re, sys

ROOT=Path.cwd()
ROOMS=['','library/','workshop/','archives/','residents/','writing/','resources/','about/']
LABELS=['Foyer','Library','Workshop','Archives','Residents','Writing','The Resource Wing','About']
PAGES=['index.html']+[r+'index.html' for r in ROOMS[1:]]+['resources/did/index.html','resources/transgender/index.html','resources/mental-health/index.html']

def require(path):
    f=ROOT/path
    if not f.is_file():
        raise FileNotFoundError(f'Missing {path}. Run this from your current Mansion repository root.')
    return f

def change(path,text):
    f=require(path)
    if f.read_text(encoding='utf-8') != text:
        f.write_text(text,encoding='utf-8')
        print('Updated',path)


def standardize():
    for path in PAGES:
        f=require(path);html=f.read_text(encoding='utf-8')
        up='../'*(len(Path(path).parts)-1)
        section='resources/' if path.startswith('resources/') else ('' if path=='index.html' else path.split('/')[0]+'/')
        nav='<nav class="main-nav" aria-label="Main navigation">\n'+'\n'.join('          <a href="'+up+room+'"'+(' aria-current="page"' if room==section else '')+'>'+label+'</a>' for room,label in zip(ROOMS,LABELS))+'\n        </nav>'
        html,ns=re.subn(r'<nav class="main-nav" aria-label="Main navigation">[\s\S]*?</nav>',lambda m:nav,html,count=1)
        if ns!=1: raise ValueError('Missing expected navigation on '+path)
        if path=='residents/index.html':
            match=re.search(r'<style>([\s\S]*?)</style>',html)
            if match:
                resident_css=match.group(1).strip()+'''\n\n/* Link to companion clinical resources */
.residents-reference{border-left:2px solid var(--rose);padding-left:15px}
.residents-reference a{color:var(--rose-light);text-decoration:underline;text-underline-offset:3px}
.residents-reference a:hover{color:var(--rose)}
'''
                (ROOT/'residents/residents.css').write_text(resident_css,encoding='utf-8')
                html=html[:match.start()]+html[match.end():]
            elif not (ROOT/'residents/residents.css').is_file():
                raise ValueError('Missing inline Residents styles and residents.css.')
            if 'href="residents.css"' not in html:
                html,ns=re.subn(r'(<link rel="stylesheet" href="\.\./CSS/style\.css(?:\?[^\"]*)?">)',r'\1\n  <link rel="stylesheet" href="residents.css">',html,count=1)
                if ns!=1:raise ValueError('Cannot insert Residents stylesheet reference.')
            anchor='<p>Here at Mythra\'s Mansion, we call ourselves the residents. The manor is an affectionate metaphor, but the experiences behind these introductions are real.</p>'
            if 'class="residents-reference"' not in html:
                if anchor not in html: raise ValueError('Residents introduction changed; add resource cross-link manually.')
                html=html.replace(anchor,anchor+'\n        <p class="residents-reference">For clinical references and current research on DID, visit <a href="../resources/did/">the Resource Wing</a>. This introduction describes our lived experience, not everyone\'s.</p>',1)
        elif path=='resources/did/index.html':
            if 'class="resource-related"' not in html:
                marker='<nav class="resource-actions" aria-label="On this page">'
                if marker not in html: raise ValueError('DID resource navigation changed unexpectedly.')
                html=html.replace(marker,'<p class="resource-related"><strong>Personal perspective:</strong> <a href="../../residents/">Meet the residents</a> for one household\'s lived experience with DID. It does not represent everyone\'s experience.</p>'+marker,1)
        if path.startswith('resources/'):
            html=html.replace('Sources last checked: November 6, 2026. Links and service availability may change.', 'Resource list compiled November 6, 2026. Links, services, and evidence may change.')
        change(path,html)
    css=require('resources/resources.css').read_text(encoding='utf-8')
    if '.resource-related{' not in css:
        css+='''\n/* Link between research references and lived experience */
.resource-related{margin:12px 0 27px;border-left:2px solid var(--rose);padding:10px 15px;background:rgba(33,23,32,.35);font-size:13px;line-height:1.7;color:var(--muted)}
.resource-related strong{color:var(--ink)}
.resource-related a{color:var(--rose-light);text-decoration:underline;text-underline-offset:3px}
.resource-related a:hover{color:var(--rose)}
'''
        change('resources/resources.css',css)
    readme=require('README.md').read_text(encoding='utf-8')
    if 'residents/index.html` — household / residents (intentionally empty for now)' in readme:
        readme=readme.replace('residents/index.html` — household / residents (intentionally empty for now)','residents/index.html` — eight resident introductions (clinically diagnosed DID)')
    if '- `resources/index.html`' not in readme:
        insert='''- `resources/index.html` — Resource Wing directory (DID, transgender information, mental-health support)
- `resources/did/index.html` — clinical literature and references
- `resources/transgender/index.html` — clinical guidance and research
- `resources/mental-health/index.html` — mental-health support services
- `residents/residents.css` — residents-specific styling
- `resources/resources.css` — resource-specific styling
'''
        readme=readme.replace('- `writing/index.html`',insert+'- `writing/index.html`',1)
    readme=re.sub(r'Work on the `mansion-renovation` branch\. The old site is saved in `legacy`\.\s*Only merge to `main` when you want the public site replaced\.', '`main` is the published branch; `legacy` preserves the original homepage. Create a review branch for future changes.',readme)
    readme=readme.replace('Information about residents and personal writing is not published until you choose to add it.','Residents profiles were published by the author; respect their pronouns and descriptions. The Writing Room remains unfinished.')
    if 'scripts/check_site.py' not in readme:
        readme+='\n## Site validation\nRun `python3 scripts/check_site.py` from the repository root to check HTML headings, local paths, anchor targets and duplicate IDs. The script has no external dependencies.\n'
    change('README.md',readme)

class Parser(HTMLParser):
    def __init__(self):
        super().__init__();self.urls=[];self.ids=[];self.h1=0;self.external_blank=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):self.ids.append(a['id'])
        if tag=='h1':self.h1+=1
        for key in ['src','href']:
            if a.get(key):self.urls.append(a[key])
        if tag=='a' and a.get('target')=='_blank' and urlsplit(a.get('href','')).scheme in ('https','http'):
            if 'noopener' not in a.get('rel','').split():self.external_blank.append(a['href'])

def validate():
    errors=[]; cache={};refs=0
    def parse(path):
        if path not in cache:
            p=Parser();p.feed(path.read_text(encoding='utf-8'));cache[path]=p
        return cache[path]
    for rel in PAGES:
        f=require(rel);p=parse(f)
        if p.h1!=1:errors.append(f'{rel}: {p.h1} h1 headings')
        for id,num in Counter(p.ids).items():
            if num>1:errors.append(f'{rel}: duplicate id {id}')
        for href in p.external_blank:errors.append(f'{rel}: external link needs rel=noopener {href}')
        for href in p.urls:
            u=urlsplit(href)
            if u.scheme or u.netloc or href.startswith('//'):continue
            target=(f.parent/unquote(u.path)).resolve() if u.path else f
            if target.is_dir():target=target/'index.html'
            try:target.relative_to(ROOT.resolve())
            except ValueError:errors.append(f'{rel}: link leaves repo: {href}');continue
            if not target.is_file():errors.append(f'{rel}: missing path: {href}');continue
            if u.fragment and target.suffix.lower()=='.html' and unquote(u.fragment) not in parse(target).ids:
                errors.append(f'{rel}: missing anchor: {href}')
            refs+=1
    if errors:
        print('FAIL: '+str(len(errors))+' issues')
        print('\n'.join(' - '+x for x in errors));return 1
    print(f'PASS: {len(PAGES)} HTML pages, {refs} local references checked.');return 0

if __name__=='__main__':
    try:
        if '--check-only' not in sys.argv:standardize()
        sys.exit(validate())
    except (FileNotFoundError,ValueError) as e:
        print('ERROR:',e,file=sys.stderr);sys.exit(2)
