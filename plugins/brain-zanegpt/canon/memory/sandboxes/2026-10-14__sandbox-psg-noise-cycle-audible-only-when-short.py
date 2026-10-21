import cmath, math
MASK = 0x0009
def step(s):
    fb = bin(s & MASK).count("1") & 1
    return (s >> 1) | (fb << 15)
def period(s, cap=70000):
    t = s
    for n in range(1, cap):
        t = step(t)
        if t == s: return n
    return None
def fft(x):
    n = len(x); j = 0
    x = list(x)
    for i in range(1, n):
        bit = n >> 1
        while j & bit: j ^= bit; bit >>= 1
        j ^= bit
        if i < j: x[i], x[j] = x[j], x[i]
    m = 2
    while m <= n:
        w = cmath.exp(-2j * math.pi / m)
        for k in range(0, n, m):
            t = 1
            for q in range(m // 2):
                u = x[k+q]; v = x[k+q+m//2] * t
                x[k+q] = u + v; x[k+q+m//2] = u - v; t *= w
        m <<= 1
    return x
def seeds():
    found = {}
    for s in range(1, 65536):
        if len(found) == 3: break
        if s in (0x8000,) or True:
            p = period(s) if s < 400 or 7 not in found or True else None
            if p in (7, 8191, 57337) and p not in found: found[p] = s
    return found
S = {57337: 0x8000}
for s in range(1, 65536):
    t = s
    for _ in range(7): t = step(t)
    if t == s and 7 not in S: S[7] = s
    if 8191 not in S and period(s) == 8191: S[8191] = s
    if len(S) == 3: break
print("seeds", {k: hex(v) for k, v in S.items()}, "check periods", {k: period(v) for k, v in S.items()})
def bits(seed, n):
    out = []; s = seed
    for _ in range(n): out.append(1.0 if s & 1 else -1.0); s = step(s)
    return out
def analyse(seed, N):
    x = bits(seed, N); mean = sum(x) / N; x = [v - mean for v in x]
    P = [abs(c) ** 2 for c in fft(x)][1:N//2]
    med = sorted(P)[len(P)//2]
    spur = 10 * math.log10(max(P) / med)
    empty = sum(1 for v in P if v < med * 0 + max(P) * 1e-4) / len(P)   # bins >40 dB below peak
    return spur, empty
res = {}
for N in (4096, 32768):
    for p, seed in sorted(S.items()):
        res[(N, p)] = analyse(seed, N)
        print(f"window={N:5d} cycle={p:5d}: peak/median {res[(N,p)][0]:6.1f} dB, empty bins {res[(N,p)][1]:.2f}")
def acorr(seed, lag, N=32768):
    x = bits(seed, N + lag)
    return sum(x[i] * x[i + lag] for i in range(N)) / N
ac = {p: acorr(seed, 8191) for p, seed in S.items()}
print("autocorrelation at lag 8191:", {p: round(v, 3) for p, v in ac.items()})
# v2 (v1 predicted a comb for the 8191 cycle; leakage from a non-integer period fills the bins, so the spectrum cannot see it)
tonal7 = res[(4096, 7)][1] > 0.9 and res[(32768, 7)][1] > 0.9
white = all(res[(N, p)][1] < 0.05 for N in (4096, 32768) for p in (8191, 57337))
acf = ac[8191] > 0.99 and abs(ac[57337]) < 0.2
frac_short = 7 / 65535; frac_cycle = 8198 / 65535
print("RESULT: %s only the 7-step cycle shows in the spectrum (empty %.2f); the 8191-step cycle stays spectrally white (empty %.2f at 32768) but autocorrelation at lag 8191 is %.2f vs %.2f; spectrally audible seeds 7/65535 = %.4f%%, not %.1f%%"
      % ("PASS" if tonal7 and white and acf else "FAIL", res[(4096,7)][1], res[(32768,8191)][1], ac[8191], ac[57337], frac_short*100, frac_cycle*100))
