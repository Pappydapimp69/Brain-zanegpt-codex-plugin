"""BRAILLE decade-shift kernel + numbers (untested in the kernel). Digits reuse the
a-j base cells after a number sign (dots 3456) and numeric mode lasts until a space,
so a letter a-j written straight after a digit reads back as a digit unless a letter
sign (dots 56, grade-1 indicator role) cancels numeric mode. Build an encoder from
the kernel's generating rule only (ten base cells + dot 3 + dots 3,6 + w exception,
French order), decode with the numeric-mode rule, and round-trip every string of
length 1-3 over a-z and 0-9 (47,988 strings). Cells are Unicode braille code points
(dot n = bit n-1 of U+2800 + bits). Deterministic, exhaustive.
PREDICTION (written before running): without a letter sign exactly the strings with
a digit immediately followed by a letter a-j fail to round-trip (k-z after a digit
are safe because their cells are not digit cells), about 10*10/36/36 per adjacent
pair; with the letter sign rule 0 fail."""
import itertools
def cell(*dots): return chr(0x2800 + sum(1 << (d - 1) for d in dots))
BASE = [(1,), (1, 2), (1, 4), (1, 4, 5), (1, 5), (1, 2, 4), (1, 2, 4, 5), (1, 2, 5), (2, 4), (2, 4, 5)]
FRENCH = "abcdefghij" "klmnopqrst" "uvxyz"
L = {}
for i, ch in enumerate(FRENCH):
    base = BASE[i % 10]
    L[ch] = cell(*base) if i < 10 else cell(*(base + (3,))) if i < 20 else cell(*(base + (3, 6)))
L["w"] = cell(2, 4, 5, 6)
assert len(set(L.values())) == 26
NUM, LET = cell(3, 4, 5, 6), cell(5, 6)
DIG = {d: L["abcdefghij"[(int(d) - 1) % 10]] for d in "1234567890"}
CELL2LET = {v: k for k, v in L.items()}
CELL2DIG = {v: k for k, v in DIG.items()}

def encode(s, letter_sign):
    out, numeric = [], False
    for ch in s:
        if ch.isdigit():
            if not numeric: out.append(NUM); numeric = True
            out.append(DIG[ch])
        else:
            if numeric and letter_sign and L[ch] in CELL2DIG: out.append(LET)
            numeric = numeric and not (letter_sign and L[ch] in CELL2DIG) and L[ch] in CELL2DIG
            out.append(L[ch])
    return "".join(out)

def decode(b):
    out, numeric = [], False
    for c in b:
        if c == NUM: numeric = True; continue
        if c == LET: numeric = False; continue
        if numeric and c in CELL2DIG: out.append(CELL2DIG[c])
        else: numeric = False; out.append(CELL2LET[c])
    return "".join(out)

ALPHA = "abcdefghijklmnopqrstuvwxyz0123456789"
strings = ["".join(p) for n in (1, 2, 3) for p in itertools.product(ALPHA, repeat=n)]
risky = lambda s: any(s[i].isdigit() and s[i + 1] in "abcdefghij" for i in range(len(s) - 1))
fail_plain = [s for s in strings if decode(encode(s, False)) != s]
fail_sign = [s for s in strings if decode(encode(s, True)) != s]
exact = set(fail_plain) == {s for s in strings if risky(s)}
print(f"strings {len(strings)}; no letter sign: {len(fail_plain)} fail ({len(fail_plain)/len(strings):.1%}), "
      f"failures == digit-then-a..j set: {exact}; examples {fail_plain[:4]}")
kz_after_digit = [s for s in strings if any(s[i].isdigit() and s[i + 1] in "klmnopqrstuvwxyz" for i in range(len(s) - 1)) and not risky(s)]
print(f"with letter sign: {len(fail_sign)} fail; digit-then-k..z strings (no a..j hazard) failing without the sign: "
      f"{sum(s in set(fail_plain) for s in kz_after_digit)}/{len(kz_after_digit)}")
print(f"RESULT: {'PASS' if exact and not fail_sign else 'FAIL'} decade-rule cells + number sign: {len(fail_plain)}/{len(strings)} "
      f"strings misread without a letter sign, all and only digit-then-a..j; 0 with it: {not fail_sign}")
