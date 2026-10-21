"""Sandbox: premise slot machine (trope x one absurd swap along a mismatch axis) fed by the 20-trope
catalog, with axis names verbatim from the study. Question: how many (trope, axis) cells are legal if a swap
must be on an axis the trope does NOT already use (else the parody copies nothing exactly), and how large a
batch survives 'different trope AND different genre-sold AND different axis per idea'?
Kernels/entries: ideas:COMEDY/fake-mobile-ad/premise-slot-machine-from-the-five-misleading-ad-patterns,
ideas:GAME-ADS/tropes/twenty-trope-catalog-pick-one-name-the-genre-it-sells, fake-ad-kernel-source-check/E1
(use verbatim axis labels). Native-axis assignments are MY judgement of each trope (assumption).
PREDICTION (before run): 18 of 20 tropes parody-safe (2 banned); with one native axis each, legal cells =
18*4 = 72 of 100; a batch needing distinct axes caps at 5 even though 18 tropes exist; giving every trope a
SECOND native axis cuts legal cells to <= 54 and max batch stays 5 (axis bound dominates);
BREAK: using the kernel's old label 'borrowed fame' as a 6th axis string makes the label-matching check drop
the celebrity trope's native axis (0 of 1 matched), inflating legal cells by exactly 1 per mislabelled trope.
Assumption: each trope has a knowable native axis. Wrong if legal cells != 72 in the one-native-axis case."""
AX = ["gameplay disguise", "narrative pretense", "popular externalization", "ruleset distortion", "incentive illusion"]
T = {  # trope: (native axes, safe, genre sold)
 "pull-the-pin": (["gameplay disguise"], 1, "puzzle-rescue"), "fail ad": (["gameplay disguise"], 1, "puzzle"),
 "lever dungeon": (["gameplay disguise"], 1, "rpg"), "bigger-number dungeon": (["ruleset distortion"], 1, "rpg"),
 "numbered barrels/gates": (["gameplay disguise"], 1, "strategy"), "fast merge army": (["gameplay disguise"], 1, "strategy-merge"),
 "save the King": (["narrative pretense"], 1, "puzzle-royalty"), "cinematic resource fantasy": (["narrative pretense"], 1, "idle-fantasy"),
 "level-1-crook-to-boss": (["narrative pretense"], 1, "mafia-sim"), "soap drama": (["narrative pretense"], 1, "match3-story"),
 "pretty-to-ugly makeover": (["gameplay disguise"], 1, "makeover"), "betrayal-then-rebuild": (["narrative pretense"], 1, "family-sim"),
 "celebrity skit": (["popular externalization"], 1, "casino-social"), "live-action TV spot": (["popular externalization"], 1, "4x"),
 "creator sponsorship": (["popular externalization"], 1, "rpg-raid"), "only 1% can solve": (["incentive illusion"], 1, "puzzle-iq"),
 "unfinished sort": (["gameplay disguise"], 1, "sort"), "choose-your-story": (["narrative pretense"], 1, "story-puzzle"),
 "won-real-money testimonial": (["incentive illusion"], 0, "social-casino"), "sexualised reveal": (["narrative pretense"], 0, "dating-sim")}
def legal(trope_native, axes):
    return [(t, a) for t, (nat, safe, g) in trope_native.items() if safe for a in axes if a not in nat]
def maxbatch(cells, tropes):
    # bipartite matching: distinct trope, distinct axis, distinct genre (genre unique per trope here)
    m = {}
    def aug(t, seen):
        for t2, a in cells:
            if t2 == t and a not in seen:
                seen.add(a)
                if a not in m or aug(m[a], seen): m[a] = t; return True
        return False
    return sum(aug(t, set()) for t in tropes)
safe = [t for t, v in T.items() if v[1]]
c1 = legal(T, AX); b1 = maxbatch(c1, safe)
T2 = {t: (nat + [AX[(AX.index(nat[0]) + 1) % 5]], s, g) for t, (nat, s, g) in T.items()}   # a second native axis
c2 = legal(T2, AX); b2 = maxbatch(c2, safe)
AXold = [a if a != "popular externalization" else "borrowed fame" for a in AX]
c3 = legal(T, AXold)   # old label: celebrity-type tropes' native axis no longer matches any axis string
inflate = len(c3) - len(c1)
nat_ct = sum(1 for t, (nat, s, g) in T.items() if s and nat[0] == "popular externalization")
print("safe tropes", len(safe), "of 20; one-native legal cells", len(c1), "/100; max batch", b1)
print("two-native legal cells", len(c2), "max batch", b2, "; old-label legal cells", len(c3), "inflation", inflate, "tropes native to that axis", nat_ct)
ok = len(safe) == 18 and len(c1) == 72 and b1 == 5 and len(c2) <= 54 and b2 == 5 and inflate == nat_ct
print("RESULT: %s safe %d/20, legal cells %d (one native) / %d (two native), max distinct-axis batch %d, old label 'borrowed fame' inflates legal cells by %d (=%d tropes)"
      % ("PASS" if ok else "FAIL", len(safe), len(c1), len(c2), b1, inflate, nat_ct))
