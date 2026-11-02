"""Build the graphics patch for Shivah.exe from the original executable.

Usage: python graphics.py <original Shivah.exe> <out_dir>

Writes to <out_dir>:
  ranges.json   list of [file offset, length] of the changed sprite pixel data
  old.bin       original bytes of all ranges, concatenated
  new.bin       patched bytes of all ranges, concatenated
All sprites keep their size, so the archive layout does not change.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import buttons  # noqa: E402
import clues  # noqa: E402
import joke  # noqa: E402
import spr  # noqa: E402
import tabpatch  # noqa: E402


def main():
    exe, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    base, size = tabpatch.clib_asset(exe, "acsprset.spr")
    with open(exe, "rb") as f:
        f.seek(base)
        data = f.read(size)

    changes = {}
    sprites = spr.read_index(data)
    for i in tabpatch.TAB_SPRITES:
        s = sprites[i]
        old = data[s["data_off"]:s["data_off"] + s["w"] * s["h"]]
        changes[i] = (old, tabpatch.redraw(old, s["w"], s["h"]), s["data_off"])
    changes.update(clues.redraw(data))
    changes.update(buttons.redraw_all(data, out))
    changes.update(joke.redraw(data))

    ranges, old_all, new_all = [], b"", b""
    for i in sorted(changes):
        old, new, off = changes[i]
        assert len(old) == len(new)
        ranges.append([base + off, len(old), i])
        old_all += old
        new_all += new
    json.dump({"exe_size": os.path.getsize(exe), "ranges": ranges}, open(os.path.join(out, "ranges.json"), "w"), indent=0)
    open(os.path.join(out, "old.bin"), "wb").write(old_all)
    open(os.path.join(out, "new.bin"), "wb").write(new_all)
    diff = sum(a != b for a, b in zip(old_all, new_all))
    print(f"{len(ranges)} sprites, {len(new_all)} bytes in ranges, {diff} bytes changed")


if __name__ == "__main__":
    main()
