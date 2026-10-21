"""Seed sandbox for domain KEYBOARD-LAYOUT: compare QWERTY, Dvorak, Colemak and an alphabetical layout on two real
texts shipped with Python (the Zen of Python from `this`, and the source of json/decoder.py), counting for letters only:
 home-row share (share of keystrokes on the home row) and same-finger bigram rate (consecutive letters typed by the
 same finger on DIFFERENT keys; the same key twice is not counted). Standard touch-typing finger map, 3 rows x 10 cols.
 Deterministic; no RNG.
PREDICTION (before run): on the prose text, home-row share Dvorak and Colemak exceed QWERTY by >= 20 points and QWERTY
has the highest same-finger rate of the three; on the code text the home-row gap to QWERTY shrinks by at least 3 points
for Dvorak (it was built for English letter frequency, code uses other letters); BREAK: the layout ranking by home-row
share differs from the ranking by same-finger rate on at least one text (one metric does not decide)."""
import inspect, io, contextlib, json.decoder, re
with contextlib.redirect_stdout(io.StringIO()) as buf:
    import this
PROSE = "".join(this.d.get(c, c) for c in this.s) if hasattr(this, "s") else buf.getvalue()
CODE = inspect.getsource(json.decoder)
LAYOUTS = {
    "qwerty":  ["qwertyuiop", "asdfghjkl;", "zxcvbnm,./"],
    "dvorak":  ["',.pyfgcrl", "aoeuidhtns", ";qjkxbmwvz"],
    "colemak": ["qwfpgjluy;", "arstdhneio", "zxcvbkm,./"],
    "alpha":   ["abcdefghij", "klmnopqrst", "uvwxyz,.;/"],
}
FINGER = [0, 1, 2, 3, 3, 4, 4, 5, 6, 7]   # column -> finger (0 left pinky ... 7 right pinky; both index fingers cover 2 cols)
def tables(rows):
    pos = {}
    for r, line in enumerate(rows):
        for c, ch in enumerate(line): pos[ch] = (r, c, FINGER[c])
    return pos
def stats(text, rows):
    pos = tables(rows); prev = None; n = home = sfb = pairs = 0
    for ch in text.lower():
        if ch not in pos or not ch.isalpha():
            prev = None; continue
        r, c, f = pos[ch]; n += 1; home += (r == 1)
        if prev is not None:
            pairs += 1
            if prev[2] == f and prev[:2] != (r, c): sfb += 1
        prev = (r, c, f)
    return home / n, sfb / pairs, n
res = {}
for tname, text in (("prose", PROSE), ("code", CODE)):
    for lname, rows in LAYOUTS.items():
        res[(tname, lname)] = stats(text, rows)
        h, s, n = res[(tname, lname)]
        print(f"{tname:5s} {lname:8s} letters={n:5d} home-row {h:.3f}  same-finger {s:.3f}")
def rank(tname, k, rev): return sorted(LAYOUTS, key=lambda l: res[(tname, l)][k], reverse=rev)
gap = lambda t, l: res[(t, l)][0] - res[(t, "qwerty")][0]
p1 = gap("prose", "dvorak") >= 0.20 and gap("prose", "colemak") >= 0.20 and res[("prose", "qwerty")][1] > max(res[("prose", "dvorak")][1], res[("prose", "colemak")][1])
p2 = gap("prose", "dvorak") - gap("code", "dvorak") >= 0.03
r_home = {t: rank(t, 0, True) for t in ("prose", "code")}; r_sfb = {t: rank(t, 1, False) for t in ("prose", "code")}
brk = any(r_home[t] != r_sfb[t] for t in r_home)
print("home-row ranking:", r_home); print("same-finger ranking:", r_sfb)
print(f"RESULT: {'PASS' if (p1 and p2 and brk) else 'FAIL'} home-row gain over qwerty prose dvorak {gap('prose','dvorak'):+.3f} colemak {gap('prose','colemak'):+.3f}, code dvorak {gap('code','dvorak'):+.3f} colemak {gap('code','colemak'):+.3f}; qwerty same-finger prose {res[('prose','qwerty')][1]:.3f} dvorak {res[('prose','dvorak')][1]:.3f} colemak {res[('prose','colemak')][1]:.3f}; rankings differ by metric: {brk}")
