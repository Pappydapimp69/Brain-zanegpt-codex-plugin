"""Rebuild of seven E62 (SEVEN's hallucination mix: player voices 0.20, companion
mean 0.241, NKEM 0.314, against ~0.55 voice-led psychosis).
Re-derived from src/state.js at seven-0.34.0 (commit 4cc7f1a^): player = rng.pick over the five
kinds; companion weights PHANTOM_MARKER 1+2w, WRONG_WAY 1+2w, CHORUS 1+2c,
FALSE_ANCHOR 1+2s, DOUBLED_PARTY 1; c, w = clamp01(base + U(-0.15, 0.15)), s = U(0,1).
Own method: E62 ignored the jitter; this integrates it WITH clamp01 on a 600x600x600 midpoint
grid. Then the real reference: Waters 2014 gives two separate prevalences (AH 59%, VH 27%
in schizophrenia), so 'share of episodes' is NOT derivable from them; bound it instead.
Predictions written before running:
 P1 player CHORUS share is exactly 0.20 (expect hold).
 P2 with clamping NKEM's share drops below E62's 0.314 by > 0.005 (expect hold: chatty 1.0 clamps).
 P3 the reference auditory share is pinned near 0.55: any episodes-per-hearer ratio between 0.5x and 2x
    (voices vs visions) keeps it within 0.45..0.65 (expect MISS).
"""
TPL = {"VOSS": (0.4, 0.5), "IREN": (0.8, 0.35), "HALDER": (0.5, 0.8), "NKEM": (1.0, 0.4), "PAO": (0.6, 0.95)}
V, G = 0.15, 60

def clamp(x): return min(1.0, max(0.0, x))

def share(c0, w0):
    tot = 0.0
    for i in range(G):
        c = clamp(c0 - V + 2 * V * (i + 0.5) / G)
        for j in range(G):
            w = clamp(w0 - V + 2 * V * (j + 0.5) / G)
            for k in range(G):
                s = (k + 0.5) / G
                tot += (1 + 2 * c) / ((1 + 2 * w) * 2 + (1 + 2 * c) + (1 + 2 * s) + 1)
    return tot / G ** 3

def share_nojitter(c, w):
    # integrate s exactly by grid
    return sum((1 + 2 * c) / ((1 + 2 * w) * 2 + (1 + 2 * c) + (1 + 2 * (k + .5) / 600) + 1) for k in range(600)) / 600

player = 1 / 5
comp = {n: share(*t) for n, t in TPL.items()}
nj = {n: share_nojitter(*t) for n, t in TPL.items()}
for n in TPL: print(f"{n:6s} chorus share with clamped jitter {comp[n]:.4f}  without jitter {nj[n]:.4f}")
mean = sum(comp.values()) / 5
print(f"player {player:.3f}; companion mean {mean:.4f}")
# reference: prevalences AH .59, VH .27, tactile ~.14, olfactory ~.08 are per-patient, not per-episode.
lo = hi = None
for ratio in (0.5, 1.0, 2.0, 4.0):
    a = 0.59 * ratio; o = 0.27 + 0.14 + 0.08
    sh = a / (a + o)
    print(f"voice episodes per hearer = {ratio}x other modalities' -> auditory episode share {sh:.3f}")
    if ratio in (0.5, 2.0): lo = sh if ratio == 0.5 else lo; hi = sh if ratio == 2.0 else hi
p1 = abs(player - 0.2) < 1e-12
p2 = comp["NKEM"] < 0.314 - 0.005
p3 = 0.45 <= lo and hi <= 0.65
checks = [("P1 player 0.20", p1), ("P2 clamp lowers NKEM below 0.309", p2), ("P3 reference pinned 0.45..0.65", p3)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 3 else 'FAIL'} {held}/3; player 0.200; NKEM clamped {comp['NKEM']:.3f} (no jitter {nj['NKEM']:.3f}); "
      f"companion mean {mean:.3f}; reference auditory share {lo:.2f}..{hi:.2f} for 0.5x..2x episode rates")
