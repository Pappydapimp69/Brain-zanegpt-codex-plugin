"""Two promotion gates in series: ZaneGPT (>=3 events, >=2 contexts, owner approval)
and Brain (steward schema/dedup hold + validate ref check on the merged batch).
Deterministic: every combination of finding attributes is enumerated once.
Ground truth: a finding is SOUND if evidence suffices (ev>=3, ctx>=2) and its refs resolve.
Schema/format failures and near-duplicates are fixable or redundant, not unsound."""
from itertools import product

CASES = [dict(ev=e, ctx=c, appr=a, schema=s, refs=r, dup=d)
         for e, c, a, s, r, d in product([1,2,3,4],[1,2,3],[0,1],[0,1],[0,1],[0,1])]
sound = lambda f: f["ev"] >= 3 and f["ctx"] >= 2 and f["refs"]
zane  = lambda f: f["ev"] >= 3 and f["ctx"] >= 2 and f["appr"]
stew  = lambda f: f["schema"] and not f["dup"]
valid = lambda f: f["refs"]

def run(policy, batch_abort=False):
    if policy == "A":   # Zane-pass enters Brain as already verified
        canon = [f for f in CASES if zane(f)]
    elif policy == "B": # Zane-pass re-enters as a proposal, faces steward + validate
        cand = [f for f in CASES if zane(f) and stew(f)]
        if batch_abort and any(not valid(f) for f in cand):
            canon = []
        else:
            canon = [f for f in cand if valid(f)]
    elif policy == "C": # split precedence: validate (structure) is hard; steward schema/dup
        # holds go back to the owner, whose approval already covers judgement
        canon = [f for f in CASES if zane(f) and valid(f)]
    bad = sum(not sound(f) for f in canon)
    owner_overruled = sum(1 for f in CASES if zane(f) and sound(f) and f not in canon)
    owner_overruled_dup = sum(1 for f in CASES if zane(f) and sound(f) and f["dup"] and f not in canon)
    return len(canon), bad, owner_overruled, owner_overruled_dup

res = {k: run(*k) for k in [("A",False),("B",False),("B",True),("C",False)]}
for k, v in res.items():
    print(f"policy {k[0]}{' batch-abort' if k[1] else ' per-item'}: canon={v[0]} unsound_in_canon={v[1]} "
          f"owner_approved_sound_blocked={v[2]} (of which near-dup={v[3]})")
a, b, bb = res[("A",False)], res[("B",False)], res[("B",True)]
c = res[("C",False)]
mixed = a[1] > 0 and b[1] == 0 and b[2] > 0 and bb[0] == 0 and c[1] == 0 and c[2] == 0
print(("RESULT: FAIL" if not mixed else "RESULT: PASS") +
      f" mixed: A admits {a[1]} unsound (bad refs); B admits 0 but blocks {b[2]} owner-approved sound findings "
      f"({b[3]} as near-dups); batch-abort B promotes {bb[0]} of {sum(zane(f) and stew(f) for f in CASES)}; "
      f"split precedence C admits 0 unsound and blocks {c[2]}")
