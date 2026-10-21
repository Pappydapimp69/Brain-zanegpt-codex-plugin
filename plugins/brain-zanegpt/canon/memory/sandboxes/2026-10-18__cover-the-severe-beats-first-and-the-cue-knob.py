"""Sandbox on the incomplete-rule-card model (escalation-needs-matching-distance/E1 gate+habituation, additive safe cue):
(1) does it matter WHICH beats the card covers (severe first vs mild first), and (2) how much cue does go-big need?
Kernel ideas:COMEDY/dark-humor/severe-harm-needs-distance-mild-harm-needs-closeness. Exact, deterministic, stdlib only."""
import math
C = 10.0
LIN = [2 + 8 * k / 5 for k in range(6)]            # 2 .. 10
FLAT = [10.0] * 6
MILD = [3, 3.5, 4, 4, 4.5, 5]
def score(seq, covered, cue, fb=0.3):
    X = tot = 0.0
    for I, cov in zip(seq, covered):
        d = I / C if cov else fb
        g = math.exp(-((d - I / C) / 0.25) ** 2)
        if not cov: g = g + cue * (1 - g)
        tot += math.exp(-0.2 * X) * (I / C) * g; X += 1 / (1 + I / 5)
    return tot
def cov_mask(seq, k, order):
    idx = sorted(range(6), key=lambda i: -seq[i] if order == "severe" else seq[i])
    chosen = set(idx[:k]); return [i in chosen for i in range(6)]
# (1) severe-first vs mild-first on the linear escalation
tab = {}
for cue in (0.0, 0.7):
    for k in range(0, 7):
        tab[(cue, k)] = (score(LIN, cov_mask(LIN, k, "severe"), cue), score(LIN, cov_mask(LIN, k, "mild"), cue))
        print(f"linear cue {cue} cover {k}: severe-first {tab[(cue,k)][0]:.2f}  mild-first {tab[(cue,k)][1]:.2f}")
gap_nocue = max(a - b for (c, k), (a, b) in tab.items() if c == 0.0)
gap_cue = max(a - b for (c, k), (a, b) in tab.items() if c == 0.7)
ordered = all(tab[(0.0, k)][0] >= tab[(0.0, k)][1] - 1e-9 for k in range(7))
# (2) cue knob at zero coverage: flat vs mild
knob = {}
for cue in (0.0, 0.3, 0.5, 0.7, 0.9):
    knob[cue] = (score(FLAT, [False] * 6, cue), score(MILD, [False] * 6, cue))
    print(f"zero coverage cue {cue}: flat {knob[cue][0]:.2f} mild {knob[cue][1]:.2f}")
need = min(c for c, (f, m) in knob.items() if f > m)
# fallback distance moved (BREAK for the cue claim): does flat still win at cue 0.7 when uncovered distance is 0.6?
fb = {d: (score(FLAT, [False] * 6, 0.7, d), score(MILD, [False] * 6, 0.7, d)) for d in (0.1, 0.3, 0.6, 0.9)}
print("flat vs mild at cue 0.7 by fallback distance:", {d: (round(f, 2), round(m, 2)) for d, (f, m) in fb.items()})
ok = ordered and gap_nocue > 0.3 and gap_cue < gap_nocue and need <= 0.7 and fb[0.3][0] > fb[0.3][1]
print(f"RESULT: {'PASS' if ok else 'FAIL'} severe-first never worse (no cue), max gap {gap_nocue:.2f} no cue vs {gap_cue:.2f} cue 0.7; min cue for flat > mild at zero coverage {need}; fallback d sweep flat>mild at {[d for d,(f,m) in fb.items() if f>m]}")
