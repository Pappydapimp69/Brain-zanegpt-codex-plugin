"""Sandbox: compose half-open 'attribute each boundary item to exactly ONE neighbour' (GEOMETRY point-in-polygon)
with 'count independent roots, not repetitions' (RESEARCH corroboration). Does exclusive attribution fix
multi-root sources? Deterministic, stdlib only. sources: name -> list of roots it derives from (a root has [])."""
def roots_of(s, g, seen=()):
    if not g[s]: return {s}
    out = set()
    for p in g[s]: out |= roots_of(p, g)
    return out
def name_count(g): return len(g)
def root_union(g): return len(set().union(*[roots_of(s, g) for s in g]))
def weight(g, mode):
    """each source passes weight 1 down to its roots; inclusive = full 1 to EACH root (double count);
    half-open = to exactly one (first sorted root); split = 1/k each. Returns total weight across roots."""
    tot = 0.0
    for s in g:
        rs = sorted(roots_of(s, g))
        if mode == "inclusive": tot += len(rs)
        elif mode == "half-open": tot += 1
        else: tot += 1
    return tot
def claim_score(g, mode):
    if mode == "names": return name_count(g)
    if mode == "union": return root_union(g)
    return weight(g, mode)

# fixtures
echo = {"R": [], "w": ["R"], "f": ["w"], "a": ["f"], "b": ["a"]}                       # 1 root, 5 names
two_primary = {"P1": [], "P2": []}                                                      # 2 independent roots
merged_pair = {"P1": [], "P2": [], "m1": ["P1", "P2"], "m2": ["P1", "P2"], "m3": ["P1", "P2"]}  # 3 aggregators over 2 roots
four_single = {"Q1": [], "Q2": [], "Q3": [], "Q4": []}
review = {"P1": [], "P2": [], "rev": ["P1", "P2"]}   # a review that genuinely re-tests both roots

rows = {}
for nm, g in (("echo", echo), ("two_primary", two_primary), ("merged_pair", merged_pair), ("four_single", four_single), ("review", review)):
    rows[nm] = {m: claim_score(g, m) for m in ("names", "inclusive", "half-open", "union")}
    print(nm, rows[nm])
# S1 names-count ranks echo above two_primary (the research kernel's failure); union fixes it
s1 = rows["echo"]["names"] > rows["two_primary"]["names"] and rows["echo"]["union"] < rows["two_primary"]["union"]
# S2 inclusive attribution double-counts multi-root aggregators; half-open attribution removes ONLY the double count
s2 = rows["merged_pair"]["inclusive"] == 8 and rows["merged_pair"]["half-open"] == rows["merged_pair"]["names"] == 5
# S3 BREAK: half-open still ranks 3 aggregators of 2 roots (5) above 4 independent singles (4); and the echo chain stays 5 vs 2.
s3 = rows["merged_pair"]["half-open"] > rows["four_single"]["half-open"] and rows["merged_pair"]["union"] < rows["four_single"]["union"] \
     and rows["echo"]["half-open"] > rows["two_primary"]["half-open"]
print("S3 half-open ranking errors left:", "merged_pair>four_single", rows["merged_pair"]["half-open"] > rows["four_single"]["half-open"], "echo>two_primary", rows["echo"]["half-open"] > rows["two_primary"]["half-open"])
# S4 per-root credit under single-owner (first root) vs set-of-all-roots, on the genuine two-root review:
def credit(g, owner):
    c = {}
    for s_ in g:
        if g[s_]:
            rs = sorted(roots_of(s_, g))
            for r in (rs[:1] if owner == "single" else rs): c[r] = c.get(r, 0) + 1
    return c
single, allr = credit(review, "single"), credit(review, "all")
print("S4 review credit: single-owner", single, "| set of all roots", allr)
s4 = len(single) == 1 and len(allr) == 2
ok = s1 and s2 and s3 and s4
print(f"RESULT: {'PASS' if ok else 'FAIL'} single-owner attribution cuts the multi-root double count (merged_pair 8 -> 5) but leaves repetition (merged_pair {rows['merged_pair']['half-open']:.0f} > four_single {rows['four_single']['half-open']:.0f}; echo {rows['echo']['half-open']:.0f} > two_primary {rows['two_primary']['half-open']:.0f}) and drops a root at the join (credit to {len(single)} root vs {len(allr)}); only root union ranks right (2<4, 1<2)")
