import random
# Variants: (name, true_ipm, true_d1). Ranking = IPM x D1. D1 comes from a hand-kept
# sidecar {name: d1} (path) vs derived from the same record that holds IPM (companion fix).
V = [("cold_open_A",.050,.20),("film_B",.080,.10),("recut_C",.060,.35),("plain_D",.040,.30),("twist_E",.055,.28)]
def score_sidecar(rows, sidecar, default):
    return {n: i*sidecar.get(n, default) for n,i,_ in rows}
def score_derived(rows):
    return {n: i*d for n,i,d in rows}
def pick(s): return max(s, key=s.get)
truth = pick(score_derived(V)); side = {n:d for n,_,d in V}
def rename(rows, old, new): return [(new if n==old else n,i,d) for n,i,d in rows]
res = {}
res["1 no drift sidecar"] = pick(score_sidecar(V, side, 0.0)) == truth
# 2 rename a NON-winner in the ranking data, sidecar stale
r = rename(V, "film_B", "film_B_v2")
res["2 rename non-winner"] = pick(score_sidecar(r, side, 0.0)) == truth
# 3 BREAK: rename the winner, sidecar stale, default D1=0 (silent) / default=population mean
r = rename(V, truth, truth+"_v2")
res["3a rename winner default0"] = pick(score_sidecar(r, side, 0.0)) == truth+"_v2"
mean = sum(side.values())/len(side)
res["3b rename winner default-mean"] = pick(score_sidecar(r, side, mean)) == truth+"_v2"
# 4 derived join survives the rename
res["4 derived join rename winner"] = pick(score_derived(r)) == truth+"_v2"
# 5 loud check: sidecar keys vs ranked names
res["5 key-diff check catches"] = bool(set(n for n,_,_ in r) - set(side))
# randomized: rename one random variant per trial, count silent wrong picks
random.seed(7); wrong=0; wrong_when_winner=0; winner_trials=0; N=400
for _ in range(N):
    rows=[(n,i*random.uniform(.8,1.2),d*random.uniform(.8,1.2)) for n,i,d in V]
    t=pick(score_derived(rows)); sc={n:d for n,_,d in rows}
    old=random.choice([n for n,_,_ in rows]); rr=rename(rows,old,old+"_v2")
    exp=t+"_v2" if old==t else t
    ok = pick(score_sidecar(rr,sc,0.0))==exp
    if old==t: winner_trials+=1; wrong_when_winner += (not ok)
    wrong += (not ok)
    assert pick(score_derived(rr))==exp
print("scenarios:", res)
print(f"random trials N={N}: sidecar wrong picks={wrong}, of which winner-renamed={wrong_when_winner}/{winner_trials}")
ok = res["1 no drift sidecar"] and res["2 rename non-winner"] and not res["3a rename winner default0"] and res["4 derived join rename winner"] and res["5 key-diff check catches"] and wrong==wrong_when_winner and wrong_when_winner>0
print("RESULT: %s sidecar wrong only when winner renamed (%d/%d winner trials, %d/%d overall); derived join 0 errors" % ("PASS" if ok else "FAIL", wrong_when_winner, winner_trials, wrong, N))
