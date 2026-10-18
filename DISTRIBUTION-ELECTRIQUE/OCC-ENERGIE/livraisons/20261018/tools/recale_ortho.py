"""Recalage de l'ancienne vue aérienne (PowerPoint « site l ardoise », build/aerial.webp) sur l'orthophoto IGN (build/ortho_full.png).
Cherche la transformation affine ancienne image -> orthophoto qui minimise l'écart des contours (Pillow seul, descente par coordonnées
multi-échelle), écrit build/ortho_affine.json et une image de contrôle (superposition) dans le dossier donné.
Usage : py -3 -I tools/recale_ortho.py <dossier build> <dossier contrôle>
"""
import sys, json, os, math
from PIL import Image, ImageChops, ImageStat, ImageFilter, ImageOps
B, OUT = sys.argv[1], sys.argv[2]
old = Image.open(os.path.join(B, 'aerial.webp')).convert('RGBA')
ort = Image.open(os.path.join(B, 'ortho_full.png')).convert('RGBA')

def prep(im, k):
    im = im.resize((im.width // k, im.height // k), Image.LANCZOS)
    g = ImageOps.equalize(im.convert('L')).filter(ImageFilter.GaussianBlur(1.2)).filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(1.5))
    return g, im.getchannel('A').point(lambda v: 255 if v > 200 else 0)

def cost(p, k, O, Om, R, Rm):
    # p = (a, b, c, d, e, f) en pixels pleine résolution : X = a x + b y + c ; Y = d x + e y + f  (x, y : ancienne image ; X, Y : orthophoto)
    a, b, c, d, e, f = p
    q = (a, b, c / k, d, e, f / k)  # à l'échelle k, les translations sont divisées par k
    t = R.transform(O.size, Image.AFFINE, q, Image.BILINEAR)
    tm = Rm.transform(O.size, Image.AFFINE, q, Image.NEAREST)
    m = ImageChops.multiply(Om, tm)
    n = ImageStat.Stat(m).sum[0] / 255
    if n < 0.25 * O.width * O.height: return 1e9
    dif = ImageChops.multiply(ImageChops.difference(O, t), m)
    return ImageStat.Stat(dif).sum[0] / 255 / n

# point de départ : quart de tour (le haut de l'ancienne vue = l'est), échelle ≈ 1,27 (château d'eau et bassin)
p = [0.0, -1.27, 1984.0, 1.27, 0.0, -15.0]
steps = [0.02, 0.02, 30.0, 0.02, 0.02, 30.0]
for k in (8, 4, 2):
    O, Om = prep(old, k); R, Rm = prep(ort, k)
    best = cost(p, k, O, Om, R, Rm)
    for it in range(60):
        improved = False
        for i in range(6):
            for sgn in (1, -1):
                q = p[:]; q[i] += sgn * steps[i]
                c = cost(q, k, O, Om, R, Rm)
                if c < best: best, p, improved = c, q, True
        if not improved:
            steps = [s / 2 for s in steps]
            if steps[2] < 0.3 * k / 2: break
    print('échelle 1/%d : coût %.2f' % (k, best), [round(v, 4) for v in p])
    steps = [max(s, 0.004), max(s, 0.004), max(s, 4.0), max(s, 0.004), max(s, 0.004), max(s, 4.0)] if False else [0.006, 0.006, 8.0, 0.006, 0.006, 8.0]
a, b, c, d, e, f = p
json.dump(dict(oldW=old.width, oldH=old.height, A=[[a, b, c], [d, e, f]], cost=best,
               note='X_ortho = a·x_old + b·y_old + c ; Y_ortho = d·x_old + e·y_old + f (pixels)'), open(os.path.join(B, 'ortho_affine.json'), 'w'))
# contrôle visuel : ancienne vue projetée sur l'orthophoto en semi-transparence
det = a * e - b * d
inv = (e / det, -b / det, (b * f - e * c) / det, -d / det, a / det, (d * c - a * f) / det)
proj = old.transform(ort.size, Image.AFFINE, inv, Image.BILINEAR)
bg = Image.new('RGBA', ort.size, (20, 20, 20, 255)); bg.alpha_composite(ort)
pr = proj.copy(); pr.putalpha(proj.getchannel('A').point(lambda v: int(v * 0.5)))
bg.alpha_composite(pr)
bg.convert('RGB').resize((ort.width // 2, ort.height // 2)).save(os.path.join(OUT, 'recale_controle.jpg'), quality=82)
print('rotation ≈ %.2f°, échelles ≈ %.3f / %.3f' % (math.degrees(math.atan2(d, a)), math.hypot(a, d), math.hypot(b, e)))
