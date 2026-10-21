"""Sandbox: the but/therefore connective test (ideas:SYSTEM/narrative/but-therefore-spine)
as a mechanical beat checker, composed with the chronicle lesson (test/E10) and the
Chekhov ledger's reach-the-ending rule (local chekhov-ledger/E1). Pushed to where the
ADJACENT-beat form breaks.
A story is a list of beats. Each beat: plants (facts it introduces), uses (facts it
consumes, by earlier beat), opposes (it thwarts the goal active before it),
coincidence ('in' = luck that makes trouble, 'out' = luck that removes trouble).
Link i->i+1 reads THEREFORE if beat i+1 uses a fact planted by beat i, BUT if it
opposes, else AND-THEN.
Checkers:
 ADJ-BT   adjacent beats must read but or therefore (the kernel as written)
 ADJ-T    adjacent beats must read therefore only (strict 'therefore only' rule)
 CAUSAL   every beat after the first must use or oppose SOME earlier beat, every
          planted fact must lie on a chain that reaches the last beat, and only
          a coincidence that gets OUT of trouble is a defect (Pixar 19)
Each story has hand-labelled true defects; a flag on a non-defect is a false positive.
PREDICTIONS (written before running):
 P1 ADJ-BT flags every link of a pure chronicle (6/6)
 P2 ADJ-T flags every BUT beat of the tight causal story as a defect (>= 2 false positives)
 P3 on a cross-cut A/B story (each beat caused two beats back) ADJ-BT false-flags >= 50% of links; CAUSAL 0
 P4 a dead-end subplot passes ADJ-BT (0 flags) and CAUSAL catches it
 P5 ADJ-BT flags the coincidence INTO trouble (a false positive under Pixar 19); CAUSAL flags only the rescue
 P6 deleting any one middle beat of the tight story is caught by ADJ-BT in every position
"""
def B(plants=(), uses=(), opposes=False, coin=None, defect=False):
    return dict(plants=set(plants), uses=set(uses), opposes=opposes, coin=coin, defect=defect)
tight = [B(["want"]), B(["plan"], ["want"]), B(["guard"], opposes=True), B(["bribe"], ["guard"]),
         B(["betrayal"], opposes=True), B(["choice"], ["betrayal"]), B(["end"], ["choice", "want"])]
chronicle = [B(["wake"])] + [B([f"e{i}"], defect=True) for i in range(6)]
crosscut = [B(["a1"]), B(["b1"]), B(["a2"], ["a1"]), B(["b2"], ["b1"]), B(["a3"], ["a2"]),
            B(["b3"], ["b2"]), B(["end"], ["a3", "b3"])]
deadend = [B(["want"]), B(["side"], ["want"], defect=True), B(["side2"], ["side"], defect=True),
           B(["side3"], ["side2"], defect=True), B(["plan"], ["want"]), B(["end"], ["plan"])]
# beats 1-3 are a side chain that never reaches the end; beat 4 resumes the main plot from beat 0.
coinc = [B(["want"]), B(["storm"], coin="in"), B(["stranded"], ["storm"]),
         B(["rescue"], ["stranded"], coin="out", defect=True), B(["end"], ["rescue", "want"])]
def link(s, i):
    a, b = s[i], s[i+1]
    if b["uses"] & a["plants"]: return "therefore"
    if b["opposes"]: return "but"
    return "and-then"
def adj(s, allowed): return {i+1 for i in range(len(s)-1) if link(s, i) not in allowed}
def causal(s):
    flags = set(); planted_at = {}
    for i, b in enumerate(s):
        for f in b["plants"]: planted_at[f] = i
        if i and not (b["uses"] or b["opposes"] or b["coin"] == "in"): flags.add(i)
        if b["coin"] == "out": flags.add(i)
    # reach the ending: beat j reaches end if it is last or a later beat uses its plants (or opposes right after)
    n = len(s); reach = [False]*n; reach[-1] = True
    for j in range(n-2, -1, -1):
        for k in range(j+1, n):
            if reach[k] and (s[k]["uses"] & s[j]["plants"] or (k == j+1 and s[k]["opposes"])):
                reach[j] = True; break
        if s[j]["coin"] == "in" and reach[j+1]: reach[j] = True
    flags |= {j for j in range(n) if not reach[j] and s[j]["plants"]}
    return flags
def score(s, flags):
    truth = {i for i, b in enumerate(s) if b["defect"]}
    return len(flags & truth), len(flags - truth), len(truth - flags)
stories = dict(tight=tight, chronicle=chronicle, crosscut=crosscut, deadend=deadend, coinc=coinc)
res = {}
for name, s in stories.items():
    r = {"ADJ-BT": score(s, adj(s, {"but", "therefore"})), "ADJ-T": score(s, adj(s, {"therefore"})),
         "CAUSAL": score(s, causal(s))}
    res[name] = r
    print(f"{name:9s} " + "  ".join(f"{k} hit/fp/miss {v[0]}/{v[1]}/{v[2]}" for k, v in r.items()))
# P6 deletion mutations on tight
caught = 0; positions = range(1, len(tight)-1)
for d in positions:
    m = tight[:d] + tight[d+1:]
    if adj(m, {"but", "therefore"}): caught += 1
print(f"deletion mutations caught by ADJ-BT: {caught}/{len(positions)}")
cc_flags = adj(coinc, {"but", "therefore"})
p1 = res["chronicle"]["ADJ-BT"][0] == 6
p2 = res["tight"]["ADJ-T"][1] >= 2
p3 = res["crosscut"]["ADJ-BT"][1] >= 3 and res["crosscut"]["CAUSAL"][1] == 0
p4 = not adj(deadend, {"but", "therefore"}) and res["deadend"]["CAUSAL"][2] == 0
p5 = 1 in cc_flags and causal(coinc) == {3}
p6 = caught == len(positions)
checks = [p1, p2, p3, p4, p5, p6]; held = sum(checks)
print(f"RESULT: {'PASS' if held == 6 else 'FAIL'} {held}/6 predictions held; chronicle ADJ-BT hits "
      f"{res['chronicle']['ADJ-BT'][0]}/6; therefore-only false positives on tight {res['tight']['ADJ-T'][1]}; "
      f"crosscut ADJ-BT fp {res['crosscut']['ADJ-BT'][1]}/6 CAUSAL fp {res['crosscut']['CAUSAL'][1]}; "
      f"deadend ADJ-BT hits {res['deadend']['ADJ-BT'][0]} CAUSAL miss {res['deadend']['CAUSAL'][2]}; "
      f"coincidence ADJ-BT flags {sorted(cc_flags)} CAUSAL {sorted(causal(coinc))}; deletions {caught}/{len(positions)}; "
      f"checks {checks}")
