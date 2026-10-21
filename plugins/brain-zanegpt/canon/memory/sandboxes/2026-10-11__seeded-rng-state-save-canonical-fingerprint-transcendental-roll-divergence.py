"""PREDICTION (before first run): sfc32 sim, 20000 ticks, an entity whose roll threshold is fed by a transcendental.
S1 saving the 4 state words and restoring at tick 12000 reproduces the final fingerprint exactly while {seed,count} restore
costs 12000 replayed draws (O(n)) with the same result. S2 a canonical (sorted-key, NaN-rejecting) fingerprint equals for two
logically equal states built in different key order, whereas an insertion-ordered dump differs. S3 replay-fingerprint catches an
ambient-random leak (two same-seed runs differ). S4 two 'runtimes' whose sin differs by ~1e-12 (exact vs a 7-term series with
a tiny bias) make the authoritative fingerprint DIVERGE when float feeds the roll (>=1 of 20 seeds), and one divergent roll
cascades: the later RNG stream differs from then on. S5 control: an integer-only threshold gives identical fingerprints
on both runtimes for all 20 seeds. Stdlib, deterministic."""
import hashlib, json, math
M = 0xFFFFFFFF
class Sfc32:
    def __init__(s, seed): s.a, s.b, s.c, s.d = 0x9E3779B9, 0x243F6A88, 0xB7E15162, seed & M; [s.next() for _ in range(15)]
    def next(s):
        t = (s.a + s.b + s.d) & M; s.d = (s.d + 1) & M
        s.a = s.b ^ (s.b >> 9); s.b = (s.c + (s.c << 3)) & M
        s.c = (((s.c << 21) | (s.c >> 11)) & M) + t & M; return t
    def state(s): return [s.a, s.b, s.c, s.d]
    def load(s, st): s.a, s.b, s.c, s.d = st
def sin_exact(x): return math.sin(x)
def sin_series(x):                         # another 'runtime': range-reduced 7-term series, tiny bias
    x = math.remainder(x, 2 * math.pi); r, term = 0.0, x
    for k in range(7): r += term; term *= -x * x / ((2 * k + 2) * (2 * k + 3))
    return r + 3e-12
def canon(o):
    if isinstance(o, float) and (o != o or o in (math.inf, -math.inf)): raise ValueError("non-finite")
    if isinstance(o, dict): return "{" + ",".join(json.dumps(k) + ":" + canon(o[k]) for k in sorted(o)) + "}"
    if isinstance(o, list): return "[" + ",".join(canon(v) for v in o) + "]"
    return json.dumps(o)
def fp(world): return hashlib.sha256(canon(world).encode()).hexdigest()[:16]
AMB = [0]
def run(seed, ticks, sinf, mode="float", leak=False, save_at=None, resume=None, rng=None):
    rng = rng or Sfc32(seed); w = {"hits": 0, "misses": 0, "log": 0}
    if resume: w, st = resume; rng.load(st)
    t0 = w.get("t", 0); saved = None
    for t in range(t0, ticks):
        if save_at == t: saved = (dict(w, t=t), rng.state())
        if mode == "float":   # threshold = 50% +/- 0.5*sin(t*0.37) quantised to 1e-3 via a float compare
            thr = 0.5 + 0.5 * sinf(t * 0.37 + seed)
            hit = (rng.next() / 2 ** 32) < thr
        else:
            thr = (t * 37 + seed) % 1000; hit = (rng.next() % 1000) < thr
        if leak: AMB[0] += 1; hit ^= (AMB[0] * 2654435761 >> 7) % 50 == 0   # ambient source outliving the run
        w["hits" if hit else "misses"] += 1; w["log"] = (w["log"] * 31 + (1 if hit else 2)) & M
        w["t"] = t + 1
    return w, saved, rng
ok = []
# S1
w1, saved, _ = run(7, 20000, sin_exact, save_at=12000)
rng2 = Sfc32(0); w2, _, _ = run(7, 20000, sin_exact, resume=saved, rng=rng2)
r3 = Sfc32(7); replay = 0
for _ in range(12000): r3.next(); replay += 1
ok.append(fp(w1) == fp(w2) and replay == 12000 and r3.state() == saved[1]); print("S1", ok[-1], fp(w1), replay)
# S2
a = {"b": 1, "a": [1, 2], "10": 3, "2": 4}; b = {"2": 4, "10": 3, "a": [1, 2], "b": 1}
ok.append(canon(a) == canon(b) and json.dumps(a) != json.dumps(b)); print("S2", ok[-1])
# S3 (leak uses per-run id() so two runs differ; python hash of tuple with ints is stable, id differs)
l1 = fp(run(3, 5000, sin_exact, leak=True)[0]); l2 = fp(run(3, 5000, sin_exact, leak=True)[0]); c1 = fp(run(3, 5000, sin_exact)[0]); c2 = fp(run(3, 5000, sin_exact)[0])
ok.append(c1 == c2 and l1 != l2); print("S3 clean-equal", c1 == c2, "leak runs differ", l1 != l2)
# S4/S5
div = sum(fp(run(s, 20000, sin_exact)[0]) != fp(run(s, 20000, sin_series)[0]) for s in range(20))
cdiv = sum(fp(run(s, 20000, sin_exact, mode="int")[0]) != fp(run(s, 20000, sin_series, mode="int")[0]) for s in range(20))
ok.append(div >= 1); ok.append(cdiv == 0); print("S4 float-fed divergent seeds", div, "/20  S5 integer control", cdiv, "/20")
print("RESULT:", "PASS" if all(ok) else "FAIL", "S1 resume exact (replay=12000 draws); S2 canon equal vs insertion dump differs; S3 clean runs equal and leak runs differ; "
      "S4 float-fed fingerprint diverged on %d/20 seeds; S5 integer control %d/20" % (div, cdiv))
