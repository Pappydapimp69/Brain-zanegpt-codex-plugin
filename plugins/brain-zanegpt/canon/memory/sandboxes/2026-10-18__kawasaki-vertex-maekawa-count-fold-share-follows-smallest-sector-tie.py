# Compose Kawasaki (angle closure) with Maekawa (count): among Kawasaki-valid vertices,
# which count-satisfying mountain/valley assignments fold flat? Folding is decided by an
# independent crimp reduction (remove a local-minimum sector whose two creases differ).
# PREDICTION (deg 4): fold share of count-satisfying assignments is 8/8 if all sectors equal,
# 6/8 if the smallest sector is tied (not all equal), 4/8 if the smallest is unique.
import itertools
from functools import lru_cache
G = 15
def compositions(total, k):
    if k == 1:
        yield (total,); return
    for f in range(1, total - k + 2):
        for r in compositions(total - f, k - 1):
            yield (f,) + r
@lru_cache(maxsize=None)
def folds(sec, cr):
    n = len(sec)
    if n == 2:
        return sec[0] == sec[1] and cr[0] == cr[1]
    for i in range(n):
        if sec[i] <= sec[i - 1] and sec[i] <= sec[(i + 1) % n]:
            j = (i + 1) % n
            if cr[i] != cr[j]:   # creases bounding sector i are cr[i] and cr[i+1]
                keep = [k for k in range(n) if k not in (i, j)]
                # remaining sectors: merge i-1 and i+1
                a, b = (i - 1) % n, (i + 1) % n
                newsec = []
                for k in range(n):
                    if k == i: continue
                    if k == a: newsec.append(sec[a] + sec[b] - sec[i])
                    elif k == b: continue
                    else: newsec.append(sec[k])
                newcr = [cr[k] for k in range(n) if k not in (i, j)]
                if len(newsec) == len(newcr) and folds(tuple(newsec), tuple(newcr)):
                    return True
    return False
def kawasaki(sec):
    return len(sec) % 2 == 0 and sum(sec[0::2]) * G == 180 and sum(sec[1::2]) * G == 180
tot = 360 // G
stats = {}
viol = 0; anyfold_nonkaw = 0; kaw_nofold = 0; bad_count_fold = 0
for deg in (4, 6):
    for sec in compositions(tot, deg):
        kw = kawasaki(sec)
        nfold = 0; ncount = 0; anyf = False
        for cr in itertools.product((0, 1), repeat=deg):
            f = folds(sec, cr)
            cnt = abs(2 * sum(cr) - deg) == 2
            if f and not cnt: bad_count_fold += 1
            if cnt: ncount += 1; nfold += f
            anyf |= f
        if not kw and anyf: anyfold_nonkaw += 1
        if kw and not anyf: kaw_nofold += 1
        if deg == 4 and kw:
            m = min(sec); ties = sec.count(m)
            key = "equal" if len(set(sec)) == 1 else ("tied-min" if ties > 1 else "unique-min")
            stats.setdefault(key, set()).add((nfold, ncount))
        if deg == 6 and kw:
            stats.setdefault("deg6", set()).add((nfold, ncount))
print({k: sorted(v) for k, v in stats.items()})
print("non-Kawasaki vertices that fold:", anyfold_nonkaw, " Kawasaki vertices that never fold:", kaw_nofold,
      " folds that break the count:", bad_count_fold)
d4 = {k: v for k, v in stats.items() if k != "deg6"}
ok = (d4.get("equal") == {(8, 8)} and d4.get("tied-min") == {(6, 8)} and d4.get("unique-min") == {(4, 8)}
      and anyfold_nonkaw == 0 and kaw_nofold == 0 and bad_count_fold == 0
      and any(nf < nc for nf, nc in stats["deg6"]) and (30, 30) in stats["deg6"])
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
      f"deg4 shares {{{', '.join(k+':'+str(sorted(v)) for k, v in d4.items())}}} deg6 {sorted(stats['deg6'])[:6]} nonKaw folds {anyfold_nonkaw} count-breaking folds {bad_count_fold}")
