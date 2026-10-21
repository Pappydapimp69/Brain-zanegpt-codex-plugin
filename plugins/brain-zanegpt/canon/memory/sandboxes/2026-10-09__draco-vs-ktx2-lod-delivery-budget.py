"""Deterministic model: mesh delivery with Draco-like compression vs GPU-resident cost.
Draco-like codec = quantize positions to 14 bits + delta-encode + zlib (stdlib).
Texture 'KTX2-like' = fixed 4:1 block compression that STAYS compressed on GPU.
LOD = decimate vertex count by factor. Network/decode speeds are parameters."""
import zlib, struct, math

def grid_mesh(n):
    pos = [(i / n, j / n, math.sin(i * 0.3) * math.cos(j * 0.3) * 0.1) for i in range(n + 1) for j in range(n + 1)]
    idx = []
    for i in range(n):
        for j in range(n):
            a = i * (n + 1) + j; b = a + 1; c = a + n + 1; d = c + 1
            idx += [a, b, c, b, d, c]
    return pos, idx

def raw_bytes(pos, idx):
    return len(pos) * 12 + len(idx) * 4          # float32 xyz + uint32 idx = what GPU gets uncompressed

def draco_like(pos, idx):
    q = []
    for p in pos:
        q += [int(round(c * 16383)) & 0x3FFF for c in p]
    d = [q[0]] + [(q[k] - q[k - 3] if k >= 3 else q[k]) for k in range(1, len(q))]
    di = [idx[0]] + [idx[k] - idx[k - 1] for k in range(1, len(idx))]
    buf = struct.pack("<%di" % len(d), *d) + struct.pack("<%di" % len(di), *di)
    comp = len(zlib.compress(buf, 9))
    gpu = len(pos) * 12 + len(idx) * 4           # decoder outputs full size
    return comp, gpu

def ttr(download_bytes, mbps, decode_mb_s, decoded_bytes):
    """time-to-ready seconds: download + decode CPU (0 if no codec)."""
    t = download_bytes * 8 / (mbps * 1e6)
    if decode_mb_s: t += decoded_bytes / (decode_mb_s * 1e6)
    return t

results = []
pos, idx = grid_mesh(200)
raw = raw_bytes(pos, idx)
comp, gpu = draco_like(pos, idx)
# S1: download shrinks, GPU size does not
s1 = comp < raw * 0.5 and gpu == raw
print("S1 download %d vs raw %d (%.1fx); gpu %d == raw %d -> %s" % (comp, raw, raw / comp, gpu, raw, s1)); results.append(s1)

# S2: texture block compression shrinks GPU too (contrast: Draco does not)
tex_raw = 1024 * 1024 * 4; tex_gpu_ktx = tex_raw // 4
s2 = tex_gpu_ktx < tex_raw and gpu == raw
print("S2 ktx-like gpu %d vs rgba8 %d; mesh gpu unchanged -> %s" % (tex_gpu_ktx, tex_raw, s2)); results.append(s2)

# S3: LOD (decimation) is what actually cuts mesh VRAM
pos2, idx2 = grid_mesh(100)                       # ~1/4 verts
raw2 = raw_bytes(pos2, idx2); comp2, gpu2 = draco_like(pos2, idx2)
s3 = gpu2 < gpu * 0.3 and comp2 < comp
print("S3 LOD1 gpu %d vs LOD0 %d (%.2fx), draco dl %d vs %d -> %s" % (gpu2, gpu, gpu2 / gpu, comp2, comp, s3)); results.append(s3)

# S4 (BREAK): decode cost makes Draco slower end-to-end on fast net + slow CPU
cases = [("slow net 5Mbps, decode 50MB/s", 5, 50), ("fast net 1000Mbps, decode 50MB/s", 1000, 50), ("fast net 1000Mbps, decode 5MB/s", 1000, 5)]
wins = []
for name, mbps, dec in cases:
    a = ttr(raw, mbps, 0, 0); b = ttr(comp, mbps, dec, raw)
    wins.append(b < a)
    print("S4 %s: raw %.3fs draco %.3fs draco_wins=%s" % (name, a, b, b < a))
s4 = wins == [True, False, False]
print("S4 crossover reproduced (win only on slow net) -> %s" % s4); results.append(s4)

ok = all(results)
print("RESULT: %s draco shrinks download %.1fx but GPU unchanged; loses end-to-end on fast net; LOD cuts VRAM %.2fx" % ("PASS" if ok else "FAIL", raw / comp, gpu2 / gpu))
