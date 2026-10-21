"""Benign-violation toy. 6 beats. Violation v_t. Cover = min(1, distance + cue + card) where cue and card
are independent additive sources of benign cover. Funny_t = v_t * 1 if v_t <= cover else
cover - 3*(v_t - cover)  (overshoot penalised).  v=0 gives 0 (no violation, no joke).
Schedules: mild (0.3 flat), gobig (0.2 -> 1.0 linear).  Score = sum of funny_t."""
B = 6
def sched(k): return [0.3]*B if k == "mild" else [0.2 + 0.8*i/(B-1) for i in range(B)]
def score(k, cover):
    cover = min(1.0, cover); s = 0.0
    for v in sched(k):
        s += v if v <= cover else cover - 3*(v - cover)
    return s
D = 0.3
def row(cue, card):
    c = D + cue + card
    return score("mild", c), score("gobig", c)
base_m, base_g = row(0, 0)
cue_m, cue_g = row(0.3, 0)
card_m, card_g = row(0, 0.3)
both_m, both_g = row(0.3, 0.3)
for n, (m, g) in {"none": (base_m, base_g), "cue .3": (cue_m, cue_g), "card .3": (card_m, card_g), "cue+card .6": (both_m, both_g)}.items():
    print(f"{n:12s} mild {m:.2f} gobig {g:.2f} winner {'gobig' if g > m else 'mild'}")
gain_first = cue_g - base_g
gain_second = both_g - cue_g
print(f"gobig gain from first source {gain_first:.2f}, from second source {gain_second:.2f} ({gain_second/gain_first*100:.0f}% of first)")
# BREAK: cover already 0.7 by distance alone (far framing): extra sources should add ~nothing past saturation at 1
far = [score("gobig", 0.7 + x) for x in (0, 0.3, 0.6)]
print(f"BREAK far framing distance .7: gobig with +0, +.3, +.6 cover = {far[0]:.2f}, {far[1]:.2f}, {far[2]:.2f}")
interchange = abs(cue_g - card_g) < 1e-9
ok = interchange and gain_second < 0.5*gain_first and abs(far[2] - far[1]) < 1e-9 and (both_g > both_m) and (base_g < base_m)
print(f"RESULT: {'PASS' if ok else 'FAIL'} cue and card interchangeable={interchange}; second source adds {gain_second/gain_first*100:.0f}% of the first; go-big flips from losing to winning once covered; far-framing extra cover adds {far[2]-far[1]:.2f}")
