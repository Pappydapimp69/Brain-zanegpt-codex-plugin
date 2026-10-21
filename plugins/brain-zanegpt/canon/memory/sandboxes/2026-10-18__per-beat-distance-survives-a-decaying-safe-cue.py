"""10 beats (4 severe 0.9, 6 mild 0.3), safe cue strength 0.4*decay**k for the k-th severe beat (habituation),
licence = distance + cue (severe beats only). Severe beat: h if h<=L else L-3(h-L). Mild beat: 1-d if d<=... scored
as closeness reward (1-d) when 0.3 <= licence (always true here).
Strategies: GLOBAL (best single distance on a 0..1 grid, 11 points) vs PER-BEAT (severe 0.5, mild 0.1).
Per-beat severe distance 0.5 relies on the cue; if the cue decays the severe beats overshoot, so the
per-beat advantage should shrink as decay falls and may flip."""
D = [i/10 for i in range(11)]
def total(ds, dm, decay):
    t = 0.0
    for k in range(4):
        L = ds + 0.4 * decay**k
        t += 0.9 if 0.9 <= L else L - 3*(0.9 - L)
    t += 6 * (1 - dm)
    return t / 10
def gain(decay, sev_d=0.5):
    g = max(total(d, d, decay) for d in D)
    p = total(sev_d, 0.1, decay)
    return g, p, p - g
res = {}
for decay in (1.0, 0.8, 0.5, 0.2):
    g, p, d = gain(decay)
    res[decay] = d
    print(f"decay={decay}: global-best {g:.3f} per-beat(sev .5) {p:.3f} gain {d:+.3f}")
# fix: per-beat with severe distance re-tuned for the decaying cue
g8, p8, _ = gain(0.5, sev_d=0.8)
print(f"BREAK decay=0.5 per-beat with severe distance 0.8: {p8:.3f} vs global {g8:.3f} gain {p8-g8:+.3f}")
ok = res[1.0] > 0 and res[0.5] < res[1.0] and res[0.2] <= 0.0 and (p8 - g8) > 0
print(f"RESULT: {'PASS' if ok else 'FAIL'} per-beat gain {res[1.0]:+.3f} at decay 1.0, {res[0.8]:+.3f} at 0.8, {res[0.5]:+.3f} at 0.5, {res[0.2]:+.3f} at 0.2; retuned severe distance 0.8 gain {p8-g8:+.3f} at 0.5")
