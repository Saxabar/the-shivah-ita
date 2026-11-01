"""Append a string the extractor missed, keeping existing indexes valid.

Usage: python addstring.py <project_dir> "<original text>" [source note]
Prints the new index to use in a tr/*.txt file.
"""
import json
import os
import sys

project, text = sys.argv[1], sys.argv[2]
src = sys.argv[3] if len(sys.argv) > 3 else "added by hand"
path = os.path.join(project, "cands.json")
cands = json.load(open(path, encoding="utf-8"))
for i, c in enumerate(cands):
    if c["en"] == text:
        sys.exit(f"already present at index {i}")
cands.append({"src": src, "en": text})
json.dump(cands, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(cands) - 1)
