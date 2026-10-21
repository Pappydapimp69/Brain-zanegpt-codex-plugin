# Deterministic: legality words from rotations; gate-only invalid(L,N,start) = #t in [start,start+N)
# with legal(t-L) and not legal(t). Valid presses: legal(t-L) and legal(t). Cutoff gate: L<=c.
import random
PHI = (5**0.5-1)/2          # 0.618..
def word(alpha, n, rho=0.0):
    return [int((t+1)*alpha+rho)-int(t*alpha+rho) for t in range(n)]
def inv(w, L, start, N):
    return sum(1 for t in range(start, start+N) if w[t-L] and not w[t])
def dev(w, L, start):
    # line fitted from the SHORT horizon N=600, tested at N=4800
    return abs(inv(w, L, start, 4800) - 8*inv(w, L, start, 600))
n = 6200
fib = word(PHI, n)
rot2 = word(2**0.5-1, n)              # deterministic control: different slope (density .414)
rnd = random.Random(0); bern = [1 if rnd.random()<PHI else 0 for _ in range(n)]
starts = list(range(130, 130+25*37, 37))   # 25 offsets
res = {}
for name, w in (("fib", fib), ("rot_sqrt2", rot2), ("bernoulli", bern)):
    for L in (55, 89, 47):
        res[(name, L)] = max(dev(w, L, s) / 1 for s in starts)
    print(name, {L: res[(name, L)] for L in (55, 89, 47)})
# Path part: lossless cutoff on top of validity = largest lag with a valid press.
def lossless(w, lags, start, N):
    valid = {L: sum(1 for t in range(start, start+N) if w[t-L] and w[t]) for L in lags}
    maxvalid = max((L for L in lags if valid[L]), default=0)
    lost = lambda c: sum(v for L, v in valid.items() if L > c)
    cs = [c for c in range(0, max(lags)+1) if lost(c) == 0]
    return (cs[0] if cs else None), maxvalid
lags = [3, 8, 21, 55, 89]
lc = lossless(fib, lags, 130, 4800)
print("lossless cutoff vs max valid lag (fib)", lc)
ok_path = lc[0] == lc[1]
# Discriminator: does fib stay tighter than control across all offsets? Report honestly.
fib_max = max(res[("fib", L)] for L in (55, 89, 47))
rot_max = max(res[("rot_sqrt2", L)] for L in (55, 89, 47))
bern_max = max(res[("bernoulli", L)] for L in (55, 89, 47))
print("max dev over 25 offsets: fib", fib_max, "rot_sqrt2", rot_max, "bernoulli", bern_max)
generic = rot_max <= 3 and fib_max <= 3 and bern_max > 3
print(f"RESULT: {'PASS' if ok_path and generic else 'FAIL'} fib dev<={fib_max} rot_sqrt2 dev<={rot_max} bernoulli dev<={bern_max} over 25 offsets fit at N600; lossless cutoff {lc[0]} == max valid lag {lc[1]}")
