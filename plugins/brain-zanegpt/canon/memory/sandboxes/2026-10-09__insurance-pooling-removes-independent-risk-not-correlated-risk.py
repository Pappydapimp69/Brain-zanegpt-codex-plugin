#!/usr/bin/env python3
"""INSURANCE seed sandbox: does adding policyholders to a risk pool shrink ruin risk?

PREDICTION (written before the first run):
  Setup: each policy has a 2% yearly chance of a 10,000 claim; premium = expected
  loss x 1.30 (30% loading), no starting capital; "ruin" = claims > premiums.
  P1  Independent claims, n = 100 -> 10,000: exact ruin probability falls
      monotonically and is < 1e-3 at n = 10,000.
  P2  Correlated claims (2%-per-year catastrophe lifts claim chance 0.0143 -> 0.30,
      same 2% marginal): ruin probability stays >= 0.015 for every n >= 1,000
      (it converges to the catastrophe chance 0.02, it does not shrink), so at
      n = 10,000 independent ruin is more than 100x smaller than correlated ruin.
  P3  Capital to cover a 1-in-100 year, per policy, as a multiple of the 0.02 mean
      claim rate: independent pool <= 1.20x at n = 10,000; correlated pool >= 10x at
      every n >= 1,000 (the floor is the catastrophe year, not the member count).
  P4  BREAK attempt: if the catastrophe chance is 0.5% (below the 1-in-100 target)
      the 99% quantile looks safe (<= 1.2x at n = 10,000) yet ruin probability is
      still >= 0.004, so a quantile target hides the floor.
  P5  Fix: splitting the same 2,000 policies across m independent catastrophe
      zones cuts ruin probability by >= 10x going from m = 1 to m = 100.
      (REFUTED by run 1: ruin went 0.020 -> 0.112. P5b below was added AFTER seeing that.)
  P6  A log-utility buyer (wealth 20,000) will pay MORE than the fair premium of 200
      and more than the loaded premium of 260, but a buyer with wealth 1,000,000
      will not pay 260 (so loading sells only to buyers for whom the loss is big).
  P7  Deductible sizing against a reserve: with a one-month reserve (4,000) the
      largest tested deductible whose out-of-pocket cost fits the reserve is 2,500,
      and it cuts the loaded premium by 25% versus a zero deductible.

Standard library only. No RNG in the verdict (exact binomial arithmetic); one fixed-seed
Monte Carlo cross-check validates the exact calculator.

Source excerpts relied on (embedded so this file is self-contained):
  [expected-utility kernel] "the agent's utility of wealth equals the logarithm of the
      monetary amount" (Bernoulli 1738 as cited by the Stanford Encyclopedia of
      Philosophy) -> used as the buyer's utility function in P6.
  [emergency-fund kernel] the CFPB cites a typical shock of roughly 3 weeks of income,
      and that even 1 month of income in reserve measurably reduces hardship; the
      kernel also names "a deductible" as a reason to hold a reserve -> used to set
      the reserve (4,000 = 1 month of 4,000 income) in P7.
  [new kernel] pooling variance of the mean loss with pairwise correlation rho:
      sd = sigma * sqrt(rho + (1 - rho) / n), floor sigma * sqrt(rho) (checked below).
"""
import math

L = 10_000.0
P = 0.02            # marginal claim chance per policy-year
LOAD = 1.30
Q = 0.02            # catastrophe chance per year
PC = 0.30           # claim chance in a catastrophe year


def lbinom_pmf(n, k, p):
    if p <= 0.0:
        return 1.0 if k == 0 else 0.0
    if p >= 1.0:
        return 1.0 if k == n else 0.0
    return math.exp(math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
                    + k * math.log(p) + (n - k) * math.log1p(-p))


def pmf(n, p):
    return [lbinom_pmf(n, k, p) for k in range(n + 1)]


def survival(pm):
    """sv[t] = P(X > t) for t in 0..len-1, and sv[-1] = 1 handled by caller."""
    out = [0.0] * len(pm)
    acc = 0.0
    for t in range(len(pm) - 1, -1, -1):
        out[t] = acc
        acc += pm[t]
    return out


def tail_gt(pm, t):
    """P(X > t) for integer or real t."""
    if t < 0:
        return 1.0
    ti = int(math.floor(t))
    return sum(pm[ti + 1:]) if ti + 1 < len(pm) else 0.0


def ruin_independent(n, p=P, load=LOAD):
    return tail_gt(pmf(n, p), n * p * load)


def p0_for(q, pc, p=P):
    return (p - q * pc) / (1 - q)


def ruin_common_shock(n, q=Q, pc=PC, p=P, load=LOAD):
    p0 = p0_for(q, pc, p)
    thr = n * p * load
    return (1 - q) * tail_gt(pmf(n, p0), thr) + q * tail_gt(pmf(n, pc), thr)


def quantile_common_shock(n, level, q=Q, pc=PC, p=P):
    p0 = p0_for(q, pc, p)
    a, b = pmf(n, p0), pmf(n, pc)
    cum = 0.0
    for k in range(n + 1):
        cum += (1 - q) * a[k] + q * b[k]
        if cum >= level:
            return k
    return n


def quantile_independent(n, level, p=P):
    pm = pmf(n, p)
    cum = 0.0
    for k in range(n + 1):
        cum += pm[k]
        if cum >= level:
            return k
    return n


def ruin_zones(n, m, q=Q, pc=PC, p=P, load=LOAD):
    """n policies split evenly into m zones; each zone has an independent catastrophe.
    Exact DP over total claims; mass above the ruin threshold is absorbed (truncation)."""
    p0 = p0_for(q, pc, p)
    per = n // m
    thr = n * p * load
    cap = int(math.floor(thr))          # totals > cap are ruin
    zone_cat = pmf(per, pc)
    zone_ok = pmf(per, p0)
    w = [(1 - q) * zone_ok[b] + q * zone_cat[b] for b in range(per + 1)]
    dist = [0.0] * (cap + 1)
    dist[0] = 1.0
    ruined = 0.0
    for _ in range(m):
        new = [0.0] * (cap + 1)
        for a, da in enumerate(dist):
            if da < 1e-18:
                continue
            for b in range(per + 1):
                t = a + b
                if t > cap:
                    ruined += da * sum(w[b:])
                    break
                new[t] += da * w[b]
        dist = new
    return ruined


def zones_needed(m, n=10000, q=Q, pc=PC, p=P, load=LOAD):
    """Noise-free approximation: catastrophic zones needed to exceed the loaded premium."""
    p0 = p0_for(q, pc, p)
    return math.floor((p * load - p0) / ((pc - p0) / m)) + 1


def binom_tail_ge(m, k, q):
    return sum(lbinom_pmf(m, j, q) for j in range(k, m + 1))


def mc_check():
    """Fixed-seed LCG Monte Carlo of the independent pool, n = 20, to validate the exact calc."""
    state = 12345

    def rnd():
        nonlocal state
        state = (1103515245 * state + 12345) % (2 ** 31)
        return state / 2 ** 31
    n, trials, bad = 20, 40000, 0
    for _ in range(trials):
        claims = sum(1 for _ in range(n) if rnd() < P)
        if claims > n * P * LOAD:
            bad += 1
    return bad / trials, ruin_independent(n)


def log_utility_max_premium(wealth, loss=L, p=P):
    eu = (1 - p) * math.log(wealth) + p * math.log(wealth - loss)
    return wealth - math.exp(eu)


def deductible_table(reserve):
    rows = []
    base = None
    for d in (0, 500, 1000, 2500, 5000):
        prem = LOAD * P * (L - d)
        if base is None:
            base = prem
        rows.append((d, prem, 1 - prem / base, d <= reserve))
    return rows


def main():
    ok = []

    def check(name, cond, detail):
        ok.append(cond)
        print(f"  [{'ok' if cond else 'XX'}] {name}: {detail}")

    print("-- exact calculator vs fixed-seed Monte Carlo (n=20)")
    mc, ex = mc_check()
    check("MC matches exact", abs(mc - ex) < 0.01, f"mc={mc:.4f} exact={ex:.4f}")

    print("-- variance floor formula (rho from the common-shock model)")
    p0 = p0_for(Q, PC)
    mean_claim = P
    # per-policy indicator variance and pairwise covariance under the shock model
    var1 = P * (1 - P)
    cov = (1 - Q) * p0 * p0 + Q * PC * PC - P * P
    rho = cov / var1
    for n in (100, 10000):
        # exact sd of the claim RATE via mixture moments
        e_rate = P
        e_rate2 = (1 - Q) * ((p0 * (1 - p0)) / n + p0 ** 2) + Q * ((PC * (1 - PC)) / n + PC ** 2)
        sd_exact = math.sqrt(e_rate2 - e_rate ** 2)
        sd_formula = math.sqrt(var1) * math.sqrt(rho + (1 - rho) / n)
        check(f"sd formula n={n}", abs(sd_exact - sd_formula) < 1e-9,
              f"exact={sd_exact:.6f} formula={sd_formula:.6f} floor={math.sqrt(var1*rho):.6f} rho={rho:.4f}")

    print("-- P1/P2 ruin probability vs pool size (loading 30%, no capital)")
    sizes = (100, 1000, 3000, 10000)
    ind = {n: ruin_independent(n) for n in sizes}
    cor = {n: ruin_common_shock(n) for n in sizes}
    for n in sizes:
        print(f"     n={n:>6}  independent={ind[n]:.2e}  correlated={cor[n]:.4f}")
    check("P1 independent falls monotonically", all(ind[a] > ind[b] for a, b in zip(sizes, sizes[1:])), "monotone")
    check("P1 independent < 1e-3 at 10000", ind[10000] < 1e-3, f"{ind[10000]:.2e}")
    check("P2 correlated >= 0.015 for n>=1000", all(cor[n] >= 0.015 for n in sizes[1:]), f"min={min(cor[n] for n in sizes[1:]):.4f}")
    check("P2 ratio > 100x at 10000", cor[10000] / ind[10000] > 100, f"{cor[10000]/ind[10000]:.0f}x")

    print("-- P3 1-in-100 capital per policy as a multiple of mean claim rate")
    ratios_ind, ratios_cor = {}, {}
    for n in (100, 1000, 3000, 10000):
        ratios_ind[n] = quantile_independent(n, 0.99) / (n * P)
        ratios_cor[n] = quantile_common_shock(n, 0.99) / (n * P)
        print(f"     n={n:>6}  independent={ratios_ind[n]:.2f}x  correlated={ratios_cor[n]:.2f}x")
    check("P3 independent <= 1.20x at 10000", ratios_ind[10000] <= 1.20, f"{ratios_ind[10000]:.2f}x")
    check("P3 correlated >= 10x for n>=1000", all(ratios_cor[n] >= 10 for n in (1000, 3000, 10000)),
          f"min={min(ratios_cor[n] for n in (1000,3000,10000)):.1f}x")

    print("-- P4 BREAK: catastrophe chance 0.5% sits below the 1-in-100 target")
    q2 = 0.005
    r99 = quantile_common_shock(10000, 0.99, q=q2) / (10000 * P)
    rr = ruin_common_shock(10000, q=q2)
    print(f"     99% quantile = {r99:.2f}x mean, ruin probability = {rr:.4f}")
    check("P4 quantile looks safe", r99 <= 1.2, f"{r99:.2f}x")
    check("P4 ruin still >= 0.004", rr >= 0.004, f"{rr:.4f}")

    print("-- P5 fix (as predicted before run 1): same 2000 policies, m=1 vs 10 vs 100 zones")
    z = {}
    for m in (1, 10, 100):
        z[m] = ruin_zones(2000, m)
        print(f"     m={m:>4}  ruin={z[m]:.2e}")
    check("P5 m=100 at least 10x lower than m=1", z[100] * 10 <= z[1],
          f"m=1 {z[1]:.3f} -> m=100 {z[100]:.3f}")

    print("-- P5b (post-hoc, added after run 1 refuted P5): ruin ~ P(Binomial(m,q) >= zones needed), n=10000")
    zz = {}
    for m in (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000):
        zz[m] = ruin_zones(10000, m)
        kneed = zones_needed(m)
        approx = binom_tail_ge(m, kneed, Q)
        print(f"     m={m:>5} need>={kneed:>3} cat zones  exact ruin={zz[m]:.2e}  noise-free approx={approx:.2e}")
    check("P5b spreading over few zones is WORSE than one zone", zz[10] > zz[1] and zz[5] > zz[1],
          f"m=1 {zz[1]:.3f}, m=5 {zz[5]:.3f}, m=10 {zz[10]:.3f}")
    check("P5b many zones beat one zone by >= 10x", zz[1000] * 10 <= zz[1], f"m=1000 {zz[1000]:.1e}")

    print("-- P6 log-utility buyer (Bernoulli) max premium")
    w1 = log_utility_max_premium(20_000)
    w2 = log_utility_max_premium(1_000_000)
    print(f"     wealth 20,000 pays up to {w1:.1f}; wealth 1,000,000 pays up to {w2:.1f}; fair=200, loaded=260")
    check("P6 modest-wealth buyer pays > loaded", w1 > 260, f"{w1:.1f}")
    check("P6 rich buyer refuses loaded", w2 < 260 and w2 > 200, f"{w2:.1f}")

    print("-- P7 deductible vs one-month reserve (4,000)")
    rows = deductible_table(4000)
    best = max((r for r in rows if r[3]), key=lambda r: r[0])
    for d, prem, cut, fits in rows:
        print(f"     deductible={d:>5} premium={prem:7.1f} saving={cut*100:5.1f}% fits_reserve={fits}")
    check("P7 largest fitting deductible tested is 2500", best[0] == 2500, f"{best[0]}")
    # 5000 > reserve of 4000 -> fails; 2500 saving vs zero deductible
    check("P7 saving 25%", abs(best[2] - 0.25) < 1e-9, f"{best[2]*100:.1f}%")

    allok = all(ok)
    print(f"RESULT: {'PASS' if allok else 'FAIL'} {sum(ok)}/{len(ok)} checks (FAIL = prediction P5 refuted, rest held); "
          f"n=10000 ruin independent={ind[10000]:.1e} vs correlated={cor[10000]:.4f}; "
          f"99% capital {ratios_ind[10000]:.2f}x vs {ratios_cor[10000]:.1f}x; zones n=2000 m=1->100 ruin {z[1]:.3f}->{z[100]:.3f}, n=10000 m=1/10/1000 {zz[1]:.3f}/{zz[10]:.3f}/{zz[1000]:.1e}")


if __name__ == "__main__":
    main()
