"""Sandbox (train kernel, B declare): SONGWRITING kernels rhyme-scheme-shape-sets-
a-songs-emotional-motion and two-pass-letter-assignment-keeps-schemes-legible,
re-verified with a NEW fixture (sandbox-lyrical-composition E7/E8 used another).
Lines end in (vowel, coda). Perfect rhyme = same vowel and coda; assonance = same
vowel only. Two scheme tools: letter assigners (one-pass vs two-pass) and three
'open-ness' metrics over a resolved-rhyme map.
PREDICTION (before run): (a) one-pass lettering gives a stray-assonance stanza and a genuine
perfect-rhyme stanza the SAME label (collision), and a stanza whose first line merely
assonates with the A pair gets a distorted ABAA-style label, while two-pass keeps them
apart by letter case and labels the latter xBAA-style with only the A pair uppercase; (b) among the
four named shapes only max closure span orders AABB < ABAB < ABBA (kernel:
stable < flowing < wistful/open); mean closure distance ties ABAB and ABBA (2.0)
and counting adjacent-couplet stops ranks ABBA as MORE settled than ABAB (wrong
way). BREAK: the metric must use only resolved (uppercase) pairs; on the distorted
one-pass label the mean closure distance reads differently from the two-pass one."""
from itertools import combinations


def assonant(a, b): return a[0] == b[0]

def one_pass(ls):
    out, nxt = [], 0
    for i, l in enumerate(ls):
        for j in range(i):
            if assonant(ls[j], l):
                out.append(out[j]); break
        else:
            out.append(chr(65 + nxt)); nxt += 1
    return "".join(out)

def two_pass(ls):
    out = [None] * len(ls); nxt = 0
    for i, l in enumerate(ls):              # pass 1: perfect rhymes get UPPERCASE
        if out[i] is None:
            grp = [k for k in range(i, len(ls)) if ls[k] == l]
            if len(grp) > 1:
                for k in grp: out[k] = chr(65 + nxt)
                nxt += 1
    low = 0
    for i, l in enumerate(ls):              # pass 2: assonance among the unlettered, lowercase
        if out[i] is None:
            grp = [k for k in range(i, len(ls)) if out[k] is None and assonant(ls[k], l)]
            for k in grp: out[k] = chr(97 + low) if len(grp) > 1 else "x"
            low += len(grp) > 1
    return "".join(out)

def metrics(scheme):                        # resolved (uppercase) pairs only
    pos = {}
    for i, c in enumerate(scheme):
        if c.isupper(): pos.setdefault(c, []).append(i)
    d = [b - a for p in pos.values() for a, b in zip(p, p[1:])]
    return (sum(d) / len(d), max(d), sum(1 for x in d if x == 1)) if d else (float("nan"), 0, 0)

print("scheme  mean-dist max-span adjacent-stops")
ms = {}
for n in ("AABB", "ABAB", "ABBA"):
    ms[n] = metrics(n); print(f"{n}    {ms[n][0]:.2f}      {ms[n][1]}        {ms[n][2]}")
span_order = ms["AABB"][1] < ms["ABAB"][1] < ms["ABBA"][1]
mean_tie = abs(ms["ABAB"][0] - ms["ABBA"][0]) < 1e-9
stops_wrong = ms["ABBA"][2] > ms["ABAB"][2]

AY_M, AY_N, OW_D, OO_T = ("ay", "m"), ("ay", "n"), ("ow", "d"), ("oo", "t")
stray = [AY_M, AY_N, OW_D, OW_D]            # lines 1,2 assonate only; 3,4 perfect
genuine = [AY_M, AY_M, OW_D, OW_D]          # AABB with two perfect couplets
steal = [AY_M, OO_T, AY_N, AY_N]            # line 1 assonates with the perfect A pair
a1, a2 = one_pass(stray), one_pass(genuine)
b1, b2 = two_pass(stray), two_pass(genuine)
c1, c2 = one_pass(steal), two_pass(steal)
print(f"stray vs genuine: one-pass {a1} / {a2} (collide={a1 == a2}); two-pass {b1} / {b2}")
print(f"first line assonates with A pair: one-pass {c1}, two-pass {c2}; mean closure {metrics(c1)[0]:.2f} vs {metrics(c2)[0]:.2f}")
collide = a1 == a2 and b1 != b2
steal_ok = c1 == "ABAA" and c2 == "xxAA" and metrics(c1)[1] == 2 and metrics(c2)[1] == 1
ok = span_order and mean_tie and stops_wrong and collide and steal_ok
print(f"RESULT: {'PASS' if ok else 'FAIL'} max-span orders AABB<ABAB<ABBA ({ms['AABB'][1]},{ms['ABAB'][1]},{ms['ABBA'][1]}); mean ties ABAB/ABBA at {ms['ABAB'][0]:.1f}; stops rank ABBA {ms['ABBA'][2]} > ABAB {ms['ABAB'][2]}; one-pass collides {a1}={a2}; stolen {c1} vs {c2}")
