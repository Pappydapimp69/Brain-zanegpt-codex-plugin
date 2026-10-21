#!/usr/bin/env python3
"""Sandbox: porting a self-contained piece into a longer work as a segment.

Model (deterministic, stdlib only, no RNG, no timing):
  - a host work with its own chrome (title, advance control, progress bar) and
    a widget grammar (how many values it can show side by side in one frame)
  - a guest piece with chrome elements, each tagged: does it ASSERT the piece
    is its own work (identity) or carry an argument (narrative)?
  - a timeline of 11 beats; elapsed years 0..43, decay index constant 0.000
    (the guest's thesis = "no decay while 43 years pass" is only visible when
    BOTH values are in one frame)
Policies compared: import_all, usefulness_keep (negative control), strip_all,
drop_identity (element level), drop_identity_attr (attribute level),
reexpress_in_host, hide_host+drop_identity (for a wanted rupture).

PREDICTION (written before the first run):
  S1 film host, rupture unwanted, normal motion:
     import_all   identity=4 mismatch=7 overlap=3 thesis=10
     usefulness   identical to import_all (it cannot discriminate)
     strip_all    identity=0 mismatch=0 overlap=0 thesis=0
     drop_identity identity=0 mismatch=3 overlap=0 thesis=10
     reexpress    identity=0 mismatch=0 overlap=0 thesis=10
  S1rm reduced-motion: import_all identity=5 (splash restored); others 0
  S2 host shows one value at a time: reexpress thesis=0 (argument lost) while
     drop_identity thesis=10 (mismatch 3); extending the host with a 2-slot
     gauge restores thesis=10 at host_changes=1
  S3 rupture wanted: only hide_host+drop_identity satisfies (language change
     visible, identity=0, overlap=0); reexpress fails (no language change)
  S4 BREAK: a guest element that bundles the decay value with a work-name
     label: element-level drop loses thesis (0); attribute-level keeps it (10)
"""

def rect_overlap(a, b):
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah

BEATS = 11
YEARS = [round(43 * b / (BEATS - 1)) for b in range(BEATS)]

# guest element: name, function, asserts_own_work, idiom, rect, values shown, only_reduced_motion
def guest_elements(bundled=False):
    els = [
        dict(n="title_plate", fn="title", own=True, idiom="guest", rect=(10, 5, 80, 10), vals=[], rm=False),
        dict(n="transport", fn="advance", own=True, idiom="guest", rect=(40, 90, 20, 6), vals=[], rm=False),
        dict(n="scrub_bar", fn="progress", own=True, idiom="guest", rect=(5, 86, 90, 2), vals=[], rm=False),
        dict(n="column_header", fn="label", own=True, idiom="guest", rect=(70, 20, 25, 4), vals=[], rm=False),
        dict(n="depth_ruler", fn="depth", own=False, idiom="guest", rect=(2, 20, 4, 60), vals=["depth"], rm=False),
        dict(n="elapsed", fn="clock", own=False, idiom="guest", rect=(70, 26, 25, 4), vals=["elapsed"], rm=False),
        dict(n="decay", fn="decay", own=False, idiom="guest", rect=(70, 32, 25, 4), vals=["decay"], rm=False),
        dict(n="splash_fallback", fn="title", own=True, idiom="guest", rect=(0, 0, 100, 100), vals=[], rm=True),
    ]
    if bundled:
        # decay value and the work-name label are ONE element
        els = [e for e in els if e["n"] not in ("column_header", "decay")]
        els.append(dict(n="decay_with_worktitle", fn="decay", own=True, idiom="guest",
                        rect=(70, 20, 25, 16), vals=["decay"], rm=False, attr_own=True))
    return els

HOST_CHROME = [("host_title", (10, 5, 80, 10)), ("host_advance", (40, 90, 20, 6)),
               ("host_progress", (5, 86, 90, 2))]
HOST_FUNCS = {"title", "advance", "progress"}

def run(policy, host_slots, rm=False, bundled=False, extend=0):
    els = [e for e in guest_elements(bundled) if (not e["rm"]) or rm]
    host_chrome = list(HOST_CHROME)
    host_changes = 0
    slots = host_slots
    if policy == "usefulness_keep":
        pass                                   # every element is useful -> keep all
    elif policy == "import_all":
        pass
    elif policy == "strip_all":
        els = []
    elif policy == "drop_identity":            # element-level test
        els = [e for e in els if not e["own"]]
    elif policy == "drop_identity_attr":       # attribute-level: strip the assertion, keep the value
        els = [dict(e, own=False) for e in els if e["vals"]]
    elif policy == "hide_host_drop_identity":
        els = [e for e in els if not e["own"]]
        host_chrome = []
    elif policy == "reexpress":
        keep = [e for e in els if e["vals"]]
        els = [dict(e, own=False, idiom="host") for e in keep]
        if extend:
            slots = extend; host_changes = 1
    # per-element metrics
    identity = sum(1 for e in els if e["own"])
    mismatch = sum(1 for e in els if e["idiom"] == "guest")
    overlap = 0
    for e in els:
        if e["idiom"] == "host":
            continue                           # re-expressed widgets live in host layout slots
        for _, hr in host_chrome:
            if rect_overlap(e["rect"], hr):
                overlap += 1
    # thesis: frames where elapsed>0 and the elapsed and decay values share one frame
    vis = {v for e in els for v in e["vals"]}
    both = {"elapsed", "decay"} <= vis
    if both and any(e["idiom"] == "host" for e in els):
        both = slots >= 2                      # host grammar must be able to juxtapose two values
    thesis = sum(1 for y in YEARS if y > 0 and both)
    lang_change = any(e["idiom"] == "guest" for e in els)
    return dict(identity=identity, mismatch=mismatch, overlap=overlap, thesis=thesis,
                lang_change=lang_change, host_changes=host_changes)

def row(name, r):
    print(f"  {name:26s} identity={r['identity']} mismatch={r['mismatch']} overlap={r['overlap']} "
          f"thesis={r['thesis']:2d} lang_change={int(r['lang_change'])} host_changes={r['host_changes']}")

ok = True
def check(label, cond):
    global ok
    print(("  ok   " if cond else "  FAIL ") + label)
    ok = ok and cond

POLS = ["import_all", "usefulness_keep", "strip_all", "drop_identity", "drop_identity_attr", "reexpress"]

print("S1 film host (3 values side by side), rupture unwanted, normal motion")
S1 = {p: run(p, 3) for p in POLS}
for p in POLS: row(p, S1[p])
a = S1["import_all"]
check("import_all identity=4 mismatch=7 overlap=3 thesis=10",
      (a["identity"], a["mismatch"], a["overlap"], a["thesis"]) == (4, 7, 3, 10))
check("usefulness_keep indistinguishable from import_all (negative control)", S1["usefulness_keep"] == a)
s = S1["strip_all"]
check("strip_all clean but argument lost (identity 0, thesis 0)", (s["identity"], s["overlap"], s["thesis"]) == (0, 0, 0))
d = S1["drop_identity"]
check("drop_identity identity=0 mismatch=3 overlap=0 thesis=10", (d["identity"], d["mismatch"], d["overlap"], d["thesis"]) == (0, 3, 0, 10))
r = S1["reexpress"]
check("reexpress identity=0 mismatch=0 overlap=0 thesis=10", (r["identity"], r["mismatch"], r["overlap"], r["thesis"]) == (0, 0, 0, 10))

print("S1rm reduced-motion (the 'restored splash' regression)")
rm_a = run("import_all", 3, rm=True); row("import_all", rm_a)
check("import_all identity=5 under reduced motion (second title screen)", rm_a["identity"] == 5)
check("drop_identity / reexpress stay at identity=0 under reduced motion",
      run("drop_identity", 3, rm=True)["identity"] == 0 and run("reexpress", 3, rm=True)["identity"] == 0)

print("S2 host that shows ONE value at a time (cannot juxtapose)")
r2 = run("reexpress", 1); d2 = run("drop_identity", 1); x2 = run("reexpress", 1, extend=2)
row("reexpress", r2); row("drop_identity", d2); row("reexpress+extend host", x2)
check("reexpress loses the argument (thesis=0) when host grammar cannot carry it", r2["thesis"] == 0)
check("drop_identity keeps it (thesis=10) at the price of mismatch=3", (d2["thesis"], d2["mismatch"]) == (10, 3))
check("extending the host (2-slot gauge) restores thesis=10 at host_changes=1", (x2["thesis"], x2["host_changes"]) == (10, 1))

print("S3 wanted rupture (segment is meant to read as a different language)")
g = run("hide_host_drop_identity", 3); row("hide_host+drop_identity", g)
r3 = run("reexpress", 3); row("reexpress", r3); a3 = run("import_all", 3); row("import_all", a3)
check("hide_host+drop_identity: language change visible, identity=0, overlap=0, thesis=10",
      g["lang_change"] and g["identity"] == 0 and g["overlap"] == 0 and g["thesis"] == 10)
check("reexpress erases the intended rupture (no language change)", not r3["lang_change"])
check("import_all fails the same wish through identity=4", a3["identity"] == 4)

print("S4 BREAK: decay value bundled with a work-name label in one element")
b_el = run("drop_identity", 3, bundled=True); b_at = run("drop_identity_attr", 3, bundled=True); b_re = run("reexpress", 3, bundled=True)
row("drop_identity (element)", b_el); row("drop_identity_attr", b_at); row("reexpress", b_re)
check("element-level test throws the argument out with the label (thesis=0)", b_el["thesis"] == 0)
check("attribute-level split keeps it (thesis=10, identity=0)", (b_at["thesis"], b_at["identity"]) == (10, 0))
check("reexpress also keeps it (thesis=10)", b_re["thesis"] == 10)

print()
print("RESULT: " + ("PASS" if ok else "FAIL") +
      " host-grammar borrowing wins only when the host can carry the argument and no rupture is wanted;"
      " usefulness test cannot discriminate; split must be per attribute")
