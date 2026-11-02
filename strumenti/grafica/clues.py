"""Compose the clue label sprites in Italian from glyphs cut out of existing labels.

Clue labels are 48x22, format 33, 4-colour palette. Normal labels use index 0 as
background and 1..3 as the text gradient; selected labels (dotted border) swap
index 0 and 1. Text rows are 5..13.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spr  # noqa: E402

W, H = 48, 22
TOP, BOTTOM = 5, 14  # text rows [TOP, BOTTOM)

# normal sprite id -> its text (used to cut glyphs)
SOURCES = {185: "Ethan G.", 186: "JDM", 187: "Joe DeMarco", 188: "Sharming",
           189: "Joe's Meeting", 195: "Joe Jewish?", 516: "Goldberg"}

# (normal sprite, selected sprite) -> new text
TARGETS = {(189, 395): "Joe e Ethan", (195, 393): "Joe ebreo?"}


def pixels(d, s):
    return bytearray(d[s["data_off"]:s["data_off"] + s["w"] * s["h"]])


def column_runs(px):
    """Split the text area into runs of non-empty columns."""
    cols = [any(px[y * W + x] for y in range(TOP, BOTTOM)) for x in range(W)]
    runs, x = [], 0
    while x < W:
        if cols[x]:
            a = x
            while x < W and cols[x]:
                x += 1
            runs.append((a, x))
        else:
            x += 1
    return runs


def cut(px, a, b):
    return [[px[y * W + x] for x in range(a, b)] for y in range(TOP, BOTTOM)]


def glyph_library(d, sprites):
    lib = {}
    for i, text in SOURCES.items():
        px = pixels(d, sprites[i])
        runs = column_runs(px)
        chars = [c for c in text if c != " "]
        if len(runs) != len(chars):
            print(f"  sprite {i}: {len(runs)} runs for {len(chars)} chars {text!r}, skipped")
            continue
        for c, (a, b) in zip(chars, runs):
            lib.setdefault(c, cut(px, a, b))
    return lib


def space_width(d, sprites):
    px = pixels(d, sprites[187])  # "Joe DeMarco": gap between 'e' and 'D'
    runs = column_runs(px)
    return runs[3][0] - runs[2][1]


def compose(old_px, text, lib, gap, selected):
    """Draw text centred in the text rows; selected sprites swap indexes 0 and 1."""
    px = bytearray(old_px)
    bg = 1 if selected else 0
    for y in range(TOP, BOTTOM):
        for x in range(2, W - 2):
            px[y * W + x] = bg
    parts = []
    for c in text:
        parts.append(None if c == " " else lib[c])
    width = 0
    for n, g in enumerate(parts):
        width += gap if g is None else len(g[0])
        if n < len(parts) - 1 and g is not None and parts[n + 1] is not None:
            width += 1
    if width > W - 4:
        raise ValueError(f"{text!r} is {width} px wide, max {W - 4}")
    x = (W - width) // 2
    for n, g in enumerate(parts):
        if g is None:
            x += gap
            continue
        for gy, row in enumerate(g):
            for gx, v in enumerate(row):
                if v:
                    v = {1: 0, 0: 1}.get(v, v) if selected else v
                    px[(TOP + gy) * W + x + gx] = v
        x += len(g[0])
        if n < len(parts) - 1 and parts[n + 1] is not None:
            x += 1
    return px


def redraw(d):
    """Return {sprite id: (old bytes, new bytes, data offset)} for all targets."""
    sprites = spr.read_index(d)
    lib = glyph_library(d, sprites)
    gap = space_width(d, sprites)
    out = {}
    for (normal, selected), text in TARGETS.items():
        for i, sel in ((normal, False), (selected, True)):
            s = sprites[i]
            assert (s["w"], s["h"], s["fmt"]) == (W, H, 33), s
            old = pixels(d, s)
            out[i] = (bytes(old), bytes(compose(old, text, lib, gap, sel)), s["data_off"])
    return out


if __name__ == "__main__":
    d = open(sys.argv[1], "rb").read()
    for i, (old, new, _) in redraw(d).items():
        print(i)
        for y in range(3, 15):
            print("".join(str(b) if b else "." for b in new[y * W:(y + 1) * W]))
