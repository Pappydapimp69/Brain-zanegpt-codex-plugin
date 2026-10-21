# Clash model: side x scores P_x * (BASE + m_x), m_x = mash count in 1..M. Enumerate ALL (m_s, m_w) pairs (no RNG).
# Kernels exercised: RPG/power-tier-clash-check (seed bias + live window), RPG/power-creep (per-tier power-budget cap on ratio),
# SYSTEM/damage-cap-can-erase-a-burst-skills-niche (measure by band, not aggregate).
# Prediction (before run): overturn rate falls monotonically with ratio r and is exactly 0 from r >= (BASE+M)/(BASE+1) (2.5 for M=10, BASE=5);
# widening M to 20 moves that threshold to 25/6; a power-budget cap (effective r clamped to 2.0) leaves the aggregate overturn over r in 1..5 looking sane
# but gives >0 overturn in a band (r>2.5) where uncapped is 0 -- i.e. the cap blurs tier meaning rather than erasing a niche (opposite direction to the damage cap).
from fractions import Fraction as F
BASE = 5
def overturn(r, M, cap=None):
    # r = true power ratio strong/weak; if cap, the SEED the clash sees is min(r, cap)
    seed = F(min(r, cap)) if cap else F(r)
    n = w = 0
    for ms in range(1, M + 1):
        for mw in range(1, M + 1):
            n += 1; w += (1 * (BASE + mw) > seed * (BASE + ms))
    return F(w, n)
ratios = [F(k, 4) for k in range(4, 21)]  # 1.0 .. 5.0 step .25
ok = True
M = 10
rates = [overturn(r, M) for r in ratios]
mono = all(a >= b for a, b in zip(rates, rates[1:]))
thr = F(BASE + M, BASE + 1)
zero_from = min(r for r, v in zip(ratios, rates) if v == 0)
ok &= mono and all(v == 0 for r, v in zip(ratios, rates) if r >= thr) and all(v > 0 for r, v in zip(ratios, rates) if r < thr)
print("M=10 thr", thr, "first zero ratio on grid", zero_from, "mono", mono)
M2 = 20; thr2 = F(BASE + M2, BASE + 1)
rates2 = [overturn(r, M2) for r in ratios]
ok &= all(v == 0 for r, v in zip(ratios, rates2) if r >= thr2) and all(v > 0 for r, v in zip(ratios, rates2) if r < thr2)
print("M=20 thr", thr2, "zero from", min(r for r, v in zip(ratios, rates2) if v == 0))
# power-budget cap at 2.0 on the seed the clash uses (true ratio keeps growing)
capped = [overturn(r, M, cap=2) for r in ratios]
agg_u = sum(rates) / len(rates); agg_c = sum(capped) / len(capped)
band_hi = [(r, u, c) for r, u, c in zip(ratios, rates, capped) if r >= thr]
print("aggregate overturn uncapped %.3f capped %.3f" % (float(agg_u), float(agg_c)))
print("band r>=2.5: uncapped", [float(u) for _, u, _ in band_hi][:3], "capped", [float(c) for _, _, c in band_hi][:3])
ok &= all(u == 0 for _, u, _ in band_hi) and all(c > 0 for _, _, c in band_hi)
# BREAK: aggregate metric hides the band change? aggregate differs only modestly while the high band flips 0 -> >0
ok &= abs(agg_c - agg_u) < F(1, 4)
print("RESULT:", "PASS" if ok else "FAIL", "overturn monotone in ratio; zero from r>=%s (M=10) and %s (M=20); cap=2 gives r>=2.5 band %.3f instead of 0 (aggregate %.3f vs %.3f)" % (thr, thr2, float(capped[-1]), float(agg_c), float(agg_u)))
