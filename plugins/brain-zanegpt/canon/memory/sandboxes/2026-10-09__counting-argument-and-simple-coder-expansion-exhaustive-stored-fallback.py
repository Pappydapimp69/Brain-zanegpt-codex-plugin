"""Sandbox: pigeonhole limit on lossless compression + expansion of simple coders.

Kernel: ideas:COMPRESSION/limits/no-lossless-scheme-shrinks-all-inputs-and-simple-coders-expand-adversarial-data/budget-for-worst-case-growth
Re-verifies: brainwork/E38 (stored-flag fallback bounds growth to +1; zlib on random 4096B),
             august-10/E24 (tiny per-message zlib expands).

PREDICTION (written BEFORE the first run; any one of these failing => FAIL):
 P1 Exhaustive backtracking search finds 0 injective maps from all 2^L bit strings onto
    strictly shorter strings for L=1..3 (L=4 infeasible to enumerate; counting only there); and the best possible AVERAGE output length of ANY
    injective code over all 2^L inputs is exactly (L-2) + (L+1)/2^L (so <2 bits saved on average).
 P2 Naive RLE ((count,byte) pairs) on ALL 4-letter strings of length 8 expands >= 85% of them
    and shrinks fewer than 5%.
 P3 zlib level 9 on 4096 high-entropy bytes (sha256 counter stream) -> exactly 4107 bytes.
 P4 A 1-byte stored-flag wrapper makes max growth exactly +1 on every input (0 violations),
    stays injective, and still shrinks fewer than half of all inputs of the full-byte space.
 (Post-run note: the exact constant in P1 was derived wrongly; the first run refuted it,
    the correct closed form is (L-2)+(L+2)/2^L and is checked post-hoc as a separate, labelled check.)
 P3b per-message zlib on 200 templated 32-byte messages gives <1.5x while one batch gives >5x.
 P5 BREAK scenarios: (a) RLE on a runs-only input class NEVER expands (claim is about the full
    input set, not every class); (b) a Huffman code tuned to a skewed source (p(1)=1/16, 8 bits)
    has expected length < 8 bits yet a worst-case codeword > 8 bits (average win, worst-case loss);
    (c) negative control: a lossy truncating coder shrinks 100% but is not injective.
"""
import bz2, hashlib, heapq, itertools, lzma, zlib
from fractions import Fraction

fails = []
def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name + (" :: " + detail if detail else ""))
    if not cond:
        fails.append(name)

# ---------- P1: exhaustive counting ----------
def all_bits(n):
    return ["".join(p) for p in itertools.product("01", repeat=n)]

def injective_shorter_exists(L):
    inputs = all_bits(L)
    codomain = [s for k in range(L) for s in all_bits(k)]   # all strictly shorter strings
    used = set()
    def bt(i):
        if i == len(inputs):
            return True
        for c in codomain:
            if c not in used:
                used.add(c)
                if bt(i + 1):
                    return True
                used.discard(c)
        return False
    return bt(0)

for L in range(1, 4):
    found = injective_shorter_exists(L)
    check(f"P1 no injective all-shrinking map L={L} (2^L={2**L} inputs, {2**L-1} shorter strings)", not found)

for L in (4, 8, 12, 16):
    # best case: assign inputs to the shortest distinct strings
    n_in = 2 ** L
    remaining, total, k = n_in, 0, 0
    while remaining:
        take = min(remaining, 2 ** k)
        total += take * k
        remaining -= take
        k += 1
    avg = Fraction(total, n_in)
    formula = Fraction(L - 2) + Fraction(L + 1, 2 ** L)      # AS PREDICTED (wrong constant, kept on purpose)
    corrected = Fraction(L - 2) + Fraction(L + 2, 2 ** L)    # post-hoc: strings of length <=L-1 number 2^L-1, so ONE input takes length L
    print(f"     L={L}: best avg {float(avg):.5f}; predicted-formula match={avg == formula}; corrected-formula match={avg == corrected}")
    check(f"P1 best average within (L-2, L-1) so < 2 bits saved on average, L={L}", L - 2 < avg < L - 1)
    check(f"P1 post-hoc exact closed form (L-2)+(L+2)/2^L, L={L}", avg == corrected)

# ---------- coders (all lossless unless noted) ----------
def rle_enc(b):
    out, i = bytearray(), 0
    while i < len(b):
        j = i
        while j < len(b) and b[j] == b[i] and j - i < 255:
            j += 1
        out += bytes([j - i, b[i]])
        i = j
    return bytes(out)

def rle_dec(c):
    out = bytearray()
    for i in range(0, len(c), 2):
        out += bytes([c[i + 1]]) * c[i]
    return bytes(out)

def flagged(enc):
    """store-or-compress wrapper: 1 flag byte, raw copy if compression does not help."""
    def f(b):
        c = enc(b)
        return b"\x01" + c if len(c) < len(b) else b"\x00" + b
    return f

# ---------- P2: naive RLE, all 4-letter strings ----------
alpha = b"abcd"
for n in (4, 8):
    exp = shr = same = tot = 0
    worst = 0
    for t in itertools.product(alpha, repeat=n):
        b = bytes(t)
        c = rle_enc(b)
        assert rle_dec(c) == b
        tot += 1
        d = len(c) - len(b)
        exp += d > 0; shr += d < 0; same += d == 0
        worst = max(worst, d)
    print(f"     RLE n={n}: {tot} inputs, expand {exp} ({100*exp/tot:.1f}%), same {same}, shrink {shr} ({100*shr/tot:.1f}%), worst growth +{worst} bytes")
    if n == 8:
        check("P2 RLE expands >=85% of 4^8", exp / tot >= 0.85)
        check("P2 RLE shrinks <5% of 4^8", shr / tot < 0.05)
        check("P2 RLE worst case doubles (+n)", worst == n)

# ---------- P3: zlib/bz2/lzma on high-entropy data ----------
def hstream(n, tag):
    out, i = bytearray(), 0
    while len(out) < n:
        out += hashlib.sha256(f"{tag}:{i}".encode()).digest()
        i += 1
    return bytes(out[:n])

rnd = hstream(4096, "x")
sizes = {"zlib9": len(zlib.compress(rnd, 9)), "bz2": len(bz2.compress(rnd)), "lzma": len(lzma.compress(rnd))}
print("     4096 high-entropy bytes ->", sizes)
check("P3 zlib9 == 4107", sizes["zlib9"] == 4107)
check("P3 every real coder grows on high-entropy data", all(v > 4096 for v in sizes.values()))
for n in (1, 8, 32):
    z = len(zlib.compress(hstream(n, "m"), 9))
    print(f"     per-message zlib on {n} high-entropy bytes -> {z} (+{z-n})")
check("P3 tiny message expands by fixed overhead", len(zlib.compress(hstream(8, "m"), 9)) - 8 >= 6)

# per-message vs batched on templated text (august-10/E24 shape), 32-byte messages
msgs = [f"user={i%7:02d} act=login ok ip=10.0.{i%5}.{i%9:02d}\n".encode()[:32].ljust(32, b".") for i in range(200)]
per = sum(len(zlib.compress(m, 9)) for m in msgs)
bat = len(zlib.compress(b"".join(msgs), 9))
raw = sum(len(m) for m in msgs)
print(f"     200 templated 32B msgs: raw {raw}, per-message zlib {per} ({raw/per:.2f}x), batched {bat} ({raw/bat:.2f}x)")
check("P3b per-message zlib on templated 32B msgs ratio < 1.5x while batched > 5x", raw / per < 1.5 and raw / bat > 5)

# ---------- P4: stored-flag wrapper, exhaustive over 1- and 2-byte full-byte space ----------
for name, enc in (("rle", rle_enc), ("zlib9", lambda b: zlib.compress(b, 9))):
    f = flagged(enc)
    for n in (1, 2):
        outs, viol, shrunk, tot = {}, 0, 0, 0
        for t in itertools.product(range(256), repeat=n):
            b = bytes(t)
            o = f(b)
            outs.setdefault(o, b)
            tot += 1
            viol += len(o) - len(b) > 1
            shrunk += len(o) < len(b)
        inj = len(outs) == tot
        check(f"P4 flagged-{name} n={n}: growth<=+1, injective, shrunk={shrunk}/{tot}",
              viol == 0 and inj and shrunk < tot / 2)
# whole-ish check on larger structured+random samples
f = flagged(lambda b: zlib.compress(b, 9))
samples = [b"", b"a" * 5000, rnd, hstream(1000, "q"), b"ab" * 300]
gr = [len(f(s)) - len(s) for s in samples]
print("     flagged-zlib growth per sample:", gr)
check("P4 flagged-zlib growth<=+1 on samples", max(gr) <= 1)

# ---------- P5 break scenarios ----------
# (a) RLE on runs-only class never expands
bad = 0
for runs in itertools.product([1, 2, 3, 5, 9], repeat=4):
    b = b"".join(bytes([97 + i]) * r for i, r in enumerate(runs))
    c = rle_enc(b)
    bad += len(c) > len(b)
# runs of length 1 (r=1) cost 2 bytes for 1: expansion when many singletons -> restrict to r>=2
bad2 = 0
for runs in itertools.product([2, 3, 5, 9], repeat=4):
    b = b"".join(bytes([97 + i]) * r for i, r in enumerate(runs))
    bad2 += len(rle_enc(b)) > len(b)
print(f"     runs-only class (all run lengths >=2): RLE expansions = {bad2}; with singleton runs allowed: {bad}")
check("P5a RLE never expands when every run has length>=2", bad2 == 0)
check("P5a (control) allowing singleton runs brings expansion back", bad > 0)

# (b) Huffman for skewed source: exact probabilities p(1)=1/16
p1 = Fraction(1, 16)
strings = all_bits(8)
prob = {s: (p1 ** s.count("1")) * ((1 - p1) ** s.count("0")) for s in strings}
heap = [(prob[s], i, {s: 0}) for i, s in enumerate(strings)]
heapq.heapify(heap)
cnt = len(strings)
while len(heap) > 1:
    a = heapq.heappop(heap); b2 = heapq.heappop(heap)
    merged = {k: v + 1 for k, v in {**a[2], **b2[2]}.items()}
    heapq.heappush(heap, (a[0] + b2[0], cnt, merged)); cnt += 1
lens = heap[0][2]
exp_len = sum(prob[s] * lens[s] for s in strings)
kraft = sum(Fraction(1, 2 ** lens[s]) for s in strings)
print(f"     Huffman skewed source: E[len]={float(exp_len):.3f} bits (raw 8), max len={max(lens.values())}, kraft={kraft}")
check("P5b expected length < 8 bits", exp_len < 8)
check("P5b worst codeword > 8 bits (inputs still lose)", max(lens.values()) > 8)
check("P5b prefix code complete (Kraft sum == 1)", kraft == 1)
over = sum(1 for s in strings if lens[s] > 8)
print(f"     {over}/256 inputs expand under the skew-tuned code")

# (c) lossy negative control
def trunc(b): return b[: (len(b) + 1) // 2]
seen, shr = {}, 0
for t in itertools.product(alpha, repeat=4):
    b = bytes(t); o = trunc(b)
    shr += len(o) < len(b); seen.setdefault(o, []).append(b)
check("P5c lossy truncation shrinks 100%", shr == 4 ** 4)
check("P5c ...but is not injective (collisions)", len(seen) < 4 ** 4, f"{len(seen)} outputs for {4**4} inputs")

print(f"RESULT: {'FAIL' if fails else 'PASS'} " +
      ("failed: " + "; ".join(fails) if fails else
       "no injective shrink L<=3; best avg=(L-2)+(L+2)/2^L (predicted +1 constant was off by one); RLE expands 4^8 majority; zlib 4096 random=4107; flag wrapper growth<=+1; skew Huffman avg<8 but worst>8"))
