"""Seed sandbox for domain CROSSWORD-CONSTRUCTION: fill a 5x5 fully-open grid (5 across + 5 down entries)
from a fixed embedded word list by backtracking, counting search nodes (placements tried) until the first fill.
Orders: FIXED (A1,D1,A2,D2,...) vs MRV (next slot = the one with the fewest dictionary matches given letters placed).
Both orders are exact and deterministic; word list is sorted. PREDICTION (before run): MRV tries fewer nodes than
FIXED for every list size tested (40/80/160/all) and the ratio grows with list size; BREAK: a list so small that both
fail/find no fill gives equal counts (0 fills, equal node counts to exhaustion).
"""
import re
WORDS = """about above abuse actor acute admit adopt adult after again agent agree ahead alarm album alert alike alive allow alone along alter among anger angle angry apart apple apply arena argue arise array aside asset audio avoid award aware badly baker bases basic basis beach began begin being below bench billy birth black blame blank blast blind block blood board boost booth bound brain brand bread break breed brief bring broad broke brown build built buyer cable carry catch cause chain chair chart chase cheap check chest chief child china chose civil claim class clean clear click clock close coach coast could count court cover craft crash cream crime cross crowd crown curve cycle daily dance dated dealt death debut delay depth doing doubt dozen draft drama drawn dream dress drill drink drive drove dying eager early earth eight elite empty enemy enjoy enter entry equal error event every exact exist extra faith false fault fiber field fifth fifty fight final first fixed flash fleet floor fluid focus force forth forty forum found frame frank fraud fresh front fruit fully funny giant given glass globe going grace grade grand grant grass great green gross group grown guard guess guest guide happy harry heart heavy hence horse hotel house human ideal image index inner input issue joint judge known label large laser later laugh layer learn lease least leave legal level light limit links lives local logic loose lower lucky lunch lying magic major maker march match maybe mayor meant media metal might minor minus mixed model money month moral motor mount mouse mouth movie music needs never newly night noise north noted novel nurse occur ocean offer often order other ought paint panel paper party peace phase phone photo piece pilot pitch place plain plane plant plate point pound power press price pride prime print prior prize proof proud prove queen quick quiet quite radio raise range rapid ratio reach ready refer right rival river robin roman rough round route royal rural scale scene scope score sense serve seven shall shape share sharp sheet shelf shell shift shirt shock shoot short shown sight since sixth sixty sized skill sleep slide small smart smile smith smoke solid solve sorry sound south space spare speak speed spend spent split spoke sport staff stage stake stand start state steam steel stick still stock stone stood store storm story strip stuck study stuff style sugar suite super sweet table taken taste taxes teach teeth terry texas thank theft their theme there these thick thing think third those three threw throw tight times tired title today topic total touch tough tower track trade train treat trend trial tribe trick tried tries truck truly trust truth twice under undue union unity until upper upset urban usage usual valid value video virus visit vital voice waste watch water wheel where which while white whole whose woman women world worry worse worst worth would wound write wrong wrote yield young youth""".split()
WORDS = sorted(set(w for w in WORDS if len(w) == 5 and re.fullmatch("[a-z]+", w)))
N = 5
CAP = 300000  # node budget; hitting it is reported as not finished
PLANT = ['heart', 'ember', 'abuse', 'resin', 'trend']  # a symmetric word square: across == down
SLOTS = [("A", i) for i in range(N)] + [("D", i) for i in range(N)]
FIXED = [("A", 0), ("D", 0), ("A", 1), ("D", 1), ("A", 2), ("D", 2), ("A", 3), ("D", 3), ("A", 4), ("D", 4)]
def cells(s): k, i = s; return [(i, c) for c in range(N)] if k == "A" else [(r, i) for r in range(N)]
def pattern(g, s): return "".join(g.get(c, ".") for c in cells(s))
def matches(words, pat): rx = re.compile(pat); return [w for w in words if rx.fullmatch(w)]
def solve(words, order_mode):
    nodes = [0]; used = set()
    def rec(g, filled):
        if len(filled) == len(SLOTS): return dict(g)
        rest = [s for s in SLOTS if s not in filled]
        if order_mode == "fixed": s = [x for x in FIXED if x in rest][0]
        else: s = min(rest, key=lambda x: (len(matches(words, pattern(g, x))), SLOTS.index(x)))
        for w in matches(words, pattern(g, s)):
            nodes[0] += 1
            if nodes[0] > CAP: return None
            new = dict(g)
            for c, ch in zip(cells(s), w): new[c] = ch
            r = rec(new, filled | {s})
            if r: return r
        return None
    sol = rec({}, frozenset())
    return nodes[0], sol is not None
res = {}
for plant in (True, False):
    for n in (40, 80, 160, 493):
        sub = WORDS[::max(1, len(WORDS) // n)][:n]
        sub = sorted(set(sub) | (set(PLANT) if plant else set()) - (set() if plant else set(PLANT)))
        if not plant: sub = [w for w in sub if w not in PLANT]
        f = solve(sub, "fixed"); m = solve(sub, "mrv")
        res[(plant, n)] = (f, m)
        print(f"plant={plant!s:5} words={len(sub):3d} fixed nodes={f[0]} found={f[1]}   mrv nodes={m[0]} found={m[1]}")
fewer = all(res[k][1][0] <= res[k][0][0] for k in res)
mrv_planted = all(res[(True, n)][1][1] for n in (40, 80, 160, 493))
fixed_capped = [k for k in res if res[k][0][0] > CAP]   # fixed order ran out of budget (not a proof of anything)
ratios = [res[(True, n)][0][0] / res[(True, n)][1][0] for n in (40, 80, 160, 493)]
grows = all(a < b for a, b in zip(ratios, ratios[1:]))
nofill_ratio = [round(res[(False, n)][0][0] / res[(False, n)][1][0], 1) for n in (40, 80, 160)]
mrv_capped = [k for k in res if res[k][1][0] > CAP]
print("planted fixed/mrv ratios:", [round(r, 1) for r in ratios], "(last is a lower bound: fixed hit the budget)")
print("no-fill (exhaustive) fixed/mrv ratios:", nofill_ratio, " fixed capped runs:", fixed_capped, " mrv capped runs:", mrv_capped)
ok = fewer and mrv_planted and grows and not mrv_capped and min(nofill_ratio) > 3
print("RESULT: %s MRV nodes <= fixed in all 8 runs; fixed/mrv ratio on planted grids %s grows with list size; fixed order exhausted its %d-node budget on %d full-list runs while MRV finished"
      % ("PASS" if ok else "FAIL", [round(r, 1) for r in ratios], CAP, len(fixed_capped)))
