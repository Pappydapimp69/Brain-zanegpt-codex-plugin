# Deterministic: where to put SECDED(8,4) relative to RLE, and what a sum check (trial-balance style) adds.
from itertools import combinations
DATA = b"aaaaaaaabbbbbbbbbbccccddddddddddddzz"

def rle(b):
    out, i = bytearray(), 0
    while i < len(b):
        j = i
        while j < len(b) and b[j] == b[i] and j - i < 255: j += 1
        out += bytes([j - i, b[i]]); i = j
    return bytes(out)
def unrle(b):
    out = bytearray()
    for i in range(0, len(b) - 1, 2): out += bytes([b[i + 1]]) * b[i]
    return bytes(out)

# Hamming(7,4) + overall parity = SECDED(8,4); bit layout p1 p2 d1 p3 d2 d3 d4 + P
def enc4(n):
    d = [(n >> k) & 1 for k in range(4)]
    p1 = d[0] ^ d[1] ^ d[3]; p2 = d[0] ^ d[2] ^ d[3]; p3 = d[1] ^ d[2] ^ d[3]
    w = [p1, p2, d[0], p3, d[1], d[2], d[3]]
    return w + [sum(w) & 1]
def dec4(w):
    w = list(w); s = (w[0]^w[2]^w[4]^w[6]) | ((w[1]^w[2]^w[5]^w[6]) << 1) | ((w[3]^w[4]^w[5]^w[6]) << 2)
    par = sum(w) & 1
    if s == 0 and par == 0: status = "ok"
    elif par == 1:
        if s: w[s - 1] ^= 1
        else: w[7] ^= 1
        status = "fixed"
    else: return None, "detected"
    return w[2] | (w[4] << 1) | (w[5] << 2) | (w[6] << 3), status
def ecc_enc(b):
    bits = []
    for x in b: bits += enc4(x & 15) + enc4(x >> 4)
    return bits
def ecc_dec(bits):
    out, flag = bytearray(), "ok"
    for i in range(0, len(bits), 16):
        lo, s1 = dec4(bits[i:i+8]); hi, s2 = dec4(bits[i+8:i+16])
        if lo is None or hi is None: return None, "detected"
        out.append(lo | (hi << 4))
    return bytes(out), "ok"

comp = rle(DATA)
size = {"raw": len(DATA), "rle": len(comp), "rle_then_ecc_bytes": len(ecc_enc(comp)) // 8,
        "ecc_then_rle": len(rle(bytes(sum(b << k for k, b in enumerate(ecc_enc(DATA)[i:i+8])) for i in range(0, len(ecc_enc(DATA)), 8))))}
checksum = sum(DATA) & 255
def flip_bytes(b, positions):
    b = bytearray(b)
    for p in positions: b[p // 8] ^= 1 << (p % 8)
    return bytes(b)
nbits = len(comp) * 8
# plain RLE stream: classify each corruption
def classify_plain(positions):
    out = unrle(flip_bytes(comp, positions))
    if out == DATA: return "harmless"
    if (sum(out) & 255) != checksum: return "sum_detects"
    return "sum_misses"
single = [classify_plain([p]) for p in range(nbits)]
double = [classify_plain(p) for p in combinations(range(nbits), 2)]
def count(l, k): return sum(1 for x in l if x == k)
amp = max(abs(len(unrle(flip_bytes(comp, [p]))) - len(DATA)) for p in range(nbits))
# ECC over the compressed stream
ebits = ecc_enc(comp)
def classify_ecc(positions):
    b = list(ebits)
    for p in positions: b[p] ^= 1
    out, st = ecc_dec(b)
    if out is None: return "detected"
    return "right" if out == comp else "wrong"
es = [classify_ecc([p]) for p in range(len(ebits))]
ed = [classify_ecc(p) for p in combinations(range(len(ebits)), 2)]
# same-nibble triples miscorrect (the guarantee ends at two)
tri = [classify_ecc(p) for p in combinations(range(8), 3)]
print("sizes", size)
print("plain RLE single flips: harmless", count(single, "harmless"), "sum detects", count(single, "sum_detects"), "sum misses", count(single, "sum_misses"), "of", nbits, "| max length change", amp)
print("plain RLE double flips: harmless", count(double, "harmless"), "sum detects", count(double, "sum_detects"), "sum misses", count(double, "sum_misses"), "of", len(double))
print("ECC single:", {k: count(es, k) for k in set(es)}, "| ECC double:", {k: count(ed, k) for k in set(ed)}, "| same-nibble triples:", {k: count(tri, k) for k in set(tri)})
ok = (size["rle"] < size["raw"] and size["ecc_then_rle"] > size["rle_then_ecc_bytes"] and size["ecc_then_rle"] > size["raw"]
      and count(es, "right") == len(es) and count(ed, "wrong") == 0 and count(ed, "detected") > 0
      and count(single, "sum_misses") + count(double, "sum_misses") > 0 and count(tri, "wrong") > 0 and amp > 0)
print(f"RESULT: {'PASS' if ok else 'FAIL'} raw {size['raw']}B rle {size['rle']}B rle-then-ecc {size['rle_then_ecc_bytes']}B ecc-then-rle {size['ecc_then_rle']}B; plain stream sum misses {count(single,'sum_misses')} single/{count(double,'sum_misses')} double; ecc single right {count(es,'right')}/{len(es)} double wrong {count(ed,'wrong')} detected {count(ed,'detected')}/{len(ed)}; triples wrong {count(tri,'wrong')}/{len(tri)}")
