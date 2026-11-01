"""Build the AGS translation source (.trs) and compiled translation (.tra).

Usage: python build.py <project_dir> <output_basename> [--ascii] [--normal-font N] [--speech-font N]

--ascii           write accented letters as apostrophe forms (e' a' ...) for fonts
                  without accented glyphs
--normal-font N   override the game's normal font (font number) in this translation
--speech-font N   override the game's speech font
"""
import argparse
import glob
import json
import os
import re
import struct
import sys

AVIS = b"Avis Durgan"
ASCII_MAP = {"à": "a'", "è": "e'", "é": "e'", "ì": "i'", "ò": "o'", "ù": "u'",
             "À": "A'", "È": "E'", "É": "E'", "Ì": "I'", "Ò": "O'", "Ù": "U'"}


def load(project):
    cands = json.load(open(os.path.join(project, "cands.json"), encoding="utf-8"))
    tr = {}
    for fn in sorted(glob.glob(os.path.join(project, "tr", "*.txt"))):
        for n, line in enumerate(open(fn, encoding="utf-8"), 1):
            line = line.rstrip("\r\n")
            if not line.strip():
                continue
            idx, text = line.split("\t", 1)
            idx = int(idx)
            if idx in tr:
                sys.exit(f"{fn}:{n}: duplicate index {idx}")
            if idx >= len(cands):
                sys.exit(f"{fn}:{n}: index {idx} out of range")
            tr[idx] = text
    return cands, tr


def check(en, it):
    problems = []
    if re.findall(r"%[sdc]", en) != re.findall(r"%[sdc]", it):
        problems.append("format specifiers differ")
    m = re.match(r"&\d+ ", en)
    if m and not it.startswith(m.group()):
        problems.append("voice tag missing")
    if not m and re.match(r"&\d+", it):
        problems.append("unexpected voice tag")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("out")
    ap.add_argument("--ascii", action="store_true")
    ap.add_argument("--normal-font", type=int, default=-1)
    ap.add_argument("--speech-font", type=int, default=-1)
    a = ap.parse_args()

    info = json.load(open(os.path.join(a.project, "gameinfo.json"), encoding="utf-8"))
    utf8 = info.get("encoding") == "65001"
    codec = "utf-8" if utf8 else "cp1252"

    def cstring(s):
        b = s.encode(codec) + b"\x00"
        return struct.pack("<i", len(b)) + bytes((c + AVIS[i % len(AVIS)]) & 0xFF for i, c in enumerate(b))

    def block(btype, payload):
        return struct.pack("<iI", btype, len(payload)) + payload

    cands, tr = load(a.project)
    pairs, errors = [], 0
    for i, c in enumerate(cands):
        it = tr.get(i)
        if it is None:
            continue
        if a.ascii:
            it = "".join(ASCII_MAP.get(ch, ch) for ch in it)
        for p in check(c["en"], it):
            print(f"[{i}] {p}: {c['en']!r} -> {it!r}")
            errors += 1
        try:
            it.encode(codec)
        except UnicodeEncodeError as e:
            print(f"[{i}] not representable in {codec}: {e}")
            errors += 1
        pairs.append((c["en"], it))
    if errors:
        sys.exit(f"{errors} problems, nothing written")

    def opt(v):
        return "DEFAULT" if v < 0 else str(v)

    with open(a.out + ".trs", "w", encoding=codec, newline="\r\n") as f:
        f.write(f"//#GameId={info['uniqueid']}\n//#GameName={info['name']}\n")
        f.write(f"//#NormalFont={opt(a.normal_font)}\n//#SpeechFont={opt(a.speech_font)}\n")
        f.write("//#TextDirection=DEFAULT\n")
        if utf8:
            f.write("//#Encoding=UTF-8\n")
        for i, c in enumerate(cands):
            f.write(c["en"] + "\n" + tr.get(i, "") + "\n")

    content = b"".join(cstring(x) + cstring(y) for x, y in pairs) + cstring("") + cstring("")
    tra = b"AGSTranslation\x00"
    tra += block(2, struct.pack("<I", info["uniqueid"] & 0xFFFFFFFF) + cstring(info["name"]))
    tra += block(1, content)
    tra += block(3, struct.pack("<iii", a.normal_font, a.speech_font, -1))
    if utf8:
        # string options extension block (id 0, 16-char name, 64-bit size); untested in game
        opts = struct.pack("<i", 1)
        for s in ("encoding", "UTF-8"):
            opts += struct.pack("<i", len(s)) + s.encode("ascii")
        tra += struct.pack("<i", 0) + b"ext_sopts".ljust(16, b"\x00") + struct.pack("<q", len(opts)) + opts
    tra += block(-1, b"")
    open(a.out + ".tra", "wb").write(tra)
    print(f"translated {len(pairs)} of {len(cands)} strings -> {a.out}.tra ({len(tra)} bytes)")


if __name__ == "__main__":
    main()
