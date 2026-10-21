"""Rule card (write-the-rules-before-the-gags) + benign-violation + matched-distance escalation,
with a NOISY distance dial. Assumption: the dial is read exactly. Question: when the framing
distance is mis-set by Gaussian error sigma, does the card keep precision (no harm beats shown)
while only funny COUNT falls, whereas without the card precision itself falls?
Beat is truly funny iff card_ok(gag) AND severity <= true_distance. A beat is SHOWN when the writer
believes severity <= believed_distance (true + noise) and (card present -> card_ok).
precision = funny/shown. Prediction (before run, revised after v1 showed a fixed schedule cannot overshoot): writer sets severity from the believed dial.
Full card keeps zero harm beats at every sigma but precision falls below 1.0 at sigma 2 and 3 (overshoot); no card precision at
sigma 3 is below 0.75; the breaker (card missing the harm rule) drops below 1.0 at sigma 0."""
import random
def pool(seed, n=360):
    r = random.Random(seed)
    return [{"harm": r.choice(["humiliate", "injure"]), "wins": r.random() < 0.3} for _ in range(n)]
def full(g): return g["harm"] == "humiliate" and not g["wins"]
def partial(g): return not g["wins"]
def run(card, sigma, seed=11, bias=0.0):
    p = pool(seed); r = random.Random(seed + 1000)
    sched = [1, 2, 3, 4, 5, 5]
    shown = funny = 0
    for i, sev in enumerate(sched):
        true_d = 1 + i                    # matched dial
        for g in p[i*60:(i+1)*60]:
            if card is not None and not card(g): continue
            believed = true_d + bias + r.gauss(0, sigma)  # bias>0: dial over-reads the real distance
            sev = max(1, min(5, round(believed)))  # writer escalates to what the dial says it can carry
            shown += 1
            if full(g) and sev <= true_d: funny += 1
    return funny, shown, (funny / shown if shown else 0.0)
R = {}
for s in (0, 1, 2, 3):
    R[("full", s)] = run(full, s); R[("none", s)] = run(None, s)
R[("partial", 0)] = run(partial, 0)
R[("fullbias", 0)] = run(full, 0, bias=2.0)  # breaker: dial over-reads by 2
for k, (f, sh, pr) in R.items(): print(f"{k[0]:8s} sigma={k[1]} funny={f:3d} shown={sh:3d} precision={pr:.3f}")
card_prec = R[("full", 0)][2] == 1.0 and R[("full", 3)][2] < 1.0
fall = R[("full", 3)][2] < R[("full", 1)][2] <= 1.0
nocard = R[("none", 3)][2] < 0.75
breaker = R[("partial", 0)][2] < 1.0
biasbreak = R[("fullbias", 0)][2] < 1.0
ok = card_prec and fall and nocard and breaker and biasbreak
print(f"RESULT: {'PASS' if ok else 'FAIL'} card_prec_s0_1_s3_lt1={card_prec} prec_monotone={fall} funny_s3/s0={R[('full',3)][0]}/{R[('full',0)][0]} "
      f"nocard_prec_s3={R[('none',3)][2]:.3f} partial_prec_s0={R[('partial',0)][2]:.3f} biased_dial_prec={R[('fullbias',0)][2]:.3f}")
