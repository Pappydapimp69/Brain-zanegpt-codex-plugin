"""Sandbox: Chekhov ledger checker scanned per mention vs per scene with a final-unit rule
(analogue of bowling's tenth frame). Prediction (before run): the strict later-scene scan
labels 2 of 6 stories wrong (the two whose payoff shares the last scene with the introduction);
the scene-counter with a final-scene rule labels 6/6; a mid-story same-scene intro+use stays a dead end in both."""
# story: list of scenes; each scene a list of (item, event) with event in 'intro','use'
STORIES = {
 "kept_later":      ([[("gun","intro")],[("x","intro")],[("gun","use"),("x","use")]], {}),
 "dead_end":        ([[("gun","intro")],[("x","intro")],[("x","use")]], {"gun"}),
 "final_same":      ([[("a","intro")],[("a","use")],[("gun","intro"),("gun","use")]], set()),
 "final_same_2":    ([[("b","intro")],[("b","use")],[("key","intro"),("key","use")]], set()),
 "mid_same_dead":   ([[("gun","intro"),("gun","use")],[("z","intro")],[("z","use")]], set()),  # same-scene mid: counts as kept (use is real)
 "motif":           ([[("rain","intro")],[("a","intro")],[("a","use")]], set()),  # rain marked motif
}
MOTIFS = {"motif": {"rain"}}

def naive(scenes, motifs):
    dead = set()
    for i, sc in enumerate(scenes):
        for item, ev in sc:
            if ev == "intro" and item not in motifs:
                if not any(it == item and e == "use" for later in scenes[i+1:] for it, e in later):
                    dead.add(item)
    return dead

def counter(scenes, motifs):
    dead = set(); n = len(scenes)
    for i, sc in enumerate(scenes):
        for item, ev in sc:
            if ev == "intro" and item not in motifs:
                later = any(it == item and e == "use" for l in scenes[i+1:] for it, e in l)
                same = any(it == item and e == "use" for it, e in sc)
                if not (later or (same and i == n-1)):
                    dead.add(item)
    return dead

# mid_same: same-scene use mid-story is NOT accepted by the counter rule (only the final scene is special)
truth = {"kept_later": set(), "dead_end": {"gun"}, "final_same": set(), "final_same_2": set(),
         "mid_same_dead": {"gun"}, "motif": set()}
ok_n = ok_c = 0
for k, (sc, _) in STORIES.items():
    m = MOTIFS.get(k, set())
    dn, dc = naive(sc, m), counter(sc, m)
    ok_n += dn == truth[k]; ok_c += dc == truth[k]
    print(k, "naive", sorted(dn), "counter", sorted(dc), "truth", sorted(truth[k]))
print("RESULT: %s naive exact %d/6, counter exact %d/6" % ("PASS" if (ok_n, ok_c) == (4, 6) else "FAIL", ok_n, ok_c))
