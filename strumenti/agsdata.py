"""Readers for compiled Adventure Game Studio (AGS) data.

Formats follow AGSUnpacker (https://github.com/adm244/AGSUnpacker) and the AGS
engine sources. Tested on AGS 3.6.1 games; older layouts are rejected with an
explicit error instead of being guessed.
"""
import os
import re
import struct

CLIB_HEAD = b"CLIB\x1a"
CLIB_TAIL = b"CLIB\x01\x02\x03\x04SIGE"
DTA_SIGNATURE = b"Adventure Creator Game File v2"
DIALOG_SIZE = 4696  # DialogTopic: 30*150 names, 30 flags, script ptr, 30 entry points, 2 shorts, 2 ints
DIALOG_NUMOPTIONS = 4688


# --- CLIB archives -----------------------------------------------------------

def _cstr(f):
    b = bytearray()
    while (c := f.read(1)) not in (b"\x00", b""):
        b += c
    return b.decode("latin1")


def _find_clib(f):
    """Return offset of the CLIB archive: at file start or appended to an exe."""
    f.seek(0)
    if f.read(5) == CLIB_HEAD:
        return 0
    f.seek(-len(CLIB_TAIL), 2)
    if f.read(len(CLIB_TAIL)) != CLIB_TAIL:
        raise ValueError("no CLIB archive found (not an AGS game file?)")
    f.seek(-(len(CLIB_TAIL) + 8), 2)
    off64 = struct.unpack("<Q", f.read(8))[0]
    f.seek(-(len(CLIB_TAIL) + 4), 2)
    off32 = struct.unpack("<I", f.read(4))[0]
    for off in (off64, off32):
        f.seek(off)
        if f.read(5) == CLIB_HEAD:
            return off
    raise ValueError("CLIB tail found but archive head is missing")


def extract_clib(path, outdir):
    """Extract every asset stored in the main archive file. Returns asset names."""
    names = []
    with open(path, "rb") as f:
        off = _find_clib(f)
        f.seek(off + 5)
        ver, idx = f.read(2)
        if ver != 30:
            raise ValueError(f"CLIB version {ver} not supported (only 30, AGS 3.5+)")
        if idx != 0:
            raise ValueError("this is not the first archive of a multi-file game")
        _seed, nfiles = struct.unpack("<ii", f.read(8))
        files = [_cstr(f) for _ in range(nfiles)]
        nassets = struct.unpack("<i", f.read(4))[0]
        assets = []
        for _ in range(nassets):
            name = _cstr(f)
            i = f.read(1)[0]
            o, s = struct.unpack("<qq", f.read(16))
            assets.append((name, i, o, s))
        os.makedirs(outdir, exist_ok=True)
        for name, i, o, s in assets:
            if i != 0:
                print(f"  skipped {name}: stored in {files[i]}")
                continue
            f.seek(off + o)
            with open(os.path.join(outdir, name), "wb") as w:
                w.write(f.read(s))
            names.append(name)
    return names


# --- game28.dta header -------------------------------------------------------

def game_info(dta_path):
    """Read game name, unique id and object counts from the game data header."""
    d = open(dta_path, "rb").read()
    if not d.startswith(DTA_SIGNATURE):
        raise ValueError("not a game28.dta file")
    p = len(DTA_SIGNATURE)
    dta_version = struct.unpack_from("<i", d, p)[0]
    p += 4
    n = struct.unpack_from("<i", d, p)[0]
    engine = d[p + 4:p + 4 + n].decode("latin1")
    p += 4 + n
    # 3.5+ data has a capability list (count + prefixed strings) before the name
    ncaps = struct.unpack_from("<i", d, p)[0]
    if 0 <= ncaps <= 64:
        q = p + 4
        for _ in range(ncaps):
            q += 4 + struct.unpack_from("<i", d, q)[0]
        p = q
    name = d[p:p + 50].split(b"\x00")[0].decode("latin1")
    o = p + 52 + 400 + 256 + 1024  # name (aligned), options, paluses, palette
    views, chars, player, score = struct.unpack_from("<4i", d, o)
    inv = struct.unpack_from("<h", d, o + 16)[0]
    dialogs, _msgs, fonts = struct.unpack_from("<3i", d, o + 20)
    uniqueid = struct.unpack_from("<i", d, o + 48)[0]
    guis, cursors = struct.unpack_from("<2i", d, o + 52)
    return {"name": name, "uniqueid": uniqueid, "engine": engine, "dta_version": dta_version,
            "characters": chars, "inventory": inv, "dialogs": dialogs, "fonts": fonts,
            "guis": guis, "cursors": cursors, "views": views}


def text_encoding(room_paths):
    """Return the 'textencoding' room option (code page, e.g. '1252' or '65001')."""
    for path in room_paths:
        d = open(path, "rb").read()
        i = d.find(b"\x0c\x00\x00\x00textencoding")
        if i >= 0:
            q = i + 16
            n = struct.unpack_from("<i", d, q)[0]
            return d[q + 4:q + 4 + n].decode("latin1")
    return None


# --- compiled scripts (SCOM) -------------------------------------------------

def parse_scom(d, p):
    """Parse one compiled script at offset p. Returns (sections, strings, end)."""
    if d[p:p + 4] != b"SCOM":
        raise ValueError("no SCOM signature")
    ver, gsz, csz, ssz = struct.unpack_from("<iiii", d, p + 4)
    q = p + 20 + gsz + csz * 4
    blob = d[q:q + ssz]
    q += ssz

    def cs(q):
        e = d.index(b"\x00", q)
        return d[q:e].decode("latin1"), e + 1

    nfix = struct.unpack_from("<i", d, q)[0]
    q += 4 + nfix * 5
    nimp = struct.unpack_from("<i", d, q)[0]
    q += 4
    for _ in range(nimp):
        _, q = cs(q)
    nexp = struct.unpack_from("<i", d, q)[0]
    q += 4
    for _ in range(nexp):
        _, q = cs(q)
        q += 4
    secs = []
    if ver >= 83:
        nsec = struct.unpack_from("<i", d, q)[0]
        q += 4
        for _ in range(nsec):
            name, q = cs(q)
            q += 4
            secs.append(name)
    if struct.unpack_from("<I", d, q)[0] != 0xBEEFCAFE:
        raise ValueError("bad SCOM tail signature")
    strings = [s.decode("latin1") for s in blob.split(b"\x00")[:-1]]
    return secs, strings, q + 4


def scripts(d):
    """Yield (name, strings, start, end) for every compiled script in a buffer."""
    p = 0
    while (p := d.find(b"SCOM", p)) >= 0:
        try:
            secs, strings, end = parse_scom(d, p)
        except (ValueError, struct.error):
            p += 4
            continue
        yield (secs[-1] if secs else "?"), strings, p, end
        p = end


# --- dialog options ----------------------------------------------------------

def _printable(b):
    return all(32 <= c < 127 or c >= 160 for c in b)


def _dialog_ok(d, b):
    """Check that a DialogTopic record plausibly starts at offset b."""
    n = struct.unpack_from("<i", d, b + DIALOG_NUMOPTIONS)[0]
    if not 0 < n <= 30:
        return False
    texts = [d[b + k * 150:b + k * 150 + 150].split(b"\x00")[0] for k in range(n)]
    if not any(texts):
        return False
    for s in texts:  # deleted options leave empty slots
        if s and (not _printable(s) or not re.search(rb"[A-Za-z]", s)):
            return False
    # unused option slots are zero-filled
    return all(d[b + k * 150] == 0 for k in range(n, 30))


def dialog_options(d, count):
    """Find the DialogTopic array and return the option texts of all dialogs."""
    if count <= 0:
        return []
    last = len(d) - DIALOG_SIZE * count
    for base in range(0, max(last, 0)):
        if not 0 < d[base + DIALOG_NUMOPTIONS] <= 30:
            continue
        if d[base + DIALOG_NUMOPTIONS + 1:base + DIALOG_NUMOPTIONS + 4] != b"\x00\x00\x00":
            continue
        if not all(_dialog_ok(d, base + i * DIALOG_SIZE) for i in range(count)):
            continue
        out = []
        for i in range(count):
            b = base + i * DIALOG_SIZE
            n = struct.unpack_from("<i", d, b + DIALOG_NUMOPTIONS)[0]
            out += [d[b + k * 150:b + k * 150 + 150].split(b"\x00")[0].decode("latin1") for k in range(n)]
        return out
    raise ValueError("dialog array not found")


# --- length-prefixed names (hotspots, objects, GUI text, inventory) ---------

_RUN = re.compile(rb"[\x20-\x7e\xa0-\xff]{2,}")


def prefixed_strings(d, skip_spans=()):
    """Return strings stored as int32 length + chars, outside the given spans."""
    out = []
    for m in _RUN.finditer(d):
        a = m.start()
        if a < 4 or any(s <= a < e for s, e in skip_spans):
            continue
        n = struct.unpack_from("<i", d, a - 4)[0]
        if 2 <= n <= len(m.group()):
            out.append(d[a:a + n].decode("latin1"))
    return out
