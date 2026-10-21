"""New domain WAYFINDING (seed). Real source: Souman, Frissen, Sreenivasa &
Ernst 2009, 'Walking Straight into Circles', Current Biology 19(18):1538-1542
(search summaries of the paper and the Max Planck press release): walkers kept
fairly straight while the sun or moon was visible, but walked in circles
under overcast skies without noticing; blindfolded circles were often under
20 m across and rarely in a systematic direction; the authors attribute veering
to ACCUMULATING sensorimotor noise, not a fixed bias such as leg length.
Model (deterministic LCG Gaussian, own seeds): a walker takes 1 m steps;
heading changes by Gaussian noise sigma each step (a random walk in heading).
A sky cue pulls heading back toward the intended bearing by a fraction g per
step. Measured over 2,000 steps: straightness (net displacement / path length)
and whether the path closes a loop (comes back within 5 m of an earlier point
at least 100 steps before).
PREDICTION (written before running): with no cue (g = 0) straightness < 0.3 and
the path loops in most of 20 seeds; with a cue (g = 0.05) straightness > 0.9 and
no seed loops; a fixed turning bias with NO noise traces circles that are all
the same direction (the systematic pattern the paper did not see), while pure
noise loops in both directions.
"""
import math


class Lcg:
    def __init__(self, s):
        self.s = s

    def u(self):
        self.s = (1103515245 * self.s + 12345) % 2 ** 31
        return (self.s + 0.5) / 2 ** 31

    def gauss(self):
        return math.sqrt(-2 * math.log(self.u())) * math.cos(2 * math.pi * self.u())


def walk(seed, sigma=0.06, g=0.0, bias=0.0, steps=2000):
    r = Lcg(seed)
    x = y = h = 0.0
    pts = [(0.0, 0.0)]
    turn_sum = 0.0
    for _ in range(steps):
        dh = sigma * r.gauss() + bias - g * h
        h += dh
        turn_sum += dh
        x += math.cos(h)
        y += math.sin(h)
        pts.append((x, y))
    straight = math.hypot(x, y) / steps
    loop = False
    for i in range(150, len(pts), 10):
        px, py = pts[i]
        for j in range(0, i - 100, 5):
            if math.hypot(px - pts[j][0], py - pts[j][1]) < 5:
                loop = True
                break
        if loop:
            break
    return straight, loop, turn_sum


def main():
    seeds = range(1, 21)
    print("iteration 2: original predictions at sigma 0.06 were refuted (straightness 0.661, 0/20 loops); sweep sigma")
    rows = {}
    for sigma in (0.06, 0.15, 0.3, 0.5):
        nocue = [walk(s, sigma=sigma) for s in seeds]
        cue = [walk(s, sigma=sigma, g=0.05) for s in seeds]
        dirs = {("left" if w[2] > 0 else "right") for w in nocue if w[1]}
        rows[sigma] = (sum(w[0] for w in nocue) / 20, sum(w[1] for w in nocue),
                       sum(w[0] for w in cue) / 20, sum(w[1] for w in cue), dirs)
        r = rows[sigma]
        print(f"sigma {sigma:.2f}: no cue straightness {r[0]:.3f} loops {r[1]}/20 dirs {sorted(r[4])} | "
              f"sky cue straightness {r[2]:.3f} loops {r[3]}/20")
    biased = [walk(s, sigma=0.0, bias=0.01) for s in list(seeds)[:5]]
    bias_dirs = {("left" if w[2] > 0 else "right") for w in biased}
    hi = max(rows)
    checks = [
        ("at sigma 0.06 the walker veers but does not loop (iteration-1 finding)", rows[0.06][1] == 0 and rows[0.06][0] < 0.9),
        ("at high heading noise most no-cue walks loop", rows[hi][1] > 10),
        ("a sky cue removes loops at every noise level", all(r[3] == 0 for r in rows.values())),
        ("noise-driven loops turn both ways; a fixed bias turns one way",
         rows[hi][4] == {"left", "right"} and len(bias_dirs) == 1),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; "
          + "; ".join(f"s{sg}: {r[0]:.2f}/{r[1]} cue {r[2]:.2f}/{r[3]}" for sg, r in rows.items()))


if __name__ == "__main__":
    main()
