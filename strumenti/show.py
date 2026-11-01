"""Print candidate strings with their indexes, for translating in batches.

Usage: python show.py <project_dir> [start] [count] [--todo]

--todo   show only strings that have no translation yet
"""
import glob
import json
import os
import sys

args = [x for x in sys.argv[1:] if not x.startswith("--")]
project = args[0]
start = int(args[1]) if len(args) > 1 else 0
count = int(args[2]) if len(args) > 2 else 300
todo = "--todo" in sys.argv

cands = json.load(open(os.path.join(project, "cands.json"), encoding="utf-8"))
done = set()
for fn in glob.glob(os.path.join(project, "tr", "*.txt")):
    for line in open(fn, encoding="utf-8"):
        if line.strip():
            done.add(int(line.split("\t", 1)[0]))

sys.stdout.reconfigure(encoding="utf-8")
last = None
for i, c in enumerate(cands[start:start + count], start):
    if todo and i in done:
        continue
    if c["src"] != last:
        print("##", c["src"])
        last = c["src"]
    print(i, c["en"])
print(f"-- {len(done)} of {len(cands)} translated")
