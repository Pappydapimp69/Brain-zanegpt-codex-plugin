# Deterministic sandbox: age gate vs validity guard on a RAMP schedule (dwells 1,2,...,20).
# PREDICTION (before run): state changes at triangular-number ticks. Every (sight tick s, age a in 1..8)
# is one press; it is VALID iff no change in (s, s+a]. Validity guard scores (wrong,lost)=(0,0) by
# construction. For age gate thr t in {0,2,4,8}: wrong = accepted(a<=t) & invalid, lost = rejected(a>t) & valid.
# Expect wrong+lost > 0 for EVERY t in 0..8 (none matches validity), lost falling and wrong rising with t;
# t=0 loses all valid presses, t=8 accepts all so wrong = all invalid.
changes = set(n * (n + 1) // 2 for n in range(1, 21))   # 1,3,6,10,...,210
T = 200
AGES = range(1, 9)

def valid(s, a):
    return not any(c in changes for c in range(s + 1, s + a + 1))

presses = [(s, a) for s in range(T) for a in AGES]
nvalid = sum(valid(s, a) for s, a in presses)

def score_gate(t):
    wrong = sum(1 for s, a in presses if a <= t and not valid(s, a))
    lost = sum(1 for s, a in presses if a > t and valid(s, a))
    return wrong, lost

res = {t: score_gate(t) for t in range(0, 9)}
for t, (w, l) in res.items():
    print("age gate", t, "wrong", w, "lost", l)
assert all(w + l > 0 for w, l in res.values())          # breaker: try every threshold
assert res[0][0] == 0 and res[0][1] == nvalid
assert res[8][1] == 0 and res[8][0] == len(presses) - nvalid
vw = sum(1 for s, a in presses if valid(s, a) is False and valid(s, a))  # validity accepts iff valid
print("validity (0,0); valid presses", nvalid, "of", len(presses))
ok = all(w + l > 0 for w, l in res.values()) and vw == 0
print("RESULT:", "PASS" if ok else "FAIL", "best gate sum", min(w + l for w, l in res.values()), "vs validity 0")
