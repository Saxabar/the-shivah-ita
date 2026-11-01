"""Extract translatable strings from a compiled AGS game.

Usage: python extract.py <game.exe|game.ags> <project_dir> [--skip-script NAME ...] [--force]

Creates in <project_dir>:
  data/            assets extracted from the game archive (can be deleted later)
  gameinfo.json    game name, unique id, text encoding, counts
  cands.json       candidate strings, in order; translations refer to their index
  rejected.json    strings filtered out as non-text (check it once)
  tr/              put translation files here (see README)
"""
import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agsdata  # noqa: E402

DEFAULT_NAMES = re.compile(
    r"^(New Button|New Label|No hotspot|Hotspot \d+|Object \d+|Region \d+|Sample\w*|textencoding|ext_sopts)$")


def is_text(s):
    if not s or s.startswith("__NEWSCRIPTSTART"):
        return False
    if not re.search(r"[^\W\d_]", s):
        return False
    if " " not in s:
        if re.fullmatch(r"[a-z_][A-Za-z0-9_]*", s):        # identifiers, keywords
            return False
        if re.fullmatch(r"[A-Z0-9_]+", s):                  # CONSTANT_NAMES, single letters
            return False
        if "::" in s:                                       # imported member names
            return False
        if re.fullmatch(r"[A-Za-z]+[A-Z][A-Za-z0-9_]*", s) and len(s) > 4:  # CamelCase ids
            return False
        if re.search(r"\.(asc|ash|bmp|png|wav|ogg|dat|svh|txt|cfg)$", s, re.I):
            return False
    if re.fullmatch(r"[0-9a-f]{16,}", s):
        return False
    return True


def looks_like_name(s):
    if DEFAULT_NAMES.match(s):
        return False
    if not re.search(r"[A-Za-z]{2}", s):
        return False
    return sum(c.isalpha() or c in " '.,!?-*&" for c in s) / len(s) > 0.85


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("game")
    ap.add_argument("project")
    ap.add_argument("--skip-script", action="append", default=[],
                    help="script section to ignore, e.g. Keyboard.asc")
    ap.add_argument("--force", action="store_true", help="overwrite an existing cands.json")
    a = ap.parse_args()

    cands_path = os.path.join(a.project, "cands.json")
    if os.path.exists(cands_path) and not a.force:
        sys.exit(f"{cands_path} exists: translations refer to its indexes. Use --force to rebuild it.")

    data = os.path.join(a.project, "data")
    print("extracting assets...")
    agsdata.extract_clib(a.game, data)
    dta = os.path.join(data, "game28.dta")
    if not os.path.exists(dta):
        sys.exit("game28.dta not found in the archive")
    rooms = sorted(glob.glob(os.path.join(data, "room*.crm")),
                   key=lambda x: int(re.findall(r"\d+", os.path.basename(x))[0]))

    info = agsdata.game_info(dta)
    info["encoding"] = agsdata.text_encoding(rooms) or "unknown"
    print(json.dumps(info, indent=1))
    utf8 = info["encoding"] == "65001"

    cands, rejected, seen = [], [], set()

    def add(s, src, check_text=True):
        if utf8:
            s = s.encode("latin1").decode("utf-8", errors="replace")
        if s in seen:
            return
        seen.add(s)
        (cands if (is_text(s) or not check_text) else rejected).append({"src": src, "en": s})

    script_spans = {}
    for path in [dta] + rooms:
        d = open(path, "rb").read()
        spans = []
        for name, strings, start, end in agsdata.scripts(d):
            spans.append((start, end))
            if name in a.skip_script:
                continue
            for s in strings:
                add(s, name)
        script_spans[path] = spans

    d = open(dta, "rb").read()
    try:
        for s in agsdata.dialog_options(d, info["dialogs"]):
            add(s, "dialog option")
    except ValueError as e:
        print("WARNING:", e)

    for path in [dta] + rooms:
        d = open(path, "rb").read()
        for s in agsdata.prefixed_strings(d, script_spans[path]):
            if looks_like_name(s):
                add(s, os.path.basename(path))

    os.makedirs(os.path.join(a.project, "tr"), exist_ok=True)
    json.dump(info, open(os.path.join(a.project, "gameinfo.json"), "w", encoding="utf-8"), indent=1)
    json.dump(cands, open(cands_path, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump(rejected, open(os.path.join(a.project, "rejected.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=0)
    print(f"{len(cands)} candidate strings, {len(rejected)} rejected")


if __name__ == "__main__":
    main()
