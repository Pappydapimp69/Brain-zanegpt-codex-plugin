# International Morse: dit = 1 unit, dah = 3, gap inside a letter = 1, gap between letters = 3.
M = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", ".- -... -.-. -.. . ..-. --. .... .. .--- -.- .-.. -- -. --- .--. --.- .-. ... - ..- ...- .-- -..- -.-- --..".split()))
INV = {}
for k, v in M.items(): INV.setdefault(v, []).append(k)
def parses(s):
    """number of letter sequences that produce the dit/dah string s when letter gaps are NOT sent"""
    n = len(s); ways = [0] * (n + 1); ways[0] = 1
    for i in range(1, n + 1):
        for L in range(1, 5):
            if i - L >= 0 and s[i - L:i] in INV: ways[i] += ways[i - L]
    return ways[n]
def enc(t): return "".join(M[c] for c in t)
def dur(code): return sum(1 if c == "." else 3 for c in code) + (len(code) - 1)
words = ["SOS", "PARIS", "HELP", "EEE", "ET", "TEA"]
for w in words: print(w, enc(w), "parses without letter gaps:", parses(enc(w)))
prefix_pairs = sum(1 for a in M.values() for b in M.values() if a != b and b.startswith(a))
# average duration per letter, English-like frequencies (per mille, fixture), vs a uniform 5-element code of dahs
F = dict(zip("ETAOINSHRDLCUMWFGYPBVKJXQZ", [127,91,82,75,70,67,63,61,60,43,40,28,28,24,24,22,20,20,19,15,10,8,2,2,1,1]))
tot = sum(F.values())
avg_morse = sum(F[c] * dur(M[c]) for c in F) / tot
avg_uniform = 5 * 3 + 4        # five dahs with inner gaps: 19 units for every letter
print("prefix pairs among letter codes:", prefix_pairs, "| average letter duration (units): morse %.2f vs uniform %d" % (avg_morse, avg_uniform))
ok = parses(enc("SOS")) > 1 and parses(enc("EEE")) > 1 and prefix_pairs > 0 and avg_morse < avg_uniform
print(f"RESULT: {'PASS' if ok else 'FAIL'} SOS parses {parses(enc('SOS'))} ways and PARIS {parses(enc('PARIS'))} without letter gaps; {prefix_pairs} letter-code prefix pairs; average letter {avg_morse:.1f} units vs {avg_uniform} for uniform dahs")
