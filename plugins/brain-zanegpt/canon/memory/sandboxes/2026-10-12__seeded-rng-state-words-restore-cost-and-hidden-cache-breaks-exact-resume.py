"""Seeded RNG save: full state words vs {seed,count}, and the hidden-state boundary.
Kernels/entries exercised: ideas:SYSTEM/seeded-rng (save state words, O(1) load),
the-game-prologue/E1 (seed+count restore replays count rolls), and
seeded-rng-save-load-vs-shared-stream-coupling/E1 (one shared stream couples consumers).
Prediction (before first run): restoring from state words costs 4 word copies regardless of
draws, seed+count costs exactly count rolls; both resume exactly for plain integer rolls;
a gaussian roller with a cached spare value resumes WRONG from state words alone unless the
cache is saved too (seed+count still wrong unless the count counts raw rolls); an extra
consumer on the shared stream shifts later rolls in a majority of ticks, separate streams in 0."""
M = 0xFFFFFFFF

class Sfc32:
    def __init__(s, seed):
        s.a, s.b, s.c, s.d = 0x9E3779B9, 0x243F6A88, 0xB7E15162, 1
        s.s = seed & M
        s.a ^= s.s; s.b ^= (s.s * 3) & M
        s.n = 0
        for _ in range(12): s.next()
        s.n = 0
    def next(s):
        t = (s.a + s.b + s.d) & M
        s.d = (s.d + 1) & M
        s.a = s.b ^ (s.b >> 9)
        s.b = (s.c + (s.c << 3)) & M
        s.c = (((s.c << 21) | (s.c >> 11)) & M) + t & M
        s.n += 1
        return t
    def state(s): return (s.a, s.b, s.c, s.d)
    def load(s, st): s.a, s.b, s.c, s.d = st

class Gauss:
    """Box-Muller-like pair generator that caches the second value (hidden state)."""
    def __init__(s, rng): s.r, s.spare = rng, None
    def next(s):
        if s.spare is not None:
            v, s.spare = s.spare, None
            return v
        u, w = s.r.next() / M, s.r.next() / M
        s.spare = round(u - w, 9)
        return round(u + w, 9)

ok = {}
# 1) restore cost, counted in rolls/word copies (no wall-clock)
seed = 12345
for n in (10, 1000, 100000):
    g = Sfc32(seed)
    for _ in range(n): g.next()
    st = g.state()
    r = Sfc32(0); r.load(st)               # state words: 4 copies
    r2 = Sfc32(seed)                        # seed+count: replay n rolls
    for _ in range(n): r2.next()
    same = r.state() == r2.state() == g.state()
    print(f"1) n={n}: state-words restore=4 copies, seed+count restore={n} rolls, equal={same}")
    ok[f"restore{n}"] = same
# 2) plain integer rolls resume exactly
g = Sfc32(seed)
for _ in range(50): g.next()
st = g.state(); a = [g.next() for _ in range(10)]
r = Sfc32(0); r.load(st); b = [r.next() for _ in range(10)]
print("2) integer resume exact:", a == b); ok["int_resume"] = a == b
# 3) BREAK: gaussian with cached spare, save taken between the pair
g = Sfc32(seed); gg = Gauss(g)
for _ in range(7): gg.next()               # odd count -> spare pending
st = g.state(); spare = gg.spare
ref = [gg.next() for _ in range(6)]
r = Sfc32(0); r.load(st); rg = Gauss(r)    # words only: spare lost
bad = [rg.next() for _ in range(6)]
r = Sfc32(0); r.load(st); rg = Gauss(r); rg.spare = spare   # words + spare
good = [rg.next() for _ in range(6)]
print(f"3) spare pending={spare is not None}; words-only exact={bad == ref}; words+spare exact={good == ref}")
ok["hidden_breaks"] = spare is not None and bad != ref
ok["hidden_fixed"] = good == ref
# 3b) seed+count with count of gauss calls (not raw rolls) also wrong
g2 = Sfc32(seed); gg2 = Gauss(g2)
for _ in range(7): gg2.next()
r = Sfc32(seed); rg = Gauss(r)
for _ in range(7): rg.next()               # replaying gauss calls works only if count is gauss calls
alt = [rg.next() for _ in range(6)]
print("3b) seed+gauss-call-count replay exact:", alt == ref)
ok["seedcount_calls"] = alt == ref
# 4) shared stream coupling vs separate streams
def run(extra, split):
    spread = Sfc32(1); other = Sfc32(2) if split else spread
    out = []
    for t in range(20):
        if extra and t % 2 == 0: other.next()
        out.append(spread.next() % 4)
    return out
sh = sum(x != y for x, y in zip(run(False, False), run(True, False)))
sp = sum(x != y for x, y in zip(run(False, True), run(True, True)))
print(f"4) shared stream changed {sh}/20 ticks, split streams {sp}/20")
ok["shared"] = sh >= 10 and sp == 0
print("ok:", ok)
passed = all(ok.values())
print(("RESULT: PASS" if passed else "RESULT: FAIL") + f" state words O(1) restore exact; hidden spare cache lost words-only (exact={bad == ref}), fixed with spare; shared stream {sh}/20 vs split {sp}/20")
