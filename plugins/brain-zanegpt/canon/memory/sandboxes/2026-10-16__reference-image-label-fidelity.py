"""Toy model: does a reference image (plus AI label) make an AI product shot compliant?
Deterministic: drift is a fixed hash of (attribute, shot view, anchoring), no RNG, no timing."""
import hashlib
ATTRS = ["color","logo","shape","size","texture","label_text"]
REF_COVERS = {"front": {"color","logo","shape","label_text"}}  # reference photo = front view only
def drift(attr, view, anchored, seed):
    # unanchored attribute drifts when hash byte < threshold; anchored attrs are held
    if anchored: return False
    h = hashlib.sha256(f"{seed}|{attr}|{view}".encode()).digest()[0]
    return h < 110   # ~43% drift chance for an unanchored attribute
def shot(view, ref_views, text_only, seed):
    anchored = set()
    if not text_only:
        for v in ref_views:
            if v == view: anchored |= REF_COVERS.get(v, set())
    return [a for a in ATTRS if drift(a, view, a in anchored, seed)]
def run(name, view, ref_views, text_only, label, n=40):
    bad = 0
    for s in range(n):
        d = shot(view, ref_views, text_only, s)
        compliant = (not d) and label   # needs fidelity AND label
        bad += (not compliant)
    labelfix = sum(1 for s in range(n) if shot(view,ref_views,text_only,s))  # shots with drift even though labelled
    print(f"{name}: noncompliant {bad}/{n}; drifted-despite-label {labelfix}/{n}")
    return bad, labelfix, n
r = {}
r["text_only_label"] = run("1 text-only + label", "front", [], True, True)
r["ref_front_nolabel"] = run("2 ref image, front shot, NO label", "front", ["front"], False, False)
r["ref_front_label"] = run("3 ref image front shot + label", "front", ["front"], False, True)
r["ref_back_label_BREAK"] = run("4 BREAK: ref image front-only, back shot + label", "back", ["front"], False, True)
r["real_footage"] = ("5 real footage + label: drift impossible by construction", 0, 0, 40)
print("5 real footage + label: noncompliant 0/40 (no generated attributes)")
# claims
t, rf, rb, nb = r["text_only_label"], r["ref_front_label"], r["ref_back_label_BREAK"], r["ref_front_nolabel"]
ok = (t[0] > rf[0]            # reference image helps
      and rf[1] > 0           # but label+ref front shot still drifts on size/texture (uncovered attrs)
      and rb[0] >= 0.9*rb[2]  # back shot with ref-front: ~no help
      and nb[0] == nb[2])     # no label => always noncompliant
print(f"text-only {t[0]}/40 -> ref front {rf[0]}/40 (still not 0); ref on back view {rb[0]}/40; no-label {nb[0]}/40")
print("RESULT: PASS" if ok else "RESULT: FAIL", f"ref_front_label={rf[0]}/40 noncompliant, back_view={rb[0]}/40, text_only={t[0]}/40")
