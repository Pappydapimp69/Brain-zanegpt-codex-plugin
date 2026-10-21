"""Rebuild of seven E60 (inner voices cannot be spread; half inner drops the budget to 2).
Own fixture: masking width w = 45/90 (E60 used E55's 60), talk share p = 0.3/0.5, inner share
s = 0.34 and 0.72 (the survey's inside-only, and inside-only + half of 'both'), voices
assigned deterministically (round(s*N) inner, rest spread evenly). An inner voice is masked
by every other voice; an outer voice by every inner voice plus outer neighbours within w.
Mean landing over voices; budget = largest N with mean landing >= 0.5 for all N' <= N.
Predictions written before running:
 P1 any inner share >= 0.34 cuts the budget below the all-outside budget in every cell (expect hold).
 P2 with s = 0.72 the budget equals the one-place budget in every cell (E60: 'same as one place').
 P3 the all-outside budget is 5 at w=45 (E60's corrected E55 number) (expect MISS: width-bound).
"""

def mean_landing(N, p, w, s):
    n_in = round(s * N); n_out = N - n_in
    tot = 0.0
    for i in range(n_in):
        tot += (1 - p) ** (N - 1)
    if n_out:
        step = 360.0 / n_out
        nb = sum(1 for k in range(1, n_out) if min(k * step, 360 - k * step) <= w + 1e-9)
        tot += n_out * (1 - p) ** (nb + n_in)
    return tot / N

def budget(p, w, s):
    b = 0
    for N in range(1, 41):
        if mean_landing(N, p, w, s) >= 0.5: b = N
        else: break
    return b

def one_place(p):
    return budget(p, 360, 0.0)

cells = {}
for w in (45, 90):
    for p in (0.3, 0.5):
        cells[(w, p)] = {s: budget(p, w, s) for s in (0.0, 0.34, 0.72)}
        print(f"w={w} p={p}: budget outside/0.34/0.72 = {cells[(w,p)][0.0]}/{cells[(w,p)][0.34]}/{cells[(w,p)][0.72]}; one place {one_place(p)}")
p1 = all(c[0.34] < c[0.0] and c[0.72] < c[0.0] for c in cells.values())
p2 = all(c[0.72] == one_place(p) for (w, p), c in cells.items())
p3 = cells[(45, 0.3)][0.0] == 5
checks = [("P1 inner share cuts budget", p1), ("P2 s=0.72 equals one place", p2), ("P3 all-outside budget 5 at w=45", p3)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 3 else 'FAIL'} {held}/3; " + "; ".join(
    f"w{w} p{p} {c[0.0]}/{c[0.34]}/{c[0.72]} (one place {one_place(p)})" for (w, p), c in cells.items()))
