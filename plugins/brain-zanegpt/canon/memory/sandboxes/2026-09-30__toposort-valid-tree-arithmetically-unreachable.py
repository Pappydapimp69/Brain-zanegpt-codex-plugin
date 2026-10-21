# Prediction (before run): a tech tree with costs summing 67 passes toposort validation (0 cycles, 0 undeclared deps)
# yet with 48 stone shared by 3 factions (16 each) each faction unlocks at most 3 of 5 buildings (cheapest-first).
# Demand/supply pre-check (sum cost*factions > supply) flags it; raising supply to 201 makes all 5 reachable for all 3.
from graphlib import TopologicalSorter
COST = {"hut": 5, "mill": 10, "forge": 14, "tower": 18, "hall": 20}   # sum 67
DEPS = {"hut": [], "mill": ["hut"], "forge": ["hut"], "tower": ["mill", "forge"], "hall": ["tower"]}
def validate(deps):
    order = list(TopologicalSorter(deps).static_order())   # raises on cycle
    known = set(deps)
    undeclared = [d for v in deps.values() for d in v if d not in known]
    return len(order), len(undeclared)
def reachable(budget):
    got, left = set(), budget
    for n in TopologicalSorter(DEPS).static_order():
        if all(d in got for d in DEPS[n]) and COST[n] <= left:
            got.add(n); left -= COST[n]
    return len(got)
def precheck(supply, factions): return sum(COST.values()) * factions > supply
ok = True
n, u = validate(DEPS); print("toposort ok: nodes", n, "undeclared", u); ok &= (n == 5 and u == 0)
for supply, fac in ((48, 3), (201, 3), (67, 1), (66, 1)):
    per = supply // fac
    r = reachable(per); flagged = precheck(supply, fac)
    print(f"supply={supply} factions={fac} per={per} reachable={r}/5 precheck_flags_shortfall={flagged}")
    ok &= (r == 5) == (not flagged)
ok &= reachable(16) == 2  # first run: predicted 3, observed 2 (hut+mill=15, forge 14 no longer fits)
print("RESULT: %s toposort passes (5 nodes, 0 undeclared) while 48 stone/3 factions reaches only %d/5; supply-vs-demand precheck matches reachability on 4 scenarios" % ("PASS" if ok else "FAIL", reachable(16)))
