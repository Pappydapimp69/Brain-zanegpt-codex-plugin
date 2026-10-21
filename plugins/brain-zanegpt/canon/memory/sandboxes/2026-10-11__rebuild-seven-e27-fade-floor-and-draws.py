"""Rebuild of seven E27 (fading call needs a floor; night step must draw a
constant number of values). Own fixture: call chance 0.8 x 0.7^n (not 0.9 x
0.6^n), floor 0.2, a 3-night hearing window (not 2). Seed check uses a real
PRNG (random.Random) and compares a downstream stream (weather rolls on
nights 0-9) between two runs from the same seed that differ only in whether a
member goes missing on night 2 and is found on night 5.
PREDICTIONS (written before running):
 P1 unfloored call is under 0.05 by night 8 and the 3-night hear chance from
    night 8 is under 0.15 (a hidden time window appears)
 P2 floored 3-night hear chance never drops below 1-(1-0.2)^3 = 0.488
 P3 conditional draws (call+bearing only while missing): the downstream
    weather stream differs between the two runs
 P4 unconditional draws: the weather stream is identical
"""
import random
def call(n, floor): return max(floor, 0.8*0.7**n)
def hear3(n, floor): return 1 - (1-call(n, floor))*(1-call(n+1, floor))*(1-call(n+2, floor))
un8, h8 = call(8, 0), hear3(8, 0)
fl_min = min(hear3(n, 0.2) for n in range(40))
def weather(conditional, missing):
    rng = random.Random(4242); out = []
    for night in range(10):
        is_missing = missing and 2 <= night < 5
        if conditional:
            if is_missing:
                rng.random(); rng.random()      # call, bearing
        else:
            c = rng.random(); b = rng.random()  # always drawn, used only if missing
        out.append(round(rng.random(), 6))      # weather
    return out
cdiff = weather(True, False) != weather(True, True)
usame = weather(False, False) == weather(False, True)
print(f"unfloored n8 {un8:.4f} hear3 {h8:.3f}; floored min hear3 {fl_min:.3f}")
print(f"conditional streams differ: {cdiff}; unconditional identical: {usame}")
checks = [un8 < 0.05 and h8 < 0.15, fl_min >= 0.488 - 1e-9, cdiff, usame]
held = sum(checks)
print(f"RESULT: {'PASS' if held == 4 else 'FAIL'} {held}/4 predictions held; unfloored n8 {un8:.4f} "
      f"hear3 {h8:.3f}; floored min hear3 {fl_min:.3f}; conditional desync {cdiff}; constant in sync {usame}")
