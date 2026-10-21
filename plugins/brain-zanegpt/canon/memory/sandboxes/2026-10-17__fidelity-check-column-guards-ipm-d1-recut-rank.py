# Sandbox: a fidelity check column (derived-from-game link, not "any new noun")
# in front of an IPM x D1 recut ranking. Composes game-of-scene-hxe-check-column/E1,
# rank-ipm-times-d1.../E1 and ideas GAME-ADS decompose-the-winner-and-recut.
import random
from collections import Counter
# (name, ipm_p, d1, new_noun, derived_from_game)
RECUTS = [("r1",.040,.30,0,1),("r2",.042,.31,0,1),("r3",.039,.34,1,1),  # r3: new noun but derived from the game
          ("r4",.041,.32,0,1),("b1",.060,.12,1,0),("b2",.055,.14,1,0),  # b*: clickbait, off-game
          ("r5",.038,.35,0,1),("r6",.043,.29,0,1)]
def true_val(r): return r[1]*r[2]
def sample(r, n, rng):
    inst = sum(rng.random() < r[1] for _ in range(n))
    ret = sum(rng.random() < r[2] for _ in range(inst))
    return (inst/n) * ((ret/inst) if inst else 0)
def run(world, check, n, seeds=range(40)):
    c = Counter(); regret = 0.0
    pool = [r for r in world if check(r)]
    best = max(true_val(r) for r in world if r[4])
    for s in seeds:
        rng = random.Random(s)
        pick = max(pool, key=lambda r: sample(r, n, rng))
        c[pick[0]] += 1; regret += best - (true_val(pick) if pick[4] else true_val(pick))
    off = sum(v for k,v in c.items() if k.startswith("b"))
    return off, c, regret/len(seeds)
none  = lambda r: True
naive = lambda r: not r[3]          # any new noun fails
link  = lambda r: bool(r[4])        # derived-from-game link
N = 300
o_none,c_none,_ = run(RECUTS, none, N)
o_naive,c_naive,_ = run(RECUTS, naive, N)
o_link,c_link,_ = run(RECUTS, link, N)
flat = [r for r in RECUTS if r[4]]                 # no clickbait present
o_flat_none,c_flat_none,_ = run(flat, none, N)
o_flat_link,c_flat_link,_ = run(flat, link, N)
def run_ipm(world, check, n, seeds=range(40)):
    pool=[r for r in world if check(r)]; off=0
    for s in seeds:
        rng=random.Random(s)
        pick=max(pool,key=lambda r: sum(rng.random()<r[1] for _ in range(n))/n)
        off+=pick[0].startswith("b")
    return off
i_none=run_ipm(RECUTS,none,N); i_link=run_ipm(RECUTS,link,N)
r3_naive = c_naive.get("r3",0); r3_link = c_link.get("r3",0)
print("IPM-only off-game picks /40  none:",i_none,"link:",i_link)
print("IPM x D1 off-game picks /40  none:",o_none,"naive:",o_naive,"link:",o_link)
print("flat world picks identical sets:", dict(c_flat_none)==dict(c_flat_link))
print("r3 (legit new noun) picked naive:",r3_naive,"link:",r3_link)
ok = (i_none >= 20 and i_link == 0 and o_none <= 5 and dict(c_flat_none)==dict(c_flat_link)
      and r3_naive == 0 and r3_link > 0)
print("RESULT:", "PASS" if ok else "FAIL",
      f"check column needed under IPM alone (off-game {i_none}/40 -> {i_link}) but nearly idle under IPM x D1 ({o_none}/40 -> {o_link}); naive check loses legit r3 ({r3_naive} vs {r3_link}/40)")
