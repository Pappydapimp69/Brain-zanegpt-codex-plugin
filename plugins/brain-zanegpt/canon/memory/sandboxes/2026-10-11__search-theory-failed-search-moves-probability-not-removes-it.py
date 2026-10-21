"""Sandbox (new domain SEARCH-THEORY, seed). Bayesian search planning (Koopman;
Stone, used for the AF447 wreck in 2011): after an unsuccessful search of a cell
with probability of detection POD, its probability becomes p(1-POD), renormalised;
search next where p x POD is highest. Applied to SEVEN's night rescue search
(seven E22: hidden position plus an unnamed call bearing; E31: tuned noise).
Exact, no RNG. Ring of 24 sectors; prior over the person's sector = discretised
normal around the heard bearing (sigma). Each night the searcher covers H
sectors; finding needs the right sector AND detection (true POD, darkness).
Policies over 3 nights:
  REPEAT   search the H sectors nearest the bearing every night
  BAYES    update with the TRUE POD, then take the top-H by p x POD
  OVERSURE plan as if POD = 1 (a searched sector is 'cleared'), true POD lower
"""
import math

S, H = 24, 4


def prior(sigma):
    def cdf(x):
        return 0.5 * (1 + math.erf(x / (sigma * math.sqrt(2))))
    raw = [cdf(k + 0.5) - cdf(k - 0.5) for k in range(-12, 12)]
    t = sum(raw)
    p = {}
    for k, v in zip(range(-12, 12), raw):
        p[k % S] = p.get(k % S, 0) + v / t
    return p


def sdist(a, b):
    d = abs(a - b) % S
    return min(d, S - d)


def run(policy, sigma, pod, nights=3):
    truth = prior(sigma)          # where the person really is
    belief = dict(truth)          # the planner's map
    alive = dict(truth)           # P(person in sector i and not yet found)
    found = 0.0
    near = sorted(range(S), key=lambda s: (sdist(s, 0), s))[:H]
    plan_pod = 1.0 if policy == "oversure" else pod
    for _ in range(nights):
        if policy == "repeat":
            block = near
        else:
            block = sorted(range(S), key=lambda s: (-belief[s] * plan_pod, sdist(s, 0), s))[:H]
        for s in block:
            found += alive[s] * pod
            alive[s] *= 1 - pod
        if policy != "repeat":
            for s in block:
                belief[s] *= 1 - plan_pod
            t = sum(belief.values()) or 1.0
            belief = {k: v / t for k, v in belief.items()}
    return found


def main():
    rows = {}
    for sigma in (1.5, 3.25):
        for pod in (0.5, 0.8, 0.98):
            r = {p: run(p, sigma, pod) for p in ("repeat", "bayes", "oversure")}
            rows[(sigma, pod)] = r
            print(f"sigma {sigma:4.2f} POD {pod:.2f}: 3-night find  repeat {r['repeat']:.3f}  "
                  f"bayes {r['bayes']:.3f}  oversure {r['oversure']:.3f}")
    checks = [
        ("Bayes never does worse than repeating the same block",
         all(r["bayes"] >= r["repeat"] - 1e-12 for r in rows.values())),
        ("planning as if POD = 1 loses to Bayes when true POD is 0.5 (both noise levels)",
         all(rows[(sg, 0.5)]["oversure"] < rows[(sg, 0.5)]["bayes"] for sg in (1.5, 3.25))),
        ("at low noise and POD 0.5, repeating the block is near-optimal (within 0.02 of Bayes)",
         rows[(1.5, 0.5)]["bayes"] - rows[(1.5, 0.5)]["repeat"] <= 0.02),
        ("break case: at POD 0.98 overconfidence costs almost nothing (within 0.01 of Bayes)",
         all(abs(rows[(sg, 0.98)]["oversure"] - rows[(sg, 0.98)]["bayes"]) <= 0.01 for sg in (1.5, 3.25))),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; "
          + "; ".join(f"s{sg}/pod{pd}: rep {r['repeat']:.3f} bay {r['bayes']:.3f} over {r['oversure']:.3f}"
                      for (sg, pd), r in rows.items()))


if __name__ == "__main__":
    main()
