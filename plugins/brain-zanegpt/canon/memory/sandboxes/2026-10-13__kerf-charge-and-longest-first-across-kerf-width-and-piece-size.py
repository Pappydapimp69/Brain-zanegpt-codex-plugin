"""Stress the kerf k-1 / longest-first cut-list rule across kerf width and piece size (1-D, stock 2400 mm).
Deterministic arithmetic generator, no RNG. Optimum by subset DP (n<=9)."""
L = 2400

def feas(tot, k, kerf, conv):
    cuts = {"zero": 0, "k-1": max(k - 1, 0), "k": k}[conv]
    return tot + cuts * kerf <= L

def ff(pieces, kerf, conv):
    bs = []
    for p in pieces:
        for b in bs:
            if feas(b[0] + p, b[1] + 1, kerf, conv):
                b[0] += p; b[1] += 1; break
        else:
            bs.append([p, 1])
    return bs

def opt(pieces, kerf, conv):
    n = len(pieces)
    ok = [False] * (1 << n)
    for m in range(1, 1 << n):
        t = sum(pieces[i] for i in range(n) if m >> i & 1)
        ok[m] = feas(t, bin(m).count("1"), kerf, conv)
    best = [99] * (1 << n); best[0] = 0
    for m in range(1, 1 << n):
        low = m & -m; s = m
        while s:
            if s & low and ok[s] and best[m ^ s] + 1 < best[m]:
                best[m] = best[m ^ s] + 1
            s = (s - 1) & m
    return best[-1]

def gen(i, lo, span):
    n = 6 + i % 4
    return [lo + (i * 7919 + j * 104729 + j * j * 31 + i * j * 17) % span for j in range(n)]

# (name, kerf, piece lo, span)
SC = [("base 3mm/300-1400", 3, 300, 1100),
      ("wide kerf 10mm/300-1400", 10, 300, 1100),
      ("mid pieces 6mm/200-700", 6, 200, 500),
      ("BREAK extreme kerf 40mm/300-1400", 40, 300, 1100)]
N = 400
res = {}
for name, kerf, lo, span in SC:
    r = dict(blind_invalid=0, k_costs=0, gt1=0, gt0=0, b_in=0, b_ffd=0, b_opt=0, k_extra_boards=0)
    for i in range(N):
        ps = gen(i, lo, span)
        blind = ff(ps, kerf, "zero")
        if not all(feas(b[0], b[1], kerf, "k-1") for b in blind): r["blind_invalid"] += 1
        f = len(ff(sorted(ps, reverse=True), kerf, "k-1")); o = opt(ps, kerf, "k-1"); ok_ = opt(ps, kerf, "k")
        r["b_in"] += len(ff(ps, kerf, "k-1")); r["b_ffd"] += f; r["b_opt"] += o
        if ok_ > o: r["k_costs"] += 1; r["k_extra_boards"] += ok_ - o
        if f > o: r["gt0"] += 1
        if f > o + 1: r["gt1"] += 1
    res[name] = r
    print(f"{name}: invalid_blind {r['blind_invalid']}/{N}, k_charge_costs_board {r['k_costs']}/{N}, ffd>opt {r['gt0']}, ffd>opt+1 {r['gt1']}, boards in-order {r['b_in']} ffd {r['b_ffd']} opt {r['b_opt']}")
base, wide, short, brk = (res[s[0]] for s in SC)
# predictions: kerf matters more as it grows relative to piece size; "never more than one board" is the claim to break
holds_kcost = base["k_costs"] < wide["k_costs"] < brk["k_costs"]
ffd_ok = all(r["b_ffd"] <= r["b_in"] for r in res.values())
print("claim 'never more than one board over optimum' broken:", any(r["gt1"] for r in res.values()))
print(("RESULT: PASS" if holds_kcost and ffd_ok else "RESULT: FAIL") + f" kcost base {base['k_costs']} wide {wide['k_costs']} mid {short['k_costs']} extreme {brk['k_costs']}; ffd_gt1 " + str([r['gt1'] for r in res.values()]))
