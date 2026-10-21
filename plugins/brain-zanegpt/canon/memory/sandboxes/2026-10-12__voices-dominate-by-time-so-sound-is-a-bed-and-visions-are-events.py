"""Loop (follow-up to the failed review of seven E62): 'how auditory is real
psychosis' depends on what is counted. E62 used prevalence (who EVER has each
kind, ~0.55); the reviewer's rebuild showed episode-rate weighting moves it
anywhere from 0.38 to 0.71. Count TIME instead.
Published inputs (checked earlier this session): prevalence auditory 0.59,
visual 0.27 (Waters 2014, PMC4141306); voice episodes typically last hours and
48% hear voices constantly (McCarthy-Jones 2014, PMC3885292); psychotic visions
last seconds to minutes (Waters 2014).
Exact, no RNG. Durations swept (ASSUMED within the published ranges): voice
episode 30, 60, 180 min; vision 0.25, 1, 5 min; episode rates per day equal
(1:1) or visions 4x as frequent (a conservative case for visuals).
Auditory share of hallucination TIME = pa*ra*Ta / (pa*ra*Ta + pv*rv*Tv).
"""
PA, PV = 0.59, 0.27


def time_share(ta, tv, ra=1.0, rv=1.0):
    a, v = PA * ra * ta, PV * rv * tv
    return a / (a + v)


def main():
    prevalence = PA / (PA + PV)
    print(f"prevalence share (E62-style, two modalities): {prevalence:.3f}")
    rows = {}
    for ta in (30, 60, 180):
        for tv in (0.25, 1, 5):
            for rv in (1, 4):
                rows[(ta, tv, rv)] = time_share(ta, tv, 1, rv)
    worst = min(rows.values())
    best = max(rows.values())
    print(f"time share across the swept ranges: {worst:.3f} .. {best:.3f}")
    print(f"central case (voices 60 min, visions 1 min, equal rates): {rows[(60, 1, 1)]:.3f}")
    print(f"visual-friendliest case (voices 30 min, visions 5 min, visions 4x as frequent): {rows[(30, 5, 4)]:.3f}")
    checks = [
        ("by time, voices exceed 0.9 in the central case", rows[(60, 1, 1)] > 0.9),
        ("by time, voices stay above the prevalence share in every swept case", worst > prevalence),
        ("break case: even the visual-friendliest case keeps voices above 0.75 of time", rows[(30, 5, 4)] > 0.75),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; prevalence {prevalence:.3f}; time share "
          f"central {rows[(60, 1, 1)]:.3f}, range {worst:.3f}..{best:.3f}")


if __name__ == "__main__":
    main()
