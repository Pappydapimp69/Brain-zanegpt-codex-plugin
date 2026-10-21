"""brain-pitch/E3 (fallback bucket collides when two id-keyed arrays merge) x
brain/E54 (suite drifts to cheap oracles). Does a cheap-oracle suite pass while the
collision inflates totals, and does a claim-based assertion catch it? Deterministic."""
IDEA_SRC = [("SYSTEM", 200), ("RPG", 150), ("MUSIC", 84), ("UI-UX", 11)]  # true 445
MEM_SRC = [("gamedev", 200), ("viz", 88), ("other", 68)]                    # true 356

def idea_nodes(map_ui_ux):
    out = []
    for d, n in IDEA_SRC:
        known = d != "UI-UX" or map_ui_ux
        out.append({"id": d if known else "other", "total": n})
    return out

def mem_nodes(prefix=""):
    return [{"id": (prefix + d) if d == "other" else d, "total": n} for d, n in MEM_SRC]

def merge(ideas, mems):
    clusters = {}
    for src in (ideas, mems):
        for c in src:
            if c["id"] in clusters: clusters[c["id"]]["total"] += c["total"]  # silent merge
            else: clusters[c["id"]] = {"total": c["total"]}
    shown_i = sum(clusters[c["id"]]["total"] for c in ideas)
    shown_m = sum(clusters[c["id"]]["total"] for c in mems)
    return clusters, shown_i, shown_m

def cheap_suite(ideas, mems, clusters):
    """E54-style: only claims with an obvious oracle."""
    ok = [all(c["id"] in clusters for c in ideas + mems),
          all(v["total"] >= 0 for v in clusters.values()),
          len(clusters) > 0, len(ideas) == len(IDEA_SRC), len(mems) == len(MEM_SRC)]
    return all(ok), len(ok)

def claim_suite(ideas, mems, clusters, shown_i, shown_m):
    """claims the picture makes: displayed counters equal source truth; ids disjoint."""
    t_i, t_m = sum(n for _, n in IDEA_SRC), sum(n for _, n in MEM_SRC)
    disjoint = not ({c["id"] for c in ideas} & {c["id"] for c in mems})
    return shown_i == t_i and shown_m == t_m and disjoint

def scenario(name, ideas, mems):
    cl, si, sm = merge(ideas, mems)
    cheap, n = cheap_suite(ideas, mems, cl)
    claim = claim_suite(ideas, mems, cl, si, sm)
    print(f"{name}: shown {si}/{sm} (true 445/356) cheap_suite_pass={cheap}({n} checks) claim_suite_pass={claim}")
    return cheap, claim, si, sm

# Prediction (before first run): bug => shown 513/367, cheap suite PASS, claim suite FAIL;
# renaming only one side's fallback => both pass; leaving fallback mapped-away => both pass.
r1 = scenario("1 bug: unmapped UI-UX -> 'other' collides", idea_nodes(False), mem_nodes())
r2 = scenario("2 fix: map UI-UX explicitly", idea_nodes(True), mem_nodes())
r3 = scenario("3 fix: namespace mem 'mem-other', idea fallback still 'other'", idea_nodes(False), mem_nodes("mem-"))
# BREAK scenario: namespace the mem side only AND a third source reuses 'other' -> rename defers collision
third = [{"id": "other", "total": 9}]
cl, si, sm = merge(idea_nodes(False), mem_nodes("mem-") + third)
r4 = (si, sm, sm == 356 + 9)
print(f"4 BREAK: rename defers collision when a 3rd 'other' arrives: mem counter {sm} (own true {356+9}); idea counter {si}")
ok = (r1[0] and not r1[1] and (r1[2], r1[3]) == (513, 367) and r2[0] and r2[1]
      and r3[0] and r3[1] and si == 445 + 9 + 0 and False is False)
# scenario 4: idea counter picks up the third source's 9 via shared 'other' key
ok = ok and si != 445
print("RESULT: %s cheap suite passes the bug (513/367 vs true 445/356); claim suite fails it; explicit mapping/namespacing fix passes; rename-only fix re-collides with a third 'other' (idea counter %d, true 445)"
      % ("PASS" if ok else "FAIL", si))
