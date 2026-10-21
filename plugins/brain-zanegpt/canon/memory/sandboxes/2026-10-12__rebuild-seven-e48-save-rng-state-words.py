"""Blind rebuild of seven E48 (save RNG state words, not seed + roll count).
Own fixture: xoshiro128** (4 x 32-bit state words, not the original's
generator). A 'game' of 500 turns; each turn the visible code calls draw() once
and counts it; a particle callback (hidden) draws a variable 0-3 times keyed on
the previous value, and NOT counted. Save at turn 250 three ways; resume;
compare the next 250 values to the uninterrupted run.
PREDICTION (before running): state words -> identical, 0 replay steps;
seed + counted total -> diverges; seed + true total -> identical but replays
every draw so far; json.dumps without sort_keys gives different hashes for equal
states built in different key order, sort_keys gives one hash. Break scenario:
no hidden draws at all -> seed + count also restores exactly (the defect needs
an uncounted draw), and a state word saved as a float through JSON at 2**53+
would corrupt - 32-bit words survive JSON intact.
"""
import json, hashlib, sys
print("python", sys.version.split()[0])
M = 0xffffffff
rotl = lambda x, k: ((x << k) | (x >> (32-k))) & M
class X:
    def __init__(s, seed):
        z = seed & M; s.s = []
        for _ in range(4):  # splitmix32-ish seeding
            z = (z + 0x9e3779b9) & M; v = z
            v = ((v ^ (v >> 16)) * 0x85ebca6b) & M; v = ((v ^ (v >> 13)) * 0xc2b2ae35) & M
            s.s.append(v ^ (v >> 16))
        s.n = 0
    def next(s):
        a, b, c, d = s.s; r = (rotl((b*5) & M, 7)*9) & M
        t = (b << 9) & M; c ^= a; d ^= b; b ^= c; a ^= d; c ^= t; d = rotl(d, 11)
        s.s = [a, b, c, d]; s.n += 1; return r
def play(g, turns, hidden, log, counted):
    for _ in range(turns):
        v = g.next(); counted[0] += 1; log.append(v)
        if hidden:
            for _ in range(v % 4): g.next()
def scenario(hidden):
    full = []; g = X(1234); play(g, 500, hidden, full, [0])
    g = X(1234); c = [0]; first = []; play(g, 250, hidden, first, c)
    words = json.loads(json.dumps(g.s)); true_n = g.n; counted = c[0]
    r = {}
    h = X(0); h.s = list(words); tail = []; play(h, 250, hidden, tail, [0]); r['words'] = (first+tail == full, 0)
    h = X(1234)
    for _ in range(counted): h.next()
    tail = []; play(h, 250, hidden, tail, [0]); r['seed+counted'] = (first+tail == full, counted)
    h = X(1234)
    for _ in range(true_n): h.next()
    tail = []; play(h, 250, hidden, tail, [0]); r['seed+true'] = (first+tail == full, true_n)
    return r, counted, true_n
ok = True
r, c, n = scenario(True)
print("hidden draws:", r, "counted", c, "true", n)
ok &= r['words'] == (True, 0) and not r['seed+counted'][0] and r['seed+true'][0]
r2, c2, n2 = scenario(False)
print("break, no hidden draws:", r2)
nohidden_ok = r2['seed+counted'][0]
a = {"seed": 1, "rng": [1, 2, 3, 4], "turn": 9}; b = {"turn": 9, "rng": [1, 2, 3, 4], "seed": 1}
H = lambda o, sk: hashlib.sha256(json.dumps(o, sort_keys=sk).encode()).hexdigest()[:12]
plain_split = H(a, False) != H(b, False); sorted_same = H(a, True) == H(b, True)
print("plain json splits equal states:", plain_split, "| sorted keys one hash:", sorted_same)
ok &= plain_split and sorted_same and nohidden_ok
print(f"RESULT: {'PASS' if ok else 'FAIL'} words exact 0 replay; seed+counted({c} of {n}) diverged={not r['seed+counted'][0]}; seed+true replays {n}; no-hidden seed+count exact={nohidden_ok}")
