"""Blind rebuild of seven E77 (fade to silence ends hopeless searches at small
rescue cost). Own fixture (exact, no rng): 14 nights. A call-following player
searches on a night iff the call is heard. Call heard prob by night n (1-based):
FLOOR: 1.0 for n<=3, then max(0.35, 1 - 0.2*(n-3)).
FADE:  1.0 for n<=3, then max(0.0, 1 - 0.2*(n-3)) (silent from night 8).
A search finds the member with prob q (depth). Cases: hopeless q=0 (member
dead/unreachable), shallow q=0.5, mid q=0.2, deep q=0.08. 'Late' = nights >= 8.
Outcome: rescue probability and expected late search nights.
PREDICTION (before running): hopeless: fade cuts late search nights >= 70%;
shallow: rescue cost <= 0.02; deep: cost >= 0.10. The rule's phrase "costs
about 0.13 even when they are easy to find" I expect to FAIL for an easy case.
Break scenario: a 'lasting non-call cue' (tracks found on search) that keeps
a fade-world player searching with prob 0.35 after silence should restore most
of the deep-case rescue while keeping the hopeless late nights well below the
floor - testing the rule's suggested pairing.
"""
import sys
print("python", sys.version.split()[0])
NIGHTS, LATE = 14, 8
def heard(n, mode, cue=0.0):
    if n <= 3: return 1.0
    v = 1 - 0.2*(n-3)
    if mode == "floor": return max(0.35, v)
    return max(cue, v)
def run(q, mode, cue=0.0):
    alive = 1.0; rescued = 0.0; late = 0.0
    for n in range(1, NIGHTS+1):
        h = heard(n, mode, cue)
        if n >= LATE: late += alive*h
        f = alive*h*q; rescued += f; alive -= f
    return rescued, late
cases = {"hopeless": 0.0, "shallow": 0.5, "mid": 0.2, "deep": 0.08}
R = {}
for k, q in cases.items():
    R[k] = (run(q, "floor"), run(q, "fade"), run(q, "fade", cue=0.35*0.6))
    (rf, lf), (rd, ld), (rc, lc) = R[k]
    print(f"{k:8s} q {q}: floor rescue {rf:.3f} late {lf:.3f} | fade rescue {rd:.3f} late {ld:.3f} cost {rf-rd:.3f} | fade+cue rescue {rc:.3f} late {lc:.3f}")
cut = 1 - R['hopeless'][1][1]/R['hopeless'][0][1]
sc = R['shallow'][0][0]-R['shallow'][1][0]; dc = R['deep'][0][0]-R['deep'][1][0]
print(f"hopeless late-night cut {cut:.3f}; shallow cost {sc:.4f}; deep cost {dc:.3f}")
easy_013 = sc >= 0.10
print("rule's 'about 0.13 even when easy':", easy_013)
p_ok = cut >= 0.70 and sc <= 0.02 and dc >= 0.10
print(f"RESULT: {'PASS' if p_ok else 'FAIL'} hopeless late nights {R['hopeless'][0][1]:.3f}->{R['hopeless'][1][1]:.3f} ({cut:.0%} cut); shallow cost {sc:.4f}; deep cost {dc:.3f}; easy-case 0.13 cost reproduced={easy_013}")
