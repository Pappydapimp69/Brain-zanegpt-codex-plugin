# Prediction (before run): (a) 32 random-looking bytes encode to a 43-char base64url verifier (RFC 7636 minimum);
# (b) an attacker holding only the intercepted code fails at the token endpoint under S256 and under plain-without-challenge;
# (c) under method=plain the observed challenge IS the verifier, so redemption succeeds; (d) S256 with a 5-digit numeric
# verifier (BREAK) is recovered from the public challenge in <=100000 guesses, i.e. the hash is no barrier to low entropy;
# (e) a byte-by-byte early-exit compare against a plain verifier lets hill-climbing recover a 43-char verifier in
# <= 43*64 guesses, while the same leak on the S256 hash prefix does no better than blind guessing (<= 2 chars of progress).
import base64, hashlib, hmac, itertools
def b64u(b): return base64.urlsafe_b64encode(b).rstrip(b"=").decode()
def s256(v): return b64u(hashlib.sha256(v.encode("ascii")).digest())
class AuthServer:
    def __init__(s): s.codes = {}
    def authorize(s, challenge, method): s.codes["CODE1"] = (challenge, method); return "CODE1"
    def token(s, code, verifier):
        if code not in s.codes: return False
        ch, m = s.codes[code]
        if verifier is None: return False
        cand = verifier if m == "plain" else s256(verifier)
        ok = hmac.compare_digest(cand.encode(), ch.encode()); 
        if ok: del s.codes[code]
        return ok
seed_bytes = hashlib.sha256(b"fixed-demo-seed").digest()          # deterministic stand-in for 32 CSPRNG bytes
V = b64u(seed_bytes)
r = {}
r["len43"] = len(V) == 43
a = AuthServer(); c = a.authorize(s256(V), "S256")
r["s2_no_verifier"] = a.token(c, None) is False
r["s2_wrong_verifier"] = a.token(c, b64u(hashlib.sha256(b"x").digest())) is False
r["s1_legit"] = a.token(c, V) is True
# plain: attacker sees the authorization request, so challenge==verifier
a = AuthServer(); c = a.authorize(V, "plain"); observed = V
r["s3_plain_redeemed"] = a.token(c, observed) is True
# S256, attacker sees challenge, tries a 1e5-word dictionary of other values: no hit for the 43-char verifier
a = AuthServer(); chal = s256(V)
hits = sum(1 for i in range(100000) if s256(f"guess{i}") == chal)
r["s4_dict_hits"] = hits == 0
# BREAK: low-entropy verifier
lowV = "48213"; chal_low = s256(lowV); g = 0
for i in range(100000):
    g += 1
    if s256(f"{i:05d}") == chal_low: break
r["s5_low_entropy_guesses"] = g
# early-exit compare leak: count matching prefix
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
def prefix_len(a, b):
    n = 0
    for x, y in zip(a, b):
        if x != y: break
        n += 1
    return n
def climb(oracle, L, secretlen):
    known = ""; guesses = 0
    while len(known) < L:
        best = None
        for ch in ALPHA:
            guesses += 1
            if oracle(known + ch + "A" * (secretlen - len(known) - 1)) > len(known): best = ch; break
        if best is None: break
        known += best
    return known, guesses
leak_plain = lambda guess: prefix_len(guess, V)                    # leaky compare on the plain verifier
k, gp = climb(leak_plain, 43, 43)
leak_hash = lambda guess: prefix_len(s256(guess), chal)            # same leak on the S256 digest prefix
k2, gh = climb(leak_hash, 43, 43)
r["s6_plain_recovered"] = (k == V, gp)
r["s6_s256_progress"] = len(k2)
for k_, v_ in r.items(): print(k_, v_)
ok = (r["len43"] and r["s2_no_verifier"] and r["s2_wrong_verifier"] and r["s1_legit"] and r["s3_plain_redeemed"]
      and r["s4_dict_hits"] and r["s5_low_entropy_guesses"] <= 100000 and r["s6_plain_recovered"][0] and gp <= 43*64 and len(k2) <= 2)
print(f"RESULT: {'PASS' if ok else 'FAIL'} len={len(V)} plain_redeemed={r['s3_plain_redeemed']} low_entropy_guesses={g} plain_leak_climb={gp} s256_leak_progress={len(k2)}")
