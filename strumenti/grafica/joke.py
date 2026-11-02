"""Redraw the title-screen joke (sprites 482 and 483) in Italian.

Both sprites are 307x35, 16-bit palette format with 2 colours (0 = transparent
magenta, 1 = white). Glyphs are cut from the original lines by column runs;
'U' and the accent of 'é' are drawn by hand in the same style.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spr  # noqa: E402

W, H = 307, 35
BAND = 13  # glyph rows: cap height 10 + descender 3

# line bands (first row) in the original sprites
L1, L2, L483 = 3, 20, 13

# glyph sources: char -> (sprite, band row, first run, last run, split)
# runs are column groups separated by empty columns, counted per line;
# split = (offset, width) to take part of a run where letters touch
SOURCES = {
    "A": (482, L1, 0, 0, None), "g": (482, L1, 1, 1, None), "o": (482, L1, 2, 2, None),
    "y": (482, L1, 3, 3, None), "c": (482, L1, 4, 4, None), "m": (482, L1, 5, 5, (7, 13)),
    "e": (482, L1, 6, 6, None), "u": (482, L1, 7, 7, None), "p": (482, L1, 8, 8, None),
    "t": (482, L1, 9, 9, None), "R": (482, L1, 11, 11, None),
    "b": (482, L1, 13, 13, None), "i": (482, L1, 14, 14, None),
    "M": (482, L1, 15, 15, None), "s": (482, L1, 18, 18, None), "h": (482, L1, 19, 19, None),
    "a": (482, L1, 23, 23, None), ",": (482, L1, 26, 26, None), "<": (482, L1, 27, 28, None),
    "d": (482, L2, 0, 0, None), "r": (482, L2, 2, 2, None), "l": (482, L2, 8, 8, None),
    "n": (482, L2, 13, 13, None), "?": (482, L2, 31, 31, None), ">": (482, L2, 32, 33, None),
    "{": (483, L483, 24, 25, None), "}": (483, L483, 32, 33, None),
}
# '<' '>' = straight quotes of sprite 482, '{' '}' = curly quotes of sprite 483

U = ["###...###"] + [".#.....#."] * 7 + ["..#...#..", "...###..."] + ["........."] * 3
SPACE, GAP = 5, 1

TEXTS = {
    482: [(L1, 'Un goy chiese a Rabbi Moishe, <Perché'),
          (L2, 'i rabbini rispondono sempre con domande?>')],
    483: [(L483, 'Al che Rabbi Moishe rispose, {Perché no?}')],
}


def runs(px, y0):
    cols = [any(px[y * W + x] for y in range(y0, y0 + BAND)) for x in range(W)]
    out, x = [], 0
    while x < W:
        if cols[x]:
            a = x
            while x < W and cols[x]:
                x += 1
            out.append((a, x))
        else:
            x += 1
    return out


def glyphs(data):
    sprites = spr.read_index(data)
    pix = {i: data[sprites[i]["data_off"]:sprites[i]["data_off"] + W * H] for i in (482, 483)}
    lib = {}
    for ch, (i, y0, r0, r1, split) in SOURCES.items():
        r = runs(pix[i], y0)
        a, b = r[r0][0], r[r1][1]
        if split:
            a, b = a + split[0], a + split[0] + split[1]
        lib[ch] = [[pix[i][(y0 + y) * W + x] for x in range(a, b)] for y in range(BAND)]
    lib["U"] = [[1 if c == "#" else 0 for c in row] for row in U]
    # P = R without the diagonal leg
    p = [row[:] for row in lib["R"][:5]]
    p += [[0, 1, 0, 0, 0, 0, 0, 0] for _ in range(4)] + [[1, 1, 1, 0, 0, 0, 0, 0]]
    lib["P"] = p + [[0] * 8 for _ in range(BAND - len(p))]
    e = [row[:] for row in lib["e"]]
    e[0][4] = 1
    e[1][3] = 1
    lib["é"] = e
    return sprites, pix, lib


def compose(lines, lib):
    px = bytearray(W * H)
    for y0, text in lines:
        x = 3
        for n, ch in enumerate(text):
            if ch == " ":
                x += SPACE
                continue
            g = lib[ch]
            for gy, row in enumerate(g):
                for gx, v in enumerate(row):
                    if v:
                        px[(y0 + gy) * W + x + gx] = 1
            x += len(g[0]) + GAP
        if x > W:
            raise ValueError(f"line too wide ({x} px): {text}")
    return px


def redraw(data):
    sprites, pix, lib = glyphs(data)
    out = {}
    for i, lines in TEXTS.items():
        s = sprites[i]
        assert (s["w"], s["h"], s["fmt"], s["palcnt"]) == (W, H, 34, 1), s
        out[i] = (pix[i], bytes(compose(lines, lib)), s["data_off"])
    return out


if __name__ == "__main__":
    data = open(sys.argv[1], "rb").read()
    _, pix, lib = glyphs(data)
    for ch in "AmM<>{}?é":
        print(repr(ch))
        for row in lib[ch]:
            print("".join("#" if v else "." for v in row))
