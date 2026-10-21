"""Does swapping the stand-in punchline-timing figures for published ones change any conclusion?

Stand-in under test (from the humor-localization sandbox, which reused the hook-fit model):
  - Spanish/English syllable ratio R ~ triangular(0.90, mode 1.87, max 1.88), mean 1.55 (fitted to 10 author-written
    hook pairs, NOT a published law)
  - fixed Spanish speech rate 7.7 syllables/s, window 2.8 s, no pause inside the window

Published figures used (READ in the source text unless marked recalled):
  READ  Stivers et al. 2009 (turn-taking, 10 languages): overall mode 0 ms, overall median +100 ms, mean +208 ms,
        language means within 250 ms of that mean, language means from +7 ms (Japanese) to +469 ms (Danish),
        language medians 0 to +300 ms.
  READ  Tian, Mazzocconi and Ginzburg 2016 (laughter in dyadic conversation, French and Chinese): only 30% of laughs
        start within 0.3 s after the laughable; mean laughter-start minus laughable-start 2.2 s (French), 1.3 s (Chinese).
  READ  Attardo and Pickering 2011 (twenty joke performances, abstract): no evidence that punch lines are preceded by
        pauses; no speech-rate change at the punch line. No durations in the abstract, so no pause figure from it.
  READ  Coupe, Oh, Dediu and Pellegrino 2019 (17 languages): speech rate mean 6.63 syll/s, SD 1.15, individual speakers
        4.3 to 9.1; information per syllable from 4.8 bits (Basque) to 8.0 bits (Vietnamese), so any pair of the 17
        languages differs by at most 8.0/4.8 = 1.67 in syllables needed for equal information.
  RECALLED (not read): Spanish-English pair information-density ratio near 1.44 (Pellegrino et al. 2011).

PREDICTIONS (written before the first run):
 P1 stand-in baseline: fit(11)=1.00, fit(14) in 0.35-0.50, n_safe (largest n with fit>=0.99) = 11.
 P2 ratio law swapped to uniform(1.0,1.67) or triangular(1.0,1.44,1.67): n_safe = 12 for both (shift +1) and the
    n* (largest n with fit>=0.5) shift is +1 to +3.
 P3 a pre-punchline pause inside the window: 0.208 s (Stivers mean) gives n_safe 10; 0.6 s gives n_safe 9.
 P4 human-speaker rate spread N(7.7, 1.15) clipped to 4.3-9.1: fit(11) falls to 0.80-0.93 and n_safe <= 8.
 P5 setup budget (clip 10 s, punchline 11 English syllables) swings by: hold after punchline 0.3 -> 2.2 s about 9.5
    syllables, ratio law stand-in -> triangular(1.0,1.44,1.67) about 6.3, pause 0 -> 0.6 s about 3.0 (each +-1.5);
    ranking hold > ratio > pause.
 P6 BREAK: the ratio-law shift in n_safe is at most 1 at windows 2.0 s and 2.8 s but 2 at 3.5 s, so "the ratio law
    does not matter" breaks for a longer window.
 P7 a fixed voice at the pooled mean rate 6.63 syll/s (stress case, not a Spanish figure): n_safe = 9, so the
    11-syllable guarantee fails for a slower voice.

Scope: this scores structure under stated assumptions (timing arithmetic for a scripted voice); it says nothing about
real audiences or any named person. Deterministic: quantile grid, no random numbers, no real timing.
"""
import math
from statistics import NormalDist

W0, RATE0 = 2.8, 7.7


# ---- ratio laws (CDFs) -------------------------------------------------------------------------------------
def tri_cdf(a, c, b):
    def f(x):
        if x <= a:
            return 0.0
        if x >= b:
            return 1.0
        if x <= c:
            return (x - a) ** 2 / ((b - a) * (c - a))
        return 1 - (b - x) ** 2 / ((b - a) * (b - c))
    return f


def uni_cdf(a, b):
    return lambda x: 0.0 if x <= a else 1.0 if x >= b else (x - a) / (b - a)


LAWS = {
    "stand-in tri(0.90,1.87,1.88)": (tri_cdf(0.90, 1.87, 1.88), 1.88, (0.90 + 1.87 + 1.88) / 3),
    "uniform(1.0,1.67)": (uni_cdf(1.0, 1.67), 1.67, 1.335),
    "tri(1.0,1.44,1.67)": (tri_cdf(1.0, 1.44, 1.67), 1.67, (1.0 + 1.44 + 1.67) / 3),
}
S, U, T = list(LAWS)


def rate_grid(sd, lo=4.3, hi=9.1, k=99, center=RATE0):
    if sd == 0:
        return [center]
    nd = NormalDist(center, sd)
    return [min(hi, max(lo, nd.inv_cdf((i + 0.5) / k))) for i in range(k)]


def fit(n, law, window=W0, pause=0.0, rates=(RATE0,)):
    cdf = LAWS[law][0]
    return sum(cdf(r * (window - pause) / n) for r in rates) / len(rates)


def n_safe(law, window=W0, pause=0.0, rates=(RATE0,), level=0.99):
    return max((n for n in range(1, 60) if fit(n, law, window, pause, rates) >= level), default=0)


def n_star(law, window=W0, pause=0.0, rates=(RATE0,)):
    return max((n for n in range(1, 60) if fit(n, law, window, pause, rates) >= 0.5), default=0)


checks = []


def check(name, ok, detail):
    checks.append((name, ok))
    print(f"  {name} {'HELD' if ok else 'MISSED'}: {detail}")


print("== Part A: punchline fit in the window (English syllables n, Spanish = n*R) ==")
print("  law                          n_safe  n*(0.5)  fit(11)  fit(14)")
for law in LAWS:
    print(f"  {law:<28} {n_safe(law):>6}  {n_star(law):>7}  {fit(11, law):>7.3f}  {fit(14, law):>7.3f}")
check("P1", fit(11, S) == 1.0 and 0.35 <= fit(14, S) <= 0.50 and n_safe(S) == 11,
      f"fit(11)={fit(11, S):.2f} fit(14)={fit(14, S):.3f} n_safe={n_safe(S)}")
sh_safe = [n_safe(l) - n_safe(S) for l in (U, T)]
sh_star = [n_star(l) - n_star(S) for l in (U, T)]
check("P2", all(n_safe(l) == 12 for l in (U, T)) and all(1 <= s <= 3 for s in sh_star),
      f"n_safe U/T = {n_safe(U)}/{n_safe(T)} (shift {sh_safe}); n* shift {sh_star}")

print("== Part B: pause placed inside the window (stand-in law, fixed rate) ==")
for p in (0.0, 0.1, 0.208, 0.25, 0.6, 1.0):
    print(f"  pause {p:.3f} s -> n_safe {n_safe(S, pause=p)}, n* {n_star(S, pause=p)}")
check("P3", n_safe(S, pause=0.208) == 10 and n_safe(S, pause=0.6) == 9,
      f"n_safe at 0.208 = {n_safe(S, pause=0.208)}, at 0.6 = {n_safe(S, pause=0.6)}")

print("== Part C: speaker rate spread (human speaker) vs fixed rate (scripted voice) ==")
for sd in (0.0, 0.6, 1.15):
    rg = rate_grid(sd)
    print(f"  rate sd {sd:.2f}: fit(11)={fit(11, S, rates=rg):.3f} fit(14)={fit(14, S, rates=rg):.3f} "
          f"n_safe={n_safe(S, rates=rg)} n*={n_star(S, rates=rg)}")
rg = rate_grid(1.15)
check("P4", 0.80 <= fit(11, S, rates=rg) <= 0.93 and n_safe(S, rates=rg) <= 8,
      f"fit(11)={fit(11, S, rates=rg):.3f}, n_safe={n_safe(S, rates=rg)}")

print("== Part D: setup budget in a 10 s clip: s_max = (T - pause - hold) * r / R - n ==")
CLIP, N_PUNCH = 10.0, 11


def s_max(R, pause, hold, r=RATE0):
    return (CLIP - pause - hold) * r / R - N_PUNCH


R_S, R_T = LAWS[S][2], LAWS[T][2]
base = s_max(R_S, 0.0, 0.3)
d_hold = base - s_max(R_S, 0.0, 2.2)
d_ratio = s_max(R_T, 0.0, 0.3) - base
d_pause = base - s_max(R_S, 0.6, 0.3)
print(f"  base (stand-in mean {R_S:.3f}, pause 0, hold 0.3 s): {base:.1f} English setup syllables")
for h, tag in ((0.3, "0.3 s (immediate-laugh window)"), (1.3, "1.3 s (Chinese mean start gap)"), (2.2, "2.2 s (French mean start gap)")):
    print(f"  hold {tag}: {s_max(R_S, 0.0, h):.1f}")
print(f"  swing from hold 0.3->2.2: {d_hold:.2f}; ratio law stand-in->tri(1.0,1.44,1.67): {d_ratio:.2f}; pause 0->0.6: {d_pause:.2f}")
rank = sorted([("hold", d_hold), ("ratio", d_ratio), ("pause", d_pause)], key=lambda x: -x[1])
check("P5", [k for k, _ in rank] == ["hold", "ratio", "pause"] and abs(d_hold - 9.5) <= 1.5 and abs(d_ratio - 6.3) <= 1.5 and abs(d_pause - 3.0) <= 1.5,
      f"swings hold {d_hold:.2f}, ratio {d_ratio:.2f}, pause {d_pause:.2f}; rank {[k for k, _ in rank]}")

print("== Part E: BREAK scenario, ratio-law shift by window length ==")
shifts = {}
for w in (2.0, 2.8, 3.5):
    ns = {l: n_safe(l, window=w) for l in LAWS}
    shifts[w] = max(ns[U], ns[T]) - ns[S]
    print(f"  window {w}: n_safe " + ", ".join(f"{l.split('(')[0].strip()}={v}" for l, v in ns.items()) + f"; shift {shifts[w]}")
check("P6", shifts[2.0] <= 1 and shifts[2.8] <= 1 and shifts[3.5] == 2, f"shifts {shifts}")

print("== Part F: scripted voice at a fixed pace (stress case) ==")
for r in (6.2, 6.63, 7.7, 8.5):
    print(f"  fixed voice {r} syll/s: n_safe {n_safe(S, rates=(r,))}, n* {n_star(S, rates=(r,))}")
check("P7", n_safe(S, rates=(6.63,)) == 9, f"n_safe at 6.63 = {n_safe(S, rates=(6.63,))}")

print("== Does the real-vs-stand-in difference change a conclusion? ==")
print(f"  ratio law only: n_safe {n_safe(S)} -> {n_safe(U)}/{n_safe(T)} ({n_safe(U)-n_safe(S):+d}/{n_safe(T)-n_safe(S):+d}): the stand-in is the conservative side, so its cap of 11 stays safe but is 1-2 syllables tight.")
print(f"  turn-gap pause 0.208 s: n_safe {n_safe(S)} -> {n_safe(S, pause=0.208)}; pause 0.6 s: -> {n_safe(S, pause=0.6)}")
print(f"  rate: spread N(7.7,1.15) drops fit(11) to {fit(11, S, rates=rg):.2f}; a 6.63 syll/s voice drops n_safe to {n_safe(S, rates=(6.63,))}.")
print(f"  laughter hold choice moves the setup budget by {d_hold:.1f} syllables, the most of the three inputs.")

held = sum(ok for _, ok in checks)
print(f"predictions held: {held}/{len(checks)}; missed: {[n for n, ok in checks if not ok]}")
print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)} pre-registered predictions held; "
      f"ratio-law swap moves n_safe {n_safe(S)} to {n_safe(U)}/{n_safe(T)}, rate spread drops fit(11) to {fit(11, S, rates=rg):.2f}, "
      f"hold choice swings setup budget {d_hold:.1f} syllables")
