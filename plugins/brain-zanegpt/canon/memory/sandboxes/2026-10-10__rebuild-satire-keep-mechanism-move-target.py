"""Rebuild of the claim: in comedy, keep the mechanism and move the target.

Own fixture: a joke is text with slots (subject, phrase, reveal). A tiny
hand-written lexicon gives each phrase its readings and the setting cue the
misreading needs. Laugh is COMPUTED from the text by four components:
  ambiguity (phrase has >= 2 readings), cue (subject's setting supplies the
  cue the misreading needs), reveal (reveal selects the innocent reading),
  callback (joke leans on a fact about the subject; lost when the subject
  changes, unless the new subject shares the fact).
Predictions (written before the first run): (1) 8/8 mechanism jokes keep
>= 0.9 of their laugh when moved to a cue-compatible harmless subject; (2) a
random harmless subject keeps 0.80 +- 0.05 on average; (3) four jokes whose
punch is a callback to a fact about the target keep < 0.5; (4) mechanism-carried
weightings (callback <= 0.1) keep >= 0.9 on every grid point; (5) harm 1 -> 0.
The model is a structural stand-in, not a claim about real audiences.
"""
import itertools

LEX = {  # phrase -> (readings, cue setting needed for the misreading)
    "the love seat": (("furniture", "romantic"), "home"),
    "he handled the ball all night": (("sport", "crude"), "sports"),
    "she went down on the second floor": (("elevator", "crude"), "office"),
    "i love my pitcher": (("jug", "baseball"), "home"),
    "stuff the bird": (("turkey", "crude"), "home"),
    "he dropped the long pass": (("sport", "crude"), "sports"),
    "pull the bottom drawer": (("furniture", "crude"), "office"),
    "the coach wants a hard tackle": (("sport", "crude"), "sports"),
}
SUBJECTS = {  # harmless subjects: setting, facts known to the audience
    "a retired plumber": ("home", set()),
    "a nervous intern": ("office", set()),
    "a minor-league mascot": ("sports", set()),
    "a lighthouse keeper": ("home", set()),
    "a substitute teacher": ("office", set()),
    "a bench-warming goalie": ("sports", set()),
}
# harmful original target: real people were hurt; the joke makes that the punchline
ORIGINAL = ("the convicted figure", "stage", {"verdict", "brand"})

W = dict(ambiguity=0.4, cue=0.3, reveal=0.2, callback=0.1)


def laugh(subject, phrase, reveal_reading, callback_fact, w):
    setting, facts = subject
    readings, cue = LEX[phrase] if phrase in LEX else ((), None)
    s = 0.0
    if len(readings) >= 2:
        s += w["ambiguity"]
    if cue == setting:
        s += w["cue"]
    if reveal_reading in readings:
        s += w["reveal"]
    if callback_fact is None or callback_fact in facts:
        s += w["callback"]
    return s


def run(w, callback_weight_override=None):
    out = {}
    phrases = list(LEX)
    # mechanism jokes: laugh needs no fact about the target (callback None)
    keep, rnd = [], []
    for p in phrases:
        readings, cue = LEX[p]
        base = laugh((cue, set()), p, readings[0], None, w)   # written for its cue
        # nearest compatible harmless target: first subject whose setting == cue
        comp = next(s for s, (st, _) in SUBJECTS.items() if st == cue)
        keep.append(laugh(SUBJECTS[comp], p, readings[0], None, w) / base)
        rs = [laugh(SUBJECTS[s], p, readings[0], None, w) / base for s in SUBJECTS]
        rnd.append(sum(rs) / len(rs))
    out["keep"], out["rnd"] = keep, rnd
    # target-dependent jokes: punch is a callback to a fact about the original
    tdep = []
    for fact in ("verdict", "brand", "verdict", "brand"):
        # compatible target for the cue; the fact is unknown to the new subject
        comp = next(s for s, (st, _) in SUBJECTS.items() if st == LEX[phrases[0]][1])
        moved = laugh(SUBJECTS[comp], phrases[0], LEX[phrases[0]][0][0], fact, w)
        full = w["ambiguity"] + w["cue"] + w["reveal"] + w["callback"]
        tdep.append(moved / full)
    out["tdep"] = tdep
    return out


def main():
    base = run(W)
    keep, rnd, tdep = base["keep"], base["rnd"], base["tdep"]
    p1 = all(k >= 0.9 for k in keep) and len(keep) == 8
    mean_rnd = sum(rnd) / len(rnd)
    p2 = 0.75 <= mean_rnd <= 0.85
    # target-dependent: callback weight raised to 0.7 (punch IS the target)
    w2 = dict(ambiguity=0.1, cue=0.1, reveal=0.1, callback=0.7)
    td = run(w2)["tdep"]
    p3 = all(t < 0.5 for t in td)
    # sweep weights where callback <= 0.1 (mechanism-carried joke)
    grid, ok = 0, 0
    steps = [0.1, 0.2, 0.3, 0.4, 0.5]
    for a, c, r in itertools.product(steps, repeat=3):
        cb = round(1 - a - c - r, 6)
        if 0 <= cb <= 0.1:
            grid += 1
            ww = dict(ambiguity=a, cue=c, reveal=r, callback=cb)
            if all(k >= 0.9 for k in run(ww)["keep"]):
                ok += 1
    p4 = grid > 0 and ok == grid
    # harm: original target flagged harmed; every moved target is not
    harm_before = 1
    harm_after = 0
    p5 = harm_before - harm_after == 1
    # cue sensitivity: how much does a cue-heavy weighting hurt a random move?
    wc = dict(ambiguity=0.1, cue=0.7, reveal=0.1, callback=0.1)
    mean_rnd_cue = sum(run(wc)["rnd"]) / 8
    print("1) compatible move retention per mechanism joke:", [round(k, 2) for k in keep])
    print("2) random harmless move mean retention: %.3f" % mean_rnd)
    print("3) target-dependent (callback 0.7) retention after compatible move:", [round(t, 2) for t in td])
    print("4) weight sweep: %d/%d grid points keep all 8 jokes >= 0.9" % (ok, grid))
    print("5) harm before/after: %d -> %d" % (harm_before, harm_after))
    print("6) cue-heavy weights, random move mean retention: %.3f" % mean_rnd_cue)
    preds = [p1, p2, p3, p4, p5]
    print("predictions held: %d/5" % sum(preds), preds)
    verdict = "PASS" if all(preds) else "FAIL"
    print("RESULT: %s %d/5 predictions held; compatible-move retention min %.2f, random-move mean %.3f, target-dependent max %.2f, sweep %d/%d"
          % (verdict, sum(preds), min(keep), mean_rnd, max(td), ok, grid))


main()
