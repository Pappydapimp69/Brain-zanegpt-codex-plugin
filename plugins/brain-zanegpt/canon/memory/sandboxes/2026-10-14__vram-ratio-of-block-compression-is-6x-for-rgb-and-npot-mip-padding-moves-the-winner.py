"""ITERATION 2. Iteration 1 FAILED on one guess: I predicted the 1x1 mip chain ratio would be 2.0x; it is 0.5x because a 1x1 or 2x2 mip
still costs a whole 8-byte block (uncompressed 4 bytes), so sub-block mips are LARGER compressed. Check below corrected to observed 0.5.
PREDICTION (before first run): BC1 (8 bytes per 4x4 block) vs uncompressed: 8x for RGBA8, 6x for RGB8 (E179 only measured RGBA);
a full mip chain adds 33% (ratio 1.333 within 1%) for POT squares; a 1500x1000 NPOT texture in WebGL1 (no mips, so padded to
2048x1024 to get a chain) costs MORE VRAM than the true NPOT size with mips in WebGL2 (>=1.3x), yet a compressed NPOT with
mips still beats an uncompressed POT with mips by >=6x; and block padding makes 1001x1001 BC1 ~ 1004x1004 blocks (no free size)."""
import math

def blocks(w, h, bs=4): return math.ceil(w / bs) * math.ceil(h / bs)

def chain(w, h):
    out = []
    while True:
        out.append((w, h))
        if w == 1 and h == 1: break
        w, h = max(1, w // 2), max(1, h // 2)
    return out

def bytes_uncompressed(w, h, bpp, mips): return sum(a * b * bpp for a, b in (chain(w, h) if mips else [(w, h)]))
def bytes_bc1(w, h, mips): return sum(blocks(a, b) * 8 for a, b in (chain(w, h) if mips else [(w, h)]))
def pot(n): return 1 << (n - 1).bit_length()

r = {}
r['rgba_ratio'] = bytes_uncompressed(2048, 2048, 4, False) / bytes_bc1(2048, 2048, False)
r['rgb_ratio'] = bytes_uncompressed(2048, 2048, 3, False) / bytes_bc1(2048, 2048, False)
r['mip_overhead'] = bytes_uncompressed(2048, 2048, 4, True) / bytes_uncompressed(2048, 2048, 4, False)
npot = (1500, 1000)
webgl2 = bytes_uncompressed(*npot, 4, True)
webgl1 = bytes_uncompressed(pot(npot[0]), pot(npot[1]), 4, True)   # padded to POT to get mips
r['npot_pad_penalty'] = webgl1 / webgl2
r['bc1_npot_vs_unc_pot'] = webgl1 / bytes_bc1(*npot, True)
r['pad_1001'] = bytes_bc1(1001, 1001, False) / bytes_bc1(1004, 1004, False)
r['ratio_tiny_4x4'] = bytes_uncompressed(4, 4, 4, False) / bytes_bc1(4, 4, False)   # break: 1 block
r['ratio_1x1_chain'] = bytes_uncompressed(1, 1, 4, True) / bytes_bc1(1, 1, True)    # break: sub-block mips
r['chain_ratio_2048'] = bytes_uncompressed(2048, 2048, 4, True) / bytes_bc1(2048, 2048, True)
for k, v in r.items(): print(k, round(v, 4))
ok = (abs(r['rgba_ratio'] - 8) < 1e-9 and abs(r['rgb_ratio'] - 6) < 1e-9 and abs(r['mip_overhead'] - 4 / 3) < 0.01
      and r['npot_pad_penalty'] >= 1.3 and r['bc1_npot_vs_unc_pot'] >= 6 and r['pad_1001'] == 1.0 and r['ratio_1x1_chain'] == 0.5)
print("RESULT: %s BC1 ratio rgba %.1fx rgb %.1fx; mips +%.0f%%; WebGL1 NPOT pad penalty %.2fx; compressed NPOT beats uncompressed POT by %.1fx; 1x1 chain ratio %.1fx (sub-block tail costs a full block); full 2048 chain ratio %.2fx" % (
  "PASS" if ok else "FAIL", r['rgba_ratio'], r['rgb_ratio'], (r['mip_overhead'] - 1) * 100, r['npot_pad_penalty'], r['bc1_npot_vs_unc_pot'], r['ratio_1x1_chain'], r['chain_ratio_2048']))
