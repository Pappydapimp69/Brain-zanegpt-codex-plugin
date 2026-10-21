"""Blind rebuild of seven E44 (rescue near-miss share falls with depth).
Own fixture: member's lateral offset (in sectors) from the call's bearing is a
discretised Normal with sd = 0.6 * depth (a call heard from farther is vaguer).
The search covers a FIXED block of 5 sectors (offset -2..+2). Near miss = the
member is exactly one sector past the block (|offset| == 3). Exact, no rng.
PREDICTION (written before running): share of failures that are near misses
falls monotonically with depth; near misses PER SEARCH rise then fall (interior
peak); shallow failures are mostly near misses (>=0.5). Break scenario: a block
that widens with depth (5 + 2*round(depth/2)) should flatten the share fall.
"""
import math, sys
print("python", sys.version.split()[0])
def P(k, sd):  # P(round(X)=k), X~N(0,sd)
    c = lambda x: 0.5*(1+math.erf(x/(sd*math.sqrt(2))))
    return c(k+0.5)-c(k-0.5)
def stats(depth, half):
    sd = 0.6*depth
    fail = 1 - sum(P(k, sd) for k in range(-half, half+1))
    near = P(half+1, sd)+P(-half-1, sd)
    return fail, near, near/fail if fail > 1e-12 else float('nan')
ok = True
rows = []
for d in [1, 2, 3, 4, 5, 6, 8, 10]:
    f, n, s = stats(d, 2); rows.append((d, f, n, s))
    print(f"fixed  depth {d:2d}: fail {f:.3f} near/search {n:.3f} near share {s:.3f}")
shares = [r[3] for r in rows if r[1] > 1e-9]
mono = all(a >= b for a, b in zip(shares, shares[1:]))
pers = [r[2] for r in rows]
pk = pers.index(max(pers)); interior = 0 < pk < len(pers)-1
shallow = rows[1][3] >= 0.5
print("share falls monotonically:", mono, "| per-search interior peak at depth", rows[pk][0], interior, "| shallow share>=0.5:", shallow)
print("-- break: block widens with depth")
ws = []
for d in [2, 4, 6, 8, 10]:
    h = 2 + round(d/2); f, n, s = stats(d, h); ws.append(s)
    print(f"widen  depth {d:2d} half {h}: fail {f:.3f} near share {s:.3f}")
flat = max(ws)-min(ws) < 0.5*(shares[0]-shares[-1])
print("widening block flattens the fall:", flat)
ok = mono and interior and shallow
print(f"RESULT: {'PASS' if ok else 'FAIL'} share {shares[0]:.3f}->{shares[-1]:.3f} monotone={mono}; per-search peak depth {rows[pk][0]} ({max(pers):.3f}); widening block range {min(ws):.3f}-{max(ws):.3f}")
