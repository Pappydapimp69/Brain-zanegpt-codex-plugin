"""Deeper follow-up to brain's immutable-key + changes-feed sync lesson, which replayed the feed in order.
Exhaustive over EVERY delivery order of one row's events, with at-least-once duplication:
  page read of v1; feed: v2 (delivered twice), v3, delete at v4.  Server truth: row deleted.
Second case without a delete: page v1, feed v2 (twice), v3. Truth: v3.
Client policies:
  plain      upsert overwrites; delete removes
  versioned  apply only if version > stored version; delete removes the record (no memory of it)
  tomb       versioned, and a delete leaves a tombstone holding its version
Predictions written before running:
 P1 plain ends wrong in more than half the orders (both cases).
 P2 versioned is always right without a delete, but resurrects the deleted row in some orders (> 0).
 P3 tomb is right in every order of both cases.
"""
from itertools import permutations

def apply(policy, evs):
    rec = None          # ("live", v) or ("tomb", v) or None
    for kind, v in evs:
        cur_v = rec[1] if rec else 0
        if policy == "plain":
            rec = None if kind == "del" else ("live", v)
        elif policy == "versioned":
            if rec is None or v > cur_v:
                rec = None if kind == "del" else ("live", v)
        else:
            if rec is None or v > cur_v:
                rec = ("tomb", v) if kind == "del" else ("live", v)
    return None if rec is None or rec[0] == "tomb" else rec[1]

cases = {"with delete": ([("put", 1), ("put", 2), ("put", 2), ("put", 3), ("del", 4)], None),
         "no delete": ([("put", 1), ("put", 2), ("put", 2), ("put", 3)], 3)}
R = {}
for cname, (evs, truth) in cases.items():
    orders = set(permutations(evs))
    for pol in ("plain", "versioned", "tomb"):
        wrong = sum(1 for o in orders if apply(pol, o) != truth)
        R[(cname, pol)] = (wrong, len(orders))
        print(f"{cname:11s} {pol:9s}: wrong in {wrong} of {len(orders)} delivery orders")
p1 = all(R[(c, "plain")][0] > R[(c, "plain")][1] / 2 for c in cases)
p2 = R[("no delete", "versioned")][0] == 0 and R[("with delete", "versioned")][0] > 0
p3 = all(R[(c, "tomb")][0] == 0 for c in cases)
checks = [("P1 plain wrong in > half", p1), ("P2 versioned ok without delete, resurrects with one", p2), ("P3 tombstones right everywhere", p3)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 3 else 'FAIL'} {held}/3; " + "; ".join(f"{c} {p} {R[(c,p)][0]}/{R[(c,p)][1]}" for c in cases for p in ("plain", "versioned", "tomb")))
