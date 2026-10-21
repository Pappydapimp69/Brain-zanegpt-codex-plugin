# Run 1 prediction (missed): the card flips the best distance to close. Run 1 observed: FAIL, best distance 1.0 for all three;
# the capped schedule is flat (1.05) from d=0.2 to 1.0, so the card FLATTENS the distance dependence instead of flipping it.
# Run 2 prediction: count distances (of 11) within 95% of each schedule's max: go-big <=2, card >=8, card with split 0.15 >=8;
# and the card loses only at d=0 (closest), where severity-0.3 beats nothing: card at d=0 is below 95% of its max.
# Prediction (before run): cover b(d,s): mild harm (s<=0.3) is covered by closeness, b=0.8-0.5d; severe harm (s>0.3)
# is covered by distance, b=0.2+0.7d (d: 0 close .. 1 far). Laugh = s if s<=b else max(0, s-3*(s-b)).
# Six-beat go-big schedule s=i/6 (to 1.0) vs a rule-card schedule whose severity is capped at 0.3 (humiliated not
# harmed, the same shape rescaled: s=0.05*i). Over d in 0.0..1.0 step 0.1: the go-big best distance is d>=0.8 (far),
# the capped best distance is d<=0.2 (close), so the card flips the best distance. Hidden assumption: the cover
# functions cross at s=0.3. BREAK: shift the mild/severe split to s=0.15, then the capped schedule (up to 0.30)
# straddles the split and its best distance is no longer close (d>=0.5).
def laugh(s, b): return s if s <= b else max(0.0, s - 3 * (s - b))
def cover(d, s, split): return 0.8 - 0.5 * d if s <= split else 0.2 + 0.7 * d
def total(sched, d, split): return sum(laugh(s, cover(d, s, split)) for s in sched)
big = [i / 6 for i in range(1, 7)]
card = [0.05 * i for i in range(1, 7)]
ds = [i / 10 for i in range(11)]
def best(sched, split):
    return max(ds, key=lambda d: (round(total(sched, d, split), 9), d))
def window(sched, split):
    m = max(total(sched, d, split) for d in ds)
    return sum(1 for d in ds if total(sched, d, split) >= 0.95 * m)
w1, w2, w3 = window(big, 0.3), window(card, 0.3), window(card, 0.15)
for d in ds: print("d %.1f big %.2f card %.2f cardsplit.15 %.2f" % (d, total(big, d, 0.3), total(card, d, 0.3), total(card, d, 0.15)))
ok = w1 <= 2 and w2 >= 8 and w3 >= 8 and total(card, 0.0, 0.3) < 0.95 * max(total(card, d, 0.3) for d in ds)
print(f"RESULT: {'PASS' if ok else 'FAIL'} distances within 95% of best (of 11): go-big {w1}, card {w2}, card split 0.15 {w3}; card at d=0 {total(card, 0.0, 0.3):.2f} vs max 1.05")
