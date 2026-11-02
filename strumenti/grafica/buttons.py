"""Replace the Ledger/Mail button labels (46x22, 32-bit BGRA) with Italian text.

The old text is removed by interpolating the paper colour along each row between
the nearest clean pixels; the new text comes from GDI coverage masks rendered by
render.ps1 (Georgia 12px), blended with the original ink colour.
"""
import os
import struct
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spr  # noqa: E402

W, H = 46, 22
BASELINE = 13  # bottom row of capitals in the original labels
INNER = (2, 1, 44, 21)  # x0, y0, x1, y1 (exclusive) inside the border
TEXT_ROWS = (5, 18)
SHADOW = 0.15
TARGETS = {180: ("Conti", False), 181: ("Conti", True), 182: ("Posta", False), 183: ("Posta", True)}
HERE = os.path.dirname(os.path.abspath(__file__))


def lum(p):
    return (p[2] * 3 + p[1] * 6 + p[0]) / 10  # BGRA


def render_mask(text, workdir, bold=False):
    out = os.path.join(workdir, f"mask_{text}{'_b' if bold else ''}.bin")
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
           os.path.join(HERE, "render.ps1"), "-Text", text, "-Size", "12", "-Out", out]
    subprocess.run(cmd + (["-Bold"] if bold else []), check=True)
    d = open(out, "rb").read()
    w, h = struct.unpack_from("<ii", d)
    m = d[8:]
    pts = [(x, y) for y in range(h) for x in range(w) if m[y * w + x] > 20]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts) + 1
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts) + 1
    return [[m[y * w + x] for x in range(x0, x1)] for y in range(y0, y1)]


def faux_bold(mask, strength=0.5):
    """Thicken strokes by blending in a copy shifted 1px right."""
    return [[max(row[x], round((row[x - 1] if x else 0) * strength)) for x in range(len(row))]
            + [round(row[-1] * strength)] for row in mask]


def redraw(old, mask):
    px = [list(old[k * 4:k * 4 + 4]) for k in range(W * H)]
    x0, y0, x1, y1 = INNER
    ink = min(px, key=lum)
    # remove old text: mark dark pixels (plus 1px halo) and interpolate the paper
    for y in range(y0, y1):
        row = [px[y * W + x] for x in range(x0, x1)]
        # the old label (with its light shadow) spans rows 5..17 and columns 3..42
        bad = [TEXT_ROWS[0] <= y < TEXT_ROWS[1] and 1 <= i < len(row) - 1 for i in range(len(row))]
        for i in range(len(row)):
            if not bad[i]:
                continue
            l = next((j for j in range(i, -1, -1) if not bad[j]), None)
            r = next((j for j in range(i, len(row)) if not bad[j]), None)
            if l is None:
                l = r
            if r is None:
                r = l
            t = 0 if r == l else (i - l) / (r - l)
            px[y * W + x0 + i] = [round(row[l][c] * (1 - t) + row[r][c] * t) for c in range(4)]
    # draw new text centred, capitals sitting on BASELINE
    mh, mw = len(mask), len(mask[0])
    ox = (W - mw) // 2
    oy = BASELINE - mh + 1
    # faint shadow 1px below, as in the original labels
    for my in range(mh):
        for mx in range(mw):
            a = mask[my][mx] / 255 * SHADOW
            k = (oy + my + 1) * W + ox + mx
            if a > 0:
                p = px[k]
                px[k] = [round(p[c] * (1 - a) + ink[c] * a) for c in range(3)] + [p[3]]
    for my in range(mh):
        for mx in range(mw):
            a = mask[my][mx] / 255
            if a <= 0:
                continue
            k = (oy + my) * W + ox + mx
            p = px[k]
            px[k] = [round(p[c] * (1 - a) + ink[c] * a) for c in range(3)] + [p[3]]
    return bytes(v for p in px for v in p)


def redraw_all(d, workdir):
    sprites = spr.read_index(d)
    masks = {}
    out = {}
    for i, (text, bold) in TARGETS.items():
        s = sprites[i]
        assert (s["w"], s["h"], s["fmt"], s["bpp"]) == (W, H, 0, 4), s
        # normal labels: regular weight thickened by 1px; highlighted labels: real bold
        if (text, bold) not in masks:
            m = render_mask(text, workdir, bold)
            masks[(text, bold)] = m if bold else faux_bold(m)
        m = masks[(text, bold)]
        old = d[s["data_off"]:s["data_off"] + W * H * 4]
        out[i] = (old, redraw(old, m), s["data_off"])
    return out
