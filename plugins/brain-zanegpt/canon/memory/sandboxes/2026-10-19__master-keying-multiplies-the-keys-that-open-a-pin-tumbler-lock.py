# Pin-tumbler lock: each chamber has a change cut depth; master keying adds a second allowed depth in
# chambers that carry a master pin. A key opens the lock if every chamber's cut is one of its allowed depths.
import itertools
DEPTHS, CH = 6, 5      # 6 cut depths, 5 chambers => 7776 possible keys
def openers(allowed):
    return sum(all(k[i] in allowed[i] for i in range(CH)) for k in itertools.product(range(DEPTHS), repeat=CH))
change = (1, 4, 2, 5, 3)
plain = [{c} for c in change]
full  = [{c, (c + 2) % DEPTHS} for c in change]                      # master in every chamber
part  = [{c, (c + 2) % DEPTHS} if i < 2 else {c} for i, c in enumerate(change)]   # master in 2 chambers
r = {"plain": openers(plain), "partial2": openers(part), "full": openers(full)}
print(r, "of", DEPTHS ** CH)
# cross-opening: a different change key from a sibling lock sharing the same master cuts
sib = (3, 0, 4, 1, 5)
sib_full = [{c, (c + 2) % DEPTHS} for c in sib]
cross = sum(all(k[i] in full[i] for i in range(CH)) for k in itertools.product(*[sorted(s) for s in sib_full]))
print("sibling-lock keys (32 per lock) that also open this lock:", cross)
ok = r["plain"] == 1 and r["partial2"] == 4 and r["full"] == 32 and cross >= 1
print(f"RESULT: {'PASS' if ok else 'FAIL'} openers plain {r['plain']}, master in 2 of 5 chambers {r['partial2']}, master in all 5 {r['full']} of {DEPTHS**CH}; sibling keys that cross-open {cross} of 32")
