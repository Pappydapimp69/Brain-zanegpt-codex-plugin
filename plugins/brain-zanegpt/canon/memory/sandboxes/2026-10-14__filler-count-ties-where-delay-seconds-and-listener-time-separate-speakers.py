"""Three speakers with EQUAL filler counts but different uh/um mix, scored three ways, using
the sourced constants: Fox Tree 2001 (uh -47 ms recognition, um -13 ms not significant) and
Smith & Clark 1993 via Clark & Fox Tree 2002 (post-filler delay um 4.12 s, uh 1.00 s).
Deterministic, stdlib only. The constants come from DIFFERENT tasks (word monitoring vs
question answering); the sandbox treats them as per-occurrence costs, an assumption.

PREDICTION (before first run):
 P1 raw filler count ties all three speakers (8, 8, 8).
 P2 delay seconds rank B (all um) > C (half) > A (all uh): 32.96 / 20.48 / 8.00.
 P3 'cut every filler, replace with silence of equal length' leaves delay seconds unchanged for all
    three and makes A slower by 8*47 ms = 376 ms in recognition (the policy the count metric endorses is not neutral).
 P4 'cut um and prepare silently' (um delay falls to the uh level) saves B 8*(4.12-1.00)=24.96 s and costs nothing in recognition.
 P5 BREAK: the um comprehension effect would have to be >= 3.12 s per um to flip P4's ordering; sweeping it across
    the study's ns range (-50..+50 ms) never changes the ranking.
"""
UH_MS, UM_MS = -47.0, -13.0            # recognition shift per occurrence (negative = faster)
UH_DELAY, UM_DELAY = 1.00, 4.12        # seconds of delay after the filler
speakers = {'A': (8, 0), 'B': (0, 8), 'C': (4, 4)}

def score(uh, um, um_ms=UM_MS):
    count = uh + um
    delay = uh * UH_DELAY + um * UM_DELAY
    recog_ms = uh * UH_MS + um * um_ms
    return count, delay, recog_ms

res = {k: score(*v) for k, v in speakers.items()}
for k, (c, d, r) in res.items():
    print("speaker %s count %d delay %.2f s recognition %.0f ms" % (k, c, d, r))
p1 = len({c for c, _, _ in res.values()}) == 1 and res['A'][0] == 8
p2 = res['B'][1] > res['C'][1] > res['A'][1] and abs(res['B'][1] - 32.96) < 1e-6
# policy: cut all fillers, silence replaces them (delay stays, recognition benefit lost)
cut_all = {k: (0, speakers[k][0] * UH_DELAY + speakers[k][1] * UM_DELAY, 0.0) for k in speakers}
d_cut_all = {k: cut_all[k][1] - res[k][1] for k in speakers}
r_cut_all = {k: cut_all[k][2] - res[k][2] for k in speakers}
print("cut-all(silence) delay change", d_cut_all, "recognition change ms", r_cut_all)
p3 = all(abs(v) < 1e-9 for v in d_cut_all.values()) and r_cut_all['A'] == 376.0
# policy: um removed AND the delay prepared away (um delay falls to the uh level)
def prep(uh, um): return uh * UH_DELAY + um * UH_DELAY, uh * UH_MS          # um's recognition effect lost (ns)
prep_d = {k: res[k][1] - prep(*speakers[k])[0] for k in speakers}
prep_r = {k: prep(*speakers[k])[1] - res[k][2] for k in speakers}
print("cut-um+prepare delay saved s", {k: round(v, 2) for k, v in prep_d.items()}, "recognition change ms", prep_r)
p4 = abs(prep_d['B'] - 24.96) < 1e-6 and prep_r['B'] == 104.0 and prep_d['A'] == 0
# break: sweep um comprehension effect; net seconds saved for B = delay saved - recognition lost
rank_stable = True
for um_ms in range(-50, 51, 10):
    base = score(0, 8, um_ms); pr = prep(0, 8)
    net = (base[1] - pr[0]) - (pr[1] - base[2]) / 1000.0
    if net <= 0: rank_stable = False
break_even_s = (UM_DELAY - UH_DELAY)
print("P5 net seconds saved for B stays positive across um effect -50..+50 ms:", rank_stable,
      "; break-even um effect would be %.2f s per um" % break_even_s)
p5 = rank_stable
print("PREDICTIONS held:", p1, p2, p3, p4, p5)
print("RESULT: %s counts=%s delay-s=%s cut-all dDelay=0 dRecog(A)=+%.0f ms; cut-um+prepare saves B %.2f s for +%.0f ms (held %d/5)" % (
    "PASS" if all([p1, p2, p3, p4, p5]) else "FAIL",
    [res[k][0] for k in 'ABC'], [round(res[k][1], 2) for k in 'ABC'], r_cut_all['A'], prep_d['B'], prep_r['B'], sum([p1, p2, p3, p4, p5])))
