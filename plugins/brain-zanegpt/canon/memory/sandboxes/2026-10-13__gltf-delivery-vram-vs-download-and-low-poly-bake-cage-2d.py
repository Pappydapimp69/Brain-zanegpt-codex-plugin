"""Three 3D-asset kernels in one deterministic stdlib model.
K1 (gpu-compressed-textures): deflate (PNG-proxy) download size varies with content, uncompressed VRAM does not, BC1 VRAM is fixed 0.5 B/px.
K2 (gltf runtime delivery): GLB binary container vs glTF with base64-embedded buffer vs JSON+external size.
K3 (bake from low poly inward): 2D bake - rays start on an offset cage line and travel inward to a high-poly profile."""
import zlib, json, base64, struct, math

W = 128
def tex(kind):
    px = []
    for y in range(W):
        for x in range(W):
            if kind == "flat": c = (90, 140, 200)
            elif kind == "gradient": c = (x * 2, y * 2, (x + y))
            elif kind == "checker": c = (255, 255, 255) if (x // 8 + y // 8) % 2 else (20, 20, 20)
            else:
                h = (x * 73856093 ^ y * 19349663) & 0xFFFFFFFF; h = (h * 2654435761) & 0xFFFFFFFF
                c = (h & 255, (h >> 8) & 255, (h >> 16) & 255)
            px.append(c + (255,))
    return px

def raw_bytes(px): return bytes(v for p in px for v in p)

def bc1(px):
    out = 0; err = 0.0; n = 0
    for by in range(0, W, 4):
        for bx in range(0, W, 4):
            blk = [px[(by + j) * W + bx + i][:3] for j in range(4) for i in range(4)]
            lum = [0.3 * r + 0.59 * g + 0.11 * b for r, g, b in blk]
            lo = blk[lum.index(min(lum))]; hi = blk[lum.index(max(lum))]
            q = lambda c: (c[0] >> 3 << 3 | c[0] >> 5, c[1] >> 2 << 2 | c[1] >> 6, c[2] >> 3 << 3 | c[2] >> 5)
            a, b = q(lo), q(hi)
            pal = [a, b, tuple((2 * a[k] + b[k]) // 3 for k in range(3)), tuple((a[k] + 2 * b[k]) // 3 for k in range(3))]
            for c in blk:
                d = min(sum((c[k] - p[k]) ** 2 for k in range(3)) for p in pal)
                err += d; n += 3
            out += 8
    mse = err / n
    return out, (99.0 if mse == 0 else 10 * math.log10(255 ** 2 / mse))

res = []
vram_raw = W * W * 4
print(f"K1 {W}x{W}: uncompressed VRAM {vram_raw} B for every texture")
sizes = {}
for kind in ("flat", "gradient", "checker", "noise"):
    px = tex(kind)
    dl = len(zlib.compress(raw_bytes(px), 9))
    b, psnr = bc1(px)
    sizes[kind] = (dl, b, psnr)
    print(f"   {kind:9s} deflate download {dl:6d} B, BC1 VRAM {b} B, BC1 PSNR {psnr:.1f} dB")
res.append(sizes["flat"][0] < vram_raw / 50)           # download tiny but VRAM unchanged
res.append(sizes["noise"][0] > 0.8 * vram_raw)         # download no help for noisy content
res.append(all(v[1] == vram_raw // 8 for v in sizes.values()))  # BC1 is 8x smaller, content-independent
res.append(sizes["noise"][2] < 20 and sizes["flat"][2] > 30)  # BREAK: compression quality is content dependent

# K2 container
buf = bytes(range(256)) * 400   # 102400 B geometry buffer
gj = {"asset": {"version": "2.0"}, "buffers": [{"byteLength": len(buf)}], "bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": len(buf)}], "meshes": [{"primitives": [{"attributes": {"POSITION": 0}}]}]}
js = json.dumps(gj, separators=(",", ":")).encode(); js += b" " * (-len(js) % 4)
glb = 12 + 8 + len(js) + 8 + len(buf)
gj_b64 = dict(gj); gj_b64["buffers"] = [{"byteLength": len(buf), "uri": "data:application/octet-stream;base64," + base64.b64encode(buf).decode()}]
emb = len(json.dumps(gj_b64, separators=(",", ":")))
ext = len(js) + len(buf)
print(f"K2 GLB {glb} B, embedded base64 glTF {emb} B ({emb/glb:.3f}x), JSON+bin {ext} B in 2 requests")
res.append(1.30 < emb / glb < 1.37 and glb - ext == 28)

# K3 2D bake
def high(x): return 0.30 * math.sin(6.0 * x) + 0.10 * math.sin(23 * x)
def bake(cage_off, max_dist, n=2000):
    ok = 0
    for i in range(n):
        x = i / n * 3.0
        y0 = cage_off          # ray origin on the cage line (above low-poly line y=0)
        # march downward (inward) to first crossing of high(x) from above
        t = 0.0; step = 0.001; hit = False
        prev_above = y0 > high(x)
        while t <= max_dist:
            y = y0 - t
            above = y > high(x)
            if prev_above and not above: hit = True; break
            prev_above = above; t += step
        if hit and abs(y - high(x)) < 0.01: ok += 1
    return ok / n
cases = [(0.05, 1.0), (0.45, 0.3), (0.45, 1.0), (0.05, 0.2)]
for off, md in cases:
    print(f"K3 cage offset {off}, max ray dist {md}: valid hits {bake(off, md):.3f}")
b_small = bake(0.05, 1.0); b_cage = bake(0.45, 1.0); b_short = bake(0.45, 0.3)
res.append(b_small < 0.9 and b_cage > 0.99 and b_short < b_cage)
print(("RESULT: PASS" if all(res) else "RESULT: FAIL") + f" checks={res}")
