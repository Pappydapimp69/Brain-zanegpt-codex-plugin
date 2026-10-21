# Simulate a gear pair meshing tooth by tooth: mesh step i puts pinion tooth i%a against gear tooth i%b.
# Claim to test: the distinct (pinion tooth, gear tooth) contact pairs number lcm(a,b) = a*b/g, the pattern repeats every lcm steps,
# and one chipped pinion tooth strikes b/g distinct gear teeth (all b only when g=1, the "hunting tooth" case).
# Prediction (before run): (17,40) g=1: 680 pairs, a chipped pinion tooth hits 40 gear teeth; (20,40) g=20: 40 pairs, chipped tooth hits 2;
# (18,42) g=6: 126 pairs, hits 7. Assumption: wear follows contact count only. Wrong if any brute count differs from the formulas.
from math import gcd
def brute(a, b):
    seen = set(); first = {}
    i = 0
    while True:
        p = (i % a, i % b)
        if p in seen: break
        seen.add(p); i += 1
    period = i
    hits = len({p[1] for p in seen if p[0] == 0})
    return len(seen), period, hits
ok = True
for a, b in ((17, 40), (20, 40), (18, 42), (19, 38), (21, 22), (24, 36)):
    g = gcd(a, b); n, per, hits = brute(a, b)
    exp = (a*b//g, a*b//g, b//g)
    good = (n, per, hits) == exp
    ok &= good
    print(f"a={a} b={b} gcd={g}: pairs={n} period={per} chipped-tooth hits={hits} of {b} gear teeth; formula {exp} {'ok' if good else 'MISMATCH'}")
# fix: adding one tooth to a bad pair
a, b = 20, 40
alt = min(range(a, a+4), key=lambda x: (gcd(x, b) != 1, x))
n, per, hits = brute(alt, b)
print(f"fix: pinion {a}->{alt} against {b}: pairs={n} chipped-tooth hits={hits}/{b}")
ok &= hits == b and n == alt*b
print("RESULT: %s brute-force meshing matches pairs = lcm(a,b) and chipped-tooth spread = b/gcd for 6 pairs; coprime 17/40 spreads over 40 of 40 gear teeth, 20/40 over 2; 20->21 against 40 restores 40 of 40" % ("PASS" if ok else "FAIL"))
