"""Redraw the CLUES tab sprites as INDIZI and compute byte patches for Shivah.exe.

Usage: python tabpatch.py <Shivah.exe> <out.json> [--preview out.png]

The tab sprites are stored uncompressed as 8-bit indexes (format 33), so the new
text keeps the sprite size and only pixel bytes change: the patch is a list of
(file offset, original byte, new byte) for the game executable.
"""
import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spr  # noqa: E402

TAB_SPRITES = (561, 567, 568, 569)
TEXT = "INDIZI"
GLYPHS = {  # 5x5, '#' = ink
    "I": ["#####", "..#..", "..#..", "..#..", "#####"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#"],
    "D": ["####.", "#...#", "#...#", "#...#", "####."],
    "Z": ["#####", "...#.", "..#..", ".#...", "#####"],
}


def clib_asset(exe, name):
    """Return the absolute file offset and size of an asset in the appended CLIB."""
    with open(exe, "rb") as f:
        f.seek(-20, 2)
        off = struct.unpack("<Q", f.read(8))[0]
        f.seek(off)
        assert f.read(7) == b"CLIB\x1a\x1e\x00"
        f.read(4)
        nfiles = struct.unpack("<i", f.read(4))[0]
        for _ in range(nfiles):
            while f.read(1) != b"\x00":
                pass
        for _ in range(struct.unpack("<i", f.read(4))[0]):
            n = bytearray()
            while (c := f.read(1)) != b"\x00":
                n += c
            f.read(1)
            o, s = struct.unpack("<qq", f.read(16))
            if n.decode("latin1") == name:
                return off + o, s
    raise KeyError(name)


def redraw(pixels, w, h):
    """Return new pixel indexes with TEXT drawn over the old label."""
    px = bytearray(pixels)
    rows = [y for y in range(h) if any(px[y * w + x] for x in range(4, w - 4))]
    text_rows = [y for y in rows if 4 < y < h - 4]
    assert len(text_rows) == 5, text_rows
    colors = []
    for y in text_rows:
        c = {px[y * w + x] for x in range(4, w - 4) if px[y * w + x]}
        assert len(c) == 1, (y, c)
        colors.append(c.pop())
    for y in text_rows:
        for x in range(1, w - 1):
            px[y * w + x] = 0
    width = len(TEXT) * 6 - 1
    x0 = (w - width) // 2
    for n, ch in enumerate(TEXT):
        for gy, line in enumerate(GLYPHS[ch]):
            for gx, c in enumerate(line):
                if c == "#":
                    px[text_rows[gy] * w + x0 + n * 6 + gx] = colors[gy]
    return bytes(px)


def main():
    exe, out = sys.argv[1], sys.argv[2]
    base, size = clib_asset(exe, "acsprset.spr")
    with open(exe, "rb") as f:
        f.seek(base)
        data = f.read(size)
    sprites = spr.read_index(data)
    patch, previews = [], []
    for i in TAB_SPRITES:
        s = sprites[i]
        assert s["fmt"] == 33 and s["comp"] == 0 and (s["w"], s["h"]) == (39, 22), s
        old = data[s["data_off"]:s["data_off"] + s["w"] * s["h"]]
        new = redraw(old, s["w"], s["h"])
        for k, (a, b) in enumerate(zip(old, new)):
            if a != b:
                patch.append([base + s["data_off"] + k, a, b])
        previews.append((s, new))
    json.dump({"asset_offset": base, "asset_size": size, "patch": patch}, open(out, "w"), indent=0)
    print(f"{len(patch)} bytes to change")
    for s, new in previews:
        print(s["i"])
        for y in range(s["h"]):
            print("".join(str(b) if b else "." for b in new[y * s["w"]:(y + 1) * s["w"]]))
        break


if __name__ == "__main__":
    main()
