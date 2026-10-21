"""Apply CHECK-DIGITS/luhn kernel (Luhn: every single-digit error and every adjacent swap
except 09/90; mod-11 weighted catches every adjacent swap) to an error class it did not
test: TWIN errors, a doubled digit typed as a different doubled digit (aa -> bb), a common
keying slip. Exhaustive over all positions of a 16-digit Luhn number (all a != b, every
start position, both parities) and of an ISBN-10 (weights 10..1, mod 11). No RNG.
PREDICTION (written before running): Luhn misses exactly the twin pairs 22<->55, 33<->66,
44<->77 (6 ordered pairs of 90) at every position; ISBN-10 catches every twin error EXCEPT
at the position where the two adjacent weights sum to 11 (weights 6 and 5), where it
misses all 90."""
def luhn_sum(d):                      # d: list of digits, rightmost is check digit position 0
    s = 0
    for i, x in enumerate(reversed(d)):
        if i % 2 == 1:
            x *= 2
            if x > 9: x -= 9
        s += x
    return s % 10
def isbn_sum(d): return sum(w * x for w, x in zip(range(10, 0, -1), d)) % 11
def twin_misses(n, summer):
    base = [0] * n; misses = {}
    for pos in range(n - 1):
        m = []
        for a in range(10):
            for b in range(10):
                if a == b: continue
                x = base[:]; y = base[:]
                x[pos] = x[pos + 1] = a; y[pos] = y[pos + 1] = b
                if summer(x) == summer(y): m.append(f"{a}{a}->{b}{b}")
        misses[pos] = m
    return misses
L = twin_misses(16, luhn_sum); I = twin_misses(10, isbn_sum)
lset = {tuple(sorted(v)) for v in L.values()}
print("Luhn twin misses per position (identical at every position:", len(lset) == 1, "):", sorted(next(iter(lset))))
iso = {p: len(v) for p, v in I.items() if v}
print("ISBN-10 positions with any twin miss:", iso, "(weights at that position:", {p: (10 - p, 9 - p) for p in iso}, ")")
ok = (len(lset) == 1 and sorted(next(iter(lset))) == sorted(["22->55", "55->22", "33->66", "66->33", "44->77", "77->44"])
      and list(iso) == [4] and iso[4] == 90)
print(f"RESULT: {'PASS' if ok else 'FAIL'} Luhn misses {len(next(iter(lset)))}/90 twin errors (22/55, 33/66, 44/77) at every position; "
      f"ISBN-10 misses twin errors only at {list(iso)} ({iso}) where weights {[(10-p, 9-p) for p in iso]} sum to 11")
