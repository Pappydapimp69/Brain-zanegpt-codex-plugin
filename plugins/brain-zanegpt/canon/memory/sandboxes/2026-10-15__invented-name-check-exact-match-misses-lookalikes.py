"""Sandbox: 'invent every game name' (parody the genre, not the brand) -- what check actually enforces it?
Entries: ideas:LEGAL/parody/parody-the-genre-not-the-brand (invent every name; confusion test, not exact match),
ideas:COMEDY/fake-mobile-ad/premise-slot-machine-from-the-five-misleading-ad-patterns (trope cells need a made-up game
name), fake-ad-kernel-source-check/E1 (verify against the real source list rather than trust the label).
Real-name list = the 17 titles quoted in the catalog/slot machine kernels. Not legal advice; checks are my own proxies.
PREDICTION (before run): (1) 400 deterministic syllable-generated names: 0 exact collisions and 0 edit-distance<=2
collisions (names are long and random-ish); (2) 8 planted lookalikes (one letter changed / sound-alike / word swap): exact
match catches 0/8, edit distance<=2 catches >=5/8, adding a phonetic (soundex) key catches >=7/8; (3) BREAK: compound lookalikes that keep one distinctive
word ('Royal Gems' vs 'Royal Match') are caught by neither char-edit nor soundex on the full string, only by word overlap,
and word overlap on generic words (coin, war, city, island, sort, water) over-flags: >=3 of 12 clean invented compounds
using such words get flagged. Assumption: collisions come from spelling similarity. Wrong if (2) exact match catches >=1."""
import itertools
REAL = ["Homescapes", "Royal Match", "Count Masters", "Last War", "Evony", "Hero Wars", "Top War", "Gold and Goblins", "Mafia City",
        "Lilys Garden", "Project Makeover", "Family Island", "Coin Master", "Game of War", "Raid", "Water Sort", "Rise of Kingdoms"]
def lev(a, b):
    a, b = a.lower(), b.lower(); prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1): cur.append(min(prev[j] + 1, cur[-1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]
def soundex(w):
    w = "".join(c for c in w.lower() if c.isalpha()); codes = {c: d for d, cs in {"1": "bfpv", "2": "cgjkqsxz", "3": "dt", "4": "l", "5": "mn", "6": "r"}.items() for c in cs}
    out = w[0].upper(); last = codes.get(w[0], "")
    for c in w[1:]:
        d = codes.get(c, "")
        if d and d != last: out += d
        last = d if c not in "hw" else last
    return (out + "000")[:4]
def phon(name): return "".join(soundex(w) for w in name.split())
GENERIC = {"coin", "war", "city", "island", "sort", "water", "match", "master", "masters", "garden", "hero", "royal", "of", "and", "top", "last", "game", "count", "family", "rise", "gold"}
def exact(n): return any(n.lower() == r.lower() for r in REAL)
def edit(n): return any(lev(n, r) <= 2 for r in REAL)
def phonetic(n): return edit(n) or any(phon(n) == phon(r) for r in REAL)
def words(n): return any((set(n.lower().split()) - {"of", "and"}) & (set(r.lower().split()) - {"of", "and"}) for r in REAL)
def distinctive(n): return any((set(n.lower().split()) - GENERIC) & (set(r.lower().split()) - GENERIC) for r in REAL)
ONS = ["b", "d", "f", "g", "k", "m", "n", "p", "s", "t", "v", "z", "bl", "kr", "sp"]; NUC = ["a", "e", "i", "o", "u", "ai", "ou"]; COD = ["", "n", "r", "l", "x"]
syl = [o + n + c for o in ONS for n in NUC for c in COD]
gen = []
for i in range(400): gen.append(syl[(i * 37) % len(syl)] + syl[(i * 101 + 7) % len(syl)] + syl[(i * 53 + 3) % len(syl)])
gen = [g.capitalize() for g in gen]
c1 = (sum(map(exact, gen)), sum(map(edit, gen)), sum(map(phonetic, gen)))
lookalikes = ["Homescapez", "Roiyal Match", "Evoni", "Hero Warz", "Koin Master", "Water Sorte", "Mafia Sitty", "Raid Legends"]
sound = [sum(map(f, lookalikes)) for f in (exact, edit, phonetic)]
compounds = ["Royal Gems", "Coin Quest", "Last Island", "Water Kingdoms", "Mafia Cafe", "Gold Garden", "Hero Tower", "Top City", "Sort Match", "Family Farm", "Count Pigs", "Rise Cats"]
clean = ["Blimbo Farm", "Zorpix Quest", "Tankura Gems", "Pimbo Words", "Skyrel Racer", "Fennix Chef", "Gloop Sort2", "Kratos Pops", "Mellow Maze", "Brindle Bakery", "Vexa Plants", "Lumo Cats"]
comp = [sum(map(f, compounds)) for f in (exact, edit, phonetic, words, distinctive)]
clean_over = (sum(map(words, clean)), sum(map(distinctive, clean)))
cleanup = [n for n in clean if words(n)]
generic_clean = ["Coin Garden", "War Chef", "Water Farm", "Top Chef", "City Cats", "Sort Pigs", "Island Tanks", "Gold Racer", "Last Words", "Hero Cats", "Match Pigs", "Family Tanks"]
gen_over = (sum(map(words, generic_clean)), sum(map(distinctive, generic_clean)))
print("S1 400 generated: exact/edit/phonetic collisions", c1)
print("S2 8 lookalikes caught: exact/edit/phonetic", sound)
print("S3 12 compound lookalikes caught: exact/edit/phonetic/word-overlap/distinctive-word", comp)
print("S3b clean invented compounds with no generic words flagged: word-overlap %d, distinctive %d; clean with generic words (12): word-overlap %d, distinctive %d" % (clean_over + gen_over))
ok = (c1[0] == 0 and c1[1] == 0 and sound[0] == 0 and sound[1] >= 5 and sound[2] >= 7
      and comp[1] == 0 and comp[2] == 0 and comp[3] >= 10 and gen_over[0] >= 3 and gen_over[1] < gen_over[0])
print("RESULT: %s generated 0/400 collide; lookalikes caught exact %d edit %d phonetic %d of 8; compound lookalikes caught char-edit %d phonetic %d word-overlap %d of 12; word-overlap flags %d of 12 clean generic-word names (distinctive-word %d)"
      % ("PASS" if ok else "FAIL", sound[0], sound[1], sound[2], comp[1], comp[2], comp[3], gen_over[0], gen_over[1]))
