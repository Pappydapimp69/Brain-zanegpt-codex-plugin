# Prediction (written before run): with window B={t mod P < w}, 3-lag sets from 1..12, the shadow count at press time T
# is identical for T, T+P, T+2P at every residue for P=10 and P=11, and takes >=3 distinct values across residues.
# Breaker: a model with a finite landing horizon (landing counted only if t+L < H) must break periodicity near H.
from itertools import combinations
def shadow_count(P, T, lags=range(1, 13), horizon=None):
    n = 0
    for w in range(1, P):
        for S in combinations(lags, 3):
            inB = lambda x: (x % P) < w
            legal = [L for L in S if (not inB(T)) or inB(T + L)]
            if horizon is not None:
                legal = [L for L in legal if T + L < horizon]
            if not legal: continue
            chosen = max(legal)
            # cutting lag: last lag (ascending) whose landing is in B (serves the window); else last lag
            serving = [L for L in S if inB(T + L) and (horizon is None or T + L < horizon)]
            cut = serving[-1] if serving else S[-1]
            n += chosen != cut
    return n
ok = True; out = []
for P in (10, 11):
    vals = []
    for r in range(P):
        c = [shadow_count(P, 600 + r + k * P) for k in range(3)]
        if len(set(c)) != 1: ok = False
        vals.append(c[0])
    d = len(set(vals)); out.append(f"P{P} distinct={d} range={min(vals)}-{max(vals)}")
    if d < 3: ok = False
# control: base offset 0 vs 600 agree on residue, different residue differ
same = shadow_count(10, 0) == shadow_count(10, 600) == shadow_count(10, 10)
# breaker: finite horizon H=640 breaks periodicity
H = 640
b = [shadow_count(10, 600 + 3 + k * 10, horizon=H) for k in range(5)]
broken = len(set(b)) > 1
out.append(f"zero_base_same={same} horizon_breaks={broken} vals={b}")
print("RESULT:", "PASS" if ok and same and broken else "FAIL", "; ".join(out))
