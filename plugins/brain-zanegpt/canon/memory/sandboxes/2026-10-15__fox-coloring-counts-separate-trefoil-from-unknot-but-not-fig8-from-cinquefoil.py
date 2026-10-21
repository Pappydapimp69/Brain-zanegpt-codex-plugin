# Sandbox (KNOT-THEORY seed): Fox n-colorings from standard PD codes (Knot Atlas): X[i,j,k,l], i incoming under edge,
# k outgoing under edge, j and l the over strand: relation 2*c(j) = c(i) + c(k) mod n, and c(j) = c(l).
# Prediction (written before running): colorings counted over all edge assignments mod n are
# unknot: n (trivial only); trefoil: 9 at n=3, 5 at n=5; figure-eight: 3 at n=3, 25 at n=5; cinquefoil: 3 at n=3, 25 at n=5.
# So the count separates trefoil from unknot (mod 3) and trefoil from fig-8 (mod 3), but figure-eight and
# cinquefoil are indistinguishable by Fox 3- and 5-colorings (same counts in both), though they are different knots.
import itertools
PD = {
 "unknot": [],
 "trefoil": [(1,5,2,4),(3,1,4,6),(5,3,6,2)],
 "fig8": [(4,2,5,1),(8,6,1,5),(6,3,7,4),(2,7,3,8)],
 "cinquefoil": [(1,6,2,7),(3,8,4,9),(5,10,6,1),(7,2,8,3),(9,4,10,5)],
}
def count(pd, n):
    if not pd: return n
    edges = sorted({e for x in pd for e in x})
    parent = {e: e for e in edges}
    def find(a):
        while parent[a] != a: a = parent[a]
        return a
    for (i, j, k, l) in pd: parent[find(j)] = find(l)
    reps = sorted({find(e) for e in edges}); idx = {r: t for t, r in enumerate(reps)}
    total = 0
    for col in itertools.product(range(n), repeat=len(reps)):
        c = lambda e: col[idx[find(e)]]
        if all((2 * c(j) - c(i) - c(k)) % n == 0 for (i, j, k, l) in pd): total += 1
    return total
want = {("unknot",3):3,("unknot",5):5,("trefoil",3):9,("trefoil",5):5,("fig8",3):3,("fig8",5):25,("cinquefoil",3):3,("cinquefoil",5):25}
got = {}
for name, pd in PD.items():
    for n in (3, 5):
        got[(name, n)] = count(pd, n); print(name, "mod", n, "->", got[(name, n)], "expected", want[(name, n)])
sep = got[("trefoil",3)] != got[("unknot",3)] and got[("trefoil",3)] != got[("fig8",3)]
blind = got[("fig8",3)] == got[("cinquefoil",3)] and got[("fig8",5)] == got[("cinquefoil",5)]
ok = got == want and sep and blind
print(("RESULT: PASS" if ok else "RESULT: FAIL"), f"counts match prediction {got == want}; trefoil separated from unknot and fig-8 at n=3 {sep}; fig-8 vs cinquefoil identical at n=3,5 {blind}")
