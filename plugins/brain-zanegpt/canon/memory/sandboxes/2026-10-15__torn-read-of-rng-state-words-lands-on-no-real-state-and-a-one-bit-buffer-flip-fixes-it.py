"""Sandbox: Gray-code torn-read kernel applied to saving multi-word PRNG state
(sandbox-seeded-rng-state-words/E1, seeded-rng kernel). Deterministic, stdlib only.
Torn-read model: every bit (or word) that changes can be read old or new."""
from itertools import product
ok = True

# S1: re-verify the kernel on counters
def gray(i): return i ^ (i >> 1)
def ungray(g):
    b = 0
    while g: b ^= g; g >>= 1
    return b
def worst_torn(seq, decode=None):
    # error in counts: the torn word decoded to a count (decode), vs the old and new counts
    worst = 0; n = len(seq)
    for t in range(n):
        a, b = seq[t], seq[(t + 1) % n]; diff = a ^ b
        bits = [1 << i for i in range(diff.bit_length()) if diff >> i & 1]
        for pick in product((0, 1), repeat=len(bits)):
            v = a
            for bit, p in zip(bits, pick):
                if p: v ^= bit
            val = decode(v) if decode else v
            cur, nxt = (decode(a), decode(b)) if decode else (a, b)
            err = min(abs(val - cur), abs(val - nxt))
            worst = max(worst, err)
    return worst
res = {k: (worst_torn(list(range(2 ** k))), worst_torn([gray(i) for i in range(2 ** k)], ungray)) for k in (3, 4, 6, 8)}
mod10_first = [gray(i) for i in range(10)]; mod10_mid = [gray(i) for i in range(3, 13)]
wrap_bits = lambda s: bin(s[-1] ^ s[0]).count("1")
print(f"S1 worst torn error binary/gray by width: {res}; mod10 first-ten wrap bits={wrap_bits(mod10_first)} err={worst_torn(mod10_first, ungray)}, "
      f"middle slice wrap bits={wrap_bits(mod10_mid)} err={worst_torn(mod10_mid, lambda g: ungray(g) - 3)}")
ok &= all(res[k] == (2 ** (k - 1) - 1, 0) for k in res)
ok &= wrap_bits(mod10_first) == 3 and worst_torn(mod10_first, ungray) == 6 and wrap_bits(mod10_mid) == 1 and worst_torn(mod10_mid, lambda g: ungray(g) - 3) == 0

# sfc32
M = 0xFFFFFFFF
def step(s):
    a, b, c, d = s; t = (a + b + d) & M; d = (d + 1) & M
    a = b ^ (b >> 9); b = (c + (c << 3)) & M; c = ((c << 21) | (c >> 11)) & M; c = (c + t) & M
    return (a, b, c, d), t
def seeded(seed):
    s = (0, seed, 0, 1)
    for _ in range(12): s, _ = step(s)
    return s
def rolls(s, n):
    out = []
    for _ in range(n): s, r = step(s); out.append(r)
    return out

# S2 (BREAK): a saver copies the 4 words one at a time while the sim steps; each word old or new
seeds = range(1, 9); torn_total = torn_real = torn_diverge = 0
for seed in seeds:
    s = seeded(seed)
    for _ in range(500): s, _ = step(s)
    window = {}; x = s
    for k in range(-0, 2001):  # states from now to +2000 steps
        window[x] = k; x, _ = step(x)
    old = s; new, _ = step(s)
    ref_old, ref_new = rolls(old, 20), rolls(new, 20)
    for pick in product((0, 1), repeat=4):
        if pick in ((0, 0, 0, 0), (1, 1, 1, 1)): continue
        torn = tuple(n if p else o for o, n, p in zip(old, new, pick))
        if torn == old or torn == new: continue
        torn_total += 1
        if torn in window: torn_real += 1
        r = rolls(torn, 20)
        if r != ref_old and r != ref_new and r[1:] != ref_new[:19]: torn_diverge += 1
print(f"S2 torn 4-word snapshots: {torn_total} distinct, {torn_real} equal a real state within 2000 steps, {torn_diverge} diverge from both streams")
ok &= torn_total > 0 and torn_real == 0 and torn_diverge == torn_total

# S3: Gray's one-bit idea applied: double buffer + 1-bit index flip (writer fills the
# inactive buffer, then flips the index). Torn read of the index is old or new by construction.
buffer_torn = 0
for seed in seeds:
    s = seeded(seed); bufs = [s, None]; idx = 0
    new, _ = step(s); bufs[1 - idx] = new; idx_new = 1 - idx
    for read_idx in (idx, idx_new):  # the only two values a 1-bit index can show
        if bufs[read_idx] not in (s, new): buffer_torn += 1
print(f"S3 double buffer with 1-bit index: torn snapshots {buffer_torn} of {2 * len(seeds)} reads")
ok &= buffer_torn == 0

# S4 control: binary-coded 2-bit ring index over 4 buffers (0->1->2->3->0): 1->2 and 3->0 change 2 bits
ring_bin = list(range(4)); ring_gray = [gray(i) for i in range(4)]
print(f"S4 4-buffer ring index worst torn slot error: binary={worst_torn(ring_bin)} gray={worst_torn(ring_gray, ungray)}")
ok &= worst_torn(ring_bin) == 1 and worst_torn(ring_gray, ungray) == 0

print(("RESULT: PASS" if ok else "RESULT: FAIL") +
      f" kernel reproduced (binary worst 3/7/31/127, gray 0, mod10 slice fixes wrap 6->0); {torn_total} torn sfc32 snapshots,"
      f" {torn_real} real, {torn_diverge} diverge; 1-bit double-buffer index 0 torn; 4-slot ring index needs gray (binary err 1)")
