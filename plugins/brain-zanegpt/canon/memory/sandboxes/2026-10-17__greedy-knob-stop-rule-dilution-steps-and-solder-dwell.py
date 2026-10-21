"""Sandbox: one stop rule for two 'turn the knob up' decisions.
Rule G (greedy): raise the knob one notch at a time; stop when the next notch does not improve the metric
by >= 1 percent of the current value. Then report whether the TARGET is met.
System A (dilution E1): knob = step count n, metric = worst-case error pct (lower is better), target <= 3 pct.
   err(a,n) as in the stored dilution sandbox (transfer + diluent error, floor 0.5 pct, a/volume uL term).
System B (solder): knob = dwell s, metric = joint temperature C (higher better), target >= 217 C.
   T(t) = Tss - (Tss - Tamb) * exp(-t/tau), tau = C/(Gt+Gb); Tss = (Gt*Ttip+Gb*Tamb)/(Gt+Gb).
Deterministic, no RNG."""
import math
def err(a, n, total=1000.0, vol=1000.0):
    f = total ** (1.0 / n); t = vol / f; d = vol - t
    rel = lambda v: max(0.005, a / v)
    return n * (rel(t) + rel(d) * (d / vol)) * 100
def greedy_n(a, nmax=8):
    n = 1
    while n < nmax and err(a, n + 1) <= err(a, n) * 0.99:
        n += 1
    return n
def best_n(a): return min(range(1, 9), key=lambda n: err(a, n))
rows = []
for a in (0.0, 0.2, 0.5, 1.0, 2.0):
    g, b = greedy_n(a), best_n(a)
    rows.append((a, g, b, err(a, g), err(a, b)))
    print("dilution a=%.1f greedy n=%d (%.2f pct) best n=%d (%.2f pct) %s" % (a, g, err(a, g), b, err(a, b), "TRAPPED" if g != b else ""))
def temp(Gt, Gb, Ttip, Tamb, t, C=0.3):
    Tss = (Gt * Ttip + Gb * Tamb) / (Gt + Gb); tau = C / (Gt + Gb)
    return Tss - (Tss - Tamb) * math.exp(-t / tau), Tss
def greedy_dwell(Gt, Gb, Ttip, Tamb, step=0.25, tmax=20.0):
    t = step
    while t < tmax:
        now, nxt = temp(Gt, Gb, Ttip, Tamb, t)[0], temp(Gt, Gb, Ttip, Tamb, t + step)[0]
        if nxt - now < 0.01 * (now - Tamb):      # next notch gains under 1 percent of the rise so far
            break
        t += step
    return t
sol = {}
for name, Gb, Tamb in (("small pad", 0.1, 25.0), ("ground plane", 0.5, 25.0), ("ground plane preheat", 0.5, 100.0)):
    t = greedy_dwell(0.5, Gb, 350.0, Tamb)
    T, Tss = temp(0.5, Gb, 350.0, Tamb, t)
    sol[name] = (t, T, Tss)
    print("solder %-20s greedy stops at %.2f s, T=%.1f C, steady %.1f C, melts=%s" % (name, t, T, Tss, T >= 217.0))
ok = True
gap = max(r[3] - r[4] for r in rows)
ok &= gap < 0.01                                   # greedy error within 0.01 pct of the true optimum for every a
ok &= any(r[1] != r[2] for r in rows)              # BREAK: greedy n differs from argmin at a=2 (plateau 5 vs 6)
ok &= sol["small pad"][1] >= 217.0 and sol["ground plane"][1] < 217.0 and sol["ground plane"][2] < 217.0
ok &= sol["ground plane preheat"][1] >= 217.0
print("RESULT: %s greedy 1 pct stop rule is within %.3f pct of the dilution optimum at every a tested (n differs at a=2.0, 5 vs 6, a plateau); in solder it stops at saturation (ground plane %.1f C of steady %.1f C, target 217 C unmet) so the target check after the stop, not the stop, says change lever" % ("PASS" if ok else "FAIL", gap, sol["ground plane"][1], sol["ground plane"][2]))
