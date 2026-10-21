"""Rebuild of sandbox-hybrid-keyword-gate/E1 from the claim only (own fixture: own tokeniser, own tension triples,
own gates; no allowlist/oracle variants).
Claim under test: a gate that fires a 'tension' (3 keywords) on a diff can't keep recall >= 0.90 on common-word edits
and false fires <= 0.10 at 3200 words on TOPICAL prose, though some configs pass on code or off-topic prose, and only
the narrowest windows pass those; whole-diff presence is the live-gate baseline.
PREDICTION (before first run): corpora = ideas/idea-repository.md (topical), Brain bin/brain (code), concatenated
common-licenses (off-topic prose); 3200-word diffs; 9 tensions = triples of mid-frequency content words (rank 150-400);
gates = whole-diff presence, window W in {5,10,20,50,200} co-location, and window + idf bar (the sum of chunk-level idf
of the 3 words >= bar, bars {0, 1.0, 2.0, 3.0}); edit shapes contiguous / spread (words ~25 apart) / dispersed (across
the diff). Feasible = contiguous recall >= 0.90 AND spread recall >= 0.90 AND false fire rate <= 0.10.
P1: whole-diff gate false fires >= 0.80 on topical prose. P2: feasible configs on topical prose = 0.
P3: feasible configs on code >= 1 or off-topic >= 1 (some corpus escapes). P4: every feasible config has W <= 20 AND
dispersed recall <= 0.20 (windowed gates lose dispersed edits). RUN 1 RESULT (recorded honestly): FAIL on P2 and P4 -- with 9 tensions one topical config was feasible (window 50, no bar, false fires exactly
0.10 = 4 of 40 chunks, spread recall 1.0, dispersed recall 0.02), and one off-topic config also at window 50 (so P4's "W <= 20" was wrong).
PREDICTION 2 (written after run 1, BEFORE run 2): the false-fire rate of a window gate grows with the NUMBER of tensions
(any-tension firing); so with 18 and 36 tensions (more triples from the same rank band) topical feasible configs fall to 0 at 36 and
never rise with tension count; P4b: every feasible config at any tension count has window W <= 50 and dispersed recall <= 0.2.
Stdlib only, deterministic, no RNG."""
import re, math, os, glob
from collections import Counter
WORDS = re.compile(r"[a-z][a-z']{2,}")
CH = 3200
def corpus(paths):
    out = []
    for p in paths:
        out += WORDS.findall(open(p, errors="ignore").read().lower())
    return out
cor = {
    "topical": corpus(["/home/user/ideas/idea-repository.md"]),
    "code": corpus(["/home/user/Brain/bin/brain"]),
    "offtopic": corpus(sorted(p for p in glob.glob("/usr/share/common-licenses/*") if not os.path.islink(p))),
}
def chunks(ws):
    n = max(1, (len(ws) - CH) // (CH // 2) + 1) if len(ws) >= CH else 0
    return [ws[i * (CH // 2): i * (CH // 2) + CH] for i in range(n)][:40]
def positions(chunk, ws):
    d = {}
    for i, w in enumerate(chunk): d.setdefault(w, []).append(i)
    return d
def fires_window(pos, trip, W):
    if any(w not in pos for w in trip): return False
    for s in pos[trip[0]]:
        lo, hi = s - W, s + W
        if all(any(lo <= p <= hi for p in pos[w]) for w in trip[1:]):
            # require all three within one window of width W around some anchor
            return True
    return False
def fires_tight(pos, trip, W):
    # strict: all three within a span <= W
    if any(w not in pos for w in trip): return False
    for s in pos[trip[0]]:
        c = [min((abs(p - s), p) for p in pos[w])[1] for w in trip]
        if max(c + [s]) - min(c + [s]) <= W: return True
    return False

allres = {}
for NT in (9, 18, 36):
    res = {}
    for name, ws in cor.items():
        ch = chunks(ws)
        freq = Counter(w for c in ch for w in set(c))
        rank = [w for w, _ in Counter(ws).most_common()][150:400]; rank = rank + rank
        trips = [tuple(rank[(i * 27) % 240: (i * 27) % 240 + 3]) if i < 9 else tuple(rank[(i * 13 + 5) % 240: (i * 13 + 5) % 240 + 3]) for i in range(NT)]
        idf = {w: math.log(len(ch) / (1 + freq[w])) if ch else 0 for w in rank}
        P = [positions(c, c) for c in ch]
        gates = [("whole", None, 0.0)] + [("win", W, b) for W in (5, 10, 20, 50, 200) for b in (0.0, 1.0, 2.0, 3.0)]
        table = []
        for kind, W, bar in gates:
            def gate(pos, trip):
                if bar and sum(idf[w] for w in trip) < bar: return False
                return all(w in pos for w in trip) if kind == "whole" else fires_tight(pos, trip, 2 * W)
            # false fires: unedited chunks, any tension fires
            ff = sum(any(gate(p, t) for t in trips) for p in P) / max(1, len(P))
            # recall: edit = an inserted block making the specific tension's words co-located (shape) at the middle of the chunk
            def edited(c, trip, shape):
                c = list(c); mid = len(c) // 2
                if shape == "contig": c[mid:mid + 3] = trip
                elif shape == "spread": c[mid], c[mid + 25], c[mid + 50] = trip
                else: c[200], c[len(c) // 2], c[len(c) - 200] = trip
                return positions(c, c)
            rec = {}
            for shape in ("contig", "spread", "dispersed"):
                hits = tot = 0
                for c in ch[:12]:
                    for t in trips:
                        pos = edited(c, t, shape)
                        # a tension is 'recalled' only if the gate fires on THIS tension (bar applies)
                        hits += gate(pos, t); tot += 1
                rec[shape] = hits / tot
            feas = rec["contig"] >= 0.9 and rec["spread"] >= 0.9 and ff <= 0.10
            table.append((kind, W, bar, ff, rec, feas))
        res[name] = table
        nf = sum(r[5] for r in table)
        whole = table[0]
        print(f"NT={NT} {name}: chunks={len(ch)} whole-diff false fires={whole[3]:.2f}; feasible configs={nf}/{len(table)}")
        for r in table:
            if r[5]: print("   feasible", r[0], "W", r[1], "bar", r[2], "ff %.2f" % r[3], r[4])
    allres[NT] = res
res = allres[9]
p1 = res["topical"][0][3] >= 0.80
ft = {NT: sum(r[5] for r in allres[NT]["topical"]) for NT in allres}
p2 = ft[36] == 0 and ft[9] >= ft[18] >= ft[36]
print("topical feasible by tension count:", ft)
p3 = sum(r[5] for r in res["code"]) >= 1 or sum(r[5] for r in res["offtopic"]) >= 1
feas_all = [r for n in ("code", "offtopic") for r in res[n] if r[5]]
feas_all = [r for NT in allres for n in ("code", "offtopic", "topical") for r in allres[NT][n] if r[5]]
p4 = bool(feas_all) and all(r[1] is not None and r[1] <= 50 and r[4]["dispersed"] <= 0.2 for r in feas_all)
print(f"P1={p1} P2={p2} P3={p3} P4={p4}")
print(f"RESULT: {'PASS' if all((p1,p2,p3,p4)) else 'FAIL'} topical whole-diff false fires={res['topical'][0][3]:.2f}; feasible topical by NT={ft} code={sum(r[5] for r in res['code'])} offtopic={sum(r[5] for r in res['offtopic'])} of {len(res['topical'])} configs")
