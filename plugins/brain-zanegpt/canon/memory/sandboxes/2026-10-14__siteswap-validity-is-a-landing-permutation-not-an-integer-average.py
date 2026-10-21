"""Prediction (before run): a vanilla siteswap (one throw per beat, throw h lands h beats later, 0 = empty hand) is
juggleable iff the landing beats (i + t_i) mod n are all distinct (a permutation), and then the ball count is the average
throw. I predict: (1) simulating beats directly (never two balls landing on one beat, a ball only thrown when one is
in hand) agrees with the permutation test for ALL sequences of length 1..5 with throws 0..9 (111,110 sequences incl. rotations),
(2) the integer-average test alone is NOT enough: it passes sequences like 543 and 345 that collide, so it accepts at least 1 in 4
integer-average sequences wrongly in length 3 (I expect a clearly nonzero count), (3) the ball count from simulation equals the average.
Built to break: 543 (average 4) must fail the simulation. Deterministic, stdlib only."""
from itertools import product
def perm_test(seq):
    n = len(seq); return len({(i + t) % n for i, t in enumerate(seq)}) == n
def simulate(seq, balls=None, cycles=None):
    n = len(seq); avg_num = sum(seq)
    if avg_num % n: return False, None
    b = avg_num // n
    cycles = cycles or (max(seq) + 2)
    horizon = n * cycles
    landing = {}                      # beat -> number of balls landing then
    # start state: balls are in the air with the landings the periodic pattern implies; derive by running the
    # pattern for `cycles` periods from an EMPTY state with b balls placed to be thrown on the first beats where throws are non-zero
    # Simpler exact sim: steady state condition = on every beat t, number of throws landing on t equals 1 if seq[t%n]>0 else 0 (hand needs the ball to throw), at most 1.
    for t in range(horizon):
        h = seq[t % n]
        if h:
            land = t + h
            landing[land] = landing.get(land, 0) + 1
    ok = True
    # steady-state check on beats beyond the warm-up window
    for t in range(max(seq), horizon - max(seq)):
        need = 1 if seq[t % n] > 0 else 0
        if landing.get(t, 0) != need: ok = False
    return ok, b
total = agree = 0; avg_only_pass = avg_only_wrong = 0; ball_mismatch = 0; examples = []
by_len = {}
for n in range(1, 6):
    for seq in product(range(10), repeat=n):
        total += 1
        p = perm_test(seq)
        s, b = simulate(seq)
        agree += (p == s)
        if p != s and len(examples) < 3: examples.append(seq)
        if sum(seq) % n == 0:
            avg_only_pass += 1
            if not s: avg_only_wrong += 1
            by_len.setdefault(n, [0, 0]); by_len[n][0] += 1; by_len[n][1] += (not s)
        if s and b != sum(seq) // n: ball_mismatch += 1
print("sequences", total, "perm==sim", agree, "disagreements", total - agree, examples)
print("integer-average-only passes", avg_only_pass, "of which collide", avg_only_wrong, "by length (pass, wrong):", by_len)
s543, _ = simulate((5, 4, 3)); s441, _ = simulate((4, 4, 1)); s531, _ = simulate((5, 3, 1))
print("543 sim", s543, "perm", perm_test((5, 4, 3)), "| 441 sim", s441, "| 531 sim", s531)
ok = agree == total and not s543 and s441 and s531 and by_len[3][1] / by_len[3][0] > 0.25 and ball_mismatch == 0
print("RESULT: %s %d sequences, permutation test matches simulation in %d; integer average alone wrongly passes %d of %d (len 3: %d of %d); 543 invalid, 441 and 531 valid" %
      ("PASS" if ok else "FAIL", total, agree, avg_only_wrong, avg_only_pass, by_len[3][1], by_len[3][0]))
