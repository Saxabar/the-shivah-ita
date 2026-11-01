"""Convert translations between index files (tr/*.txt) and a hash-keyed TSV.

The TSV holds only the translated text, keyed by a hash of the original string,
so it can be published without the original game text and re-applied to the
strings extracted from any copy of the game.

Usage:
  python tsv.py export <project_dir> <file.tsv>
  python tsv.py import <project_dir> <file.tsv>   (writes tr/from_tsv.txt)
"""
import glob
import hashlib
import json
import os
import sys


def key(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def load_index_files(project):
    tr = {}
    for fn in sorted(glob.glob(os.path.join(project, "tr", "*.txt"))):
        for line in open(fn, encoding="utf-8"):
            line = line.rstrip("\r\n")
            if line.strip():
                idx, text = line.split("\t", 1)
                tr[int(idx)] = text
    return tr


def export(project, path):
    cands = json.load(open(os.path.join(project, "cands.json"), encoding="utf-8"))
    rows = {}
    for idx, text in sorted(load_index_files(project).items()):
        rows[key(cands[idx]["en"])] = text
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("# key = first 12 hex digits of SHA-1 of the original UTF-8 string\n")
        for k, text in rows.items():
            f.write(f"{k}\t{text}\n")
    print(f"exported {len(rows)} translations to {path}")


def import_(project, path):
    cands = json.load(open(os.path.join(project, "cands.json"), encoding="utf-8"))
    rows = {}
    for line in open(path, encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        k, text = line.rstrip("\r\n").split("\t", 1)
        rows[k] = text
    out, used = [], set()
    for i, c in enumerate(cands):
        k = key(c["en"])
        if k in rows:
            out.append(f"{i}\t{rows[k]}")
            used.add(k)
    tr_dir = os.path.join(project, "tr")
    if glob.glob(os.path.join(tr_dir, "*.txt")):
        sys.exit(f"{tr_dir} already contains translation files; import into an empty project")
    os.makedirs(tr_dir, exist_ok=True)
    with open(os.path.join(tr_dir, "from_tsv.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print(f"imported {len(used)} of {len(rows)} translations; {len(rows) - len(used)} not found in this game")


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] not in ("export", "import"):
        sys.exit(__doc__)
    (export if sys.argv[1] == "export" else import_)(sys.argv[2], sys.argv[3])
