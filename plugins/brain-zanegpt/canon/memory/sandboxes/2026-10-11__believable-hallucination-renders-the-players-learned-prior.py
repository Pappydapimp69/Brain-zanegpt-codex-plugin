"""Loop 3 sandbox: predictive-processing view of hallucination (perception =
prior x evidence; hallucinations arise when priors outweigh weak evidence;
Powers, Mathys & Corlett 2017 conditioned hallucinations) used as an ART STYLE.
Which phantom is believed: one placed where the player has LEARNED things
appear, or one placed at random?
Exact Bayes, no RNG. A map has J junctions and K open stretches. Real pylons
stand at junctions with rate q (the world's regularity) and on open stretches
with rate 0.02. The player has learned q. A phantom pylon is shown either at a
junction (PRIOR-SHAPED) or on an open stretch (RANDOM). The player sees a pylon
with a noisy cue that it is real (likelihood ratio L for real vs phantom).
Belief = P(real | seen here), using the learned location prior.
"""


def belief(prior_real, lr):
    odds = prior_real / (1 - prior_real) * lr
    return odds / (1 + odds)


def main():
    lr = 1.0          # the phantom renders exactly like a real one (no visual tell)
    rows = {}
    for q in (0.8, 0.5, 0.1):
        prior_junction = q
        prior_open = 0.02
        rows[q] = (belief(prior_junction, lr), belief(prior_open, lr))
        print(f"world regularity q={q:.2f}: phantom at a junction believed {rows[q][0]:.3f}, "
              f"phantom on an open stretch believed {rows[q][1]:.3f}  (x{rows[q][0] / rows[q][1]:.1f})")
    weak_tell = (belief(0.8, 0.5), belief(0.02, 0.5))
    print(f"with a weak visual tell (LR 0.5): junction {weak_tell[0]:.3f}, open {weak_tell[1]:.3f}")
    checks = [
        (f"a prior-shaped phantom is believed >= 10x more than a random one at q=0.8 (x{rows[0.8][0] / rows[0.8][1]:.1f})",
         rows[0.8][0] / rows[0.8][1] >= 10),
        ("believability tracks the world's regularity (q 0.8 > 0.5 > 0.1)", rows[0.8][0] > rows[0.5][0] > rows[0.1][0]),
        ("break case: when the world has no regularity at junctions (q=0.1) the advantage drops below 6x",
         rows[0.1][0] / rows[0.1][1] < 6),
        ("a weak visual tell barely dents a prior-shaped phantom (still >= 0.6)", weak_tell[0] >= 0.6),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; believed junction/open "
          + "; ".join(f"q{q}: {a:.3f}/{b:.3f}" for q, (a, b) in rows.items()) + f"; weak tell {weak_tell[0]:.3f}")


if __name__ == "__main__":
    main()
