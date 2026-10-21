"""Prediction (written before the first run), roster of 24 fighters with lore power levels log-spaced 1e3..1e9, clash =
C*(5+m) with mash count m enumerated over 1..10 for both sides (brainwork/E76):
 P1 lore number load-bearing (A): the lore-weaker side never wins when the lore ratio exceeds (5+10)/(5+1)=2.5, so the
    upset rate in the ratio>1000 band is exactly 0.
 P2 fully decoupled combat values (B): upset rate ~0.5 in every band, but the displayed number contradicts combat order
    in ~half of all pairs (lie rate ~0.5).
 P3 combat values derived from the display (monotone): lie rate 0 and the ratio>1000 upset rate is 0 again.
 P4 (built to BREAK the kernel's 'decouple them' fix): giving a fraction f of fighters high combat value despite a low
    displayed number, an upset rate of >=10% in the ratio>1000 band costs a lie rate of >=10%; there is no f that buys
    far-band upsets with a lie rate near 0.
 P5 display layer: sorting short-scale labels like '120M' and '90K' as text puts 120M before 90K, so the label order
    differs from the numeric order unless the sort uses the parsed value."""
from fractions import Fraction as F
M = 10
N = 24
PL = [round(1000 * 10 ** (i * 6 / (N - 1))) for i in range(N)]

def clash(Ca, Cb):
    """P(a beats b), mash counts uniform 1..M each; tie goes to b (defender)."""
    wins = sum(1 for ma in range(1, M + 1) for mb in range(1, M + 1) if Ca * (5 + ma) > Cb * (5 + mb))
    return F(wins, M * M)

def h(i, k):
    return (i * 2654435761 + k * 40503 + 12345) % (2 ** 32)

def bands(C):
    """upset rate by lore ratio band, and lie rate (display order contradicts combat order)."""
    acc = {"<10": [F(0), 0], "10-1000": [F(0), 0], ">1000": [F(0), 0]}
    lie = tot = 0
    for i in range(N):
        for j in range(i + 1, N):          # i lore-weaker, j lore-stronger
            r = PL[j] / PL[i]
            band = "<10" if r < 10 else ("10-1000" if r <= 1000 else ">1000")
            acc[band][0] += clash(C[i], C[j]); acc[band][1] += 1
            tot += 1; lie += C[i] > C[j]
    return {k: (float(v[0] / v[1]) if v[1] else float('nan')) for k, v in acc.items()}, lie / tot

res = {}
# A: lore number is the combat number
A = bands(PL); res["A"] = A
# B: fully decoupled, hash-derived combat values 50..149
Cb = [50 + h(i, 1) % 100 for i in range(N)]
B = bands(Cb); res["B"] = B
# derived: monotone combat value
Cd = [50 + 4 * i for i in range(N)]
D = bands(Cd); res["D"] = D
for k, (b, l) in res.items():
    print(k, {x: round(y, 3) for x, y in b.items()}, "lie", round(l, 3))
# P4: a fraction f of fighters are specialists: low display but combat value of a top fighter
curve = []
for f in (0, 0.1, 0.25, 0.5):
    C = list(Cd)
    n_spec = int(round(f * N))
    low = [i for i in range(N) if i < N // 2][:n_spec] if n_spec else []
    for i in low: C[i] = 50 + 4 * (N - 1)       # strongest combat value, but low lore number
    b, l = bands(C)
    curve.append((f, b[">1000"], l))
    print(f"f={f}: far-band upset {b['>1000']:.3f} lie {l:.3f}")
# P5: label order vs numeric order
def label(n):
    for s, suf in ((10**9, "B"), (10**6, "M"), (10**3, "K")):
        if n >= s: return f"{n // s}{suf}"
    return str(n)
labs = [label(p) for p in PL]
text_sorted = sorted(labs); num_sorted = labs
mismatch = text_sorted != num_sorted
print("goku/frieza labels", label(90_000), label(120_000_000), "text order != numeric order:", mismatch)

far = {f: (u, l) for f, u, l in curve}
held = {
 "P1": res["A"][0][">1000"] == 0 and res["A"][0]["10-1000"] == 0,
 "P2": abs(res["B"][0][">1000"] - 0.5) < 0.12 and abs(res["B"][1] - 0.5) < 0.12,
 "P3": res["D"][1] == 0 and res["D"][0][">1000"] == 0,          # missed on first run: 0.061
 "P4": far[0][0] == 0 and all(not (far[f][0] >= 0.10 and far[f][1] < 0.10) for f in far),
 "P5": mismatch,
}
# post-hoc diagnostic: the derived roster's combat range is 50..142, ratio 2.84 > (5+M)/(5+1)=2.5, so the window leaks
print("post-hoc: derived combat ratio", Cd[-1] / Cd[0], "vs window bound", (5 + M) / 6)
print("predictions:", ", ".join(f"{k}={'held' if v else 'MISSED'}" for k, v in held.items()))
n = sum(held.values())
print("RESULT:", "PASS" if n == len(held) else "FAIL",
      f"{n}/{len(held)} predictions held; A far-band upset {res['A'][0]['>1000']:.3f}; decoupled upset {res['B'][0]['>1000']:.3f} lie {res['B'][1]:.3f}; "
      f"derived upset {res['D'][0]['>1000']:.3f} lie {res['D'][1]:.3f}; specialists f=0.1 upset {far[0.1][0]:.3f} lie {far[0.1][1]:.3f}; "
      f"f=0.25 upset {far[0.25][0]:.3f} lie {far[0.25][1]:.3f}; labels misordered {mismatch}")
