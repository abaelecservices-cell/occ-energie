"""Recalage de la photo aérienne fournie par l'exploitant (capture, nord en haut) sur l'orthophoto IGN (build/ortho_full.png).
Cherche la transformation affine photo -> orthophoto qui minimise l'écart des contours (Pillow seul, descente par coordonnées),
écrit build/photo_affine.json (orthophoto -> photo, pour reporter les repères) et une image de contrôle.
Usage : py -3 -I tools/recale_photo.py <photo> <dossier build> <dossier contrôle>
"""
import sys, json, os
from PIL import Image, ImageChops, ImageStat, ImageFilter, ImageOps
PH, B, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
pho = Image.open(PH).convert('RGB')
ort = Image.open(os.path.join(B, 'ortho_full.png')).convert('RGBA')
K = 4  # orthophoto réduite au 1/4 (résolution proche de la capture)
ors = ort.resize((ort.width // K, ort.height // K), Image.LANCZOS)
edge = lambda im: ImageOps.equalize(im.convert('L')).filter(ImageFilter.GaussianBlur(1.0)).filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(1.2))
O, R = edge(pho), edge(ors)
Om = Image.new('L', pho.size, 255)
Rm = ors.getchannel('A').point(lambda v: 255 if v > 200 else 0)

def cost(q):  # q : photo (x, y) -> orthophoto réduite (X, Y) = (a x + b y + c, d x + e y + f)
    t = R.transform(O.size, Image.AFFINE, tuple(q), Image.BILINEAR)
    m = ImageChops.multiply(Om, Rm.transform(O.size, Image.AFFINE, tuple(q), Image.NEAREST))
    n = ImageStat.Stat(m).sum[0] / 255
    if n < 0.2 * O.width * O.height: return 1e9
    return ImageStat.Stat(ImageChops.multiply(ImageChops.difference(O, t), m)).sum[0] / 255 / n

# point de départ : toit principal de l'usine (capture x 90-225 ↔ orthophoto x 560-1320), nord en haut
s = 5.62 / K
q = [s, 0.0, 56.0 / K, 0.0, s, 31.0 / K]
steps = [0.04, 0.04, 6.0, 0.04, 0.04, 6.0]
best = cost(q)
for rnd in range(4):
    for it in range(80):
        imp = False
        for i in range(6):
            for sg in (1, -1):
                t = q[:]; t[i] += sg * steps[i]; c = cost(t)
                if c < best: best, q, imp = c, t, True
        if not imp:
            steps = [v / 2 for v in steps]
            if steps[2] < 0.15: break
    steps = [0.01, 0.01, 2.0, 0.01, 0.01, 2.0]
print('coût', round(best, 3), [round(v, 4) for v in q])
a, b, c, d, e, f = [v * K for v in q]          # photo -> orthophoto pleine résolution
det = a * e - b * d                              # inverse : orthophoto -> photo
inv = [[e / det, -b / det, (b * f - e * c) / det], [-d / det, a / det, (d * c - a * f) / det]]
json.dump(dict(photo=os.path.basename(PH), pw=pho.width, ph=pho.height, ortho_to_photo=inv, photo_to_ortho=[[a, b, c], [d, e, f]], cost=best), open(os.path.join(B, 'photo_affine.json'), 'w'))
# contrôle : contours de l'orthophoto superposés à la capture
t = ors.transform(pho.size, Image.AFFINE, tuple(q), Image.BILINEAR)
mix = pho.convert('RGBA').copy(); t.putalpha(t.getchannel('A').point(lambda v: v // 2)); mix.alpha_composite(t)
mix.convert('RGB').resize((pho.width * 2, pho.height * 2)).save(os.path.join(OUT, 'photo_recale.jpg'), quality=88)
