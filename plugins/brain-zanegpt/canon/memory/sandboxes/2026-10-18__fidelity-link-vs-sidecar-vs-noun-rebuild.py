"""Blind rebuild: rank ad variants on IPM x D1 where D1 comes from a fidelity link that is (a) derived from the
game with read noise p, (b) a hand sidecar stale for a fixed 25% of variant identities, (c) a new-noun flag, plus
(d) IPM alone. Own fixture: all 84 six-variant sheets chosen from the 9 (hook, fidelity) types, deterministic masks."""
import itertools
HOOK = (0.7, 1.0, 1.4); FID = (0.4, 0.7, 1.0)
TYPES = [(h, f) for h in HOOK for f in FID]
def ipm(h, f): return 10 * h * (1.6 - 0.6 * f)
def d1(f): return 0.15 + 0.25 * f
def val(t): return ipm(*t) * d1(t[1])
SHEETS = list(itertools.combinations(range(9), 6))          # 84 sheets
STALE = {1, 5}                                              # 2 of 9 identities (22%) stale in the sidecar
NOUN = {0, 2, 3, 7}                                         # arbitrary "new noun" flags, unrelated to fidelity
def shift(f): return FID[(FID.index(f) + 1) % 3]
def pick(sheet, method, p=0.0, si=0):
    def score(k, ti):
        h, f = TYPES[ti]
        if method == "ipm": return ipm(h, f)
        if method == "derived":
            wrong = ((k * 7 + si * 3) % 20) < round(20 * p)
            return ipm(h, f) * d1(shift(f) if wrong else f)
        if method == "sidecar": return ipm(h, f) * d1(shift(f) if ti in STALE else f)
        if method == "noun": return ipm(h, f) * (1.0 if ti in NOUN else 0.8)   # flag only
        if method == "truth": return val(TYPES[ti])
    return max(((score(k, ti), -k, ti) for k, ti in enumerate(sheet)))[2]
def acc(method, p=0.0):
    best = lambda sh: max(sh, key=lambda ti: val(TYPES[ti]))
    return sum(val(TYPES[pick(sh, method, p, si)]) >= val(TYPES[best(sh)]) - 1e-9 for si, sh in enumerate(SHEETS)) / len(SHEETS)
res = {"ipm": acc("ipm"), "noun": acc("noun"), "sidecar": acc("sidecar")}
for p in (0.0, 0.1, 0.2, 0.3, 0.5, 0.7): res[f"derived@{p}"] = acc("derived", p)
for k, v in res.items(): print(k, f"{v:.3f}")
# sensitivity: which identities are stale decides the sidecar's accuracy and so the crossover (all 2- and 3-subsets)
PS = (0.0, 0.1, 0.2, 0.3, 0.5, 0.7)
cross_by = {}
for k in (2, 3):
    for S in itertools.combinations(range(9), k):
        STALE = set(S); a = acc("sidecar")
        c = next((p for p in PS if res[f"derived@{p}"] <= a), None)
        cross_by[c] = cross_by.get(c, 0) + 1
STALE = {1, 5}
print("crossover noise by stale-set (count of 120 sets):", dict(sorted(cross_by.items(), key=lambda kv: (kv[0] is None, kv[0]))))
chance = sum(1 / 6 for _ in SHEETS) / len(SHEETS)
cross = [p for p in (0.0, 0.1, 0.2, 0.3, 0.5, 0.7) if res[f"derived@{p}"] <= res["sidecar"]]
ok = res["derived@0.0"] == 1.0 and res["derived@0.0"] > res["sidecar"] and res["noun"] < 0.4 and res["ipm"] < 0.4 and bool(cross) and res["derived@0.7"] < res["sidecar"]
print(f"RESULT: {'PASS' if ok else 'FAIL'} derived@0 {res['derived@0.0']:.3f} vs sidecar {res['sidecar']:.3f}; noun {res['noun']:.3f} ipm {res['ipm']:.3f} (chance {chance:.3f}); derived<=sidecar from noise {cross[0] if cross else None}; derived@0.2 {res['derived@0.2']:.3f} derived@0.5 {res['derived@0.5']:.3f}; crossover over 120 stale sets {dict(sorted(cross_by.items(), key=lambda kv: (kv[0] is None, kv[0])))}")
