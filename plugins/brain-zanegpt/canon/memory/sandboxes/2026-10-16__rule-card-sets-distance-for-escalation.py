# Sandbox: a gag rule card that fixes the framing distance per beat, vs fixed distance.
# Beat = (severity s 1..5, distance d 1..5). Violation needs s>=2; benign iff s<=d.
# Funny points of a beat = s if (s>=2 and s<=d) else 0.  Unfunny-harm beat = s>d.
def score(beats):
    funny = sum(s for s, d in beats if s >= 2 and s <= d)
    harm = sum(1 for s, d in beats if s > d)
    return funny, harm
N = 5
sched = {"flat-mild": [2]*N, "go-big": [2, 3, 4, 5, 5], "go-big-late": [1, 2, 3, 4, 5]}
res = {}
for name, sev in sched.items():
    fixed = score([(s, 2) for s in sev])                  # one grounded distance d=2 throughout
    card = score([(s, min(5, s)) for s in sev])            # card gives each beat distance = what the world rule allows
    res[name] = (fixed, card)
    print(f"{name:12s} fixed-d2 funny/harm {fixed}  card-matched funny/harm {card}")
# break: the card's distance resets after a severe beat (callback beat in a plain room, d=2)
brk = [(2,2),(5,5),(4,2),(5,2),(3,3)]
bf, bh = score(brk)
print("break (distance resets in callback beats): funny/harm", (bf, bh))
ok = (res["go-big"][0][0] < res["flat-mild"][0][0]          # go-big loses at fixed distance (mild wins)
      and res["go-big"][1][0] > res["flat-mild"][1][0]      # go-big wins when matched
      and all(r[1][1] == 0 for r in res.values())           # card keeps harm at 0
      and bh == 2)
print("RESULT: %s fixed d=2: go-big %d vs mild %d funny; card-matched: go-big %d, harm 0 in 3/3 schedules; callback break leaves %d harm beats" %
      ("PASS" if ok else "FAIL", res["go-big"][0][0], res["flat-mild"][0][0], res["go-big"][1][0], bh))
