"""Sandbox: intermediate refusal-disclosure designs for a guard that defends a secret limit.
Measures legitimate repair cost and secret-recovery probes for each design.
Stdlib only, deterministic, no RNG, no timing.

World
  Guard refuses an amount v when v > T, T a secret in 32..127 (floor 32 is published).
  Legit actor wants amount v (already refused once) and tolerates utility a/v >= 0.6
  (prefers >= 0.85); it uses only what the message says plus the public design spec.
  Prober: greedy-halving oracle over every v in 0..255; counts probes until T is isolated.
Designs (message sent on refusal)
  NOVAL   rule + remedy, no operand            FULL    matched value and limit
  ABS(w)  which w-wide bucket holds T          LOG     lower edge of a x1.25 geometric bucket
  REL(w)  excess v-T rounded up to w           NEAR    exact T only if overshoot <= 25%
  CLAMP   execute min(v,T) in place            CLAMPQ  execute floor16(T) in place
  RATE    exact (or coarse) operand for the first K refusals per identity
  FLOOR   hint: split into chunks of the public floor (no operand)
Extra worlds: two-field guard (public field + secret field), clean / derived / shared-pool;
  cumulative guard vs per-action guard for the chunk hint.
"""
import math

DOM = list(range(32, 128))
VS = list(range(0, 256))
FLOORM0 = 32
THETA, U_OK = 0.6, 0.85
STEP = 0.05   # legit actor's descent ladder step (sensitivity-swept in main)


# ------------------------------------------------------------ message functions
# step(T, v, s) -> (response, disclosed_flag).  Stateless; rate limiting wraps it.
def r_noval(T, v):
    return ("refused", "limit-rule", "reduce"), False

def d_full(T, v):
    return ("refused", "limit-rule", "limit", T), True

def d_abs(w):
    def f(T, v):
        return ("refused", "limit-rule", "bucket", w, (T - FLOORM0) // w), True
    return f

def _edges():
    e, out = FLOORM0, []
    while e < 128:
        out.append(e)
        e = max(e + 1, math.ceil(e * 1.25))
    return out
EDGES = _edges()

def d_log(T, v):
    lo = max(e for e in EDGES if e <= T)
    return ("refused", "limit-rule", "floor-edge", lo), True

def d_rel(w):
    def f(T, v):
        return ("refused", "limit-rule", "reduce-by-at-least", w * math.ceil((v - T) / w)), True
    return f

def d_near(delta):
    def f(T, v):
        if v <= int(T * (1 + delta)):
            return ("refused", "limit-rule", "limit", T), True
        return ("refused", "limit-rule", "reduce"), False
    return f


class Design:
    def __init__(self, name, refuse_fn, clamp=None, rate_k=None, sybil=False, chunk=False):
        self.name, self.refuse_fn, self.clamp = name, refuse_fn, clamp
        self.rate_k, self.sybil, self.chunk = rate_k, sybil, chunk

    def step(self, T, v, s):
        """-> (response, new_state)."""
        if v <= T:
            return ("ok",), s
        if self.clamp:
            return ("clamped", (T // self.clamp) * self.clamp if self.clamp > 1 else T), s
        resp, disclosed = self.refuse_fn(T, v)
        if self.rate_k is not None and disclosed:
            if s < self.rate_k:
                return resp, (0 if self.sybil else s + 1)
            return r_noval(T, v)[0], s
        return resp, s


def mk_designs():
    D = {}
    D["NOVAL"] = Design("NOVAL", r_noval)
    D["FULL"] = Design("FULL", d_full)
    for w in (4, 8, 16, 32):
        D["ABS%d" % w] = Design("ABS%d" % w, d_abs(w))
    D["LOG1.25"] = Design("LOG1.25", d_log)
    D["REL16"] = Design("REL16", d_rel(16))
    D["NEAR.25"] = Design("NEAR.25", d_near(0.25))
    D["CLAMP"] = Design("CLAMP", None, clamp=1)
    D["CLAMPQ16"] = Design("CLAMPQ16", None, clamp=16)
    D["RATE2+FULL"] = Design("RATE2+FULL", d_full, rate_k=2)
    D["RATE2+FULL(sybil)"] = Design("RATE2+FULL(sybil)", d_full, rate_k=2, sybil=True)
    D["RATE0"] = Design("RATE0", d_full, rate_k=0)
    D["RATE2+ABS16"] = Design("RATE2+ABS16", d_abs(16), rate_k=2)
    D["RATE2+ABS16(sybil)"] = Design("RATE2+ABS16(sybil)", d_abs(16), rate_k=2, sybil=True)
    D["FLOOR"] = Design("FLOOR", r_noval, chunk=True)
    return D


# ------------------------------------------------------------ prober
def split(design, belief, v):
    groups = {}
    for c, s in belief:
        resp, s2 = design.step(c, v, s)
        groups.setdefault(resp, []).append((c, s2))
    return groups

_memo = {}

def choose(design, belief):
    key = (design.name, belief)
    if key in _memo:
        return _memo[key]
    best = None
    for v in VS:
        g = split(design, belief, v)
        score = (max(len(x) for x in g.values()), -len(g), v)
        if best is None or score < best[0]:
            best = (score, v)
    _memo[key] = best[1]
    return best[1]

def probe_run(design, T):
    belief = tuple((c, 0) for c in DOM)
    left = []
    n = 0
    while len({c for c, _ in belief}) > 1 and n < 30:
        v = choose(design, belief)
        resp, _ = design.step(T, v, dict(belief)[T])
        belief = tuple(split(design, belief, v)[resp])
        n += 1
        left.append(len({c for c, _ in belief}))
    return n, left

def prober_stats(design):
    ns, left1 = [], []
    for T in DOM:
        n, left = probe_run(design, T)
        ns.append(n)
        left1.append(left[0] if left else 1)
    return max(ns), sum(ns) / len(ns), sum(left1) / len(left1)


# ------------------------------------------------------------ legit actor
def ladder(v):
    n = int(round((1 - THETA) / STEP)) + 1
    return sorted({max(math.ceil(v * (1 - STEP * k)), 1) for k in range(0, n)}, reverse=True)

def repair(design, T, v, s0=0):
    """Repair a refused request.  Returns dict(calls, escalated, utility, unwanted)."""
    floor_amt = math.ceil(THETA * v)
    belief = tuple((c, s0) for c in DOM)
    resp, s_true = design.step(T, v, s0)
    calls = 1
    if resp[0] == "clamped":
        u = resp[1] / v
        return dict(calls=1, escalated=False, utility=u, unwanted=u < THETA, state=s_true)
    belief = tuple(split(design, belief, v)[resp])
    if design.chunk:
        return chunk_repair(T, v, calls, s_true, cumulative=False)
    while calls < 25:
        cands = [c for c, _ in belief]
        Tlo, Thi = min(cands), max(cands)
        under = [a for a in ladder(v) if a <= Thi]
        a_u = under[0] if under else 0
        cert = min(v, Tlo)
        if cert >= math.ceil(U_OK * v) or cert >= a_u:
            a = cert
        else:
            a = a_u
        if a < floor_amt:
            return dict(calls=calls, escalated=True, utility=None, unwanted=False, state=s_true)
        resp, s_true = design.step(T, a, s_true)
        calls += 1
        if resp[0] == "ok":
            return dict(calls=calls, escalated=False, utility=a / v, unwanted=False, state=s_true)
        belief = tuple(split(design, belief, a)[resp])
    return dict(calls=calls, escalated=True, utility=None, unwanted=False, state=s_true)

def chunk_repair(T, v, calls, s_true, cumulative):
    """Hint: split into chunks of the public floor.  Per-action guard: every chunk passes.
    Cumulative guard (window sum must stay <= T): chunks pass until the sum crosses T."""
    chunks = []
    left = v
    while left > 0:
        c = min(FLOORM0, left)
        chunks.append(c)
        left -= c
    delivered = 0
    for c in chunks:
        calls += 1
        if cumulative and delivered + c > T:
            return dict(calls=calls, escalated=True, utility=delivered / v, unwanted=False, state=s_true)
        delivered += c
    return dict(calls=calls, escalated=False, utility=1.0, unwanted=False, state=s_true)

def population(only=None):
    reqs = []
    for T in range(32, 128, 4):
        for f in (1.05, 1.15, 1.3, 1.8):
            v = max(T + 1, math.ceil(T * f))
            if v <= 255 and (only is None or (f in only)):
                reqs.append((T, v))
    return reqs

def legit_stats(design, window=1, only=None):
    reqs = population(only)
    calls = esc = unw = 0
    util = []
    waste = 0
    s = 0
    for i, (T, v) in enumerate(reqs):
        if window > 1 and i % window == 0:
            s = 0
        r = repair(design, T, v, s if window > 1 else 0)
        s = r["state"]
        calls += r["calls"]
        esc += r["escalated"]
        unw += r["unwanted"]
        if r["escalated"]:
            waste += r["calls"]
        if r["utility"] is not None and not r["escalated"]:
            util.append(r["utility"])
    n = len(reqs)
    return dict(calls=calls / n, esc=esc, unwanted=unw, util=sum(util) / len(util) if util else 0.0,
                waste=waste, n=n)


# ------------------------------------------------------------ two-field worlds
LA = 60

def two_field_resp(kind, T, req):
    a, b = req
    limA = LA if kind == "clean" else (T // 2 + 10 if kind == "derived" else None)
    if kind == "pool":
        if a + b > T:
            return ("refused", "pool-rule", "limit", T)
        return ("ok",)
    if a > limA:
        return ("refused", "public-rule", "limit", limA)          # operand allowed: field judged non-secret
    if b > T:
        return ("refused", "secret-rule", "reduce")                 # operand withheld
    return ("ok",)

def two_field_probes(kind):
    reqs = [(x, 0) for x in range(0, 256)] + [(0, x) for x in range(0, 256)]
    worst = 0
    ns = []
    memo = {}
    for T in DOM:
        cand = tuple(DOM)
        n = 0
        while len(cand) > 1 and n < 30:
            if cand not in memo:
                best = None
                for r in reqs:
                    g = {}
                    for c in cand:
                        g.setdefault(two_field_resp(kind, c, r), []).append(c)
                    sc = (max(len(x) for x in g.values()), -len(g), r)
                    if best is None or sc < best[0]:
                        best = (sc, r)
                memo[cand] = best[1]
            r = memo[cand]
            resp = two_field_resp(kind, T, r)
            cand = tuple(c for c in cand if two_field_resp(kind, c, r) == resp)
            n += 1
        ns.append(n)
    return max(ns), sum(ns) / len(ns)


def main():
    D = mk_designs()
    print("population: %d refused legit requests (T 32..127 step 4 x overshoot 1.05/1.15/1.3/1.8)" % len(population()))
    print("%-20s | legit: calls  esc waste unw util | prober: worst mean left@1" % "design")
    rows = {}
    for name, d in D.items():
        window = 4 if d.rate_k is not None else 1
        L = legit_stats(d, window)
        P = prober_stats(d)
        rows[name] = (L, P)
        tag = "  (legit col n/a: a legit actor does not mint identities)" if d.sybil else ""
        print("%-20s | %6.2f %4d %5d %3d %.2f | %5d %5.2f %6.1f%s" %
              (name, L["calls"], L["esc"], L["waste"], L["unwanted"], L["util"], P[0], P[1], P[2], tag))

    base_calls, base_p = rows["NOVAL"][0]["calls"], rows["NOVAL"][1][1]
    full_calls, full_p = rows["FULL"][0]["calls"], rows["FULL"][1][1]
    print("\nnormalised: benefit = share of FULL's call saving; leak = share of FULL's probe drop")
    frontier = {}
    for name, (L, P) in rows.items():
        ben = (base_calls - L["calls"]) / (base_calls - full_calls)
        leak = (base_p - P[1]) / (base_p - full_p)
        frontier[name] = (ben, leak)
        print("  %-20s benefit=%5.2f leak=%5.2f  benefit-per-leak=%s" %
              (name, ben, leak, ("%.2f" % (ben / leak)) if leak > 0.005 else "inf"))

    print("\ntwo-field guard (public field limit 60, secret field limit T): worst/mean probes")
    tf = {}
    for kind in ("clean", "derived", "pool"):
        tf[kind] = two_field_probes(kind)
        print("  %-8s worst=%d mean=%.2f" % ((kind,) + tf[kind]))
    # repair benefit on the non-secret half: request on public field costs 2 calls (FULL on A), secret field costs NOVAL
    ben_two = 0.5   # by construction: half the violations hit the public field (FULL cost), half the secret field (NOVAL cost)
    print("  clean split: repair benefit on a 50/50 mix of public/secret violations ~= %.2f of FULL's" % ben_two)

    print("\nchunk hint (FLOOR) vs cumulative guard")
    per = [chunk_repair(T, v, 1, 0, False) for T, v in population()]
    cum = [chunk_repair(T, v, 1, 0, True) for T, v in population()]
    chunk_stats = {
        "per_calls": sum(r["calls"] for r in per) / len(per),
        "per_util": sum(r["utility"] for r in per) / len(per),
        "cum_esc": sum(r["escalated"] for r in cum),
        "cum_util": sum(r["utility"] for r in cum) / len(cum),
        "cum_calls": sum(r["calls"] for r in cum) / len(cum),
    }
    print("  per-action guard: calls=%.2f utility=%.2f ; cumulative guard: calls=%.2f utility=%.2f escalated=%d/%d" %
          (chunk_stats["per_calls"], chunk_stats["per_util"], chunk_stats["cum_calls"], chunk_stats["cum_util"],
           chunk_stats["cum_esc"], len(cum)))

    # rate sweep: legit calls vs K, prober probes
    print("\nrate sweep (exact operand, window of 4 refused requests): K -> legit calls, prober worst")
    sweep = {}
    for K in (0, 1, 2, 4):
        d = Design("R%d" % K, d_full, rate_k=K)
        sweep[K] = (legit_stats(d, 4)["calls"], prober_stats(d)[0])
        print("  K=%d calls=%.2f prober_worst=%d" % ((K,) + sweep[K]))

    # ---- post-hoc scenarios (formed AFTER the first run; reported as H checks, not as predictions)
    global STEP
    print("\nsensitivity to the legit actor's ladder step: benefit/leak of ABS8, ABS16, LOG1.25, NEAR.25")
    sens = {}
    sens_util = {}
    for st in (0.05, 0.10, 0.20):
        STEP = st
        base = legit_stats(D["NOVAL"])["calls"]
        full = legit_stats(D["FULL"])["calls"]
        sens_util[st] = (legit_stats(D["NOVAL"])["util"], legit_stats(D["FULL"])["util"])
        sens[st] = {}
        for n in ("ABS8", "ABS16", "LOG1.25", "NEAR.25"):
            c = legit_stats(D[n])["calls"]
            sens[st][n] = ((base - c) / (base - full), frontier[n][1])
        print("  step=%.2f NOVAL=%.2f (util %.2f) FULL=%.2f (util %.2f)  %s" % (st, base, sens_util[st][0], full, sens_util[st][1],
              "  ".join("%s ben=%.2f leak=%.2f" % (n, b, l) for n, (b, l) in sens[st].items())))
    STEP = 0.05
    print("\nbenefit split: requests the guard could repair (overshoot <= 1.3x) vs hopeless (1.8x, utility < tolerance)")
    split_rows = {}
    for n in ("NOVAL", "FULL", "ABS8", "ABS16", "NEAR.25"):
        rep = legit_stats(D[n], only=(1.05, 1.15, 1.3))
        hop = legit_stats(D[n], only=(1.8,))
        split_rows[n] = (rep["calls"], hop["calls"])
        print("  %-8s calls on repairable=%.2f  calls on hopeless=%.2f" % (n, rep["calls"], hop["calls"]))
    belief = tuple((c, 0) for c in DOM)
    g = split(D["NEAR.25"], belief, 100)
    near_left = max(len(x) for x in g.values())
    print("NEAR.25: a refusal at v=100 carries NO operand, yet the candidates left = %d of %d (absence of disclosure is itself information)" % (near_left, len(DOM)))

    A = lambda n: rows[n]
    checks = []
    def chk(name, ok, val):
        checks.append((name, bool(ok), val))
    chk("P1 NOVAL prober worst==7", A("NOVAL")[1][0] == 7, A("NOVAL")[1][0])
    chk("P1 NOVAL calls>=4.5", A("NOVAL")[0]["calls"] >= 4.5, round(A("NOVAL")[0]["calls"], 2))
    chk("P2 FULL probes==1", A("FULL")[1][0] == 1, A("FULL")[1][0])
    chk("P2 FULL calls<=2.0", A("FULL")[0]["calls"] <= 2.0, round(A("FULL")[0]["calls"], 2))
    b16, l16 = frontier["ABS16"]
    chk("P3 ABS16 benefit>=0.75", b16 >= 0.75, round(b16, 2))
    chk("P3 ABS16 leak<=0.5", l16 <= 0.5, round(l16, 2))
    chk("P3 ABS16 leak>0 (not free)", l16 > 0.05, round(l16, 2))
    chk("P4 RATE2+FULL probes==1", A("RATE2+FULL")[1][0] == 1, A("RATE2+FULL")[1][0])
    chk("P4 RATE costs calls vs FULL", A("RATE2+FULL")[0]["calls"] > A("FULL")[0]["calls"], round(A("RATE2+FULL")[0]["calls"], 2))
    chk("P4 RATE2+ABS16 sybil == ABS16 probes", A("RATE2+ABS16(sybil)")[1][0] == A("ABS16")[1][0], (A("RATE2+ABS16(sybil)")[1][0], A("ABS16")[1][0]))
    bn, ln = frontier["NEAR.25"]
    chk("P5 NEAR benefit<=0.45", bn <= 0.45, round(bn, 2))
    chk("P5 NEAR leak>=0.25", ln >= 0.25, round(ln, 2))
    chk("P6 clean two-field == NOVAL leak", tf["clean"][0] == 7, tf["clean"][0])
    chk("P6 derived limit probes<=2", tf["derived"][0] <= 2, tf["derived"][0])
    chk("P6 pool probes==1", tf["pool"][0] == 1, tf["pool"][0])
    chk("P7 CLAMP probes==1 calls==1", A("CLAMP")[1][0] == 1 and abs(A("CLAMP")[0]["calls"] - 1.0) < 1e-9, (A("CLAMP")[1][0], A("CLAMP")[0]["calls"]))
    chk("P7 CLAMP unwanted>0", A("CLAMP")[0]["unwanted"] > 0, A("CLAMP")[0]["unwanted"])
    chk("P7 CLAMPQ16 probes == ABS16", A("CLAMPQ16")[1][0] == A("ABS16")[1][0], (A("CLAMPQ16")[1][0], A("ABS16")[1][0]))
    chk("P8 FLOOR probes == NOVAL", A("FLOOR")[1][0] == A("NOVAL")[1][0], A("FLOOR")[1][0])
    chk("P8 FLOOR calls < NOVAL", chunk_stats["per_calls"] < A("NOVAL")[0]["calls"], round(chunk_stats["per_calls"], 2))
    chk("P8 cumulative guard breaks chunking", chunk_stats["cum_esc"] > 0 and chunk_stats["cum_util"] < 1.0, (chunk_stats["cum_esc"], round(chunk_stats["cum_util"], 2)))
    # post-hoc checks
    chk("H1 coarse buckets benefit>leak at every ladder step", all(sens[st][n][0] > sens[st][n][1] for st in sens for n in ("ABS8", "ABS16", "LOG1.25")), {st: round(min(sens[st][n][0] - sens[st][n][1] for n in ("ABS8", "ABS16", "LOG1.25")), 2) for st in sens})
    chk("H2 NEAR undisclosed refusal still shrinks candidates", near_left < len(DOM), near_left)
    chk("H3 NOVAL wastes more calls on hopeless than FULL", split_rows["NOVAL"][1] > 3 * split_rows["FULL"][1], (round(split_rows["NOVAL"][1], 2), round(split_rows["FULL"][1], 2)))
    chk("H4 ABS8 benefit>=0.75 and leak<=0.5", frontier["ABS8"][0] >= 0.75 and frontier["ABS8"][1] <= 0.5, (round(frontier["ABS8"][0], 2), round(frontier["ABS8"][1], 2)))
    chk("H5 no design has benefit>=0.5 with leak==0", not any(b >= 0.5 and l < 0.02 for (b, l) in [frontier[n] for n in frontier if n not in ("FLOOR", "RATE0")]), "none")
    chk("H6 FLOOR hint: full utility, zero extra leak, but no call saving", chunk_stats["per_util"] == 1.0 and A("FLOOR")[1][0] == 7, (chunk_stats["per_util"], A("FLOOR")[1][0]))
    bad = [c for c in checks if not c[1]]
    for n, ok, v in checks:
        print("  check %-46s %s %s" % (n, "ok" if ok else "FAILED", v))
    if bad:
        print("RESULT: FAIL %d of %d checks refuted (pre-registered predictions: ABS16 benefit %.2f<0.75, NEAR benefit %.2f>0.45, FLOOR calls %.2f>=NOVAL %.2f): %s" %
              (len(bad), len(checks), b16, bn, chunk_stats["per_calls"], A("NOVAL")[0]["calls"], [b[0] for b in bad]))
    else:
        print("RESULT: PASS ABS16 coarse operand keeps %.2f of exact-operand repair benefit for %.2f of its leak; rate limit alone saves nothing; public-floor chunk hint repairs at %.2f calls with zero extra leak but only for per-action guards" %
              (b16, l16, chunk_stats["per_calls"]))

main()
