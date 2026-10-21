"""Sandbox: sign-the-payload AND compare-in-constant-time, two independent properties.

PREDICTION (written before the first run):
  P1. Unsigned submission: a forged score is accepted with 0 queries.
  P2. HMAC-SHA256 + early-exit compare, with the comparison step count as the oracle (a deterministic
      stand-in for timing): an attacker recovers a valid 32-byte tag for a forged score in at most
      256*32 = 8192 queries (expected about 4096 for the average byte value), no secret needed.
  P3. Same HMAC + a comparison that always does 32 steps: the same attack recovers the correct tag in 0 of 5 trials
      (its guess is wrong) - the oracle is flat.
  P4. (break) Constant-time compare over an UNKEYED sha256 of the payload: forged score accepted with 0 queries.
  P5. (break) HMAC over the score only: a valid tag replayed onto another player is accepted; signing the
      full payload rejects it.
  P6. (break) HMAC over naive concatenation without delimiters: moving a character across the field boundary
      keeps the tag valid; canonical sorted-key JSON rejects it.
"""
import hmac, hashlib, json

SECRET = b"server-only-secret-0123456789abcdef"

def canon(p):
    return json.dumps(p, sort_keys=True, separators=(",", ":")).encode()

def tag_full(p):
    return hmac.new(SECRET, canon(p), hashlib.sha256).digest()

def tag_score_only(p):
    return hmac.new(SECRET, str(p["score"]).encode(), hashlib.sha256).digest()

def tag_concat(p):
    return hmac.new(SECRET, (p["player"] + str(p["level"])).encode(), hashlib.sha256).digest()

def tag_unkeyed(p):
    return hashlib.sha256(canon(p)).digest()

class Counter:
    steps = 0

def cmp_early(a, b):
    """Early-exit comparison; Counter.steps is the deterministic timing signal."""
    for x, y in zip(a, b):
        Counter.steps += 1
        if x != y:
            return False
    return len(a) == len(b)

def cmp_const(a, b):
    """Always inspects every byte; steps are flat. Cross-checked against hmac.compare_digest."""
    acc = len(a) ^ len(b)
    for i in range(max(len(a), len(b))):
        Counter.steps += 1
        acc |= (a[i] if i < len(a) else 0) ^ (b[i] if i < len(b) else 0)
    assert (acc == 0) == hmac.compare_digest(a, b)
    return acc == 0

def server(tagger, cmp):
    def verify(payload, tag):
        Counter.steps = 0
        ok = cmp(tagger(payload), tag)
        return ok, Counter.steps
    return verify

def attack(verify, payload, length=32):
    """Recover the tag byte by byte using step count as the oracle. Returns (guess, queries)."""
    known = b""
    q = 0
    for i in range(length):
        best, best_steps = 0, -1
        for v in range(256):
            cand = known + bytes([v]) + bytes(length - i - 1)
            ok, steps = verify(payload, cand)
            q += 1
            if ok:
                return cand, q
            if steps > best_steps:
                best, best_steps = v, steps
        known += bytes([best])
    return known, q

forged = {"player": "mallory", "level": 3, "score": 999999}
res = []

# S1 unsigned
accepted = True  # no check exists
print("S1 unsigned: forged accepted with 0 queries ->", accepted)
res.append(accepted)

# S2 early-exit compare
v = server(tag_full, cmp_early)
guess, q = attack(v, forged)
ok2 = v(forged, guess)[0] and guess == tag_full(forged) and q <= 8192
print("S2 early-exit: recovered tag valid=%s queries=%d (bound 8192, brute force 2^256)" % (v(forged, guess)[0], q))
res.append(ok2)

# S3 constant-time compare, 5 different forged scores
wrong = 0
for s in (1, 2, 3, 4, 5):
    f = dict(forged, score=s)
    v3 = server(tag_full, cmp_const)
    g, _ = attack(v3, f)
    if not v3(f, g)[0]:
        wrong += 1
print("S3 constant-time: attack failed in %d of 5 trials" % wrong)
res.append(wrong == 5)

# S4 unkeyed hash with constant-time compare
v4 = server(tag_unkeyed, cmp_const)
acc4 = v4(forged, tag_unkeyed(forged))[0]
print("S4 unkeyed sha256 + constant-time compare: forged accepted with 0 queries ->", acc4)
res.append(acc4)

# S5 score-only signing
alice = {"player": "alice", "level": 3, "score": 500}
bob = {"player": "bob", "level": 9, "score": 500}
t = tag_score_only(alice)
v5 = server(tag_score_only, cmp_const)
v5full = server(tag_full, cmp_const)
r5 = v5(bob, t)[0] and not v5full(bob, tag_full(alice))[0]
print("S5 score-only tag replayed onto bob accepted=%s; full-payload rejects=%s" % (v5(bob, t)[0], not v5full(bob, tag_full(alice))[0]))
res.append(r5)

# S6 delimiter ambiguity
p1 = {"player": "ab", "level": 12, "score": 1}
p2 = {"player": "ab1", "level": 2, "score": 1}
v6 = server(tag_concat, cmp_const)
acc6 = v6(p2, tag_concat(p1))[0]
rej6 = not v5full(p2, tag_full(p1))[0]
print("S6 concat without delimiter accepts moved boundary=%s; canonical JSON rejects=%s" % (acc6, rej6))
res.append(acc6 and rej6)

print("RESULT: %s early-exit compare leaked the full tag in %d queries, constant-time stopped it (%d/5), and keyed-but-score-only, unkeyed and delimiter-free signing each still accepted forgeries" % ("PASS" if all(res) else "FAIL", q, wrong))
