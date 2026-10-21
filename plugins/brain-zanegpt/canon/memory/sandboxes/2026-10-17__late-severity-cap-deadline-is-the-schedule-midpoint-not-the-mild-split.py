# Robustness of late-severity-cap-leaves-the-distance-dial-sharp (cap must land by beat 3 of 6) using the cover and
# laugh forms of rule-card-severity-cap-flattens-the-distance-dial, with the mild/severe split, the schedule length n
# and the cap level varied. Go-big schedule s=i/n for the first L beats, then capped s=cap*i/n*... kept as cap_level*i/n.
# Window = number of 11 distances within 95% of the best total; "forgiving" = window >= 7.
# PREDICTION (before run): the last cap-arrival beat L* that stays forgiving is NOT a fixed 3: it tracks the beat where
# the uncapped schedule crosses the mild split, i.e. L* is within 1 of n*split for each of 9 (n, split) cells
# (n 6, 9, 12; split 0.2, 0.3, 0.4), and shrinks as the split gets lower; BREAK: a cap level of 0.5 (above every split)
# never becomes forgiving (window <= 2 at L=0).
def laugh(s, b): return s if s <= b else max(0.0, s - 3 * (s - b))
def make(split):
    return lambda d, s: 0.8 - 0.5 * d if s <= split else 0.2 + 0.7 * d
ds = [i / 10 for i in range(11)]
def window(n, split, L, level):
    cover = make(split)
    def total(d): return sum(laugh(s, cover(d, s)) for s in [(i / n if i <= L else level * i / n) for i in range(1, n + 1)])
    m = max(total(d) for d in ds)
    return sum(1 for d in ds if total(d) >= 0.95 * m)
def lstar(n, split, level):
    last = None
    for L in range(0, n + 1):
        if window(n, split, L, level) >= 7: last = L
        else: break
    return last
rows = {}
for n in (6, 9, 12):
    for split in (0.2, 0.3, 0.4):
        level = split / 6 * 6 / n * n / 6 * 0 + split * 0.8      # a cap level just under the split
        rows[(n, split)] = (lstar(n, split, split * 0.8), n * split)
        print(f"n {n} split {split}: forgiving through cap beat L* = {rows[(n, split)][0]}  (n*split = {n * split:.1f})")
brk = window(6, 0.3, 0, 0.5)
print("break, cap level 0.5 above the split, L=0 window:", brk)
near = sum(1 for (ls, ns) in rows.values() if ls is not None and abs(ls - ns) <= 1)
mono = all(rows[(n, 0.2)][0] <= rows[(n, 0.3)][0] <= rows[(n, 0.4)][0] for n in (6, 9, 12))
ok = near == 9 and mono and brk <= 2
print(f"RESULT: {'PASS' if ok else 'FAIL'} L* within 1 of n*split in {near}/9 cells; monotone in split {mono}; break window {brk}; L* {[(k, v[0]) for k, v in rows.items()]}")
