"""Sandbox: PKCE S256 against the RFC 7636 Appendix B vector, plus an interception model.

Source facts (RFC 7636, fetched from rfc-editor.org and grep-confirmed): Appendix B octets, verifier
dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk, challenge E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM;
code-verifier = 43*128 unreserved characters.

PREDICTION (written before the first run):
  P1. base64url(32 RFC octets) with padding stripped == the RFC verifier, and
      base64url(sha256(verifier ASCII)) == the RFC challenge, byte for byte.
  P2. Standard base64 with '=' padding and +/ gives a DIFFERENT challenge string (44 chars, ends '=').
  P3. Interception: an attacker holding code + challenge redeems it under method=plain (verifier = challenge)
      but is rejected under S256.
  P4. Length: 32 octets -> 43 chars (valid), 31 octets -> 42 chars (invalid), 96 octets -> 128 chars (valid),
      97 octets -> 130 chars (invalid).
  P5. (break) An early-exit comparison at the token endpoint leaks hash-prefix matches, but that gives no
      path to the verifier: finding a candidate whose hash matches k leading challenge bytes costs about
      256^k candidates (k=1: within 4x of 256; k=2: within 4x of 65536), i.e. no incremental refinement.
"""
import base64, hashlib, hmac

OCTETS = [116, 24, 223, 180, 151, 153, 224, 37, 79, 250, 96, 125, 216, 173, 187, 186, 22, 212, 37, 77, 105, 214,
          191, 240, 91, 88, 5, 88, 83, 132, 141, 121]
RFC_VERIFIER = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
RFC_CHALLENGE = "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"
UNRESERVED = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~")

def b64u(b):
    return base64.urlsafe_b64encode(b).decode().rstrip("=")

def s256(v):
    return b64u(hashlib.sha256(v.encode("ascii")).digest())

def valid_verifier(v):
    return 43 <= len(v) <= 128 and set(v) <= UNRESERVED

res = []
# S1
verifier = b64u(bytes(OCTETS))
challenge = s256(verifier)
digest = list(hashlib.sha256(verifier.encode()).digest())
print("S1 verifier match:", verifier == RFC_VERIFIER, "challenge match:", challenge == RFC_CHALLENGE, "digest[0..3]:", digest[:4])
res.append(verifier == RFC_VERIFIER and challenge == RFC_CHALLENGE and digest[:4] == [19, 211, 30, 150])

# S2
std = base64.b64encode(hashlib.sha256(verifier.encode()).digest()).decode()
print("S2 standard base64: %s (len %d) differs: %s" % (std, len(std), std != RFC_CHALLENGE))
res.append(std != RFC_CHALLENGE and len(std) == 44 and std.endswith("="))

# S3 interception
def make_server(method):
    store = {}
    def authorize(challenge_value):
        store["code"] = ("CODE-1", challenge_value)
        return "CODE-1"
    def token(code, verifier_in):
        c, ch = store["code"]
        if code != c or not valid_verifier(verifier_in):
            return False
        expect = verifier_in if method == "plain" else s256(verifier_in)
        return hmac.compare_digest(expect.encode(), ch.encode())
    return authorize, token

for method in ("plain", "S256"):
    auth, tok = make_server(method)
    ch = RFC_VERIFIER if method == "plain" else RFC_CHALLENGE
    code = auth(ch)
    legit = tok(code, RFC_VERIFIER)
    attack = tok(code, ch)   # attacker saw code and challenge only
    print("S3 %-5s legit redeem=%s attacker (verifier := observed challenge) redeem=%s" % (method, legit, attack))
    res.append(legit and (attack if method == "plain" else not attack))

# S4 lengths
cases = {32: True, 31: False, 96: True, 97: False}
ok4 = True
for n, want in cases.items():
    v = b64u(bytes(range(n)) if n < 256 else bytes(n))
    got = valid_verifier(v)
    print("S4 %3d octets -> %3d chars valid=%s" % (n, len(v), got))
    ok4 &= (got == want)
res.append(ok4)

# S5 break: prefix-match cost
def first_k_match(k, limit=1 << 22):
    target = base64.urlsafe_b64decode(RFC_CHALLENGE + "=")[:k]
    for i in range(limit):
        cand = ("probe-%d" % i)
        if hashlib.sha256(cand.encode()).digest()[:k] == target:
            return i + 1
    return None
c1 = first_k_match(1); c2 = first_k_match(2)
print("S5 candidates until k-byte hash prefix matches: k=1 -> %s, k=2 -> %s (256^k = 256, 65536)" % (c1, c2))
res.append(c1 is not None and c2 is not None and 64 <= c1 <= 1024 and 16384 <= c2 <= 262144 and c2 / c1 > 20)

print("RESULT: %s RFC 7636 Appendix B verifier and challenge reproduced exactly; padded standard base64 differs; plain redeemed by an interceptor, S256 not; 43-128 length bounds hold at 32/31/96/97 octets; hash-prefix leak costs %s then %s candidates (no refinement)"
      % ("PASS" if all(res) else "FAIL", c1, c2))
