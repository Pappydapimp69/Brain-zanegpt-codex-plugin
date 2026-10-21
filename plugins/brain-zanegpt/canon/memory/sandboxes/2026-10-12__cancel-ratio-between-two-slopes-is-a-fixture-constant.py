"""Blind rebuild of seven E76 (a sanity penalty on competence cancels only with
recovery damping 3-5x steeper; a 0.10 penalty cannot be cancelled).
Own fixture (exact DP, no rng): sanity s on a 0..20 grid (s/20 in [0,1]),
start 20. Each of 60 turns the lead attempts a task: success prob
c(s) = p0 * (1 - a*(1 - s/20))   [a = competence lost at zero sanity]
success: s += 1 (capped 20). failure: s -= 3. Then passive recovery: with
prob r(s) = min(1, r0 * (1 + b*(1 - s/20))) s += 1. Run ENDS at s = 0
(breakdown). Outcome = expected tasks succeeded. Baseline a = b = 0.
'Cancel' = outcome(a, b) >= outcome(0, 0). For each a find the least b (grid
0.01, up to 10) that cancels; report b*/a. Two parameter sets (A: p0 .7 r0 .15;
B: p0 .8 r0 .30) to see if the ratio is a property of the claim or the model.
PREDICTION (before running): small penalties can be cancelled and need b > a;
some penalty is uncancellable once r hits its cap of 1 (holds in both sets);
BUT the 3-5x ratio is NOT stable: b*/a differs by more than 2x between sets A
and B, so the '3 to 5 times' number is a fixture constant, not a rule.
Iteration note: iteration 1 scaled a and b per 0.1 sanity (x10); it gave
ratios 28x (set A) and 158x (set B) at a=0.01. Iteration 2 (this file) uses
slopes over the full range, the units the claim's numbers appear to use.
"""
import sys
print("python", sys.version.split()[0])
G, TURNS = 20, 60
def outcome(a, b, p0, r0):
    dist = [0.0]*(G+1); dist[G] = 1.0; tasks = 0.0
    for _ in range(TURNS):
        nd = [0.0]*(G+1)
        for s in range(1, G+1):
            m = dist[s]
            if m == 0: continue
            c = max(0.0, p0*(1 - a*(1 - s/G)))
            tasks += m*c
            for s2, w in ((min(G, s+1), c), (max(0, s-3), 1-c)):
                if s2 == 0: nd[0] += m*w; continue
                r = min(1.0, r0*(1 + b*(1 - s2/G)))
                nd[min(G, s2+1)] += m*w*r; nd[s2] += m*w*(1-r)
        nd[0] += dist[0]; dist = nd
    return tasks
def least_b(a, p0, r0):
    base = outcome(0, 0, p0, r0)
    for k in range(0, 1001):
        b = k*0.01
        if outcome(a, b, p0, r0) >= base - 1e-12: return b
    return None
sets = {"A": (0.7, 0.15), "B": (0.8, 0.30)}
ratios = {}
for name, (p0, r0) in sets.items():
    print(f"set {name}: baseline tasks {outcome(0,0,p0,r0):.3f}")
    ratios[name] = {}
    for a in (0.03, 0.06, 0.10, 0.20, 0.40):
        b = least_b(a, p0, r0); ratios[name][a] = (b/a if b is not None else None)
        print(f"  a {a:.2f}: least cancelling b {b}  ratio {ratios[name][a]}")
canc_small = all(ratios[n][0.03] is not None for n in sets)
bgt = all(r is None or r > 1 for n in sets for r in ratios[n].values())
uncanc = all(any(r is None for r in ratios[n].values()) for n in sets)
ra = [r for r in ratios['A'].values() if r]; rb = [r for r in ratios['B'].values() if r]
ra0 = ratios['A'][0.03]; rb0 = ratios['B'][0.03]
unstable = ra0 and rb0 and max(ra0, rb0)/min(ra0, rb0) > 2
in35 = {n: [a for a, r in ratios[n].items() if r and 3 <= r <= 5] for n in sets}
print("small cancellable:", canc_small, "| needs b>a:", bgt, "| some uncancellable:", uncanc, "| ratio@0.03 A", ra0, "B", rb0, "unstable(>2x):", unstable)
print("penalties whose ratio falls in 3-5x:", in35)
claim_ratio = all(not (r and not 3 <= r <= 5) for n in sets for r in ratios[n].values())
claim_010 = all(ratios[n][0.10] is None for n in sets)
print("my prediction: shape", canc_small and bgt and uncanc, "| >2x instability at 0.03:", unstable, "(at 0.06:", round(ratios['B'][0.06]/ratios['A'][0.06], 2), ")")
print("claim: every cancelling ratio in 3-5x:", claim_ratio, "| 0.10 uncancellable in both sets:", claim_010)
print(f"RESULT: {'PASS' if (claim_ratio and claim_010) else 'FAIL'} shape holds (small penalty cancels, b>a, a cap makes big ones uncancellable) but ratios {min(ra):.0f}-{max(rb):.0f}x not 3-5x; 0.10 cancelled in set A (b {ratios['A'][0.10]*0.10:.2f}); numbers are fixture constants")
