# Composes escalation-needs-matching-distance (go big needs distance matched to severity), safe-cue-escalation
# (a safe cue licenses going big at grounded distance) and the kernel write-the-rules-before-the-gags (a rule card of
# who can hurt whom sets each beat's distance). Added: the card is a hand-kept table that covers only a fraction p
# of the beats' (actor, target) pairs; a beat with no card entry falls back to fixed grounded distance 0.3.
# Model as in the escalation lessons (habituation exp(-0.2X), gate exp(-((d-I/C)/0.25)^2), additive cue
# g'=g+c(1-g), six beats, ceiling 10). Expected score is exact over all 2^6 covered/uncovered patterns (no RNG),
# each beat covered independently with probability p. Compare flat-at-ceiling, rule-of-three, mild schedules,
# with no cue and with a permanent cue of 0.7 on uncovered beats.
# PREDICTION (before run): with no cue, flat-at-ceiling beats the mild schedule only at coverage p >= 0.8; with the
# cue, flat wins at every p from 0 to 1 and the margin over mild at p=0.5 is above 1.0. The break case (a wrong guess): a mild
# schedule loses nothing to missing entries (its severities sit near 0.3).
import itertools, math
C = 10.0
SCHED = {"flat": [10]*6, "three": [2,6,10,10,10,10], "mild": [3,3.5,4,4,4.5,5]}
def score(seq, covered, cue):
    X = tot = 0.0
    for I, cov in zip(seq, covered):
        d = I / C if cov else 0.3
        g = math.exp(-((d - I/C)/0.25)**2)
        if not cov: g = g + cue * (1 - g)
        tot += math.exp(-0.2*X) * (I/C) * g; X += 1/(1+I/5)
    return tot
def expected(seq, p, cue):
    e = 0.0
    for cov in itertools.product((0, 1), repeat=len(seq)):
        w = 1.0
        for c in cov: w *= p if c else 1 - p
        e += w * score(seq, cov, cue)
    return e
res = {}
for cue in (0.0, 0.7):
    for p in (0.0, 0.25, 0.5, 0.75, 0.9, 1.0):
        row = {n: expected(s, p, cue) for n, s in SCHED.items()}
        res[(cue, p)] = row
        print(f"cue {cue} coverage {p}: " + " ".join(f"{n} {v:.2f}" for n, v in row.items()),
              "-> best", max(row, key=row.get))
flat_wins_nocue = [p for p in (0.0, 0.25, 0.5, 0.75, 0.9, 1.0) if max(res[(0.0, p)], key=res[(0.0, p)].get) == "flat"]
flat_wins_cue = [p for p in (0.0, 0.25, 0.5, 0.75, 0.9, 1.0) if max(res[(0.7, p)], key=res[(0.7, p)].get) == "flat"]
mild_loss = res[(0.0, 1.0)]["mild"] - res[(0.0, 0.0)]["mild"]
margin_half = res[(0.7, 0.5)]["flat"] - res[(0.7, 0.5)]["mild"]
ok = (min(flat_wins_nocue, default=9) >= 0.75 and len(flat_wins_cue) == 6 and margin_half > 1.0)
print(f"RESULT: {'PASS' if ok else 'FAIL'} flat wins without cue at coverage {flat_wins_nocue}, with cue at {flat_wins_cue}; margin over mild at p 0.5 with cue {margin_half:.2f}; mild gains {mild_loss:.2f} from a full card (flat gains 5.11)")
