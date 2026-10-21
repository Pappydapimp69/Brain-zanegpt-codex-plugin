"""Compose drywall layout (local drywall E1: full sheets per course + remainders
packed into offcuts) with the cut-list kerf rule (brainwork E178: charge k-1 kerfs
per board; kerf changed the board count in under 1% of random lists).
Units: eighths of an inch (exact integers). Sheet 12 ft = 1152. Deterministic.
"""
SHEET = 144 * 8
COURSES = 2

def remainders(runs):
    full, pieces = 0, []
    for L in runs:
        for _ in range(COURSES):
            f, r = divmod(L, SHEET)
            full += f
            if r: pieces.append(r)
    return full, pieces

def fits(load, n, kerf):  # k-1 kerf charge (E178): n pieces need n-1 cuts
    return load + max(n - 1, 0) * kerf <= SHEET

def ffd(pieces, kerf):
    bins = []  # [load, count]
    for p in sorted(pieces, reverse=True):
        best = None
        for b in bins:  # best fit, as in the drywall layout
            if fits(b[0] + p, b[1] + 1, kerf) and (best is None or b[0] > best[0]):
                best = b
        if best: best[0] += p; best[1] += 1
        else: bins.append([p, 1])
    return len(bins)

def opt(pieces, kerf):
    n = len(pieces)
    if n == 0: return 0
    ok = [False] * (1 << n)
    for m in range(1, 1 << n):
        s = sum(pieces[i] for i in range(n) if m >> i & 1)
        ok[m] = fits(s, bin(m).count("1"), kerf)
    INF = 99
    dp = [INF] * (1 << n); dp[0] = 0
    for m in range(1, 1 << n):
        low = m & -m
        sub = m
        while sub:
            if sub & low and ok[sub] and dp[m ^ sub] + 1 < dp[m]:
                dp[m] = dp[m ^ sub] + 1
            sub = (sub - 1) & m
    return dp[-1]

def sheets(runs, kerf, method):
    full, pcs = remainders(runs)
    return full + (ffd(pcs, kerf) if method == "ffd" else opt(pcs, kerf))

def survey(rooms, kerf):
    ffd_gt_opt = changed = added = exact = 0
    for runs in rooms:
        a0, o0 = sheets(runs, 0, "ffd"), sheets(runs, 0, "opt")
        ak = sheets(runs, kerf, "ffd")
        ffd_gt_opt += a0 > o0
        changed += ak != a0
        added += ak - a0
        _, pcs = remainders(runs)
        k = len(pcs)  # any subset of 2+ remainders that fills a sheet exactly
        exact += any(bin(m).count("1") >= 2 and sum(pcs[i] for i in range(k) if m >> i & 1) == SHEET for m in range(1, 1 << k))
    return ffd_gt_opt, changed, added, exact

FT = 12 * 8
int_rooms = [[W * FT, L * FT] * 2 for W in range(8, 21) for L in range(W, 21)]
# Control: same size range but measured to the inch (deterministic LCG), so exact fits are rare
seed, inch_rooms = 12345, []
for _ in range(len(int_rooms)):
    seed = (1103515245 * seed + 12345) % 2**31; W = 96 + seed % 145
    seed = (1103515245 * seed + 12345) % 2**31; L = 96 + seed % 145
    inch_rooms.append([W * 8, L * 8] * 2)

n = len(int_rooms)
KERF = 1  # 1/8 in saw kerf
i_ffd, i_chg, i_add, i_exact = survey(int_rooms, KERF)
c_ffd, c_chg, c_add, c_exact = survey(inch_rooms, KERF)
r1214 = sheets([12 * FT, 14 * FT] * 2, 0, "ffd"), sheets([12 * FT, 14 * FT] * 2, KERF, "ffd")
print(f"integer-foot rooms {n}: ffd>opt {i_ffd}, rooms with an exact-fill remainder subset {i_exact}, kerf changes count {i_chg} (+{i_add} sheets)")
print(f"inch-measured rooms {n}: ffd>opt {c_ffd}, exact-fill subsets {c_exact}, kerf changes count {c_chg} (+{c_add} sheets)")
print(f"12x14 room: {r1214[0]} sheets snap-cut, {r1214[1]} with 1/8 in kerf")
print(f"E178 reference: kerf changed count in 5/1500 = {5/1500:.4f}; here integer {i_chg/n:.4f}, inch {c_chg/n:.4f}")

# Predictions written before the first run
checks = {
    "FFD equals optimum in all integer rooms": i_ffd == 0,
    "kerf changes count in >10% of integer rooms": i_chg / n > 0.10,
    "kerf changes count in <2% of inch rooms (E178 regime)": c_chg / n < 0.02,
    "12x14 reproduces 9 sheets (drywall E1)": r1214[0] == 9,
}
for k, v in checks.items(): print(("ok  " if v else "MISS"), k)
s = sum(checks.values())
print(f"RESULT: {'PASS' if s == len(checks) else 'FAIL'} {s}/{len(checks)}; kerf adds sheets in {i_chg}/{n} integer-foot rooms vs {c_chg}/{n} inch-measured; ffd>opt {i_ffd} and {c_ffd}; 12x14 {r1214[0]}->{r1214[1]}")
