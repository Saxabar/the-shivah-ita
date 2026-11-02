"""Read AGS sprite file version 12 (acsprset.spr): headers and raw data spans."""
import struct, sys
from collections import Counter

PAL_BYTES = {0: 0, 32: 3, 33: 4, 34: 2}

def read_index(d):
    assert d[2:15] == b" Sprite File " and struct.unpack_from("<h", d, 0)[0] == 12
    count = struct.unpack_from("<i", d, 20)[0]
    p = 28
    sprites = []
    for i in range(count + 1):
        start = p
        bpp, fmt = d[p], d[p + 1]
        if bpp == 0:
            sprites.append(None); p += 2; continue
        palcnt, comp = d[p + 2], d[p + 3]
        w, h = struct.unpack_from("<HH", d, p + 4)
        p += 8
        pal = (palcnt + 1) * PAL_BYTES[fmt] if fmt else 0
        p += pal
        size = struct.unpack_from("<I", d, p)[0]
        p += 4
        sprites.append(dict(i=i, start=start, end=p + size, bpp=bpp, fmt=fmt, palcnt=palcnt,
                            comp=comp, w=w, h=h, pal_off=start + 8, data_off=p, size=size))
        p += size
    assert p == len(d), (p, len(d))
    return sprites

if __name__ == "__main__":
    d = open(sys.argv[1], "rb").read()
    sp = read_index(d)
    real = [s for s in sp if s]
    print(len(sp), "slots", len(real), "sprites")
    print("bpp/fmt/comp:", Counter((s["bpp"], s["fmt"], s["comp"]) for s in real))
