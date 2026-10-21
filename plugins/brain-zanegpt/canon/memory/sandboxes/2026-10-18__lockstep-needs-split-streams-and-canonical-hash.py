# Deterministic lockstep check: two clients, same seed and inputs.
# Kernel seeded-rng: one stream, state words saved, lockstep viable. Tests: shared vs split streams,
# insertion-order hashing (JS puts integer-like keys first, then strings in insertion order) vs sorted
# canonical hashing, and a mid-run save/load through the four state words.
M = 0xFFFFFFFF
class Sfc32:
    def __init__(s, a, b, c, d): s.w = [a & M, b & M, c & M, d & M]
    @classmethod
    def seed(cls, n):
        r = cls(0, n, n * 3 + 1, 1)
        for _ in range(12): r.next()
        return r
    def next(s):
        a, b, c, d = s.w
        t = (a + b + d) & M
        d = (d + 1) & M
        a = b ^ (b >> 9)
        b = (c + (c << 3)) & M
        c = (((c << 21) | (c >> 11)) & M) + t & M
        s.w = [a, b, c, d]
        return t / 4294967296.0
    def state(s): return list(s.w)

def js_order(d):                       # key order JSON.stringify would use
    ints = sorted((k for k in d if str(k).isdigit()), key=int)
    return ints + [k for k in d if not str(k).isdigit()]
def h_insertion(state):
    s = ",".join(f"{k}:{state[k]}" for k in js_order(state))
    return sum((i + 1) * ord(ch) for i, ch in enumerate(s)) % 1000003
def h_sorted(state):
    s = ",".join(f"{k}:{state[k]}" for k in sorted(map(str, state)))
    return sum((i + 1) * ord(ch) for i, ch in enumerate(s)) % 1000003

def run(ticks, rng, cosmetic_rng=None, order=("hp", "gold")):
    st = {}
    for k in order: st[k] = 0
    log = []
    for t in range(ticks):
        st["hp"] += int(rng.next() * 6) + 1
        st["gold"] += int(rng.next() * 3)
        if cosmetic_rng is not None: cosmetic_rng.next()     # particle jitter
        log.append(dict(st))
    return log

def first_diff(a, b, h):
    for i, (x, y) in enumerate(zip(a, b)):
        if h(x) != h(y): return i
    return None

N = 50
A = run(N, Sfc32.seed(7))
# 1) identical clients, shared stream
B1 = run(N, Sfc32.seed(7))
d1 = first_diff(A, B1, h_sorted)
# 2) client B draws cosmetic rolls from the SAME stream between sim rolls
shared = Sfc32.seed(7)
def run_shared_cosmetic(ticks, rng):
    st = {"hp": 0, "gold": 0}; log = []
    for t in range(ticks):
        st["hp"] += int(rng.next() * 6) + 1
        rng.next()                                  # cosmetic draw on the shared stream
        st["gold"] += int(rng.next() * 3)
        log.append(dict(st))
    return log
B2 = run_shared_cosmetic(N, shared)
d2 = first_diff(A, B2, h_sorted)
# 3) cosmetic draws from a SEPARATE stream
B3 = run(N, Sfc32.seed(7), cosmetic_rng=Sfc32.seed(99))
d3 = first_diff(A, B3, h_sorted)
# 4) same logical state built in a different key order, with integer-like keys present
def with_int_keys(order):
    d = {}
    for k in order: d[k] = 5
    return d
s1 = with_int_keys(("10", "hp", "2", "gold")); s2 = with_int_keys(("gold", "2", "hp", "10"))
ins_equal = h_insertion(s1) == h_insertion(s2); sort_equal = h_sorted(s1) == h_sorted(s2)
# 5) save/load through state words mid-run == continuing
r = Sfc32.seed(7); run(20, r); saved = r.state()
cont = [r.next() for _ in range(5)]
r2 = Sfc32(*saved); resumed = [r2.next() for _ in range(5)]
# 6) BREAK: gaussian-style wrapper cache not in words (brainwork/E127)
class Gauss:
    def __init__(s, rng): s.r = rng; s.spare = None
    def next(s):
        if s.spare is not None: v, s.spare = s.spare, None; return v
        a, b = s.r.next(), s.r.next(); s.spare = b - 0.5; return a - 0.5
g = Gauss(Sfc32.seed(7)); g.next()                  # saved mid-pair
words = g.r.state(); spare = g.spare
cont_g = [g.next() for _ in range(4)]
g2 = Gauss(Sfc32(*words)); words_only = [g2.next() for _ in range(4)]
g3 = Gauss(Sfc32(*words)); g3.spare = spare; with_spare = [g3.next() for _ in range(4)]
print("desync tick: identical", d1, "| shared cosmetic", d2, "| split streams", d3)
print("key-order hash equal: insertion", ins_equal, "sorted", sort_equal)
print("save/load words resume equal:", cont == resumed, "| gauss words-only equal:", cont_g == words_only, "| with spare:", cont_g == with_spare)
ok = (d1 is None and d2 is not None and d2 <= 2 and d3 is None and (not ins_equal) and sort_equal
      and cont == resumed and cont_g != words_only and cont_g == with_spare)
print(f"RESULT: {'PASS' if ok else 'FAIL'} lockstep desync at tick {d2} with shared cosmetic draws vs none with split streams; insertion-order hash differs for equal state ({not ins_equal}) sorted equal; words restore exact; gaussian spare lost on words-only ({cont_g != words_only})")
