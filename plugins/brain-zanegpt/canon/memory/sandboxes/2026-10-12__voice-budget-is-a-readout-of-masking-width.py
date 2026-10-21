"""Rebuild of seven E58 (voices: content up to ~2 in one place / ~4 spread; texture past ~6).
Own fixture: masking width w = 30/45/90/120 deg (E58 used 60 only), talk share p = 0.2/0.4/0.6,
voices placed evenly; a phrase lands if no masker talks over it; masker = another voice
within w (inclusive). Budget = largest N with landing >= 0.5 for every N' <= N.
Predictions written before running:
 P1 the one-place budget is 2 at every p (expect MISS: it moves with p).
 P2 the spread budget stays within 3..5 across w in 30..120 at p = 0.4 (expect MISS).
 P3 spreading at least doubles the one-place budget in every cell (expect hold).
"""

def masked_by(N, w):
    if N == 1: return 0
    step = 360.0 / N
    return sum(1 for k in range(1, N) if min(k * step, 360 - k * step) <= w + 1e-9)

def landing(N, p, w=None):
    m = N - 1 if w is None else masked_by(N, w)
    return (1 - p) ** m

def budget(p, w=None):
    b = 0
    for N in range(1, 41):
        if landing(N, p, w) >= 0.5: b = N
        else: break
    return b

one = {p: budget(p) for p in (0.2, 0.4, 0.6)}
spread = {(w, p): budget(p, w) for w in (30, 45, 60, 90, 120) for p in (0.2, 0.4, 0.6)}
for p in (0.2, 0.4, 0.6):
    print(f"p={p}: one-place budget {one[p]}; spread budgets by w 30/45/60/90/120: " +
          "/".join(str(spread[(w, p)]) for w in (30, 45, 60, 90, 120)))
p1 = all(v == 2 for v in one.values())
p2 = all(3 <= spread[(w, 0.4)] <= 5 for w in (30, 45, 60, 90, 120))
p3 = all(spread[(w, p)] >= 2 * one[p] for w in (30, 45, 60, 90, 120) for p in (0.2, 0.4, 0.6))
checks = [("P1 one-place budget always 2", p1), ("P2 spread budget 3..5 across widths", p2), ("P3 spread >= 2x one-place", p3)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 3 else 'FAIL'} {held}/3; one-place budget p0.2/0.4/0.6 {one[0.2]}/{one[0.4]}/{one[0.6]}; "
      f"spread at p0.4 w30..120 " + "/".join(str(spread[(w, 0.4)]) for w in (30, 45, 60, 90, 120)) +
      f"; spread range {min(spread.values())}-{max(spread.values())}")
