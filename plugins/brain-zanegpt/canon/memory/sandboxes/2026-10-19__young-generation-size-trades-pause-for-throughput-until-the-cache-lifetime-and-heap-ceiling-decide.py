"""Sandbox: young-generation size sweep with a cache whose entries live T ticks then are invalidated.
Toy copying generational GC, deterministic, no RNG, no wall time.
Each tick: 8 short-lived objects (garbage at once) + 2 cache entries that die (invalidated) at tick+T.
Minor GC when young holds Y objects: pause = 20 + survivors copied (cache entries still alive); they go to old.
Full GC when old + Y would exceed heap H=1500: pause = 40 + live old objects; OOM if live + Y still > H.
Mutator time = 1 per allocated object. Throughput = mutator / (mutator + gc pauses).
Prediction, iteration 1 (written before first run; PARTLY REFUTED, see the iteration 2 note below):
  T=500 (long-lived cache): throughput rises with Y (50<100<200<400) AND max minor pause rises with Y;
     Y=400 breaches the heap ceiling (OOM ticks > 0) while Y=50 does not.
  T=5 (short-lived, invalidated before the next GC): max minor pause stays at the 20 overhead for every Y, so the pause-for-throughput trade vanishes (pause flat, throughput still rises).
  BREAK: T=100 with Y=200 sits between: promotion nonzero but below the T=500 level.
"""
def run(Y, T, H=1500, ticks=20000):
    young = []; old = []; gc = 0; mut = 0; maxpause = 0; oom = 0; fulls = 0; minors = 0; promoted = 0
    for t in range(ticks):
        mut += 10
        young += [None] * 8 + [t + T] * 2
        if len(young) >= Y:
            alive = [d for d in young if d is not None and d > t]
            if len(old) + Y > H:
                old = [d for d in old if d > t]; p = 40 + len(old); gc += p; fulls += 1
                if len(old) + Y > H: oom += 1
            p = 20 + len(alive); gc += p; maxpause = max(maxpause, p); minors += 1
            old += alive; promoted += len(alive); young = []
    return dict(thr=round(mut / (mut + gc), 4), maxminor=maxpause, oom=oom, fulls=fulls, minors=minors, promoted=promoted)

res = {}
for T in (500, 100, 5):
    for Y in (50, 100, 200, 400):
        res[(T, Y)] = run(Y, T); print("T", T, "Y", Y, res[(T, Y)])
# Iteration 1 (above) predicted throughput rising with Y at T=500, an OOM at Y=400 and ordered promotion across T; observed throughput
# [0.4945, 0.5409, 0.5435, 0.4932] (peak at Y=200, then FALLING), no OOM at Y=400, and equal promotion at T=100 and T=500.
# Iteration 2 prediction: T=500 throughput peaks at an interior Y (200) because a bigger young gen leaves less old room and triggers more full GCs;
# OOM only appears once Y + live (1000) > H, i.e. Y=600 (REFUTED, see iteration 3); promotion at T=100 equals T=500 (lifetime exceeds the young window Y/10) and is lower only at T=5.
for y in (600, 700): res[(500, y)] = run(y, 500); print("T 500 Y", y, res[(500, y)])
thr500 = {y: res[(500, y)]["thr"] for y in (50, 100, 200, 400)}
c1 = max(thr500, key=thr500.get) == 200 and thr500[400] < thr500[200]
c2 = all(res[(500, a)]["maxminor"] < res[(500, b)]["maxminor"] for a, b in [(50, 100), (100, 200), (200, 400)])
# Iteration 3 prediction: iteration 2 saw no OOM at Y=600 (live old is about 2*(500 - Y/10) = 880, so 880 + 600 < 1500); OOM starts once live + Y > 1500, so Y=700 breaches.
c3 = res[(500, 400)]["oom"] == 0 and res[(500, 600)]["oom"] == 0 and res[(500, 700)]["oom"] > 0
c4 = len({res[(5, y)]["maxminor"] for y in (50, 100, 200, 400)}) == 1
c5 = all(res[(100, y)]["promoted"] == res[(500, y)]["promoted"] for y in (50, 100, 200, 400)) and res[(5, 200)]["promoted"] < res[(100, 200)]["promoted"]
c6 = all(res[(100, a)]["thr"] < res[(100, b)]["thr"] for a, b in [(50, 100), (100, 200), (200, 400)])   # BREAK: with moderate lifetime the trade is monotone
print("c1 interior peak at T500", c1, "| c2 pause rises", c2, "| c3 ceiling at Y600", c3, "| c4 flat pause T5", c4, "| c5 promotion threshold", c5, "| c6 T100 monotone", c6)
ok = c1 and c2 and c3 and c4 and c5 and c6
print(("RESULT: PASS" if ok else "RESULT: FAIL"), f"T500 interior peak Y=200; T500 thr {[res[(500,y)]['thr'] for y in (50,100,200,400)]} maxminor {[res[(500,y)]['maxminor'] for y in (50,100,200,400)]} oom Y400/Y600/Y700 {res[(500,400)]['oom']}/{res[(500,600)]['oom']}/{res[(500,700)]['oom']}; T5 maxminor {[res[(5,y)]['maxminor'] for y in (50,100,200,400)]}")
