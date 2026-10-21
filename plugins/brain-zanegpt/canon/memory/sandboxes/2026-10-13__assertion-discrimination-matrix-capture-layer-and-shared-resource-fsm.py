"""Which assertions actually tell a fixed build from a buggy one?
System A (capture layer): zones A (a1,a2) and B (b1); capture vocab buggy={A} vs fixed={A,B}; 65 click sequences of length 4 containing b1.
System B (shared resource): 4 agents claim one resource in fixed order; per-action re-validation on (fixed) or off (buggy).
For each assertion we measure DISCRIMINATION = share of scenarios where it passes on the fixed build AND fails on the buggy one."""
from itertools import product

def sysA(vocab):
    out = []
    for seq in product(["a1", "a2", "b1"], repeat=4):
        if "b1" not in seq: continue
        zone = lambda e: "B" if e == "b1" else "A"
        seen = [e for e in seq if zone(e) in vocab]          # events that survive the capture layer
        generic_done = len(seen) > 0                         # any tap completes tutorial
        pinned_done = "b1" in seen                           # tap on b1 completes tutorial
        resolver_saw_B = "b1" in seen
        out.append(dict(generic=generic_done, pinned=pinned_done, resolver=resolver_saw_B))
    return out

def sysB(revalidate, order):
    # agents claim in 'order'; all FSM -> approaching; owner = first claimer
    owner = order[0]; fsm = {a: "approaching" for a in order}; at_resource = {owner}
    for a in order:                                           # dependent action
        if a == owner or not revalidate: fsm[a] = "using"
    # non-owner under no-revalidate only advances FSM; position stays with the owner
    pos_ok = len(at_resource) == 1
    fsm_ok = all(fsm[a] != "using" for a in order if a != owner)
    return dict(position=pos_ok, fsm=fsm_ok)

res = []
A_fix, A_bug = sysA({"A", "B"}), sysA({"A"})
def disc_A(key):
    return sum(f[key] and not b[key] for f, b in zip(A_fix, A_bug)) / len(A_fix), sum(f[key] for f in A_fix) / len(A_fix), sum(b[key] for b in A_bug) / len(A_bug)
print(f"System A scenarios: {len(A_fix)}")
dA = {}
for k in ("generic", "pinned", "resolver"):
    d, pf, pb = disc_A(k); dA[k] = d
    print(f"  A assertion {k:9s}: pass(fixed)={pf:.3f} pass(buggy)={pb:.3f} discrimination={d:.3f}")
orders = [list(p) for p in __import__("itertools").permutations([0, 1, 2, 3])]
dB = {}
for k in ("position", "fsm"):
    d = sum(sysB(True, o)[k] and not sysB(False, o)[k] for o in orders) / len(orders)
    pb = sum(sysB(False, o)[k] for o in orders) / len(orders)
    dB[k] = d
    print(f"  B assertion {k:9s}: pass(buggy)={pb:.3f} discrimination={d:.3f} over {len(orders)} claim orders")
res += [dA["generic"] < 0.05, dA["pinned"] > 0.95, dA["resolver"] > 0.95, dB["position"] == 0, dB["fsm"] == 1]
# composite suites: ANY-pass (green if one assertion green) vs ALL-pass
anyA_fix = sum(f["generic"] or f["pinned"] for f in A_fix); anyA_bug = sum(b["generic"] or b["pinned"] for b in A_bug)
allA_bug = sum(b["generic"] and b["pinned"] for b in A_bug)
print(f"Composite A: ANY-of(generic,pinned) green on buggy {anyA_bug}/{len(A_bug)} (fixed {anyA_fix}/{len(A_fix)}); ALL-of green on buggy {allA_bug}/{len(A_bug)}")
res.append(anyA_bug > 0.9 * len(A_bug) and allA_bug < anyA_bug)
# BREAK: pinned trigger is a detector only if the pinned entity is in the changed zone
A_bug2 = sysA({"B"})   # bug inverted: zone A starved, pinned on b1 stays green
pin_green = sum(b["pinned"] for b in A_bug2) / len(A_bug2)
print(f"BREAK: starve zone A instead; pinned-on-b1 still green in {pin_green:.3f} of scenarios (detector only covers the zone it is pinned to)")
res.append(pin_green == 1.0)
print(("RESULT: PASS" if all(res) else "RESULT: FAIL") + f" checks={res}")
