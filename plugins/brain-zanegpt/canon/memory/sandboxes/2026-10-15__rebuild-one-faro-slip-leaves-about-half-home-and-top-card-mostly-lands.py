# Own fixture: 52 cards, labelled by start position. Faro = cut then riffle alternately.
# Slip kinds (my own definitions): cut26+1 / cut26-1 (uneven cut, riffle alternates
# until a half runs out, remainder dropped on the bottom), and doubledrop at index j
# (two cards from the same half fall together at output position j).
# PREDICTION (before run): mean cards home after 8 out-faros with one random slip
# in 40-60% (in any slip kind); Elmsley top card lands at target p in 60-90% of
# single-slip cases; a slip at faro 1 (earliest) is more damaging than at faro 8.
import random
n = 52
def faro(deck, out=True, cut=26, dd=None):
    a, b = deck[:cut], deck[cut:]
    first, second = (a, b) if out else (b, a)
    res = []; i = j = 0; k = 0
    while i < len(first) or j < len(second):
        if dd is not None and k == dd and i + 1 < len(first):   # double drop from `first`
            res += first[i:i + 2]; i += 2; k += 2; continue
        if i < len(first): res.append(first[i]); i += 1; k += 1
        if j < len(second): res.append(second[j]); j += 1; k += 1
    return res
def run(seq, slip_at=None, kind=None, arg=None):
    d = list(range(n))
    for f, out in enumerate(seq):
        if f == slip_at:
            d = faro(d, out, cut=26 + arg) if kind == "cut" else faro(d, out, dd=arg)
        else:
            d = faro(d, out)
    return d
assert run([True] * 8) == list(range(n))          # perfect 8 out-faros restore
home = {}; rnd = random.Random(11)
allhome = []
for slip_at in range(8):
    vals = []
    for kind, arg in [("cut", -1), ("cut", 1)] + [("dd", j) for j in range(0, 51)]:
        d = run([True] * 8, slip_at, kind, arg)
        vals.append(sum(d[i] == i for i in range(n)) / n)
    home[slip_at] = sum(vals) / len(vals); allhome += vals
mean_home = sum(allhome) / len(allhome)
for s in home: print(f"slip at faro {s+1}: mean home {home[s]:.2f}")
# Elmsley: target position p -> in/out per bit (MSB first, 6 bits for 0..51 gives 6 faros)
def seq_for(p):
    bits = [int(c) for c in format(p, "06b")]
    return [not bool(b) for b in bits]            # 1 -> in-faro (out=False)
perfect = all(run(seq_for(p)).index(0) == p for p in range(n))
land = tot = 0
for p in range(n):
    s = seq_for(p)
    for slip_at in range(len(s)):
        for kind, arg in [("cut", -1), ("cut", 1), *[("dd", j) for j in range(0, 51)]]:
            tot += 1; land += run(s, slip_at, kind, arg).index(0) == p
land_rate = land / tot
print(f"mean home after 8-faro restore with one slip: {mean_home:.2f}; Elmsley single-slip landing: {land_rate:.2f}; perfect Elmsley ok: {perfect}")
ok = perfect and 0.35 <= mean_home <= 0.65 and 0.6 <= land_rate <= 0.9
print(f"RESULT: {'PASS' if ok else 'FAIL'} mean home {mean_home:.2f}, Elmsley top-card landing {land_rate:.2f}")
