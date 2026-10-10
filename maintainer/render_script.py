"""Render a vendor fmxmlsnippet example as readable FileMaker script steps.

The skill ships readable steps only: with Claris ADT, scripts are written into the file
directly, so clipboard XML is never needed. Used by build_catalog.py.
"""
import re
import xml.etree.ElementTree as ET
OPEN={'If','Loop'}; MID={'Else','Else If'}; CLOSE={'End If','End Loop'}
def calc(e): return (e.text or '').strip() if e is not None else ''
def step(s):
    n=s.get('name'); dis='' if s.get('enable','True')=='True' else '// '
    if n=='# (comment)': return dis+'# '+(s.findtext('Text') or '').strip()
    if n=='Set Variable':
        v=calc(s.find('Value/Calculation')); r=calc(s.find('Repetition/Calculation')); nm=(s.findtext('Name') or '').strip()
        return f"{dis}Set Variable [ {nm}{'['+r+']' if r and r!='1' else ''} ; Value: {v} ]"
    parts=[]
    f=s.find('Field')
    if f is not None and f.get('name'): parts.append((f.get('table')+'::' if f.get('table') else '')+f.get('name'))
    for tag in ('Layout','Script'):
        e=s.find(tag)
        if e is not None and e.get('name'): parts.append(f'"{e.get("name")}"')
    if n=='Show Custom Dialog':
        t=calc(s.find('Title/Calculation')); m=calc(s.find('Message/Calculation'))
        parts += [p for p in (t,m) if p]
    else:
        for c in s.findall('Calculation')+s.findall('*/Calculation'):
            if c in [s.find('Repetition/Calculation')]: continue
            t=calc(c)
            if t: parts.append(t)
    return f"{dis}{n}" + (f" [ {' ; '.join(parts)} ]" if parts else '')
def render(x):
    r=ET.fromstring(x.encode()); out=[]; d=0
    for s in r.iter('Step'):
        n=s.get('name')
        if n in CLOSE or n in MID: d=max(d-1,0)
        out.append('    '*d+step(s))
        if n in OPEN or n in MID: d+=1
    return '\n'.join(out)

XML_BLOCK = re.compile(r'\s*<\?xml[^>]*\?>\s*<fmxmlsnippet\b.*?</fmxmlsnippet>\s*', re.S)
def strip_xml(text):
    """Remove any fmxmlsnippet blocks the vendor page carried inside prose sections."""
    return XML_BLOCK.sub(' ', text).strip() if text else text

# Sections the vendor page prints after the description. The HTML parser sometimes runs them
# into the description text; cut at the first one.
TAIL = re.compile(r'\s(?:Examples\s.{0,160}?Copy Text Copy XML|Release notes\s+Version\s|Example Databases\s|'
                  r'Blog Entries\s|FileMaker Magazin\s|This function (?:checks for a license|is free to use)\.|'
                  r'Created \d)', re.S)
def trim_description(text):
    if not text:
        return text
    m = TAIL.search(text)
    return text[:m.start()].strip() if m else text
