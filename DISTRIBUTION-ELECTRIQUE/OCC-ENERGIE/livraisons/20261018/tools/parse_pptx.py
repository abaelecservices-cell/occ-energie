"""Extrait la géométrie des diapositives PowerPoint (formes, textes, connecteurs, images).

Coordonnées de sortie en points (1 pt = 12700 EMU), repère de la diapositive.
Usage : py -3 -I parse_pptx.py <fichier.pptx> <out.json>
"""
import sys, json, zipfile, re
import xml.etree.ElementTree as ET

NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
EMU = 12700.0
z = zipfile.ZipFile(sys.argv[1])
pres = ET.fromstring(z.read('ppt/presentation.xml'))
sz = pres.find('p:sldSz', NS)
W, H = int(sz.get('cx')) / EMU, int(sz.get('cy')) / EMU
slides = sorted([n for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$', n)], key=lambda s: int(re.findall(r'\d+', s)[-1]))

def xfrm_of(el):
    x = el.find('.//a:xfrm', NS)
    if x is None: return None
    off, ext = x.find('a:off', NS), x.find('a:ext', NS)
    if off is None or ext is None: return None
    return dict(x=int(off.get('x')) / EMU, y=int(off.get('y')) / EMU, w=int(ext.get('cx')) / EMU, h=int(ext.get('cy')) / EMU,
                fh=x.get('flipH') == '1', fv=x.get('flipV') == '1', rot=int(x.get('rot', '0')) / 60000)

def color(el):
    if el is None: return None
    c = el.find('.//a:srgbClr', NS)
    if c is not None: return '#' + c.get('val')
    c = el.find('.//a:schemeClr', NS)
    return 'scheme:' + c.get('val') if c is not None else None

def text(el):
    paras = []
    for p in el.findall('.//a:p', NS):
        t = ''.join(r.text or '' for r in p.findall('.//a:t', NS))
        if t.strip(): paras.append(t.strip())
    return ' '.join(paras)

def walk(parent, tf, out, rels):
    # tf : fonction (x, y, w, h) -> coordonnées diapositive
    for el in parent:
        tag = el.tag.split('}')[1]
        if tag == 'grpSp':
            gx = el.find('p:grpSpPr/a:xfrm', NS)
            off, ext, cho, che = (gx.find('a:' + k, NS) for k in ('off', 'ext', 'chOff', 'chExt'))
            ox, oy, ew, eh = int(off.get('x')), int(off.get('y')), int(ext.get('cx')), int(ext.get('cy'))
            cx, cy, cw, ch = int(cho.get('x')), int(cho.get('y')), int(che.get('cx')) or 1, int(che.get('cy')) or 1
            sx, sy = ew / cw, eh / ch
            def tf2(x, y, w, h, tf=tf, ox=ox, oy=oy, cx=cx, cy=cy, sx=sx, sy=sy):
                return tf((ox + (x * EMU - cx) * sx) / EMU, (oy + (y * EMU - cy) * sy) / EMU, w * sx, h * sy)
            walk(el, tf2, out, rels)
        elif tag in ('sp', 'cxnSp', 'pic'):
            xf = xfrm_of(el.find('p:spPr', NS) if tag != 'pic' else el.find('p:spPr', NS))
            if not xf: continue
            x, y, w, h = tf(xf['x'], xf['y'], xf['w'], xf['h'])
            sppr = el.find('p:spPr', NS)
            geom = sppr.find('a:prstGeom', NS)
            ln = sppr.find('a:ln', NS)
            item = dict(kind=tag, x=round(x, 2), y=round(y, 2), w=round(w, 2), h=round(h, 2), fh=xf['fh'], fv=xf['fv'], rot=xf['rot'],
                        geom=geom.get('prst') if geom is not None else None,
                        fill=color(sppr.find('a:solidFill', NS)), line=color(ln) if ln is not None else None,
                        lw=round(int(ln.get('w', '12700')) / EMU, 2) if ln is not None else None,
                        head=(ln.find('a:headEnd', NS).get('type') if ln is not None and ln.find('a:headEnd', NS) is not None else None),
                        tail=(ln.find('a:tailEnd', NS).get('type') if ln is not None and ln.find('a:tailEnd', NS) is not None else None),
                        text=text(el))
            if tag in ('sp', 'cxnSp') and item['line'] is None:
                st = el.find('p:style/a:lnRef', NS)
                if st is not None: item['line'] = color(st) or 'style'
            if tag == 'pic':
                b = el.find('.//a:blip', NS)
                item['img'] = rels.get(b.get('{%s}embed' % NS['r'])) if b is not None else None
            out.append(item)

res = dict(w=W, h=H, slides=[])
for s in slides:
    root = ET.fromstring(z.read(s))
    relp = s.replace('slides/', 'slides/_rels/') + '.rels'
    rels = {}
    if relp in z.namelist():
        for r in ET.fromstring(z.read(relp)):
            rels[r.get('Id')] = r.get('Target')
    out = []
    walk(root.find('p:cSld/p:spTree', NS), lambda x, y, w, h: (x, y, w, h), out, rels)
    res['slides'].append(dict(name=s.split('/')[-1], items=out))
json.dump(res, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
for s in res['slides']:
    print(s['name'], len(s['items']), [i['text'][:28] for i in s['items'] if i['text']][:60])
