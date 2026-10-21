"""Sandbox: recut a 20 s film-style ad by moving one of four beats to the front, then rank the four recuts
on IPM x D1 (rank-ipm-times-d1-needs-fidelity-retention-link; kernel
ideas:GAME-ADS/concept-then-variants-ranked-on-ipm-times-early-retention, decompose-the-winner-and-recut).
film lesson E7: insert/move a beat by remapping time at the dispatcher (0/40 cues off) versus hand edits
(3/40 off) because absolute-time tables are missed.
Model: 4 beats of length [4,6,5,5] s, 10 cues each at fixed offsets (40 cues). Remap recut places every cue
exactly. Hand-edit recut moves relative cues but leaves cue index % 13 == 0 (absolute table: cues 0,13,26,39)
at their OLD absolute time, so those cues are off whenever their beat moved. Each off cue multiplies IPM by
0.9 (assumed). Promise per opening beat [0.4,0.9,0.6,0.5], delivery 0.5, D1 as in the sibling sandboxes.
Prediction (written before first run): hand edits leave 1 to 4 cues off in variants whose moved beat holds
an absolute cue; the IPM x D1 winner stays the same under both edit methods (opening beat 3, promise 0.5)
while the IPM-alone winner changes from beat 1 (0.9) under hand edits. Remap leaves 0 cues off.
Assumption: cue errors are independent of promise. BREAK: raise the per-cue penalty to 0.7."""
LEN = [4, 6, 5, 5]; PROMISE = [0.4, 0.9, 0.6, 0.5]; DELIVERY = 0.5
OFFS = [i * 0.37 for i in range(10)]
def starts(order):
    t, s = 0.0, {}
    for b in order: s[b] = t; t += LEN[b]
    return s
ORIG = starts([0, 1, 2, 3])
def cues(order, hand):
    s = starts(order); out = []
    for b in range(4):
        for k in range(10):
            idx = b * 10 + k
            correct = s[b] + OFFS[k]
            stale = ORIG[b] + OFFS[k]
            out.append(stale if (hand and idx % 13 == 0) else correct)
    return out
def off_cues(order, hand):
    ref = cues(order, False); got = cues(order, hand)
    return sum(1 for a, b in zip(ref, got) if abs(a - b) > 1e-9)
def d1(p): return 0.4 * (1 - 1.5 * max(0.0, p - DELIVERY))
def run(pen):
    res = {}
    for first in range(4):
        order = [first] + [b for b in range(4) if b != first]
        for hand in (False, True):
            m = off_cues(order, hand)
            ipm = 10 * (0.5 + PROMISE[first]) * pen ** m
            res[(first, hand)] = (m, ipm, ipm * d1(PROMISE[first]))
    return res
def winner(res, hand, idx): return max(range(4), key=lambda f: (round(res[(f, hand)][idx], 12), -f))
ok = True
for pen in (0.9, 0.7):
    res = run(pen)
    print(f"penalty {pen}: off cues per variant (remap/hand):",
          [(res[(f, False)][0], res[(f, True)][0]) for f in range(4)])
    for name, idx in (("IPM", 1), ("IPM*D1", 2)):
        print(f"  {name} winner remap={winner(res, False, idx)} hand={winner(res, True, idx)}")
r9 = run(0.9)
same_d1 = winner(r9, False, 2) == winner(r9, True, 2)
remap_zero = all(r9[(f, False)][0] == 0 for f in range(4))
hand_some = sum(r9[(f, True)][0] for f in range(4))
diff_ipm = winner(r9, False, 1) != winner(r9, True, 1)
ok = same_d1 and remap_zero and hand_some > 0 and diff_ipm
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" remap 0 off cues; hand edits {hand_some} off cues over 4 variants; IPM*D1 winner same={same_d1}; IPM winner changed={diff_ipm}")
