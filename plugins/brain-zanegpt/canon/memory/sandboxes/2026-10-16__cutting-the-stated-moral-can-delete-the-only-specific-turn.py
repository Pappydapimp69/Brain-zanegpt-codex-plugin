import itertools
# Sentence types: (turn, moral, derived)
T = {"stock": (0, 0, 1), "derived": (0, 0, 1), "turn": (1, 0, 1), "moral": (0, 1, 1), "moral_turn": (1, 1, 1), "stray": (0, 0, 0)}
names = list(T)
def hack_ok(d): return any(T[s][0] for s in d)                 # needs one specific turn the stock form lacks
def derived_ok(d): return all(T[s][2] for s in d[1:])          # every beat after the opener derives from the game
def moral_ok(d): return not any(T[s][1] for s in d)            # no sentence states the lesson outright
def cut(d): return tuple(s for s in d if not T[s][1])          # the writer's fix: delete moral sentences
drafts = [d for d in itertools.product(names, repeat=5)]
with_moral = [d for d in drafts if not moral_ok(d)]
fixes_moral = all(moral_ok(cut(d)) for d in with_moral)
had_turn = [d for d in with_moral if hack_ok(d)]
lost_turn = [d for d in had_turn if not hack_ok(cut(d)) ]
# derived check after cut when the opener was a moral sentence: the new opener is exempt
changed_derived = [d for d in with_moral if derived_ok(d) != derived_ok(cut(d))]
pct = len(lost_turn) / len(had_turn)
print(len(drafts), len(with_moral), len(had_turn), len(lost_turn), round(pct, 3), len(changed_derived))
ok = fixes_moral and len(lost_turn) > 0 and len(changed_derived) > 0
print("RESULT: %s cut removes the stated moral in %d/%d drafts but erases the only specific turn in %d of %d (%.1f%%) that had one; derived-check verdict flips in %d" % (
    "PASS" if ok else "FAIL", len(with_moral), len(with_moral), len(lost_turn), len(had_turn), 100 * pct, len(changed_derived)))
