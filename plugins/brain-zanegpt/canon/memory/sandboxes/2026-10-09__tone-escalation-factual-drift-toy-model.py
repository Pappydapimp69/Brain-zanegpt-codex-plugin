#!/usr/bin/env python3
"""Toy model of factual drift under a repeated tone-escalation loop.

THIS IS A MODEL, NOT A MEASUREMENT OF ANY REAL SYSTEM. Every number below is
produced by rules written in this file (a leak coefficient, a dependency
chain, a tolerance). It shows what follows IF tone pressure leaks into claim
strength with those rules; it says nothing about how often that happens in
any real conversation. No external source was fetched or cited by this run.

Kernel under test: ideas:PERSUASION/long-conversation-drift/
  chasing-a-tonal-target-produces-incidental-factual-drift/
  correct-within-the-turn-that-introduces-it
Siblings exercised: a-bundled-request-should-be-split-not-averaged
  (policy "averaged" vs "split"), whole-artifact-rewrite-converges-faster-
  than-local-patching... (policy "local" vs "sweep").

PREDICTION (written before the first run; each item could come out wrong):
 P1 no-check, 24 escalation turns: distorted fraction at turn 24 >= 0.50,
    at turn 6 <= 0.10, mean excess strictly increasing every turn.
 P2 per-turn sweep ("split": full tone step, separate fact check inside the
    same turn): distorted fraction after every check == 0.0, tone achieved ==
    24. Delayed sweep every 8 turns: peak distorted fraction >= 0.30.
 P3 with a dependency chain (claims built on earlier claims), delayed-8 total
    edits / per-turn total edits >= 1.3 ("unwinding"). BREAK: with no
    dependencies the ratio is < 1.0 (delaying is NOT costlier).
 P4 local-only check (only the one complained-about section): that section
    stays clean, but the other sections end within 0.10 of the no-check
    fraction.
 P5 "averaged" (halve the tone step, no fact check): tone achieved == 12
    (half), yet final distorted fraction >= 0.10 (still drifts).
 P6 negative controls: leak=0 -> 0 drift in every policy; flat tone (step 0)
    -> 0 drift; oscillating tone (+1,-1) -> final distorted fraction <= 0.10.
    BREAK: if 25% of claims have no checkable source, the per-turn sweep
    leaves final distorted fraction >= 0.15 (checking cannot fix what it
    cannot check).
"""

N_SEC, PER_SEC = 8, 5
N = N_SEC * PER_SEC
TOL = 1.0
CAP = 6.0
T = 24


def susceptibility(n, seed=7):
    # fixed-seed LCG, values in [0.3, 1.0]
    s, out = seed, []
    for _ in range(n):
        s = (1103515245 * s + 12345) % (2 ** 31)
        out.append(0.3 + 0.7 * (s % 1000) / 999.0)
    return out


def parent(i, dep):
    return i - 1 if dep and i % PER_SEC != 0 else None


def run(policy, leak=0.15, inh=0.10, dep=True, steps=None, k=8,
        unverifiable=False, local_sec=0):
    """Returns dict of per-turn series and totals."""
    if steps is None:
        steps = [1.0] * T
    sus = susceptibility(N)
    e = [0.0] * N
    taint = [False] * N
    edits = 0
    tone = 0.0
    frac_after, mean_after, peak = [], [], 0.0
    sec_frac_other = []
    checkable = [not (unverifiable and i % 4 == 3) for i in range(N)]
    for t in range(1, len(steps) + 1):
        d = steps[t - 1]
        if policy == "averaged":
            d = d * 0.5
        tone += abs(d) if d > 0 else 0.0
        prev = e[:]
        for i in range(N):
            p = parent(i, dep)
            inherited = inh * prev[p] if p is not None else 0.0
            if p is not None and abs(prev[p]) > TOL:
                taint[i] = True
            v = prev[i] + leak * d * sus[i] + inherited
            e[i] = max(-CAP, min(CAP, v))
        # check phase
        if policy in ("sweep", "averaged_check"):
            scope = range(N)
        elif policy == "delayed":
            scope = range(N) if t % k == 0 else []
        elif policy == "local":
            scope = range(local_sec * PER_SEC, (local_sec + 1) * PER_SEC)
        else:
            scope = []
        for i in scope:
            if checkable[i] and (abs(e[i]) > TOL or taint[i]):
                edits += 1
                e[i] = 0.0
                taint[i] = False
        dist = sum(1 for x in e if abs(x) > TOL)
        frac_after.append(dist / N)
        mean_after.append(sum(abs(x) for x in e) / N)
        peak = max(peak, dist / N)
        o = [x for j, x in enumerate(e) if j // PER_SEC != local_sec]
        sec_frac_other.append(sum(1 for x in o if abs(x) > TOL) / len(o))
        # peak measured BEFORE check for delayed policies
    return dict(frac=frac_after, mean=mean_after, edits=edits, tone=tone,
                other=sec_frac_other, e=e)


def run_peak_precheck(policy, **kw):
    """Peak distorted fraction as a reader would see it between checks
    (i.e. before the check of that turn runs)."""
    r_none = run("none", **kw)
    if policy == "none":
        return max(r_none["frac"])
    # replay with check disabled in the turn but state carried: emulate by
    # measuring state at turn end before check using a manual loop.
    return None


def peak_seen(policy, k=8, **kw):
    # distorted fraction visible at the end of each turn BEFORE that turn's
    # check, maximised over turns (what the reader sees going into the check)
    steps = kw.pop("steps", None) or [1.0] * T
    leak = kw.get("leak", 0.15)
    inh = kw.get("inh", 0.10)
    dep = kw.get("dep", True)
    sus = susceptibility(N)
    e = [0.0] * N
    taint = [False] * N
    best = 0.0
    for t in range(1, len(steps) + 1):
        d = steps[t - 1]
        prev = e[:]
        for i in range(N):
            p = parent(i, dep)
            inherited = inh * prev[p] if p is not None else 0.0
            if p is not None and abs(prev[p]) > TOL:
                taint[i] = True
            e[i] = max(-CAP, min(CAP, prev[i] + leak * d * sus[i] + inherited))
        best = max(best, sum(1 for x in e if abs(x) > TOL) / N)
        if (policy == "sweep") or (policy == "delayed" and t % k == 0):
            for i in range(N):
                if abs(e[i]) > TOL or taint[i]:
                    e[i] = 0.0
                    taint[i] = False
    return best


def main():
    checks = []

    def ck(name, ok, detail):
        checks.append(ok)
        print(("  ok   " if ok else "  FAIL ") + name + " :: " + detail)

    print("MODEL ONLY - not a measurement of any real system")
    # S1 baseline
    A = run("none")
    print("S1 no-check: frac@6=%.3f frac@24=%.3f mean@24=%.3f"
          % (A["frac"][5], A["frac"][-1], A["mean"][-1]))
    inc = all(A["mean"][i] < A["mean"][i + 1] for i in range(T - 1))
    ck("P1", A["frac"][-1] >= 0.50 and A["frac"][5] <= 0.10 and inc,
       "frac@24=%.3f (>=.50) frac@6=%.3f (<=.10) strictly-increasing=%s"
       % (A["frac"][-1], A["frac"][5], inc))
    # S2 sweep per turn vs delayed
    B = run("sweep")
    C = run("delayed", k=8)
    pkC = peak_seen("delayed", k=8)
    pkB = peak_seen("sweep")
    print("S2 sweep: max frac after check=%.3f edits=%d tone=%.0f ; "
          "delayed8: peak seen=%.3f edits=%d ; sweep peak seen=%.3f"
          % (max(B["frac"]), B["edits"], B["tone"], pkC and pkC, C["edits"], pkB))
    ck("P2", max(B["frac"]) == 0.0 and B["tone"] == 24 and pkC >= 0.30,
       "sweep max=%.3f tone=%.0f delayed peak=%.3f" % (max(B["frac"]), B["tone"], pkC))
    L0 = run("local", local_sec=0)
    ratio = C["edits"] / B["edits"] if B["edits"] else float("inf")
    Bn = run("sweep", dep=False, inh=0.0)
    Cn = run("delayed", k=8, dep=False, inh=0.0)
    rnd = Cn["edits"] / Bn["edits"] if Bn["edits"] else float("inf")
    print("S3 edits dep: delayed8=%d sweep=%d ratio=%.2f | no-dep (BREAK): "
          "delayed8=%d sweep=%d ratio=%.2f"
          % (C["edits"], B["edits"], ratio, Cn["edits"], Bn["edits"], rnd))
    # POST-HOC (added after the first run showed P3-dep failing; NOT a
    # prediction and not part of the RESULT): exposure = distorted claim-turns
    # left standing after each turn's check, i.e. wrongness a reader sees.
    for nm, r in (("none", A), ("delayed8", C), ("sweep", B), ("local", L0)):
        print("S3b post-hoc exposure %-8s = %4.0f claim-turns (edits %d)"
              % (nm, sum(f * N for f in r["frac"]), r["edits"]))
    ck("P3-dep", ratio >= 1.3, "ratio with deps=%.2f (>=1.3)" % ratio)
    ck("P3-break", rnd < 1.0, "ratio without deps=%.2f (<1.0)" % rnd)
    # S4 local
    L = run("local", local_sec=0)
    gap = abs(L["other"][-1] - A["frac"][-1])
    sec0_clean = all(x == 0.0 for x in [0.0])  # placeholder replaced below
    sus = None
    # section 0 distorted count: replay state
    sec0 = [L["e"][i] for i in range(PER_SEC)]
    sec0_ok = all(abs(x) <= TOL for x in sec0)
    print("S4 local-only: sec0 max|e|=%.3f; other-sections frac@24=%.3f vs "
          "no-check %.3f (gap %.3f)" % (max(abs(x) for x in sec0), L["other"][-1],
                                       A["frac"][-1], gap))
    ck("P4", sec0_ok and gap <= 0.10, "sec0 clean=%s gap=%.3f" % (sec0_ok, gap))
    # S5 averaged
    E = run("averaged")
    print("S5 averaged: tone=%.0f frac@24=%.3f mean@24=%.3f"
          % (E["tone"], E["frac"][-1], E["mean"][-1]))
    ck("P5", E["tone"] == 12 and E["frac"][-1] >= 0.10,
       "tone=%.0f (==12) frac@24=%.3f (>=.10)" % (E["tone"], E["frac"][-1]))
    # S6 negative controls
    z = [run(p, leak=0.0)["frac"][-1] for p in ("none", "sweep", "delayed", "local")]
    zd = [run(p, steps=[0.0] * T)["frac"][-1] for p in ("none", "sweep", "delayed", "local")]
    osc = run("none", steps=[1.0 if i % 2 == 0 else -1.0 for i in range(T)])
    z_edits = run("sweep", leak=0.0)["edits"]
    print("S6 controls: leak0 finals=%s (sweep edits %d) ; flat finals=%s ; "
          "oscillating no-check final=%.3f" % (z, z_edits, zd, osc["frac"][-1]))
    ck("P6-leak0", all(x == 0.0 for x in z) and z_edits == 0, "finals=%s" % z)
    ck("P6-flat", all(x == 0.0 for x in zd), "finals=%s" % zd)
    ck("P6-osc", osc["frac"][-1] <= 0.10, "final=%.3f (<=.10)" % osc["frac"][-1])
    U = run("sweep", unverifiable=True)
    print("S7 BREAK sweep with 25%% uncheckable claims: final frac=%.3f" % U["frac"][-1])
    ck("P6-break", U["frac"][-1] >= 0.15, "final=%.3f (>=.15)" % U["frac"][-1])

    ok = all(checks)
    print("RESULT: %s %d/%d predicted items held (model only; no real-system measurement)"
          % ("PASS" if ok else "FAIL", sum(checks), len(checks)))


if __name__ == "__main__":
    main()
