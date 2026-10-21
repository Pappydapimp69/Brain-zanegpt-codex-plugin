"""ABA version tag: exhaustive adversarial schedules, two counter policies.

Model (deterministic, no rng, no threads): a Treiber stack over a 5-node pool.
Initial stack [X, Y, Z] (X on top), free list {P, Q}. Thread A reads
(head=X, next=Y, tag) to pop, then stalls. The adversary B runs EVERY sequence
of L operations, where an op is pop (if nonempty) or push of ANY currently free
node (freed nodes recycle). Then A's CAS(head: X->Y) runs.

A CAS is a CORRUPT success when it matches (head is X again and the tag
matches) but the correct new head (X's current successor) is not Y.

Counter policies:
  per-change: tag += 1 on every head change (every push and every pop)
  push-only : tag += 1 only when a node is pushed (a common variant)
The tag matches when its counter advanced by a multiple of 2^k.

Counting is exact: a DP over (stack, pushes) counts sequences, so every
schedule of length L is covered.
"""
from collections import defaultdict

X, Y, Z, P, Q = "XYZPQ"
POOL = (X, Y, Z, P, Q)
INIT = (X, Y, Z)
LMAX = 12


def layers():
    """Yield (L, {(stack, pushes): count}) for L = 1..LMAX."""
    cur = {(INIT, 0): 1}
    for L in range(1, LMAX + 1):
        nxt = defaultdict(int)
        for (st, pu), c in cur.items():
            if st:
                nxt[(st[1:], pu)] += c
            for n in POOL:
                if n not in st:
                    nxt[((n,) + st, pu + 1)] += c
        cur = dict(nxt)
        yield L, cur


def corrupt_state(st):
    if not st or st[0] != X:
        return False
    succ = st[1] if len(st) > 1 else None
    return succ != Y


def table():
    """res[policy][k][L] = corrupt CAS successes over all schedules of length L."""
    res = {"per-change": defaultdict(dict), "push-only": defaultdict(dict)}
    totals = {}
    for L, layer in layers():
        totals[L] = sum(layer.values())
        for k in range(0, 4):
            m = 1 << k
            pc = po = 0
            for (st, pu), c in layer.items():
                if not corrupt_state(st):
                    continue
                if L % m == 0:
                    pc += c
                if pu % m == 0:
                    po += c
            res["per-change"][k][L] = pc
            res["push-only"][k][L] = po
    return res, totals


def first_defeat(row):
    for L in sorted(row):
        if row[L] > 0:
            return L
    return None


def main():
    res, totals = table()
    pc, po = res["per-change"], res["push-only"]
    untag = pc[0]
    ok = True

    print("L  schedules  untagged  pc1  pc2  pc3 | po1  po2  po3")
    for L in range(1, LMAX + 1):
        print(f"{L:2d} {totals[L]:10d} {untag[L]:9d} {pc[1][L]:4d} {pc[2][L]:4d} {pc[3][L]:4d}"
              f" | {po[1][L]:4d} {po[2][L]:4d} {po[3][L]:4d}")

    # Scenario 1: per-change tag fails exactly at multiples of 2^k, and there it
    # gives ZERO protection (same count as no tag at all).
    s1 = all(
        pc[k][L] == (untag[L] if L % (1 << k) == 0 else 0)
        for k in (1, 2, 3) for L in range(1, LMAX + 1)
    )
    print(f"S1 per-change: corrupt == untagged at L%2^k==0 else 0: {s1}")
    ok &= s1

    # Scenario 2: minimal defeating schedule length per width (adversary cost).
    mins = {k: first_defeat(pc[k]) for k in range(4)}
    print(f"S2 min defeating L per-change: {mins}")
    s2 = mins == {0: 3, 1: 4, 2: 4, 3: 8}
    ok &= s2

    # Scenario 3 (BREAK): push-only counter. If E2's 'multiple of head changes'
    # were the predicate for any tag, po1 would be 0 at every odd L.
    odd_hits = [L for L in range(1, LMAX + 1, 2) if po[1][L] > 0]
    po_mins = {k: first_defeat(po[k]) for k in range(1, 4)}
    print(f"S3 push-only 1-bit corrupting odd L: {odd_hits}")
    print(f"S3 min defeating L push-only: {po_mins}")
    s3 = bool(odd_hits) and odd_hits[0] == 5 and po_mins[2] == 6
    ok &= s3

    # Scenario 4: same width, which policy leaves more corrupt schedules in
    # total over L<=12 (protection per bit depends on the counter policy).
    tot_pc = {k: sum(pc[k].values()) for k in (1, 2, 3)}
    tot_po = {k: sum(po[k].values()) for k in (1, 2, 3)}
    print(f"S4 total corrupt L<=12 per-change {tot_pc} push-only {tot_po} untagged {sum(untag.values())}")

    # Negative control: a predicate that ignores the tag must see untagged counts.
    nc = all(pc[0][L] == untag[L] for L in untag) and sum(untag.values()) > 0
    print(f"NC untagged has corrupt schedules: {nc}")
    ok &= nc

    summ = (f"per-change wraps only at L%2^k==0 (=untagged there), min L {mins}; "
            f"push-only 1-bit corrupts at odd L {odd_hits[:3]}, min L {po_mins}")
    print(("RESULT: PASS " if ok else "RESULT: FAIL ") + summ)


if __name__ == "__main__":
    main()
