"""Loop 5 sandbox: hallucination VFX that flicker (lights stuttering, a world
'glitching') against the photosensitive-epilepsy rule used by WCAG 2.3.1 and
broadcast flash tests: no more than THREE flashes in ANY one-second period
(above the area/luminance thresholds).
Claim under test: keeping the AVERAGE flash rate under 3 per second is not
enough when flashes are jittered; the cap must hold in every sliding window.
Deterministic: flash start times come from an LCG (own seed), 60 s of effect.
  JITTER     exponential-ish gaps with mean 1/rate (irregular 'glitch' feel)
  CAPPED     same generator, but a flash is dropped if it would make 4 flashes
             within any 1.0 s window (look-back on accepted flashes)
  METRONOME  perfectly regular flashes at the same mean rate
"""
import math


class Lcg:
    def __init__(self, s):
        self.s = s

    def u(self):
        self.s = (1103515245 * self.s + 12345) % 2 ** 31
        return (self.s + 0.5) / 2 ** 31


def jitter_times(rate, secs, seed):
    r, t, out = Lcg(seed), 0.0, []
    while True:
        t += -math.log(r.u()) / rate
        if t >= secs:
            return out
        out.append(t)


def capped(times):
    acc = []
    for t in times:
        if len([a for a in acc if t - a < 1.0]) >= 3:
            continue
        acc.append(t)
    return acc


def worst_window(times):
    return max((sum(1 for u in times if t <= u < t + 1.0) for t in times), default=0)


def violating_seconds(times, secs):
    bad = 0
    for k in range(int(secs * 10)):
        t0 = k / 10
        if sum(1 for u in times if t0 <= u < t0 + 1.0) > 3:
            bad += 1
    return bad / (secs * 10)


def main():
    secs, rows = 60, {}
    for rate in (1.5, 2.0, 2.5):
        j = jitter_times(rate, secs, 2024)
        c = capped(j)
        m = [i / rate for i in range(1, int(secs * rate))]
        rows[rate] = (len(j) / secs, worst_window(j), violating_seconds(j, secs), len(c) / secs,
                      worst_window(c), worst_window(m))
        print(f"mean {rate:.1f}/s: jitter actual {rows[rate][0]:.2f}/s worst 1s window {rows[rate][1]} "
              f"(windows over 3: {rows[rate][2]:.3f}) | capped {rows[rate][3]:.2f}/s worst {rows[rate][4]} | "
              f"metronome worst {rows[rate][5]}")
    checks = [
        ("jittered flicker at a 2.5/s average breaks the 3-per-second rule in some window", rows[2.5][1] > 3),
        ("even a 1.5/s average breaks it when jittered (break case for 'stay well under the average')", rows[1.5][1] > 3),
        ("the window cap never exceeds 3 in any window at any rate", all(r[4] <= 3 for r in rows.values())),
        ("the cap keeps most of the flicker (>= 80% of flashes at 2.0/s)", rows[2.0][3] / rows[2.0][0] >= 0.8),
        ("a regular 2.5/s metronome stays within 3", rows[2.5][5] <= 3),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; worst windows jitter "
          + "/".join(str(rows[r][1]) for r in rows) + " capped " + "/".join(str(rows[r][4]) for r in rows)
          + f"; cap keeps {rows[2.0][3] / rows[2.0][0]:.2f} at 2.0/s")


if __name__ == "__main__":
    main()
