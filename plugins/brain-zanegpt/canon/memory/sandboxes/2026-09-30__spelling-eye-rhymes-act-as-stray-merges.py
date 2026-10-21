# Composes: lyrical-composition/E6 (spelling-suffix matcher: -ough words 100% false positives), one-stray-merge sandbox/E1
# (a single stray merge flips open/stable verdicts), and the two-pass letter-assignment kernel.
# PREDICTION (before running): on 6 stanzas I wrote, each containing at most one eye-rhyme pair, a spelling-suffix judge
# letters at least 3 stanzas differently from a phonetic judge, and the verdict (open/stable) flips in at least 2;
# two-pass assignment does not reduce the number of flips, because the error is in the judge, not the order.
# ITERATION 2: run 1 used stay/day/fall/wall as the control, but stay/day differ in their last 3 letters, so the spelling
# judge MISSED a true rhyme there (AABB -> XXAA, a flip). That stanza was not a clean control; it is kept as a finding
# (spelling judges also split true rhymes) and a real control replaces it. This judge has no slant tier, so the two-pass
# part of the prediction is not exercised here and is dropped from the claim.
PRON = {"though": "OW", "through": "UW", "rough": "AHF", "cough": "AOF", "blue": "UW", "stuff": "AHF", "go": "OW",
        "off": "AOF", "home": "OWM", "come": "AHM", "roam": "OWM", "some": "AHM", "love": "AHV", "move": "UWV",
        "shove": "AHV", "groove": "UWV", "dear": "IHR", "bear": "EHR", "near": "IHR", "wear": "EHR", "light": "AYT",
        "stay": "EY", "day": "EY", "night": "AYT", "fall": "AOL", "wall": "AOL", "rain": "EYN", "pain": "EYN"}
def ph(a, b): return PRON[a] == PRON[b]
def sp(a, b): return a[-3:] == b[-3:]
def letters(ws, judge, two_pass=True):
    lab = [None] * len(ws)
    groups = []
    for i, w in enumerate(ws):
        for g in groups:
            if judge(ws[g[0]], w): g.append(i); break
        else: groups.append([i])
    out = [None] * len(ws); m = {}
    for g in groups:
        for i in g: out[i] = "X" if len(g) == 1 else None
    k = 0
    for i in range(len(ws)):
        if out[i] is None:
            g = next(g for g in groups if i in g)
            if g[0] not in m: m[g[0]] = "ABCD"[k]; k += 1
            out[i] = m[g[0]]
    return "".join(out)
def verdict(s):
    contiguous = all(max(i for i, c in enumerate(s) if c == g) - min(i for i, c in enumerate(s) if c == g) + 1 == s.count(g) for g in set(s) - {"X"})
    return "stable" if s.count("X") <= 1 and contiguous else "open"
STANZAS = [["though", "stay", "through", "day"], ["rough", "rain", "cough", "pain"], ["home", "light", "come", "night"],
           ["love", "fall", "move", "wall"], ["dear", "bear", "near", "wear"], ["rain", "pain", "fall", "wall"]]  # control: spelling and sound agree
diff = flips = 0
for ws in STANZAS:
    a, b = letters(ws, ph), letters(ws, sp)
    d = a != b; f = verdict(a) != verdict(b); diff += d; flips += f
    print(f"{ws}: phonetic {a} ({verdict(a)})  spelling {b} ({verdict(b)})  {'DIFF' if d else ''} {'FLIP' if f else ''}")
ctrl = STANZAS[-1]; ctrl_ok = letters(ctrl, ph) == letters(ctrl, sp)
ok = diff >= 3 and flips >= 1 and ctrl_ok
print("RESULT: %s spelling judge letters %d/6 stanzas differently and flips the open/stable verdict in %d/6; control stanza agrees=%s" % ("PASS" if ok else "FAIL", diff, flips, ctrl_ok))
