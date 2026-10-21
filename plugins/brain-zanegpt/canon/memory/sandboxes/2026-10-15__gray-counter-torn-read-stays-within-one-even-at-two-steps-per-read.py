"""Train kernel (apply): GRAY-CODES/asynchronous-counters - a counter read while
its bits change returns, per changing bit, old or new; binary can be far off,
reflected Gray is always old or new; a mod-10 counter must use the middle slice
(codes 3..12). Re-verifies brainwork E293 with my own enumeration, then pushes
the claim to where it breaks:
 (a) the writer advances TWO steps during one read window (each bit that ever
     changes can show any value it held) - is Gray still old-or-new?
 (b) which moduli have a one-bit cyclic slice of the 4-bit reflected sequence?
     (an odd cycle cannot exist: each one-bit step flips popcount parity).
Exhaustive, no rng.
PREDICTION (written before running): binary worst error 3/7/31 for 3/4/6 bits
(2^(k-1)-1, as E293), Gray 0 for one step per read; with two steps per read
Gray reads can be a value from neither old, middle nor new state, worst error
>= 1 (I expect 2 or more for 4 bits); centred slices work for every even
modulus 2..16 and no slice (indeed no cycle) works for any odd modulus.
"""
import sys
from itertools import product
print("python", sys.version.split()[0])
gray = lambda n: n ^ (n >> 1)
def torn(seq_vals, decode, k, steps):
    """worst |decoded - nearest of the visited counts| over every start and mix."""
    L = len(seq_vals); worst = 0
    for i in range(L):
        states = [seq_vals[(i + s) % L] for s in range(steps + 1)]
        counts = [(i + s) % L for s in range(steps + 1)]
        choices = [sorted({(st >> b) & 1 for st in states}) for b in range(k)]
        for bits in product(*choices):
            v = sum(bit << b for b, bit in enumerate(bits))
            d = decode.get(v)
            if d is None: worst = max(worst, L); continue      # not a valid code at all
            if d in counts: continue
            err = min(min(abs(d - c), L - abs(d - c)) for c in counts)
            worst = max(worst, err)
    return worst
res = {}
for k in (3, 4, 6):
    N = 1 << k
    b = list(range(N)); g = [gray(n) for n in range(N)]
    res[k] = (torn(b, {v: i for i, v in enumerate(b)}, k, 1), torn(g, {v: i for i, v in enumerate(g)}, k, 1),
              torn(g, {v: i for i, v in enumerate(g)}, k, 2))
    print(f"{k} bits: binary 1-step worst {res[k][0]}, gray 1-step {res[k][1]}, gray 2-steps-per-read {res[k][2]}")
def one_bit_cycle(seq): return all(bin(seq[i] ^ seq[(i + 1) % len(seq)]).count("1") == 1 for i in range(len(seq)))
ok_mod = {}
for M in range(2, 17):
    s = (16 - M) // 2
    sl = [gray(n) for n in range(s, s + M)]
    first = [gray(n) for n in range(M)]
    any_slice = any(one_bit_cycle([gray(n) for n in range(a, a + M)]) for a in range(0, 17 - M))
    ok_mod[M] = (one_bit_cycle(first), one_bit_cycle(sl), any_slice)
print("modulus: first-M ok / centred slice ok / any slice ok")
print("  " + "  ".join(f"{M}:{''.join('Y' if x else 'n' for x in v)}" for M, v in ok_mod.items()))
g10 = [gray(n) for n in range(3, 13)]
w10 = torn(g10, {v: i for i, v in enumerate(g10)}, 4, 1)
c = [res[3][0] == 3 and res[4][0] == 7 and res[6][0] == 31, all(res[k][1] == 0 for k in res),
     all(res[k][2] >= 1 for k in res), res[4][2] >= 2,
     all(ok_mod[M][1] for M in range(2, 17, 2)), not any(ok_mod[M][2] for M in range(3, 17, 2)), w10 == 0]
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} binary worst {res[3][0]}/{res[4][0]}/{res[6][0]}; gray 1-step 0; gray 2-steps-per-read worst {res[3][2]}/{res[4][2]}/{res[6][2]}; centred slice works every even modulus, no slice for odd; mod-10 slice torn worst {w10}")
