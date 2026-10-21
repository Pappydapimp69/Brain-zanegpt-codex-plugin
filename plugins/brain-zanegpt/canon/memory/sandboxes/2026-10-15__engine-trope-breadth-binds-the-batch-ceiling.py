"""Sandbox: the batch-ceiling entry left one thing untested: an engine restricted to WHOLE tropes. Here each of the 8 engines
(x 2 skeletons = 16 slots) may only be used with a window of w tropes (cyclic: engine e allows tropes e, e+1, ... e+w-1 mod 6),
each trope can host at most R videos, each slot hosts one video. Ceiling = max number of videos = maximum b-matching, computed
by augmenting paths on my own fixture (slots -> tropes with capacity R), no randomness.
Entries composed: ideas:AI-VIDEO/monetization-policy/every-video-gets-its-own-joke-and-script (each video its own engine-skeleton and joke),
fake-ad-kernel-source-check/E1 (engine labels verbatim from a closed list, so an engine's trope window is a checkable fact),
batch-ceiling-trope-cap/E1 (ceiling min(16, 6R) when engines are open or axis-restricted).
PREDICTION (before first run): w=6 (open) gives 6, 12, 16, 16 for R=1..4 (reproduces the entry); w=1 (engine e tied to trope e mod 6,
so tropes 0 and 1 have 4 slots, tropes 2-5 have 2) gives 6, 12, 14, 16, so raising the trope cap to 3 no longer reaches 16;
w=2 gives 6, 12, 16, 16. BREAK: the w=1 row at R=3 (the entry's advice 'raise the cap to 3' stops being enough).
Assumption: the ceiling depends on the trope cap only. Wrong if w=1 at R=3 gives 16."""
ENG, SK, TROPES = 8, 2, 6
def ceiling(w, R):
    slots = [(e, s) for e in range(ENG) for s in range(SK)]
    allowed = {sl: [(sl[0] + k) % TROPES for k in range(w)] for sl in slots}
    load = {t: [] for t in range(TROPES)}          # trope -> slots currently assigned
    def augment(sl, seen):
        for t in allowed[sl]:
            if t in seen: continue
            seen.add(t)
            if len(load[t]) < R: load[t].append(sl); return True
            for other in list(load[t]):
                if augment_move(other, seen, t): load[t].remove(other); load[t].append(sl); return True
        return False
    def augment_move(sl, seen, frm):
        for t in allowed[sl]:
            if t in seen: continue
            seen.add(t)
            if len(load[t]) < R: load[t].append(sl); return True
            for other in list(load[t]):
                if augment_move(other, seen, t): load[t].remove(other); load[t].append(sl); return True
        return False
    return sum(augment(sl, set()) for sl in slots)
rows = {}
for w in (6, 3, 2, 1):
    rows[w] = [ceiling(w, R) for R in (1, 2, 3, 4)]
    print("window w=%d  ceiling for R=1..4: %s" % (w, rows[w]))
ok = rows[6] == [6, 12, 16, 16] and rows[1] == [6, 12, 14, 16] and rows[2] == [6, 12, 16, 16]
print("RESULT: %s open %s, w=2 %s, w=1 %s (R=3 gives %d, not 16)" % ("PASS" if ok else "FAIL", rows[6], rows[2], rows[1], rows[1][2]))
