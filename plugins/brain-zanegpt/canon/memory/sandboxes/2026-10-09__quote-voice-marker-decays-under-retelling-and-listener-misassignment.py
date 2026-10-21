"""Prediction (before run): (1) a range threshold separates direct quotes from narrative with balanced accuracy ~0.65-0.70 using the published Jansen et al.
female figures (direct 119 Hz SD66, narrative 61 Hz SD44) -- far from perfect; (2) if each retelling turns a direct quote into an indirect one (flat, range 62 Hz) with
probability q, the share of quotes still carrying the range marker is (1-q)^g, so with q=0.3 it is below 25% by g=4; (3) adding the Pautz et al. listener limits (hit 38%,
correct rejection 15%) the chance a listener correctly registers "a NEW voice is speaking" after g retellings stays under 6% (iteration 1; wrong: it is detection x 0.15 = 0.107 at best, so iteration 2 asserts <0.11 and that it falls 22% from g0 to g8 at q=0.3); (4) BREAK: widening the teller's range by the
paper's +47 Hz reset raises detection above 0.75, but only if the quote stays direct. Deterministic: normal quantile grids, no RNG. stdlib only."""
from statistics import NormalDist
def grid(mu, sd, n=999):
    d = NormalDist(mu, sd); return [d.inv_cdf((i + .5) / n) for i in range(n)]
def best_balanced(a, b):                      # best single-threshold balanced accuracy, a expected high
    best = 0
    for th in sorted(set(round(x, 1) for x in a + b)):
        tpr = sum(x >= th for x in a) / len(a); tnr = sum(x < th for x in b) / len(b)
        best = max(best, (tpr + tnr) / 2)
    return best
DIR, NAR, IND = (119, 66), (61, 44), (62, 30)  # Jansen, Gregory & Brenier 2001, female speakers
narr = grid(*NAR)
base = best_balanced(grid(*DIR), narr)
wide = best_balanced(grid(DIR[0] + 47, DIR[1]), narr)       # teller adds the +47 Hz reset
indirect = best_balanced(grid(*IND), narr)                   # an indirect quote is prosodically narration
HIT, CR = 0.38, 0.15                                         # Pautz et al. 2023 target-present hit, target-absent correct rejection
print(f"detect: direct {base:.3f} direct+47Hz {wide:.3f} indirect {indirect:.3f}")
rows = {}
for q in (0.0, 0.1, 0.3, 0.5):
    out = []
    for g in (0, 1, 2, 4, 8):
        direct_share = (1 - q) ** g
        det = direct_share * base + (1 - direct_share) * indirect   # blended detectability
        register_new = det * CR                                      # detect the shift AND correctly say "unfamiliar"
        out.append((g, round(direct_share, 3), round(det, 3), round(register_new, 3)))
    rows[q] = out
    print(f"q={q}: " + "  ".join(f"g{g}: share {s} det {d} new-voice {r}" for g, s, d, r in out))
ok = (0.60 <= base <= 0.72 and rows[0.3][3][1] < 0.25 and all(r[3] < 0.11 for rows_q in rows.values() for r in rows_q)
      and rows[0.3][4][3] < 0.8 * rows[0.3][0][3] and wide > 0.75 and indirect < base and rows[0.0][4][2] == round(base, 3))
print("RESULT:", "PASS" if ok else "FAIL",
      f"detect direct={base:.3f} +47Hz={wide:.3f} indirect={indirect:.3f}; q=0.3 g=4 direct share {rows[0.3][3][1]}; max new-voice registration {max(r[3] for v in rows.values() for r in v)}")
