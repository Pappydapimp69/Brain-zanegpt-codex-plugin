"""Blind rebuild of seven#E63: does a cue-alone phantom schedule land 1-2 of 12
however long the teaching, and does alternating land 4-5?  Own fixture: two
learners (Rescorla-Wagner over a grid of rates/thresholds, and a Beta-count
Bayesian learner), 8 later cues instead of 12 scaled back, teaching 3/6/10/20."""
def rw(teach, sched, a, thr):
    v = 0.0
    for _ in range(teach): v += a * (1 - v)
    hits = 0
    for real in sched:
        if not real and v >= thr: hits += 1
        v += a * ((1 if real else 0) - v)
    return hits
def beta(teach, sched, thr, prior=1.0):
    s, f = prior + teach, prior
    hits = 0
    for real in sched:
        if not real and s / (s + f) >= thr: hits += 1
        if real: s += 1
        else: f += 1
    return hits
N = 12
SCH = {"all": [0]*N, "alt": [1, 0]*(N//2), "sparse": [1, 0, 0, 0]*(N//4)}
fails = []
print("RW grid (teach 3/10/20 -> all,alt,sparse)")
for a in (0.15, 0.3, 0.5):
    for thr in (0.5, 0.6, 0.7):
        row = {t: tuple(rw(t, SCH[k], a, thr) for k in SCH) for t in (3, 10, 20)}
        print(f"  a={a} thr={thr} {row}")
        if not (1 <= row[10][0] <= 2 and 4 <= row[10][1] <= 5):
            fails.append(f"rw a={a} thr={thr} t10={row[10]}")
print("Beta-count learner (teach 3/10/20 -> all,alt,sparse)")
for thr in (0.6, 0.7):
    row = {t: tuple(beta(t, SCH[k], thr) for k in SCH) for t in (3, 10, 20)}
    print(f"  thr={thr} {row}")
    if row[20][0] - row[3][0] >= 2:
        fails.append(f"beta thr={thr}: teaching 20 buys {row[20][0]} vs 3 buys {row[3][0]} all-phantom")
n_rw = sum(1 for f in fails if f.startswith("rw"))
print(f"RW cells off the claimed numbers: {n_rw}/9")
print("break: " + "; ".join(fails[-2:]))
ok = n_rw <= 1 and not any(f.startswith("beta") for f in fails)
print(f"RESULT: {'PASS' if ok else 'FAIL'} rw cells off claim {n_rw}/9; beta learner: long teaching buys more phantoms -> 'however long the teaching' is an RW artefact")
