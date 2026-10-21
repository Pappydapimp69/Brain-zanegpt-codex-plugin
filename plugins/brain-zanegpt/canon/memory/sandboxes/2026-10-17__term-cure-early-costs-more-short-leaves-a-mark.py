"""A cure with a term (The StoryTeller: Hans My Hedgehog, from "Hans My Hedgehog" + "The
Enchanted Pig"; The Three Ravens, from Grimm's "The Six Swans"). Deterministic, stdlib.
Part 1: the spell lifts after T days of waiting; acting at day t < T fails and adds a search
penalty P (iron shoes). Total time to freedom: wait = T, act early = t + P.
Part 2: six shirts for six brothers; the last lacks one sleeve. Partial credit restores each
brother whose shirt is whole and leaves the missing part as a visible remainder (a wing);
all-or-nothing restores nobody unless every shirt is whole."""
def freedom_time(T, t, P):
    return T if t >= T else t + P
T = 100
rows = []
for P in (1, 2, 3, 30, 300):                       # penalty sizes; the tale's is enormous
    early = freedom_time(T, T - 3, P)              # "three days short"
    rows.append((P, early, early > T))
for P, e, worse in rows:
    print(f"penalty {P:3d}: act 3 days early -> free at {e} vs wait {T}  early_worse={worse}")
shirts = [1.0] * 5 + [0.95]                         # last shirt: one sleeve missing
partial = sum(1 for s in shirts if s == 1.0); wings = sum(1 for s in shirts if s < 1.0)
all_or_nothing = len(shirts) if all(s == 1.0 for s in shirts) else 0
print(f"partial credit: {partial} restored, {wings} keeps a wing; all-or-nothing: {all_or_nothing} restored")
# BREAK: penalties at or below the days saved make impatience the better play
flip = [P for P, e, worse in rows if not worse]
ok = flip == [1, 2, 3] and partial == 5 and wings == 1 and all_or_nothing == 0
print(("RESULT: PASS " if ok else "RESULT: FAIL ") + f"acting early only loses when the penalty exceeds the days saved (penalties {flip} "
      f"of 1-3 days make it pay or tie; 30 and 300 lose); one missing sleeve leaves {partial} of 6 restored and 1 wing under partial credit, "
      f"{all_or_nothing} under all-or-nothing")
