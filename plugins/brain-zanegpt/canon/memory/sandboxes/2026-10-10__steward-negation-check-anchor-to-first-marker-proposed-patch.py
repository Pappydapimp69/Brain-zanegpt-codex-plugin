"""Proposed fix for the memory steward's provenance negation check (brain#E47).
Self-contained: copies the CURRENT and PROPOSED provenance_ok and runs both on a case table.
Prediction (written first): the proposed version passes the honest-hedge cases the current one
wrongly holds, and still holds every genuine negation of the primary claim; mutating the
anchoring away reproduces the current false positives."""
import re

NEG = re.compile(r"(?:\b(?:not|never|no|without)\b|n['’]t\b)[\w\s,'’-]{0,15}"
                 r"(?:verif|first[\s-]?hand|confirm)|\bun(?:verif|confirm)")
MARK = re.compile(r"verif|first[\s-]?hand|confirm")


def current(prov):
    p = prov.lower()
    has = "verified" in p or "firsthand" in p or "first-hand" in p
    if not has or NEG.search(p):
        return False
    return "assumed only" not in p and "assumed-only" not in p


def proposed(prov, anchored=True):
    p = prov.lower()
    has = "verified" in p or "firsthand" in p or "first-hand" in p
    if not has:
        return False
    first = MARK.search(p)
    for m in NEG.finditer(p):
        if not anchored or (first and m.start() <= first.start() < m.end()):
            return False
    return "assumed only" not in p and "assumed-only" not in p


# (text, what_current_does_now, what_it_should_do)
CASES = [
    ("Verified first-hand: X ran. Separately, not machine-verified: W.", False, True),
    ("Verified first-hand: A ran. Does not and cannot verify B.", False, True),
    ("Verified first-hand: A. Unverified: B.", False, True),
    ("Verified first-hand: every number comes from the saved run. Engine behaviour is modelled.", True, True),
    ("NOT verified firsthand, purely assumed", False, False),
    ("No first-hand verification was done.", False, False),
    ("Unverified guess.", False, False),
    ("Without confirming anything, assumed.", False, False),
    ("Not verified. Later: verified first-hand: Y.", False, False),
    ("Verified first-hand; assumed only for the TTS part.", False, False),
    ("", False, False),
    ("Assumed-only, verified nothing.", False, False),
]
PATCH = """--- a/scripts/steward.py
+++ b/scripts/steward.py
@@ def provenance_ok(prov: str) -> bool:
-    if not has_marker or NEG_PROV_RE.search(prov):
-        return False
+    if not has_marker:
+        return False
+    # a negation only counts when it attaches to the FIRST verification marker:
+    # an opening affirmative claim passes whatever a later clause hedges
+    first = _MARK_RE.search(prov)
+    for m in NEG_PROV_RE.finditer(prov):
+        if first and m.start() <= first.start() < m.end():
+            return False
+# plus: _MARK_RE = re.compile(r"verif|first[\\s-]?hand|confirm")
"""

bad = []
cur_wrong = 0
for text, cur_expect, want in CASES:
    c, n = current(text), proposed(text)
    if c != cur_expect:
        bad.append(("current-model-drift", text))
    if n != want:
        bad.append(("proposed-wrong", text))
    if c != want:
        cur_wrong += 1
mut = [t for t, _c, w in CASES if proposed(t, anchored=False) != w]
holds_real = all(not proposed(t) for t, _c, w in CASES if not w)
ok = (not bad) and holds_real and len(mut) >= 3 and cur_wrong >= 3
print(f"cases={len(CASES)} current_wrong={cur_wrong} proposed_wrong={sum(1 for b in bad if b[0]=='proposed-wrong')}"
      f" real_negations_still_held={holds_real} mutant_(no_anchor)_wrong={len(mut)}")
if bad:
    print("BAD:", bad)
print("RESULT:", "PASS" if ok else "FAIL",
      f"anchoring fixes {cur_wrong} false holds, keeps every genuine negation held; no-anchor mutant is wrong on {len(mut)}")
