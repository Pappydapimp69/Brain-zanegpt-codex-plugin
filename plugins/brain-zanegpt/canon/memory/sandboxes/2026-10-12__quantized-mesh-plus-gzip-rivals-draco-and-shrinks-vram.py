"""Re-verify the Draco kernel (Draco cuts download only, never VRAM) and brainwork E26 (17x smaller
download vs RAW) against the baselines a real server ships anyway: (a) the raw float32 buffer under
HTTP gzip, and (b) KHR_mesh_quantization-style int16 positions/normals + uint16 indices, gzipped,
which needs no decoder and stays int16 ON THE GPU. Own fixture: a 160x160 terrain with a
deterministic bumpy height field plus LCG noise (not E26's smooth grid). zlib level 6 throughout.
Draco-like = 14-bit quantize + delta along rows + zlib 9.
Predictions written before running:
 P1 raw+gzip is still at least 3x larger than Draco-like (gzip does little on float32).
 P2 quantized+gzip download lands within 2.5x of Draco-like.
 P3 quantized GPU bytes are <= 0.6x raw (Draco-like GPU bytes = raw, 1.0x).
 P4 on a perfectly smooth grid Draco-like beats quantized+gzip by more than on the noisy terrain.
"""
import math, struct, zlib

def lcg(seed):
    s = seed
    while True:
        s = (1103515245 * s + 12345) & 0x7fffffff
        yield s / 0x7fffffff

def mesh(n, noisy):
    g = lcg(42); pos, nrm = [], []
    for y in range(n):
        for x in range(n):
            h = 3 * math.sin(x * 0.11) * math.cos(y * 0.07) + (0.15 * (next(g) - 0.5) if noisy else 0.0)
            pos.append((x * 0.5, h, y * 0.5))
    for y in range(n):
        for x in range(n):
            hx = pos[y * n + min(x + 1, n - 1)][1] - pos[y * n + max(x - 1, 0)][1]
            hz = pos[min(y + 1, n - 1) * n + x][1] - pos[max(y - 1, 0) * n + x][1]
            l = math.sqrt(hx * hx + 1 + hz * hz); nrm.append((-hx / l, 1 / l, -hz / l))
    idx = []
    for y in range(n - 1):
        for x in range(n - 1):
            a = y * n + x; idx += [a, a + n, a + 1, a + 1, a + n, a + n + 1]
    return pos, nrm, idx

def raw(pos, nrm, idx):
    return b"".join(struct.pack("<3f", *p) for p in pos) + b"".join(struct.pack("<3f", *v) for v in nrm) + struct.pack(f"<{len(idx)}I", *idx)

def quantized(pos, nrm, idx):
    lo = [min(p[i] for p in pos) for i in range(3)]; hi = [max(p[i] for p in pos) for i in range(3)]
    q = lambda v, i: int(round((v - lo[i]) / (hi[i] - lo[i] or 1) * 65535)) - 32768
    out = b"".join(struct.pack("<4h", q(p[0], 0), q(p[1], 1), q(p[2], 2), 0) for p in pos)   # 8-byte aligned
    out += b"".join(struct.pack("<4b", *(int(round(c * 127)) for c in v), 0) for v in nrm)
    return out + struct.pack(f"<{len(idx)}H", *idx)

def draco_like(pos, nrm, idx, n):
    lo = [min(p[i] for p in pos) for i in range(3)]; hi = [max(p[i] for p in pos) for i in range(3)]
    q = [[int(round((p[i] - lo[i]) / (hi[i] - lo[i] or 1) * 16383)) for i in range(3)] for p in pos]
    deltas = []
    for k in range(len(q)):
        prev = q[k - 1] if k % n else [0, 0, 0]
        deltas += [q[k][i] - prev[i] for i in range(3)]
    nq = [int(round(c * 127)) for v in nrm for c in v]
    nd = [nq[k] - (nq[k - 3] if k >= 3 else 0) for k in range(len(nq))]
    idd = [idx[k] - (idx[k - 1] if k else 0) for k in range(len(idx))]
    blob = struct.pack(f"<{len(deltas)}h", *deltas) + struct.pack(f"<{len(nd)}h", *nd) + struct.pack(f"<{len(idd)}i", *idd)
    return zlib.compress(blob, 9)

res = {}
for name, noisy in (("noisy", True), ("smooth", False)):
    pos, nrm, idx = mesh(160, noisy)
    r, qz = raw(pos, nrm, idx), quantized(pos, nrm, idx)
    d = draco_like(pos, nrm, idx, 160)
    res[name] = dict(raw=len(r), raw_gz=len(zlib.compress(r, 6)), q_gpu=len(qz), q_gz=len(zlib.compress(qz, 6)), draco=len(d))
    x = res[name]
    print(f"{name:6s}: raw {x['raw']}  raw+gzip {x['raw_gz']}  quant+gzip {x['q_gz']}  draco-like {x['draco']}  | GPU raw {x['raw']} quant {x['q_gpu']} draco {x['raw']}")
n, s = res["noisy"], res["smooth"]
p1 = n["raw_gz"] >= 3 * n["draco"]
p2 = n["q_gz"] <= 2.5 * n["draco"]
p3 = n["q_gpu"] <= 0.6 * n["raw"]
p4 = s["q_gz"] / s["draco"] > n["q_gz"] / n["draco"]
checks = [("P1 raw+gzip >= 3x draco", p1), ("P2 quant+gzip within 2.5x draco", p2), ("P3 quant GPU <= 0.6x raw", p3), ("P4 smooth widens draco's lead", p4)]
held = sum(ok for _, ok in checks)
for c, ok in checks: print(("held   " if ok else "MISSED ") + c)
print(f"RESULT: {'PASS' if held == 4 else 'FAIL'} {held}/4; noisy download raw/raw+gz/quant+gz/draco "
      f"{n['raw']}/{n['raw_gz']}/{n['q_gz']}/{n['draco']} (quant+gz x{n['q_gz']/n['draco']:.2f} of draco); "
      f"GPU quant {n['q_gpu']/n['raw']:.2f}x raw; smooth quant+gz x{s['q_gz']/s['draco']:.2f} of draco")
