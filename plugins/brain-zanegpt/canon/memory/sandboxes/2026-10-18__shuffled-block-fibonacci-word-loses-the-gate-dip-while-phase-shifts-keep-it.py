import random, statistics
N, LMAX = 600, 120
def fibword(n):
    s = "1"
    while len(s) < n:
        s = "".join("10" if c == "1" else "1" for c in s)
    return [int(c) for c in s[:n]]
def inval(sig, L): return sum(1 for t in range(N) if sig[t] and not sig[t + L])
def valid(sig, L): return sum(1 for t in range(N) if sig[t] and sig[t + L])
M = N + LMAX + 400
base = fibword(M)
def window(shift): return base[shift:shift + N + LMAX]
# 1) phase shifts keep the dip
shifts = range(0, 400, 37)
dips = []
for s in shifts:
    w = window(s)
    med = statistics.median(inval(w, L) for L in range(40, 71))
    dips.append((inval(w, 55), inval(w, 89), med))
# 2) BREAK: block-shuffled copies (block 13), same density
def shuffled(seed, B=13):
    w = window(0)
    blocks = [w[i:i + B] for i in range(0, len(w), B)]
    random.Random(seed).shuffle(blocks)
    return [x for b in blocks for x in b][:N + LMAX]
sh = []
for seed in range(20):
    w = shuffled(seed)
    med = statistics.median(inval(w, L) for L in range(40, 71))
    sh.append((inval(w, 55), inval(w, 89), med))
d55 = max(d[0] for d in dips); d89 = max(d[1] for d in dips)
dmed = min(d[2] for d in dips)
s55 = statistics.mean(x[0] for x in sh); s89 = statistics.mean(x[1] for x in sh); smed = statistics.mean(x[2] for x in sh)
# 3) validity lossless lag: still the scan limit on the unshuffled word?
ll = max(L for L in range(1, LMAX + 1) if valid(window(0), L) > 0)
print("phase-shifted words: worst inv55 %d inv89 %d, smallest window median %d" % (d55, d89, dmed))
print("shuffled blocks (20): mean inv55 %.1f inv89 %.1f window median %.1f; lossless lag of word %d" % (s55, s89, smed, ll))
ok = d55 <= 15 and d89 <= 15 and dmed > 100 and s55 > 0.5 * smed and s89 > 0.5 * smed
print("RESULT: %s Fibonacci phase shifts (11 starts) keep inv55<=%d inv89<=%d against median>=%d; block-shuffled copies give %.0f and %.0f against %.0f"
      % ("PASS" if ok else "FAIL", d55, d89, dmed, s55, s89, smed))
