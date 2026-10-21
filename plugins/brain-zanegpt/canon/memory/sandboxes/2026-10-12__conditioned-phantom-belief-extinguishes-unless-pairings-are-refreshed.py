"""Loop 2 (kernel GAME-DESIGN/hallucination/conditioned-hallucination-staging:
teach a cue-stimulus pairing, then present the cue alone). How many honest
pairings are needed, and how many cue-alone phantoms does that buy before the
player stops 'perceiving' the missing half?
Model: Rescorla-Wagner learning (a standard associative-learning model, used
here as an assumption about players). Association V starts at 0; a paired trial
moves V by alpha*(1 - V); a cue-alone trial moves it by alpha*(0 - V). The
phantom is 'perceived' while V >= 0.6. Exact, no RNG. alpha = 0.3.
Schedules after T teaching pairings, for 12 later cue events:
  ALL-PHANTOM  every later cue is alone
  PARTIAL      later cues alternate real, alone, real, alone...
  SPARSE       1 real pairing then 3 alone, repeating
Count phantoms perceived (cue-alone events with V >= 0.6 before the event).
"""
A, THRESH = 0.3, 0.6


def teach(t):
    v = 0.0
    for _ in range(t):
        v += A * (1 - v)
    return v


def run(v, pattern, events=12):
    perceived = 0
    for i in range(events):
        real = pattern[i % len(pattern)]
        if real:
            v += A * (1 - v)
        else:
            if v >= THRESH:
                perceived += 1
            v += A * (0 - v)
    return perceived


def main():
    need = next(t for t in range(1, 30) if teach(t) >= THRESH)
    print(f"pairings needed before the first phantom can be perceived: {need} (V={teach(need):.3f})")
    rows = {}
    for t in (need, 6, 10):
        v = teach(t)
        rows[t] = {name: run(v, pat) for name, pat in
                   (("all-phantom", [0]), ("partial", [1, 0]), ("sparse", [1, 0, 0, 0]))}
        print(f"taught {t:2d} (V={v:.3f}): phantoms perceived out of 12 cues: " +
              ", ".join(f"{k} {n}" for k, n in rows[t].items()))
    checks = [
        ("at least 3 honest pairings are needed before a phantom works", need >= 3),
        ("with all later cues alone, at most 2 phantoms land however long the teaching (10 pairings)",
         rows[10]["all-phantom"] <= 2),
        ("refreshing with alternate real pairings lands more phantoms than all-phantom", rows[need]["partial"] > rows[need]["all-phantom"]),
        ("break case: sparse refresh (1 real per 3 alone) still beats all-phantom", rows[need]["sparse"] > rows[need]["all-phantom"]),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; need {need}; "
          + "; ".join(f"t{t}: " + "/".join(str(x) for x in r.values()) for t, r in rows.items()))


if __name__ == "__main__":
    main()
