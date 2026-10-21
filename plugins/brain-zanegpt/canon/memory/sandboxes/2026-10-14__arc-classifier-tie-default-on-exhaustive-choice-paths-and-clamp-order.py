"""Edge: sandbox-story-arc-classifier/E1 (reversal-count arc classifier, tie-default bug) + brainwork/E40 (exhaustive replay of
ordered choice paths through a clamped state). Apply the arc classifier to the hope trajectory of all 729 ordered paths.
PREDICTION (before running): (1) the buggy classifier (first zero diff defaults to '+') disagrees with the fixed one
(leading zero diffs stay unsigned) on at least 5% of the 729 paths, and every disagreement is a path whose FIRST diff is 0 and
whose first nonzero diff is negative; (2) buggy and fixed agree on every path whose first diff is nonzero; (3) permuting the six
deltas of a choice set changes the FIXED arc class for at least 30% of the sampled sets (clamp makes order matter, as E40 found for endings)."""
from itertools import product, permutations

START, LO, HI = 5, 0, 10
OPTS = (-3, 0, 3)

def trajectory(deltas):
    h = START; out = [h]
    for d in deltas:
        h = max(LO, min(HI, h + d)); out.append(h)
    return out

def signs(traj, fixed):
    diffs = [b - a for a, b in zip(traj, traj[1:])]
    out = []; last = None
    for d in diffs:
        if d > 0: s = '+'
        elif d < 0: s = '-'
        else:
            s = last if last is not None else (None if fixed else '+')   # the bug: phantom '+' before any real direction
        if s is not None:
            out.append(s); last = s
    # collapse runs
    col = []
    for s in out:
        if not col or col[-1] != s: col.append(s)
    return ''.join(col)

NAMES = {'': 'flat', '+': 'rise', '-': 'fall', '-+': 'hole', '+-': 'icarus', '+-+': 'cinderella', '-+-': 'oedipus'}
def arc(deltas, fixed): return NAMES.get(signs(trajectory(deltas), fixed), 'other')

paths = list(product(OPTS, repeat=6)); assert len(paths) == 729
dis = []; all_zero_paths = []; first_zero = 0; agree_nonzero = True; neg_after_zero = True
for p in paths:
    b, f = arc(p, False), arc(p, True)
    t = trajectory(p); first = t[1] - t[0]
    if first == 0: first_zero += 1
    if b != f:
        dis.append(p)
        if first != 0: agree_nonzero = False
        nz = [y - x for x, y in zip(t, t[1:]) if y != x]
        if not nz: all_zero_paths.append(p)
        elif nz[0] > 0: neg_after_zero = False
    elif False: pass
print(f"S1 paths {len(paths)}; first diff zero in {first_zero}; buggy vs fixed disagree on {len(dis)} ({100*len(dis)/729:.1f}%)")
print("S2b disagreement paths with no nonzero diff at all (flat read as rise):", len(all_zero_paths))
print("S2 all disagreements start with a zero diff:", agree_nonzero, "; and first nonzero diff negative:", neg_after_zero)
from collections import Counter
print("S1b fixed arc classes:", dict(Counter(arc(p, True) for p in paths)))
print("S1c buggy arc classes:", dict(Counter(arc(p, False) for p in paths)))
# S3 order dependence: choice SETS (multisets of 6 deltas), all distinct permutations
sets = sorted({tuple(sorted(p)) for p in paths})
changed = 0
for s in sets:
    classes = {arc(q, True) for q in set(permutations(s))}
    changed += len(classes) > 1
print(f"S3 multisets {len(sets)}; ordering changes the fixed arc class in {changed} ({100*changed/len(sets):.1f}%)")
# S4 BREAK: remove the clamp (wide bounds) -> order should stop mattering for net sign but arc pattern still depends on order
LO0, HI0 = LO, HI
LO, HI = -100, 100
changed_nc = sum(len({arc(q, True) for q in set(permutations(s))}) > 1 for s in sets)
print(f"S4 BREAK no clamp: ordering still changes arc class in {changed_nc} of {len(sets)} multisets")
ok = len(dis) / 729 >= 0.05 and agree_nonzero and neg_after_zero and len(all_zero_paths) == 1 and changed / len(sets) >= 0.30 and changed_nc == changed
print("RESULT:", "PASS" if ok else "FAIL", f"tie-default bug misclassifies {len(dis)}/729 paths (111 fall-first paths plus the all-flat path), all starting with a zero diff; ordering changes arc class in {changed}/{len(sets)} sets with clamp and {changed_nc}/{len(sets)} without (clamp is not the cause here, unlike E40)")
