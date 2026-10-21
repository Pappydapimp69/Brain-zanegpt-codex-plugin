# Prediction (written before the first run): survivor of the Josephus circle (people 1..n, every k-th eliminated, counting from 1).
# (1) the recurrence J(1)=0, J(n)=(J(n-1)+k) mod n (0-based) equals direct list simulation for all k in 2..7 and n in 1..100 (600 cells);
# (2) for k=2 the closed form 'rotate the leading bit of n to the end' equals the simulation for all n in 1..300;
# (3) BREAK: the same bit-rotation rule applied to k=3 disagrees with simulation for more than 50 percent of n in 2..100;
# (4) simulation order matters: eliminating by 'skip k-1' off-by-one (counting k+1) disagrees with the recurrence for k=2 at some n.
def sim(n, k):
    p = list(range(n)); i = 0
    while len(p) > 1:
        i = (i + k - 1) % len(p); p.pop(i)
    return p[0]
def rec(n, k):
    j = 0
    for m in range(2, n+1): j = (j + k) % m
    return j
def rot(n): return ((n - (1 << (n.bit_length()-1))) << 1) | 1
bad1 = sum(1 for k in range(2, 8) for n in range(1, 101) if sim(n, k) != rec(n, k))
bad2 = sum(1 for n in range(1, 301) if sim(n, 2) + 1 != rot(n))
bad3 = sum(1 for n in range(2, 101) if sim(n, 3) + 1 != rot(n))
def sim_off(n, k):
    p = list(range(n)); i = 0
    while len(p) > 1:
        i = (i + k) % len(p); p.pop(i)
    return p[0]
bad4 = sum(1 for n in range(2, 101) if sim_off(n, 2) != rec(n, 2))
print("recurrence vs sim mismatches (600 cells):", bad1)
print("k=2 bit rotation vs sim mismatches (300):", bad2)
print("k=3 bit rotation mismatches of 99:", bad3, " off-by-one sim vs recurrence mismatches of 99:", bad4)
ok = bad1 == 0 and bad2 == 0 and bad3 > 49 and bad4 > 0
print("RESULT: %s recurrence matches simulation on 600 cells (k 2..7, n 1..100); k=2 bit-rotation exact on 300 n; same rule wrong for k=3 on %d of 99 n; off-by-one counting wrong on %d of 99 n" % ("PASS" if ok else "FAIL", bad3, bad4))
