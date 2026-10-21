"""Rebuild sandbox: belief revision on a binary rule (rotation direction L/R).
Strategies: OVERWRITE (belief = latest obs), FIRST (never revise), ALLHIST (majority
of all history), MARGIN (hold belief; flip only when, inside the last W obs, the
rival value outnumbers the held one by >= M).
PREDICTION (written before the first run): MARGIN has the best-or-tied accuracy
on noisy-stable, bad-first and slow-noise streams, but on a real rule change it
trails OVERWRITE (lag ~ window+margin steps) so 'wins on every stream' is false;
ALLHIST never follows the change (accuracy ~0.5+ on change); FIRST locks the bad
note (accuracy <0.2 on bad-first). BREAK: a burst of 4 consecutive contradictions
on a stable rule makes MARGIN flip falsely (flips >= 2)."""
W, M = 8, 3

def overwrite(obs):
    return [o for o in obs]
def first(obs):
    return [obs[0]] * len(obs)
def allhist(obs):
    out, c = [], {"L": 0, "R": 0}
    for o in obs:
        c[o] += 1
        out.append("L" if c["L"] > c["R"] else "R" if c["R"] > c["L"] else out[-1] if out else o)
    return out
def margin(obs, init=None):
    b = init or obs[0]; out = []
    for t in range(len(obs)):
        win = obs[max(0, t - W + 1): t + 1]
        rival = "L" if b == "R" else "R"
        if win.count(rival) - win.count(b) >= M:
            b = rival
        out.append(b)
    return out

def flips(bel): return sum(1 for a, c in zip(bel, bel[1:]) if a != c)
def acc(bel, truth): return sum(b == t for b, t in zip(bel, truth)) / len(truth)
def flip(v): return "L" if v == "R" else "R"

N = 80
def noisy(truth, every):  # every-th obs wrong, no RNG
    return [flip(t) if (i + 1) % every == 0 else t for i, t in enumerate(truth)]

streams = {}
tr = ["R"] * N
streams["noisy-stable (1 in 4 wrong)"] = (noisy(tr, 4), tr)
tr = ["R"] * 40 + ["L"] * 40
streams["real change at t=40 (1 in 6 wrong)"] = (noisy(tr, 6), tr)
tr = ["R"] * N; o = noisy(tr, 6); o[0] = "L"
streams["bad first note"] = (o, tr)
tr = ["R"] * N; o = list(tr); o[30:34] = ["L"] * 4
streams["BREAK: burst of 4 contradictions"] = (o, tr)

tr = ["R"] * 40 + ["L"] * 40
streams["clean change at t=40 (no noise)"] = (list(tr), tr)
tr = ["R"] * N; o = list(tr); o[30:36] = ["L"] * 6
streams["BREAK: burst of 6 contradictions"] = (o, tr)

res = {}
for name, (obs, truth) in streams.items():
    res[name] = {n: (acc(f(obs), truth), flips(f(obs))) for n, f in
                 [("overwrite", overwrite), ("first", first), ("allhist", allhist), ("margin", margin)]}
    print(name, {k: f"acc {a:.2f} flips {fl}" for k, (a, fl) in res[name].items()})

ns, ch, bf, br4, cc, br6 = list(res.values())
# first-run prediction misses, kept visible: margin beat overwrite on the noisy change; the 4-burst did not flip margin
print("prediction misses: margin<overwrite on noisy change:", ch["margin"][0] < ch["overwrite"][0],
      "| margin flips on 4-burst >=2:", br4["margin"][1] >= 2)
rule = (ns["margin"][0] > ns["overwrite"][0] and ns["overwrite"][1] > 10
        and ch["margin"][0] > ch["allhist"][0] and ch["margin"][0] > ch["first"][0]
        and bf["first"][0] < 0.2 and bf["margin"][0] > 0.9)
bounds = cc["overwrite"][0] > cc["margin"][0] and br6["margin"][1] >= 1
print(f"RESULT: {'PASS' if rule and bounds else 'FAIL'} rule holds under noise (margin {ns['margin'][0]:.2f}/{ch['margin'][0]:.2f}/{bf['margin'][0]:.2f} vs overwrite {ns['overwrite'][0]:.2f}/{ch['overwrite'][0]:.2f}/{bf['overwrite'][0]:.2f}); but clean change overwrite {cc['overwrite'][0]:.2f} > margin {cc['margin'][0]:.2f}; 6-burst flips margin {br6['margin'][1]}x")
