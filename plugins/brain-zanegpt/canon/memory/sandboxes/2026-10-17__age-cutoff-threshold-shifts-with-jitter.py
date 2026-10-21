# Sandbox: age cutoff over a validity gate when observed lag = true lag + jitter.
# Valid presses have true lag in V; cutoff c drops presses whose OBSERVED lag exceeds c.
# Deterministic jitter: every offset in [-J, +J] (or [-J, 0] in the early-only scenario).
def presses(V, J, early_only):
    offs = range(-J, 1) if early_only else range(-J, J + 1)
    return [(lag, lag + o) for lag in V for o in offs]      # every lag meets every jitter offset

def lost(V, J, c, early_only=False):
    return sum(1 for true, obs in presses(V, J, early_only) if obs > c)

V = [4, 8, 12, 20]            # valid-press lags, max 20, wave period 12
mx = max(V)
rows, ok = [], True
for J in range(0, 9):
    at_max = lost(V, J, mx)
    at_mx_j = lost(V, J, mx + J)
    below = lost(V, J, mx + J - 1)
    period = lost(V, J, 12)
    rows.append((J, at_max, at_mx_j, below, period))
    ok &= at_mx_j == 0 and below > 0 and period > 0
    ok &= (at_max > 0) == (J > 0)
early = [lost(V, J, mx, True) for J in range(0, 9)]
ok &= all(e == 0 for e in early)          # BREAK: lag-only-early jitter leaves threshold at max lag
for r in rows:
    print("J=%d  cutoff=max:%d  cutoff=max+J:%d  max+J-1:%d  period12:%d" % r)
print("early-only jitter, cutoff=max lost:", early)
print("RESULT: %s lossless threshold = max valid lag + J (0 lost at all J=0..8), one below lost >0 each, max-only lost >0 for all J>0, period cutoff lost >0 each; early-only jitter kept 0 lost at max" % ("PASS" if ok else "FAIL"))
