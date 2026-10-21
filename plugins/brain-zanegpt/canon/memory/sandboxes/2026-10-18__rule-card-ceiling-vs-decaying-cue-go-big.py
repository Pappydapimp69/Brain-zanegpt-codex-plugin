"""Toy: 6-beat sketch. Severity s_t in [0,1]. Safe-cue strength c_t = decay**t (decay=1 -> no habituation).
Licence at beat t = distance + 0.5*c_t (how much harm the framing can bear).
Funny_t = s_t if s_t <= licence else (licence - (s_t - licence)*3)  (overshoot hurts, can go negative).
Rule card: clamps every beat's severity at ceiling = distance (fixed at write time, so ignores decay).
Schedules: mild (0.3 flat), flat (0.7 flat), gobig (0.2 -> 1.0 linear). Score = mean funny."""
BEATS = 6
def sched(kind):
    if kind == "mild": return [0.3]*BEATS
    if kind == "flat": return [0.7]*BEATS
    return [0.2 + 0.8*i/(BEATS-1) for i in range(BEATS)]
def score(kind, distance, decay, card, ceiling_slack=0.0):
    tot = 0.0
    for t, s in enumerate(sched(kind)):
        if card: s = min(s, distance + ceiling_slack)
        lic = distance + 0.5*(decay**t)
        tot += s if s <= lic else lic - (s - lic)*3
    return tot/BEATS
def best(distance, decay, card, slack=0.0):
    r = {k: score(k, distance, decay, card, slack) for k in ("mild","flat","gobig")}
    return max(r, key=r.get), r
rows = []
for distance in (0.2, 0.5):
    for decay in (1.0, 0.8, 0.5):
        b0, r0 = best(distance, decay, False)
        b1, r1 = best(distance, decay, True)
        print(f"d={distance} decay={decay}: no card -> {b0} gobig={r0['gobig']:.2f}; card -> {b1} gobig={r1['gobig']:.2f}")
        rows.append((distance, decay, b0, b1, r0, r1))
# prediction: at distance .5 decay .8 gobig loses w/o card; with card gobig becomes >= mild.
d,dec,b0,b1,r0,r1 = [r for r in rows if r[0]==0.5 and r[1]==0.8][0]
# BREAK: low distance 0.2, strong decay .5: card ceiling (fixed at distance) vs mild
bd = [r for r in rows if r[0]==0.2 and r[1]==0.5][0]
card_helps = r1['gobig'] > r0['gobig']
go_wins = b1 == "gobig"
card_fails_break = bd[5]['gobig'] < bd[5]['mild']
print(f"card helps gobig at d=.5 decay=.8: {card_helps} (gobig {r0['gobig']:.2f} -> {r1['gobig']:.2f}); gobig wins with card: {go_wins}; at break d=.2 decay=.5 gobig<mild under card: {card_fails_break}")
ok = card_helps and go_wins
print(f"RESULT: {'PASS' if ok else 'FAIL'} card lifts gobig {r0['gobig']:.2f}->{r1['gobig']:.2f} at d=.5 decay=.8 (winner {b0}->{b1}); break d=.2 decay=.5 card gobig {bd[5]['gobig']:.2f} vs mild {bd[5]['mild']:.2f}")
