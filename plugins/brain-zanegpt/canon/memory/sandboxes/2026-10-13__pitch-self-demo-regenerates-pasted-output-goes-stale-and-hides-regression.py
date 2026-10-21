"""Prediction (before run): over 6 tool versions on one fixed pitch document, a pasted v1 snapshot matches the current tool's
output in at most 2 of 6 versions (v1 plus any version whose output happens to coincide), a version-stamped paste is flagged
stale in every version after v1 but still shows the old number, and a build-time self-demo is fresh in 6 of 6.
Built to break: v4 crashes on a tab, which the document (the tool's own creation) contains; the pasted snapshot should keep
claiming success in 6 of 6 renders while truth is 5 of 6, and the self-demo should expose the crash in exactly 1 render.
Deterministic, stdlib only."""
DOC = "Pitch: wc-tool\n\nIt counts things.\n\tindented demo line\nA well-known, state-of-the-art counter.\n\n"

def tool(v, text):
    if v == 1: return "lines=%d" % len(text.splitlines())
    if v == 2: return "lines=%d" % len([l for l in text.splitlines() if l.strip()])
    if v == 3: return "words=%d" % len(text.split())
    if v == 4:
        if "\t" in text: raise ValueError("tab not handled")
        return "words=%d" % len(text.split())
    if v == 5: return "words=%d" % len(text.split())
    if v == 6: return "words=%d" % len(text.replace("-", " ").split())

def run(v, text):
    try: return tool(v, text), True
    except ValueError as e: return "ERROR: %s" % e, False

V = range(1, 7)
snap, _ = run(1, DOC)
rows = []
for v in V:
    now, ok = run(v, DOC)
    rows.append({"v": v, "now": now, "ok": ok,
                 "paste_fresh": snap == now,
                 "stamp_flag": v != 1,
                 "demo_fresh": True,
                 "paste_claims_ok": True,
                 "demo_claims_ok": ok})
    print(rows[-1])
paste_fresh = sum(r["paste_fresh"] for r in rows)
flagged = sum(r["stamp_flag"] for r in rows)
demo_fresh = sum(r["demo_fresh"] for r in rows)
paste_claims = sum(r["paste_claims_ok"] for r in rows)
truth = sum(r["ok"] for r in rows)
demo_exposed = sum(not r["demo_claims_ok"] for r in rows)
ok = paste_fresh <= 2 and flagged == 5 and demo_fresh == 6 and paste_claims == 6 and truth == 5 and demo_exposed == 1
print("RESULT: %s paste fresh %d/6, stamp flags %d/5 stale versions, self-demo fresh %d/6, paste claims success %d/6 vs truth %d/6, self-demo exposes %d crash" %
      ("PASS" if ok else "FAIL", paste_fresh, flagged, demo_fresh, paste_claims, truth, demo_exposed))
