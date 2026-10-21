"""Sandbox: the late severity cap (late-severity-cap-leaves-the-distance-dial-sharp) run on the escalation model of
escalation-needs-matching-distance/E1 (habituation exp(-0.2X), X += 1/(1+I/5), response I/C, ceiling C=10, gate
g = exp(-((d - I/C)/W)^2)) instead of the cover/laugh model, with a rule-card cap (write-the-rules-before-the-gags)
arriving at beat L. Deterministic, stdlib only. W (gate width) is assumed 0.25 in E1; swept here."""
import math
C = 10.0
DS = [i / 10 for i in range(11)]
def total(d, n, L, cap, W, habit=True):
    x, t = 0.0, 0.0
    for i in range(1, n + 1):
        I = C * i / n
        if i > L: I = min(I, cap * C)            # rule card caps severity at cap*C from beat L+1
        g = math.exp(-(((d - I / C) / W) ** 2))
        h = math.exp(-0.2 * x) if habit else 1.0
        t += h * (I / C) * g
        x += 1 / (1 + I / 5)
    return t
def window(n, L, cap, W):
    ts = [total(d, n, L, cap, W) for d in DS]
    m = max(ts)
    return sum(1 for t in ts if t >= 0.95 * m), DS[ts.index(m)]
rows = {}
for W in (0.15, 0.25, 0.5):
    rows[W] = [window(6, L, 0.3, W) for L in range(0, 7)]
    print(f"W={W}: (window, best d) for L=0..6 -> {rows[W]}")
# S2: cap level sweep at W=0.25, L=0
lv = {c: window(6, 0, c, 0.25) for c in (0.1, 0.3, 0.5, 0.8)}
print("cap level sweep (W=0.25, L=0):", lv)
w25 = [w for w, _ in rows[0.25]]
mono = all(a >= b for a, b in zip(w25, w25[1:]))
forgiving_L3 = w25[3] >= 7
wide_better = rows[0.5][0][0] > rows[0.15][0][0]
best_moves = rows[0.25][0][1] != rows[0.25][6][1]
print("window by L (W=0.25):", w25, "| monotone:", mono, "| L=3 forgiving (>=7):", forgiving_L3,
      "| wider gate wider window at L=0:", wide_better, "| best d moves with cap timing:", best_moves)
ok = (not forgiving_L3) and wide_better
print(f"RESULT: {'PASS' if ok else 'FAIL'} window by cap beat L (W 0.25) {w25}; forgiving at L=3 {forgiving_L3}; W0.15 L0 {rows[0.15][0][0]} vs W0.5 L0 {rows[0.5][0][0]}; best d at L=0 {rows[0.25][0][1]} vs L=6 {rows[0.25][6][1]}")
