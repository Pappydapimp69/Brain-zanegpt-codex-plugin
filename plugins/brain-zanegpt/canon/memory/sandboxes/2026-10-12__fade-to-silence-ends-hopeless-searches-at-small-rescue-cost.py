"""Fair test of the OWNER'S fade decision (seven tension: floor the missing
member's call vs let it fade to silence, a time limit). E27 argued for a floor;
the owner chose fade. What does fading BUY?
Exact, no RNG. A player who goes out on every night a call is heard (the
natural play, since the call is the only cue) over 12 nights. Call chance per
night n: FADE 0.9*0.6^n; FLOOR max(0.9*0.6^n, 0.25). A search finds with p
(shallow 0.6, deep 0.1, hopeless 0.02: the member has drifted beyond reach).
Measured: P(rescue) and expected nights spent searching AFTER night 5 (late,
when a find is least likely and night risk accumulates).
PREDICTION (written before running): in the hopeless case fade cuts late search
nights by at least 70%; in the shallow case fade costs at most 0.02 of rescue
probability; in the deep case fade costs at least 0.10 of rescue probability
(the honest price of the owner's choice).
"""


def run(p, floored, nights=12):
    alive = 1.0          # P(not yet found)
    rescue = 0.0
    late = 0.0
    for n in range(nights):
        c = 0.9 * 0.6 ** n
        if floored:
            c = max(c, 0.25)
        go = alive * c
        if n >= 5:
            late += go
        rescue += go * p
        alive -= go * p
    return rescue, late


def main():
    rows = {}
    for name, p in (("shallow", 0.6), ("deep", 0.1), ("hopeless", 0.02)):
        rows[name] = (run(p, False), run(p, True))
        (rf, lf), (rl, ll) = rows[name]
        print(f"{name:8s}: rescue fade {rf:.3f} floor {rl:.3f} (cost {rl - rf:+.3f}); late search nights fade {lf:.3f} floor {ll:.3f}")
    hop = rows["hopeless"]
    cut = 1 - hop[0][1] / hop[1][1]
    checks = [
        (f"hopeless case: fade cuts late search nights >= 70% (got {cut:.0%})", cut >= 0.70),
        ("shallow case: fade costs <= 0.02 rescue probability", rows["shallow"][1][0] - rows["shallow"][0][0] <= 0.02),
        ("deep case: fade costs >= 0.10 rescue probability", rows["deep"][1][0] - rows["deep"][0][0] >= 0.10),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; "
          + "; ".join(f"{k}: rescue {v[0][0]:.3f}/{v[1][0]:.3f} late {v[0][1]:.3f}/{v[1][1]:.3f}" for k, v in rows.items())
          + " (fade/floor)")


if __name__ == "__main__":
    main()
