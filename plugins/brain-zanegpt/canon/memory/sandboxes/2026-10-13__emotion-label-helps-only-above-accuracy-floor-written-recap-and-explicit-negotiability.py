"""Prediction (before run), model with assumed constants, deterministic expected values:
Seller B reservation 100, buyer A budget 120, A opens 90, B asks 130 when B asks at all. Each round both concede; B's step = 4*(1-f), f = B's frustration,
f rises 0.15/round while B's feelings go unnamed and gap>10. A label at round 2 with accuracy a changes f to f*(1-0.8a) + 0.3*(1-a) (a mislabel adds frustration).
P1 label with a=1 reaches a deal at least 2 rounds sooner than no label. P2 there is an accuracy floor a* in (0,0.6): below it, labelling is slower than no label. P3 when B starts calm (f0=0, no frustration growth),
labelling gives no speed-up (0 rounds). P4 (written-vs-verbal) retreat when a rival offer gains g over the deal price happens at g > k*c with c=1 spoken, 2 written: over the gain grid 1..12 (k=3), written deals survive in >= 2x more grid points than spoken. P5 (BREAK) with an empty deal zone (budget 95) neither label nor recap makes a deal.
P6 (ask gap) when negotiability is ambiguous the seller asks with prob 0.5 vs 0.9 when explicit; expected final price is higher explicit by >= 5 (price 90 if no ask, label-and-bargain outcome if ask). Stdlib, no RNG."""
from fractions import Fraction as F
def bargain(budget=120, f0=0.0, grow=0.15, label_round=None, a=1.0, horizon=40, calm=False):
    A, B, f, r = 90.0, 130.0, f0, 0
    while r < horizon:
        r += 1
        if B <= A: return r - 1, (A + B) / 2
        if label_round == r: f = f * (1 - 0.8 * a) + 0.3 * (1 - a)
        elif B - A > 10 and not calm: f = min(0.95, f + grow)
        stepA = 4.0; stepB = 4.0 * (1 - f)
        if A + stepA > budget: stepA = max(0.0, budget - A)
        A += stepA; B -= stepB
        if B < 100 and not (B < 100): pass
        B = max(B, 100.0)
        if B <= A: return r, round((A + B) / 2, 2)
    return None, None
def rounds(**k):
    r, p = bargain(**k); return (r if r is not None else 99), p
base = rounds(f0=0.3)
lab = {a: rounds(f0=0.3, label_round=2, a=a) for a in (0, .25, .5, .75, 1.0)}
print("none", base, "labels", lab)
p1 = base[0] - lab[1.0][0] >= 2
worse = [a for a in lab if lab[a][0] > base[0]]
p2 = len(worse) > 0 and max(worse) < .6 and lab[.75][0] <= base[0] if True else False
calm_none = rounds(f0=0.0, calm=True); calm_lab = rounds(f0=0.0, calm=True, label_round=2, a=1.0)
p3 = calm_none[0] - calm_lab[0] == 0
print("calm", calm_none, calm_lab)
k = 3
surv = lambda c: sum(1 for g in range(1, 13) if g <= k * c)
p4 = surv(2) >= 2 * surv(1)
empty = rounds(f0=.3, budget=95, label_round=2, a=1.0)
p5 = empty[0] == 99
fin = lambda p_ask: p_ask * lab[1.0][1] + (1 - p_ask) * 90
p6 = fin(.9) - fin(.5) >= 5
print("empty zone", empty, "survival grid verbal/written", surv(1), surv(2), "price ambiguous %.2f explicit %.2f" % (fin(.5), fin(.9)))
print("P1", p1, "P2", p2, "P3", p3, "P4", p4, "P5", p5, "P6", p6)
print("RESULT:", "PASS" if all([p1, p2, p3, p4, p5, p6]) else "FAIL", f"{sum([p1,p2,p3,p4,p5,p6])}/6 held; rounds none {base[0]}, label a=1 {lab[1.0][0]}, a=.5 {lab[.5][0]}, a=0 {lab[0][0]}; calm {calm_none[0]} vs {calm_lab[0]}; survival {surv(1)} vs {surv(2)}; empty zone {empty[0]}; price {fin(.5):.2f} vs {fin(.9):.2f}")
