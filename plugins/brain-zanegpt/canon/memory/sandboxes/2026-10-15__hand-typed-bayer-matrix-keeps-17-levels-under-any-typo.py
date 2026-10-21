# Sandbox: a hand-typed Bayer 4x4 (the sidecar copy) versus the same matrix derived by recursion (the source).
# Prediction (written before running): (a) recursion reproduces the hand-typed matrix exactly; (b) all 120 single
# cell swaps and 20 random full shuffles still render 17 distinct tones on a 0..16 ramp, so the 17-level check
# cannot detect a typo; (c) a derived-from-recursion check catches 120/120 swaps; (d) a check of 'every 2x2 block
# holds one value from each residue class mod 4' catches >= 100 of 120 swaps; (e) a duplicated value (typo that
# repeats a number) drops the level count below 17 in 100% of 240 tried.
import itertools, random
def bayer(n):
    if n == 1: return [[0]]
    b = bayer(n // 2); h = n // 2; m = [[0] * n for _ in range(n)]
    for y in range(h):
        for x in range(h):
            v = 4 * b[y][x]
            m[y][x] = v; m[y][x + h] = v + 2; m[y + h][x] = v + 3; m[y + h][x + h] = v + 1
    return m
typed = [[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]
derived = bayer(4)
print("derived equals typed:", derived == typed)
def levels(m):
    flat = [v for r in m for v in r]
    # ramp of 0..16 sixteenths over every cell; count distinct revealed-cell counts
    return len({sum(1 for v in flat if k > v) for k in range(17)})
def block_ok(m):
    for by in (0, 2):
        for bx in (0, 2):
            if sorted(m[by + j][bx + i] % 4 for j in (0, 1) for i in (0, 1)) != [0, 1, 2, 3]: return False
    return True
cells = [(y, x) for y in range(4) for x in range(4)]
swaps = []
for (p, q) in itertools.combinations(cells, 2):
    m = [r[:] for r in typed]; m[p[0]][p[1]], m[q[0]][q[1]] = m[q[0]][q[1]], m[p[0]][p[1]]; swaps.append(m)
lev = sum(levels(m) == 17 for m in swaps); rec = sum(m != derived for m in swaps); blk = sum(not block_ok(m) for m in swaps)
rnd = random.Random(5); sh = 0
for _ in range(20):
    v = list(range(16)); rnd.shuffle(v); m = [v[i*4:i*4+4] for i in range(4)]; sh += levels(m) == 17
dup = 0; tried = 0
for p in cells:
    for newv in range(16):
        if newv == typed[p[0]][p[1]]: continue
        m = [r[:] for r in typed]; m[p[0]][p[1]] = newv; tried += 1; dup += levels(m) < 17
print(f"swaps: still 17 levels {lev}/120, caught by recursion {rec}/120, caught by block-residue check {blk}/120")
print(f"random shuffles still 17 levels {sh}/20; value overwrites dropping levels {dup}/{tried}")
ok = derived == typed and lev == 120 and sh == 20 and rec == 120 and blk >= 100 and dup == tried
print(("RESULT: PASS" if ok else "RESULT: FAIL"), f"17-level check blind to {lev}/120 swaps, recursion catches {rec}/120, residue check {blk}/120, overwrites caught {dup}/{tried}")
