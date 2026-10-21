"""A 'deck' is a list of claims about a small library. Each claim is shown in one of three ways:
  PROSE   : 'parse_price handles thousands separators' (assertion only)
  PASTED  : the call and its output pasted as text, captured when the deck was written
  LIVE    : the call is stored as a callable plus its expected output and RE-RUN by a checker
Library v1 is correct. Then v2 is released with 3 behavior changes (the deck is NOT updated). A 4th claim is fabricated (never run).
Metric 1 'evidence ratio' = share of claims that display a concrete artifact (the kernel's rule; also the data-ink analogue: marks that carry checkable information).
Metric 2 false-claims-undetected after v2 for a reader who can only inspect the slide vs a checker that re-runs it.
Prediction (before run): all three PASTED/LIVE decks have evidence ratio 1.0 at v1 and the fabricated pasted claim has the SAME ratio (1.0) as the real ones;
after v2: PASTED decks keep 3 stale claims + 1 fabricated = 4 undetected for slide-only readers; LIVE decks flag exactly the 3 changed + the fabricated claim (4/4);
PROSE deck has evidence ratio 0 but ALSO 4 undetected (nothing to check). BREAK: a LIVE check whose expected output was pasted from v2 behavior (checker re-baselined) flags 0 of 3 - re-running proves consistency, not correctness."""
def v1_price(s): return float(s.replace(",", "").replace("$", ""))
def v1_round(x): return round(x)
def v1_split(s): return s.split(",")
def v1_neg(s): return -float(s.strip("()"))

def v2_price(s): return float(s.replace("$", ""))            # regression: thousands separators now crash
def v2_round(x): return int(x + 0.5)                          # behavior change at .5 for even ints
def v2_split(s): return [p.strip() for p in s.split(",")]      # trims whitespace
v2_neg = v1_neg                                               # unchanged

CALLS = [("price", "$1,234.50", v1_price, v2_price), ("round", 2.5, v1_round, v2_round),
         ("split", "a, b", v1_split, v2_split), ("neg", "(5)", v1_neg, v2_neg)]
def run(f, a):
    try: return repr(f(a))
    except Exception as e: return "ERR:" + type(e).__name__

deck = [dict(name=n, arg=a, shown=run(f1, a)) for n, a, f1, f2 in CALLS]
deck.append(dict(name="fabricated", arg="x", shown="42.0", fabricated=True))     # never run
prose = [dict(name=d["name"], shown=None, fabricated=d.get("fabricated", False)) for d in deck]

def ratio(d): return sum(1 for c in d if c["shown"] is not None) / len(d)
def stale_slide_only(d): return 0                         # a reader inspecting only the slide sees nothing wrong with any claim
def undetected_slide_only(d, v):   # claims that are false now but not flagged
    wrong = 0
    for c in d:
        if c.get("fabricated"): wrong += 1; continue
        f2 = [x[3] for x in CALLS if x[0] == c["name"]][0]
        a = [x[1] for x in CALLS if x[0] == c["name"]][0]
        if c["shown"] is not None and run(f2, a) != c["shown"]: wrong += 1
        if c["shown"] is None and run(f2, a) != run([x[2] for x in CALLS if x[0] == c["name"]][0], a): wrong += 1
    return wrong
def live_flags(d, impl, rebaseline=False):
    flags = 0
    for c in d:
        if c.get("fabricated"):
            flags += 1; continue                               # no callable behind it: checker cannot run it
        f = [x[impl] for x in CALLS if x[0] == c["name"]][0]
        a = [x[1] for x in CALLS if x[0] == c["name"]][0]
        exp = run(f, a) if rebaseline else c["shown"]
        flags += run(f, a) != exp
    return flags
pasted_undetected_slide = undetected_slide_only(deck, 2)
prose_undetected = undetected_slide_only(prose, 2)
live = live_flags(deck, 3)
rebased = live_flags(deck, 3, rebaseline=True)
real_ratio = ratio(deck[:4]); fab_ratio = ratio(deck[4:])
print("evidence ratio: pasted/live deck", ratio(deck), "| real claims", real_ratio, "| fabricated claim", fab_ratio, "| prose deck", ratio(prose))
print("false claims after v2: pasted slide-only", pasted_undetected_slide, "| prose slide-only", prose_undetected, "| live re-run flags", live, "| rebaselined re-run flags (excl. fabricated)", rebased - 1)
ok = (ratio(deck) == 1.0 and real_ratio == fab_ratio == 1.0 and ratio(prose) == 0.0
      and pasted_undetected_slide == 4 and prose_undetected == 4 and live == 4 and rebased - 1 == 0)
print(f"RESULT: {'PASS' if ok else 'FAIL'} evidence ratio 1.0 for real and fabricated alike; v2 leaves {pasted_undetected_slide} false pasted claims, re-run flags {live}, rebaselined re-run flags {rebased-1} of 3 changed")
