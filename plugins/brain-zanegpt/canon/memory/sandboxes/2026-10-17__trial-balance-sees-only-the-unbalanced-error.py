"""Sandbox: what can a double-entry trial balance (total debits == total credits) detect?
Seed domain DOUBLE-ENTRY-BOOKKEEPING. Real rule being tested (standard bookkeeping teaching, e.g. the
trial balance and the divisible-by-nine transposition test): the check sees only errors that leave the
two sides unequal. It is the same shape as an even-parity bit (ideas:ERROR-CORRECTION/hamming
single-error-correcting-code-miscorrects-double-errors) and account numbers can carry a Luhn digit
(ideas:CHECK-DIGITS/luhn ... adjacent swap exceptions 09/90).
Prediction (written before first run): single-sided amount errors 100% detected; one-sided adjacent-digit
transpositions 100% detected with every difference divisible by 9; omitted whole entries 0%; right amount
to a wrong but valid account 0%; equal-and-opposite pair errors 0%, but unequal pair errors detected so
the pair test over k1,k2 in 1..9 with both signs detects 306 of 324 (the 18 undetected are k2==-k1
). Luhn on account numbers catches all single-digit keying errors and all
adjacent swaps except 09/90. Assumption: the books start balanced; BREAK: the pair-error sweep."""
def luhn_ok(n):
    s, alt = 0, False
    for ch in reversed(str(n)):
        d = int(ch)
        if alt:
            d *= 2
            if d > 9: d -= 9
        s += d; alt = not alt
    return s % 10 == 0
def with_check(body):
    for c in range(10):
        if luhn_ok(body * 10 + c): return body * 10 + c
LEDGER = [(100 + 7 * i, 5000 + 11 * i) for i in range(1, 21)]      # (amount, one transaction) both sides equal
def totals(debits, credits): return sum(debits), sum(credits)
D = [a for a, _ in LEDGER]; C = list(D)
assert totals(D, C)[0] == totals(D, C)[1]
def detected(d, c): return sum(d) != sum(c)
# 1 single-sided amount error k in -50..50 (k != 0) at each of 20 postings
one = [detected([x + (k if i == j else 0) for i, x in enumerate(D)], C) for j in range(20) for k in range(-50, 51) if k]
print("single-sided amount errors detected:", sum(one), "of", len(one))
# 2 one-sided adjacent-digit transposition of every 3-digit amount 100..999 whose swap changes the number
tr = diff9 = 0; tot = 0
for amt in range(100, 1000):
    s = str(amt)
    for p in range(2):
        t = list(s); t[p], t[p + 1] = t[p + 1], t[p]; t = int("".join(t))
        if t != amt:
            tot += 1; tr += detected([t], [amt]); diff9 += (t - amt) % 9 == 0
print("one-sided adjacent transpositions detected:", tr, "of", tot, "; difference divisible by 9:", diff9, "of", tot)
# 3 omission of a whole entry (both sides) and 4 right amount, wrong valid account (the totals are unchanged)
omit = [detected(D[:j] + D[j + 1:], C[:j] + C[j + 1:]) for j in range(20)]
print("omitted whole entries detected:", sum(omit), "of", len(omit))
wrong_acct = [detected(D, C) for _ in range(20)]           # amounts untouched, only the account differs
print("right amount, wrong valid account detected by the trial balance:", sum(wrong_acct), "of", len(wrong_acct))
# 5 pair errors: +k1 on one posting, then k2 on another, both signs, k in 1..9
pair = [detected([D[0] + k1] + [D[1] + k2] + D[2:], C) for k1 in range(-9, 10) if k1 for k2 in range(-9, 10) if k2]
print("pair errors detected:", sum(pair), "of", len(pair), "; undetected = equal-and-opposite pairs:", len(pair) - sum(pair))
# 6 Luhn on 5-digit account numbers: single-digit keying errors and adjacent swaps
accts = [with_check(1000 + i) for i in range(0, 3000, 7)]
sd = swp = swp_miss = sdt = 0
for a in accts:
    s = str(a)
    for p in range(5):
        for dgt in "0123456789":
            if dgt != s[p]:
                sdt += 1; sd += not luhn_ok(int(s[:p] + dgt + s[p + 1:]))
    for p in range(4):
        if s[p] != s[p + 1]:
            t = s[:p] + s[p + 1] + s[p] + s[p + 2:]; swp += 1
            if luhn_ok(int(t)): swp_miss += 1
print("Luhn single-digit account keying errors caught:", sd, "of", sdt, "; adjacent swaps missed:", swp_miss, "of", swp)
ok = (sum(one) == len(one) and tr == tot and diff9 == tot and sum(omit) == 0 and sum(wrong_acct) == 0
      and len(pair) - sum(pair) == 18 and sd == sdt and swp_miss > 0)
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" trial balance caught {sum(one)}/{len(one)} one-sided errors and {tr}/{tot} transpositions (all diffs %9==0) but 0/{len(omit)} omissions, 0/{len(wrong_acct)} wrong-account postings and missed {len(pair)-sum(pair)}/{len(pair)} pair errors; Luhn caught {sd}/{sdt} keying errors, missed {swp_miss}/{swp} swaps")
