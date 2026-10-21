# Prediction (before run): valid ages 0..L (1 event each), invalid ages L+1..L+80, frame q,
# measured age = ceil(age/q). floor cutoff loses L mod q valid events; ceil cutoff leaks (-L) mod q
# invalid events; no integer-frame cutoff gives 0 errors unless q divides L. Reproduces L=60:
# q=16 ceil leaks 4 / floor loses 12; q=19 ceil leaks 16 / floor loses 3 (earlier recorded values).
def errs(L, q, c):
    lost = sum(1 for a in range(0, L + 1) if -(-a // q) > c)
    leak = sum(1 for a in range(L + 1, L + 81) if -(-a // q) <= c)
    return lost, leak
fails = []; n = 0
for L in range(20, 120):
    for q in (2, 3, 7, 10, 16, 19, 25, 33):
        fl, ce = L // q, -(-L // q)
        lf = errs(L, q, fl); lc = errs(L, q, ce)
        best = min(sum(errs(L, q, c)) for c in range(0, 200))
        n += 1
        ok = lf == (L % q, 0) and lc == (0, (-L) % q) and ((best == 0) == (L % q == 0))
        if not ok: fails.append((L, q, lf, lc, best))
print("L=60:", {q: (errs(60, q, 60 // q), errs(60, q, -(-60 // q))) for q in (16, 19)})
print(f"cases={n}")
print("RESULT: " + ("PASS" if not fails else "FAIL") + f" floor loses L%q, ceil leaks (-L)%q, exact iff q|L; fails={fails[:3]}")
