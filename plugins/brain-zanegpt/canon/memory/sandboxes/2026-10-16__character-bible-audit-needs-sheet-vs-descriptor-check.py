"""Sandbox: locked character bible (reference sheet + verbatim descriptor) as a hand-built attribute model, NOT a video model.
Kernel: ideas:AI-VIDEO/locked-character-bible-pasted-verbatim-into-every-shot (paste the descriptor word for word; audit the sheet's panels against each other first).
Model: attributes jaw, hair, skin, outfit. A shot takes an attribute from the descriptor when the descriptor locks it, else from the sheet panel
chosen round-robin by shot index (stand-in for a re-roll). A paraphrased descriptor rotates three shade words per attribute that count as different values.
Drift = number of distinct values of an attribute across 12 shots (1 = no drift).
PREDICTION (before run): verbatim+complete descriptor+clean sheet -> 1 distinct value on all 4 attributes; paraphrasing the descriptor -> 3 distinct on every locked attribute;
verbatim descriptor that omits jaw + a sheet with one off-panel jaw -> jaw 2 distinct despite the verbatim paste; a cross-panel audit finds 12/12 planted
single-panel flaws (4 attributes x 3 panels); BREAK: a flaw present in ALL panels (sheet consistently disagrees with the descriptor) is found by the cross-panel audit in 0/4 cases,
and a sheet-vs-descriptor check finds 4/4."""
ATTRS = ["jaw", "hair", "skin", "outfit"]
BASE = {"jaw": "square", "hair": "brown", "skin": "tan", "outfit": "red coat"}
ALT = {"jaw": "round", "hair": "auburn", "skin": "pale", "outfit": "blue coat"}
SHADES = {"jaw": ["square", "angular", "blocky"], "hair": ["brown", "chestnut", "auburn"], "skin": ["tan", "olive", "bronze"], "outfit": ["red coat", "crimson jacket", "scarlet parka"]}

def shots(sheet, locked, mode, n=12):
    out = []
    for i in range(n):
        s = {}
        for a in ATTRS:
            if a in locked:
                s[a] = BASE[a] if mode == "verbatim" else SHADES[a][i % 3]
            else:
                s[a] = sheet[i % len(sheet)][a]
        out.append(s)
    return out

def drift(sh): return {a: len({s[a] for s in sh}) for a in ATTRS}
clean = [dict(BASE) for _ in range(3)]
r1 = drift(shots(clean, set(ATTRS), "verbatim"))
r2 = drift(shots(clean, set(ATTRS), "paraphrase"))
flawed = [dict(BASE), dict(BASE, jaw=ALT["jaw"]), dict(BASE)]
r3 = drift(shots(flawed, {"hair", "skin", "outfit"}, "verbatim"))
def audit(sheet):  # cross-panel: attributes whose panels disagree
    return {a for a in ATTRS if len({p[a] for p in sheet}) > 1}
found = 0
for a in ATTRS:
    for k in range(3):
        sh = [dict(BASE) for _ in range(3)]; sh[k][a] = ALT[a]
        found += audit(sh) == {a}
sys_found_cross = sys_found_desc = 0
for a in ATTRS:
    sh = [dict(BASE, **{a: ALT[a]}) for _ in range(3)]          # all panels consistently off-descriptor
    sys_found_cross += a in audit(sh)
    sys_found_desc += any(p[a] != BASE[a] for p in sh)           # sheet-vs-descriptor
print("clean verbatim", r1, "paraphrase", r2, "flawed sheet+jaw unlocked", r3, "audit", found, "/12 systematic cross", sys_found_cross, "desc", sys_found_desc)
ok = (set(r1.values()) == {1} and set(r2.values()) == {3} and r3["jaw"] == 2 and found == 12 and sys_found_cross == 0 and sys_found_desc == 4)
print("RESULT: %s verbatim 1 distinct value, paraphrase 3 distinct, unlocked jaw %d distinct under verbatim paste; cross-panel audit %d/12 single flaws but %d/4 systematic, sheet-vs-descriptor %d/4" % (
    "PASS" if ok else "FAIL", r3["jaw"], found, sys_found_cross, sys_found_desc))
