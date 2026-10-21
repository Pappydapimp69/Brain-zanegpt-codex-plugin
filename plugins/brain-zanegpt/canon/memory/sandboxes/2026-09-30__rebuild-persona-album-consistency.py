# Rebuild of: at 90% per-song persona consistency a 10-song project is fully consistent 34.9% (12 songs 28.2%), about one
# off-voice song per 10, ~11.1 generations for 10 good; check every song against the FIRST, not the last.
# Own method: exact enumeration over all 2^n good/bad outcome vectors with Fraction weights (not the closed form),
# plus a deterministic drift model for the first-vs-last check. The 90% rate itself is a community report, NOT tested.
from fractions import Fraction as F
from itertools import product
def p_all(n, p):
    tot = F(0)
    for v in product((0, 1), repeat=n):
        if all(v): tot += p ** n
    return tot
def exp_bad(n, p):
    return sum((n - sum(v)) * (p ** sum(v)) * ((1 - p) ** (n - sum(v))) for v in product((0, 1), repeat=n))
p = F(9, 10)
a10, a12, eb, gens = p_all(10, p), p_all(12, p), exp_bad(10, p), F(10) / p
print(f"p=0.9: all-good 10 songs {float(a10):.4f}, 12 songs {float(a12):.4f}, expected off-voice per 10 {float(eb):.2f}, generations for 10 good {float(gens):.2f}")
p8 = F(4, 5); print(f"other rate p=0.8, 8 songs: all-good {float(p_all(8, p8)):.4f}, generations for 8 good {float(8 / p8):.2f}")
# Drift model: each accepted take drifts +0.4 units in timbre from the reference it was checked against; tolerance 1.0.
def drift(n, ref_mode, step=0.4, tol=1.0):
    first = 0.0; last = 0.0; accepted = [first]
    for i in range(1, n):
        ref = first if ref_mode == "first" else last
        cand = last + step                       # each new take lands near the previous song's voice
        if abs(cand - ref) <= tol: accepted.append(cand); last = cand
        else: cand = first + step; accepted.append(cand); last = cand   # rejected -> regenerate near the first
    return max(abs(x - first) for x in accepted)
df, dl = drift(10, "first"), drift(10, "last")
print(f"max distance from song 1 over 10 songs: check vs first {df:.1f}, check vs last {dl:.1f}")
ok = round(float(a10), 3) == 0.349 and round(float(a12), 3) == 0.282 and eb == 1 and round(float(gens), 1) == 11.1 and df <= 1.0 < dl
print("RESULT: %s exact enumeration 10 songs %.1f%%, 12 songs %.1f%%, E[off-voice]=%s, 10/p=%.2f; drift vs first stays %.1f, vs last reaches %.1f" % ("PASS" if ok else "FAIL", 100 * float(a10), 100 * float(a12), eb, float(gens), df, dl))
