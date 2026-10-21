"""Train kernel (declare): SYSTEM/determinism/seeded-rng, quoted in prose by
the-game-prologue E1 (canonicalize state before hashing - sorted keys, reject
non-finite, normalise -0; save PRNG state words; grep-guard transcendental math
in the sim). Re-verified here with my own fixture, pushing each part:
 1) hashing: equal states built in different key order, with -0.0 vs 0.0, and
    with NaN; plain json vs a canonical serializer;
 2) transcendentals: two correct-looking sin() implementations (libm math.sin
    vs a range-reduce-by-float-pi + 13th-order Taylor 'fast sin', as two engines
    might ship) driving a sim that branches on sin(x) > 0.5 over 100,000 steps;
 3) the grep guard, negative-controlled on a planted call and on an alias.
Deterministic, stdlib only.
PREDICTION (written before running): plain json gives different hashes for key
order and for -0.0 vs 0.0 and cannot hash NaN equal to itself; canonical gives
one hash for each equal pair and rejects NaN; the two sin()s differ in the last
bits on > 10% of large arguments and the branching sim diverges somewhere in
100,000 steps; the grep guard catches a planted Math.sin but MISSES an alias
(const s = Math['sin']) - a grep guard is a tripwire, not a proof.
ITERATION 1: the branch-only sim did NOT diverge (sin differed by <= 6.6e-10 on
every argument but no branch flipped in 100,000 steps, because sin never fed
back into state). ITERATION 2 PREDICTION (written before re-running): a sim
whose state feeds on sin (x = 3.9 x (1 - x) logistic step plus 1e-3 sin(1000 x))
diverges within 200 steps, and the branch-only sim still never does.
"""
import json, hashlib, math, re, sys
print("python", sys.version.split()[0])
H = lambda s: hashlib.sha256(s.encode()).hexdigest()[:12]
def canon(o):
    if isinstance(o, float):
        if not math.isfinite(o): raise ValueError("non-finite")
        return "0" if o == 0 else repr(o)
    if isinstance(o, dict): return "{" + ",".join(json.dumps(str(k)) + ":" + canon(o[k]) for k in sorted(o, key=str)) + "}"
    if isinstance(o, list): return "[" + ",".join(canon(v) for v in o) + "]"
    return json.dumps(o)
a = {"hp": 10, "pos": [1.0, 0.0], "rng": [1, 2, 3, 4]}
b = {"rng": [1, 2, 3, 4], "pos": [1.0, -0.0], "hp": 10}
plain_split = H(json.dumps(a)) != H(json.dumps(b)); canon_same = H(canon(a)) == H(canon(b))
nan_state = {"x": float("nan")}
plain_nan_self = nan_state == json.loads(json.dumps(nan_state))
try: canon(nan_state); canon_rejects = False
except ValueError: canon_rejects = True
print(f"plain json splits equal states {plain_split}; canonical one hash {canon_same}; NaN state equals its own round trip {plain_nan_self}; canonical rejects NaN {canon_rejects}")
PI = 3.141592653589793
def fast_sin(x):
    k = round(x / PI); r = x - k * PI
    s = r - r**3/6 + r**5/120 - r**7/5040 + r**9/362880 - r**11/39916800 + r**13/6227020800
    return -s if k % 2 else s
xs = [1000.0 + i * 7.31 for i in range(20000)]
diff = sum(math.sin(x) != fast_sin(x) for x in xs) / len(xs)
maxd = max(abs(math.sin(x) - fast_sin(x)) for x in xs)
def sim(sinf, steps=100000):
    x = 0.5; trace = 0
    for i in range(steps):
        x = (x * 1.000173 + 0.37) % 10000.0
        if sinf(x) > 0.5: trace = (trace * 31 + i) & 0xffffffff
    return trace
t1, t2 = sim(math.sin), sim(fast_sin)
def fb(sinf, steps=100000):
    x = 0.3141
    for i in range(steps):
        x = (3.9 * x * (1 - x) + 1e-3 * sinf(1000 * x)) % 1.0
        yield x
first = next((i for i, (u, v) in enumerate(zip(fb(math.sin), fb(fast_sin))) if u != v), None)
apart = next((i for i, (u, v) in enumerate(zip(fb(math.sin), fb(fast_sin))) if abs(u - v) > 0.1), None)
print(f"feedback sim: first bit difference at step {first}, states > 0.1 apart by step {apart}")
print(f"sin implementations differ on {diff:.3f} of large arguments (max {maxd:.2e}); branching sim traces equal {t1 == t2}")
BANNED = re.compile(r"Math\.(sin|cos|tan|exp|log|pow|atan2|asin|acos|atan)\b")
srcs = {"clean": "x = Math.sqrt(a) + Math.floor(b);", "planted": "y = Math.sin(t) * 2;", "alias": "const s = Math['sin']; y = s(t);"}
caught = {k: bool(BANNED.search(v)) for k, v in srcs.items()}
print("grep guard:", caught)
c = [plain_split, canon_same, not plain_nan_self, canon_rejects, diff > 0.10, t1 == t2 and apart is not None and apart <= 200,
     caught["planted"] and not caught["clean"], not caught["alias"]]
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} {sum(c)}/8; plain json splits equal states, canonical one hash; NaN never equals itself; sin impls differ on {diff:.1%} of args, branch-only sim traces {'diverge' if t1 != t2 else 'agree'}, feedback sim differs at step {first} and is > 0.1 apart by step {apart}; grep guard catches planted {caught['planted']}, misses alias {not caught['alias']}")
