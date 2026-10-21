"""Sandbox: a two-observation Bayes update written as a product of two single-observation
'priors' (prior*likelihood)**2 applies the prior twice. Measure how far that bug moves the
posterior across priors and likelihood ratios, and whether it can flip a design conclusion.
Correct: P(H | o1,o2) = p L1^2 / (p L1^2 + (1-p) L0^2) for two iid observations.
Bug:     (p L1)^2 / ((p L1)^2 + ((1-p) L0)^2)  (prior squared).
Exact, no RNG. Cases include seven E23's constants (p 0.15, call 0.9, false 0.15,
consistency 0.749 vs 0.293).
PREDICTIONS (written before running):
 P1 the bug always pulls the posterior toward the more likely prior side (down when p < 0.5)
 P2 at seven E23's constants the bug moves the consistent-pair posterior by more than 0.15
 P3 at p = 0.5 the bug changes nothing (squared prior ratio is 1)
 P4 there is a case where the bug flips a 0.85 'proof' threshold from crossed to not crossed
"""
def correct(p, l1, l0, extra=(1.0, 1.0)):
    a = p*l1*l1*extra[0]; b = (1-p)*l0*l0*extra[1]; return a/(a+b)
def buggy(p, l1, l0, extra=(1.0, 1.0)):
    a = (p*l1)**2*extra[0]; b = ((1-p)*l0)**2*extra[1]; return a/(a+b)
rows = []
for p in (0.05, 0.15, 0.3, 0.5, 0.7):
    for l1, l0 in ((0.9, 0.15), (0.9, 0.3), (0.6, 0.1)):
        c, b = correct(p, l1, l0), buggy(p, l1, l0)
        rows.append((p, l1, l0, c, b))
        print(f"p {p:.2f} L1 {l1} L0 {l0}: correct {c:.3f} buggy {b:.3f} shift {b-c:+.3f}")
e23c = correct(0.15, 0.9, 0.15, (0.749, 0.293)); e23b = buggy(0.15, 0.9, 0.15, (0.749, 0.293))
print(f"seven E23 consistent pair: correct {e23c:.3f} buggy {e23b:.3f}")
p1 = all((b < c) if p < 0.5 else (b > c) if p > 0.5 else True for p, _, _, c, b in rows)
p2 = abs(e23c - e23b) > 0.15
p3 = all(abs(c-b) < 1e-12 for p, _, _, c, b in rows if p == 0.5)
p4 = any(c >= 0.85 > b for _, _, _, c, b in rows) or (e23c >= 0.85 > e23b)
held = p1 + p2 + p3 + p4
print(f"RESULT: {'PASS' if held == 4 else 'FAIL'} {held}/4 predictions held; E23 pair correct {e23c:.3f} "
      f"buggy {e23b:.3f}; checks {[p1, p2, p3, p4]}")
