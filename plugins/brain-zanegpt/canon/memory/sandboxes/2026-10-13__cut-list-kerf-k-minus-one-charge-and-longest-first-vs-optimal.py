"""Cut list on stock boards (1-D). Stock 2400 mm, kerf 3 mm, deterministic arithmetic generator (no RNG).
Compares kerf conventions (0, k-1, k per board) and in-order vs longest-first vs exact optimum (subset DP)."""
L, KERF = 2400, 3

def feasible(total, k, conv):
    cuts = {"zero": 0, "k-1": max(k - 1, 0), "k": k}[conv]
    return total + cuts * KERF <= L

def first_fit(pieces, conv):
    boards = []  # [total, k]
    for p in pieces:
        for b in boards:
            if feasible(b[0] + p, b[1] + 1, conv):
                b[0] += p; b[1] += 1; break
        else:
            boards.append([p, 1])
    return boards

def optimum(pieces, conv):
    n = len(pieces); full = (1 << n) - 1
    ok = [False] * (1 << n)
    for m in range(1, 1 << n):
        tot = sum(pieces[i] for i in range(n) if m >> i & 1); k = bin(m).count("1")
        ok[m] = feasible(tot, k, conv)
    INF = 99; best = [INF] * (1 << n); best[0] = 0
    for m in range(1, 1 << n):
        low = m & -m; sub = m
        while sub:
            if sub & low and ok[sub] and best[m ^ sub] + 1 < best[m]:
                best[m] = best[m ^ sub] + 1
            sub = (sub - 1) & m
    return best[full]

def gen(i):
    n = 6 + i % 5
    return [300 + (i * 7919 + j * 104729 + j * j * 31 + i * j * 17) % 1100 for j in range(n)]

def valid_with_truth(boards):   # is a layout made under some convention valid under the true k-1 rule?
    return all(feasible(b[0], b[1], "k-1") for b in boards)

N = 1500
stats = dict(blind_invalid=0, ffd_gt_opt=0, ffd_gt_opt_plus1=0, inorder_gt_ffd=0, k_costs_board=0, zero_fewer=0)
tot_ffd = tot_opt = tot_in = 0
for i in range(N):
    ps = gen(i)
    blind = first_fit(ps, "zero")
    if not valid_with_truth(blind): stats["blind_invalid"] += 1
    ffd = len(first_fit(sorted(ps, reverse=True), "k-1"))
    inord = len(first_fit(ps, "k-1"))
    opt = optimum(ps, "k-1")
    optk = optimum(ps, "k")
    tot_ffd += ffd; tot_opt += opt; tot_in += inord
    if ffd > opt: stats["ffd_gt_opt"] += 1
    if ffd > opt + 1: stats["ffd_gt_opt_plus1"] += 1
    if inord > ffd: stats["inorder_gt_ffd"] += 1
    if optk > opt: stats["k_costs_board"] += 1
    if len(blind) < opt: stats["zero_fewer"] += 1
print(f"cases={N}: kerf-blind layouts invalid under true rule {stats['blind_invalid']} ({stats['blind_invalid']/N:.3f}); "
      f"zero-kerf plan claims fewer boards than the true optimum in {stats['zero_fewer']}")
print(f"charging k kerfs instead of k-1 costs an extra board in {stats['k_costs_board']} ({stats['k_costs_board']/N:.3f})")
print(f"longest-first beats in-order in {stats['inorder_gt_ffd']} cases; boards in-order {tot_in}, longest-first {tot_ffd}, optimum {tot_opt}")
print(f"longest-first above optimum in {stats['ffd_gt_opt']} ({stats['ffd_gt_opt']/N:.3f}), by more than one board in {stats['ffd_gt_opt_plus1']}")
ok = stats["blind_invalid"] > 0 and stats["zero_fewer"] > 0 and stats["ffd_gt_opt"] > 0 and tot_ffd < tot_in and stats["k_costs_board"] > 0
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" {stats}")
