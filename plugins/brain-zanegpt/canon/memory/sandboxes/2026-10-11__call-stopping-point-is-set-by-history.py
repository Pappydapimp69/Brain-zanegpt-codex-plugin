"""Rebuild of seven E28 (answering a fading call stops paying by itself).
E28 scores night k with a FIXED prior and a known k. The player knows neither
k nor a fresh prior: they have a history (calls heard, searches that failed).
Own fixture: prior 0.20 that a member went missing at night 0, real call
0.85 x 0.65^k, false calls 0.12 per night (union with a real call), a night
out finds a missing member with 0.85, night risk 0.20. Policy: answer every
call. Exact Bayes over the two hypotheses (missing since night 0 / nobody).
Histories scored at night k:
 MEMORYLESS  E28-style: prior 0.20, call on night k, k known
 REPEATED    a call every night 0..k, every search before k failed
 RETURNING   call on night 0 (search failed), silent nights 1..k-1, call on k
 FRESH       silent nights 0..k-1, first call on night k
PREDICTIONS (written before running):
 P1 memoryless value turns negative by night 3 (the E28 shape reproduces)
 P2 at some night, a real history's posterior differs from memoryless by
    more than 0.15 (history matters)
 P3 the last night where answering pays differs between histories by at
    least 2 nights (so the fade + false calls do NOT set one natural stopping
    point; the player's history does)
"""
P0, F, FIND, RISK, N = 0.20, 0.12, 0.85, 0.20, 7
def real(k): return 0.85*0.65**k
def pcall(k, missing): return 1-(1-real(k))*(1-F) if missing else F
def posterior(events):
    # events: list of (night, heard, searched_and_failed)
    lm, ln = P0, 1-P0
    for k, heard, failed in events:
        lm *= pcall(k, True) if heard else 1-pcall(k, True)
        ln *= pcall(k, False) if heard else 1-pcall(k, False)
        if failed: lm *= 1-FIND
    return lm/(lm+ln)
hist = {
 "memoryless": lambda k: posterior([(k, True, False)]) if False else P0*pcall(k, True)/(P0*pcall(k, True)+(1-P0)*F),
 "repeated":   lambda k: posterior([(j, True, True) for j in range(k)] + [(k, True, False)]),
 "returning":  lambda k: posterior(([(0, True, True)] + [(j, False, False) for j in range(1, k)] + [(k, True, False)]) if k else [(0, True, False)]),
 "fresh":      lambda k: posterior([(j, False, False) for j in range(k)] + [(k, True, False)]),
}
last = {}; post = {}
for name, f in hist.items():
    post[name] = [f(k) for k in range(N)]
    pays = [k for k in range(N) if post[name][k]*FIND - RISK > 0]
    last[name] = max(pays) if pays else -1
    print(f"{name:10s} " + " ".join(f"{p:.3f}" for p in post[name]) + f"  last pays night {last[name]}")
maxdiff = max(abs(post[h][k]-post['memoryless'][k]) for h in hist for k in range(N))
spread = max(last.values()) - min(last.values())
neg3 = post['memoryless'][3]*FIND - RISK < 0
checks = [neg3, maxdiff > 0.15, spread >= 2]
held = sum(checks)
print(f"RESULT: {'PASS' if held == 3 else 'FAIL'} {held}/3 predictions held; last-pays night "
      + ", ".join(f"{h} {v}" for h, v in last.items()) + f"; max posterior gap vs memoryless {maxdiff:.3f}")
