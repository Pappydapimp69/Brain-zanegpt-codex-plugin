"""ITERATION 3. Iteration 2 also FAILED: my 60/120/60/120 'Kawasaki' set was wrong (60+60 is not 180), and creases on the same folded line
need an arc-nesting (no interleave) rule, not only the pierce rule. Fixed both; sets now Kawasaki-correct.
ITERATION 2. Iteration 1 FAILED (90s gave 14 foldable, not 8): my layer rule ignored that sectors alternate face-up/face-down, and
my "non-Kawasaki" set (100,100,80,80) actually satisfies Kawasaki (100+80=180 twice). Both fixed (face-parity in the stacking rule;
non-Kawasaki set now (100,90,100,70)); prediction text unchanged apart from that angle set.
PREDICTION (written before first run). Degree-4 flat-fold vertex, 16 mountain/valley assignments, folded by reflection and checked
for a consistent layer stack (crease rays may not pierce a sector stacked between its two sides).
 (90,90,90,90): foldable = exactly the 8 assignments with |M-V|=2 (Maekawa sufficient here).
 (45,90,135,90) and (30,60,150,120): Kawasaki holds (a1+a3=a2+a4=180); foldable count 4 (<8 Maekawa-valid) (Maekawa NOT sufficient, the smallest-angle rule bites).
 (100,90,100,70): sums to 360, Maekawa-valid assignments exist (8) but 0 foldable (Kawasaki necessary).
 BREAK: every foldable assignment, for every angle set tried, satisfies |M-V|=2 (Maekawa necessary, 0 exceptions)."""
import itertools, math

def foldable(ang, mv):
    n = len(ang)
    # unfold: ray directions of creases in the sheet; sector i lies between ray i and ray i+1
    rays = [sum(ang[:i]) for i in range(n)]
    # folded direction of ray k after reflecting across previous creases (flat folding, 1-D alternating sum)
    f = [0.0]
    for i in range(n - 1):
        f.append(f[-1] + (ang[i] if i % 2 == 0 else -ang[i]))
    closure = f[-1] + (ang[n - 1] if (n - 1) % 2 == 0 else -ang[n - 1])
    if abs(closure) > 1e-9: return False        # Kawasaki: rays must come back to start
    def interval(i):
        a, b = f[i], f[(i + 1) % n] if i + 1 < n else f[0]
        return (min(a, b), max(a, b))
    iv = [interval(i) for i in range(n)]
    for order in itertools.permutations(range(n)):   # order[0] is bottom of stack
        pos = {s: k for k, s in enumerate(order)}
        ok = True
        for c in range(n):                     # crease c between sector c-1 and sector c
            s1, s2 = (c - 1) % n, c
            s2_below = (mv[c] == 'M') == (s1 % 2 == 0)   # mountain: s2 goes behind s1 in s1's own frame; sectors alternate face-up/down
            above_s = s1 if s2_below else s2
            below_s = s1 if above_s == s2 else s2
            if pos[above_s] < pos[below_s]: ok = False; break
            lo, hi = sorted((pos[s1], pos[s2]))
            for k in range(lo + 1, hi):         # sectors stacked strictly between must not be pierced by this crease's ray
                a, b = iv[order[k]]
                if a + 1e-9 < f[c] % 1e9 < b - 1e-9 or (a < f[c] < b): ok = False; break
            if not ok: break
        if ok:
            arcs = []
            for c in range(n):
                s1, s2 = (c - 1) % n, c
                arcs.append((tuple(sorted((pos[s1], pos[s2]))), round(f[c] % 360, 6)))
            for (x, fx), (y, fy) in itertools.combinations(arcs, 2):
                if fx == fy and (x[0] < y[0] < x[1] < y[1] or y[0] < x[0] < y[1] < x[1]): ok = False
        if ok: return True
    return False

def run(ang):
    maek = fold = fold_not_maek = 0
    for mv in itertools.product('MV', repeat=len(ang)):
        m = abs(mv.count('M') - mv.count('V')) == 2
        maek += m
        fl = foldable(ang, mv)
        fold += fl
        fold_not_maek += fl and not m
    return maek, fold, fold_not_maek

res = {a: run(a) for a in [(90, 90, 90, 90), (45, 90, 135, 90), (100, 90, 100, 70), (30, 60, 150, 120)]}
for k, v in res.items(): print(k, "maekawa-valid=%d foldable=%d foldable-but-not-maekawa=%d" % v)
ok = (res[(90, 90, 90, 90)][:2] == (8, 8) and res[(45, 90, 135, 90)][1] == 4 and res[(30, 60, 150, 120)][1] == 4 and res[(100, 90, 100, 70)][0] == 8
      and res[(100, 90, 100, 70)][1] == 0 and all(v[2] == 0 for v in res.values()))
print("RESULT: %s Maekawa-valid/foldable: 90s %d/%d, 45-90-135-90 %d/%d, 100-90-100-70 %d/%d (Kawasaki fails), 30-60-150-120 %d/%d; exceptions to Maekawa-necessary: %d" % (
  "PASS" if ok else "FAIL", *res[(90, 90, 90, 90)][:2], *res[(45, 90, 135, 90)][:2], *res[(100, 90, 100, 70)][:2], *res[(30, 60, 150, 120)][:2], sum(v[2] for v in res.values())))
