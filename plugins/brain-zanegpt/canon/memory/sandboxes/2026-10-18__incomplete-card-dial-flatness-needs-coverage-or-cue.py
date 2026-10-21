"""Distance dial sweep: 11 distances d=0..1. 10 beats, 5 severe (0.9) / 5 mild (0.3).
Funny of a beat with harm h at distance d: licence L = d + (0.4 if safe cue on that beat else 0);
funny = h if h <= L else L - 3*(h - L); violation floor: score counts max(.,-1) not needed.
Rule card caps severity at 0.3 on the covered fraction f of severe beats (those become mild).
Cue backstop applies only to UNCOVERED severe beats when on.  Robustness = number of the 11 distances
whose total >= 95% of the best total (only meaningful when best > 0)."""
D = [i/10 for i in range(11)]
def total(d, f, cue):
    n_cov = round(f*5); t = 0.0
    for i in range(10):
        if i < 5:
            h = 0.3 if i < n_cov else 0.9
            L = d + (0.4 if (cue and i >= n_cov) else 0.0)
        else:
            h, L = 0.3, d
        t += h if h <= L else L - 3*(h - L)
    return t
def robust(f, cue):
    ts = [total(d, f, cue) for d in D]; b = max(ts)
    return sum(t >= 0.95*b for t in ts), b
out = {}
for cue in (False, True):
    for f in (0.0, 0.5, 1.0):
        out[(cue, f)] = robust(f, cue)
        print(f"cue={cue} coverage={f}: {out[(cue,f)][0]} of 11 distances within 95% of best (best {out[(cue,f)][1]:.2f})")
full = out[(False, 1.0)][0]; none = out[(False, 0.0)][0]; half_cue = out[(True, 0.5)][0]; half = out[(False, 0.5)][0]
ok = full >= 8 and none <= 3 and half_cue >= 6
# BREAK: half coverage without cue (should be fragile) - check claim 'incomplete card alone keeps flatness' is false
print(f"BREAK half coverage no cue: {half} of 11")
print(f"RESULT: {'PASS' if ok and half <= 4 else 'FAIL'} within-95% distances: full card {full}, no card {none}, half card no cue {half}, half card with cue {half_cue}")
