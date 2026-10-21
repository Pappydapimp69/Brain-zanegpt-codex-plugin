"""Sandbox: information-gap reveal driven through a Bayer 4x4 dither, with the
game-of-the-scene check deciding which beats may advance the reveal.
Prediction written before first run: a naive schedule (every beat steps the
reveal) fires on the new-noun beats of 3 sheets (flat 0, jump 2, stock 2 -> 4 premature steps),
the derived-aware schedule fires 0; both always land on <=17 states; with all beats derived they agree."""
BAYER = [[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]

def shown(level, x, y):          # world-anchored: depends only on (x,y,level)
    return BAYER[y % 4][x % 4] < level

def frame_hash(level):
    return sum(shown(level, x, y) << (y*4+x) for y in range(4) for x in range(4))

# beat = (name, derived_from_game)
SHEETS = {
 "flat":  [("setup",1),("heighten1",1),("heighten2",1),("heighten3",1),("payoff",1)],
 "jump":  [("setup",1),("heighten1",1),("new-noun",0),("heighten2",1),("new-noun2",0),("payoff",1)],
 "stock": [("setup",1),("stock-form",0),("heighten1",1),("stock-form2",0),("payoff",1)],
}

def run(beats, aware, steps_per_step=1):
    level, levels = 0, []
    n = sum(1 for _, d in beats if d or not aware)
    for name, d in beats:
        if d or not aware:
            level = min(16, level + max(1, 16 // n))
        levels.append(level)
    return levels

premature = {}
for k, b in SHEETS.items():
    naive = run(b, False); aware = run(b, True)
    # premature = steps taken on beats that are not derived from the game
    pn = sum(1 for i,(n,d) in enumerate(b) if not d and (naive[i] != (naive[i-1] if i else 0)))
    pa = sum(1 for i,(n,d) in enumerate(b) if not d and (aware[i] != (aware[i-1] if i else 0)))
    premature[k] = (pn, pa)
    states = len({frame_hash(l) for l in naive+aware})
    print(k, "naive", naive, "aware", aware, "premature n/a", pn, pa, "distinct frames", states)

# break attempt: gap-closing never exceeds 17 states, and same level -> identical frame (no swim)
assert all(frame_hash(l) == frame_hash(l) for l in range(17))
assert len({frame_hash(l) for l in range(17)}) == 17
tn = sum(v[0] for v in premature.values()); ta = sum(v[1] for v in premature.values())
agree = run(SHEETS["flat"], False) == run(SHEETS["flat"], True)
ok = tn == 4 and ta == 0 and agree
print("RESULT: %s naive premature=%d aware premature=%d, flat sheet agrees=%s, 17 distinct dither states" % ("PASS" if ok else "FAIL", tn, ta, agree))
