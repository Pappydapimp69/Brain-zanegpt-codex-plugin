"""Pedigree collapse toy: ancestor SLOTS double each generation (2^g) but DISTINCT people are capped.
Closed population of N per generation. Child i has parents (a*i) % N and (a*i + d) % N in the previous generation
(a, d = mating structure: d is how far apart the two parents' indices sit). Deterministic, no RNG."""
def distinct(N, a, d, g):
    cur = {0}
    for _ in range(g):
        nxt = set()
        for x in cur:
            nxt.add((a * x) % N); nxt.add((a * x + d) % N)
        cur = nxt
    return len(cur)
rows = {}
for name, N, a, d in (("outbred big", 2**20, 2, 1), ("outbred small", 64, 2, 1), ("cousin-heavy small", 64, 2, 2), ("selfing-like", 64, 2, 0)):
    rows[name] = [distinct(N, a, d, g) for g in range(0, 11)]
    print(name, "N=%d" % N, rows[name])
slots = [2 ** g for g in range(11)]
print("slots     ", slots)
cap_ok = all(r[g] <= min(slots[g], n) for (nm, n), r in zip((("outbred big", 2**20), ("outbred small", 64), ("cousin-heavy small", 64), ("selfing-like", 64)), rows.values()) for g in range(11))
big_free = rows["outbred big"] == slots              # no collapse within 10 generations when N >> 2^10
small_cap = rows["outbred small"][6] == 64 and rows["outbred small"][10] == 64 and rows["outbred small"][5] == 32
cousin = rows["cousin-heavy small"][10] < rows["outbred small"][10] and rows["cousin-heavy small"][10] == 32
selfing = rows["selfing-like"][10] == 1
ok = cap_ok and big_free and small_cap and cousin and selfing
print(f"RESULT: {'PASS' if ok else 'FAIL'} distinct<=min(2^g,N) always; big pop none lost by g=10 ({rows['outbred big'][10]}/1024); N=64 saturates at g=6 (64); cousin-heavy mating g=10 {rows['cousin-heavy small'][10]} vs outbred {rows['outbred small'][10]}; selfing {rows['selfing-like'][10]}")
