# Karplus-Strong: the 2-tap average adds half a sample, so f = FS/(N+0.5); integer N detunes high notes.
import math, random
FS = 44100
def ks(N, n, seed=1):      # textbook: y[n] = .5(y[n-N] + y[n-N-1])  -> loop delay N+.5
    r = random.Random(seed); y = [r.uniform(-1, 1) for _ in range(N + 1)]
    for i in range(N + 1, n): y.append(.5 * (y[i - N] + y[i - N - 1]) * .999)
    return y
def ks_inplace(N, n, seed=1):   # common ring-buffer shortcut averages with the NEXT slot -> loop delay N-.5
    r = random.Random(seed); buf = [r.uniform(-1, 1) for _ in range(N)]; out = []
    for i in range(n):
        a = buf[i % N]; b = buf[(i + 1) % N]; out.append(a); buf[i % N] = .5 * (a + b) * .999
    return out
def pitch(x, lo, hi):
    best, bl = -1e9, lo; ac = {}
    for L in range(lo, hi + 1):
        ac[L] = sum(x[i] * x[i + L] for i in range(len(x) - hi - 1)); 
        if ac[L] > best: best, bl = ac[L], L
    a, b, c = ac.get(bl - 1, best), best, ac.get(bl + 1, best)
    d = .5 * (a - c) / (a - 2 * b + c) if (a - 2 * b + c) else 0
    return FS / (bl + d)
def cents(f, ref): return 1200 * math.log2(f / ref)
res = []; rows = []
for target in (110, 440, 1760):
    Nn = round(FS / target); Nc = round(FS / target - .5)
    x = ks(Nn, 6000)[1000:]; fn = pitch(x, Nn - 3, Nn + 3)
    x = ks(Nc, 6000)[1000:]; fc = pitch(x, Nc - 3, Nc + 3)
    rows.append((target, Nn, fn, cents(fn, target), Nc, fc, cents(fc, target)))
    print(f"{target}Hz naive N={Nn} -> {fn:.1f}Hz ({cents(fn,target):+.1f}c) | half-sample N={Nc} -> {fc:.1f}Hz ({cents(fc,target):+.1f}c) | model FS/(N+.5)={FS/(Nn+.5):.1f}")
    res.append(abs(cents(fn, FS / (Nn + .5))) < 2)          # model f=FS/(N+.5) holds
fi = pitch(ks_inplace(100, 6000)[1000:], 97, 103)
print(f"ring-buffer variant N=100 -> {fi:.1f}Hz, model FS/(N-.5)={FS/99.5:.1f}")
res.append(abs(cents(fi, FS / 99.5)) < 2)
# 1) low note: naive error small (<5c). 2) 440: naive ~ -5c. 3) BREAK: 1760 even with half-sample fix stays >10c off -> needs fractional delay
res.append(abs(rows[0][3]) < 5); res.append(abs(rows[1][3]) > 3); res.append(abs(rows[2][6]) > 10)
thr = FS / (1200 / (10 * math.log(2)) * .5)   # P where worst-case half-sample rounding = 10 cents
print(("RESULT: PASS" if all(res) else "RESULT: FAIL") + f" textbook FS/(N+.5) and ring-buffer FS/(N-.5) both within 2c; naive 110/440/1760 = {rows[0][3]:+.0f}/{rows[1][3]:+.0f}/{rows[2][3]:+.0f}c; 1760 after half-sample fix still {rows[2][6]:+.0f}c; 10c worst-case threshold ~{thr:.0f}Hz")
