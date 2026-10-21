"""Prediction (before run): 8 rooms, a 4-event causal chain, player visits 3 rooms (all 56 subsets, exhaustive, no RNG); story 'reads' if >=3 of 4 events are inferred.
P1 one cue per event reads in < 25% of subsets; three cues per event spread over distinct rooms reads in >= 70%.
P2 BREAK: three cues per event all placed in ONE room per event (clustered) reads in < 40%, i.e. redundancy needs independent locations (the kernel's 'independent cues').
P3 index cues (each cue implies its event and the previous event) with ONE cue per event read in more subsets than event cues with one cue per event by >= 15 points, but less than three spread event cues.
P4 a sightline (a visited room also shows its two neighbours) lifts the one-cue-per-event event-cue case by >= 20 points, and lifts the clustered case by less than it lifts the spread case's... (clustered lift measured, reported).
Stdlib, deterministic."""
from itertools import combinations
R, E, V = 8, 4, 3
def place(r, spread, offset=0):
    cues = []  # (room, event)
    for j in range(E):
        for c in range(r):
            room = (2 * j + (3 * c if spread else 0) + offset) % R
            cues.append((room, j))
    return cues
def seen(visit, sight):
    s = set()
    for v in visit:
        s.add(v)
        if sight: s.add((v - 1) % R); s.add((v + 1) % R)
    return s
def reads(cues, visit, sight, imply, need=3):
    s = seen(visit, sight); inferred = set()
    for room, j in cues:
        if room in s:
            for d in range(imply + 1):
                if j - d >= 0: inferred.add(j - d)
    return len(inferred) >= need
def rate(r, spread, sight=False, imply=0):
    cues = place(r, spread)
    subs = list(combinations(range(R), V))
    return sum(reads(cues, s, sight, imply) for s in subs) / len(subs)
tab = {}
for name, (r, sp, sg, im) in {
    "event1": (1, True, False, 0), "event3_spread": (3, True, False, 0), "event3_clustered": (3, False, False, 0),
    "index1": (1, True, False, 1), "index1_depth2": (1, True, False, 2),
    "event1_sight": (1, True, True, 0), "event3_spread_sight": (3, True, True, 0), "event3_clustered_sight": (3, False, True, 0),
    "index1_sight": (1, True, True, 1)}.items():
    tab[name] = rate(r, sp, sg, im); print(f"{name:24s} reads {tab[name]:.3f}")
p1 = tab["event1"] < .25 and tab["event3_spread"] >= .70
p2 = tab["event3_clustered"] < .40
p3 = tab["index1"] - tab["event1"] >= .15 and tab["index1"] < tab["event3_spread"]
lift_s = tab["event3_spread_sight"] - tab["event3_spread"]; lift_c = tab["event3_clustered_sight"] - tab["event3_clustered"]
p4 = tab["event1_sight"] - tab["event1"] >= .20
# P5 (added before run 2, after seeing that the sightline lift depends on the room layout): with the four events packed into adjacent rooms 0..3, one-cue-per-event sightline lift is smaller than in the even-spaced layout.
def rate_packed(sight):
    cues = [(j, j) for j in range(E)]
    subs = list(combinations(range(R), V))
    return sum(reads(cues, s_, sight, 0) for s_ in subs) / len(subs)
pk0, pk1 = rate_packed(False), rate_packed(True)
print(f"packed rooms 0-3: no sight {pk0:.3f} sight {pk1:.3f} lift {pk1-pk0:.3f}")
p5 = (pk1 - pk0) < (tab["event1_sight"] - tab["event1"])
print("P1", p1, "P2", p2, "P3", p3, "P4", p4, "P5", p5, f"sight lift spread {lift_s:.3f} clustered {lift_c:.3f}")
print("RESULT:", "PASS" if all([p1, p2, p3, p4, p5]) else "FAIL", f"{sum([p1,p2,p3,p4,p5])}/5 held; event1 {tab['event1']:.3f}, event3 spread {tab['event3_spread']:.3f}, clustered {tab['event3_clustered']:.3f}, index1 {tab['index1']:.3f}, index depth2 {tab['index1_depth2']:.3f}, event1+sight {tab['event1_sight']:.3f}, index1+sight {tab['index1_sight']:.3f}; packed layout sight lift {pk1-pk0:.3f}")
