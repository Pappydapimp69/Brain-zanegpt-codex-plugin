# Rebuild of: over coda consonants and 5 features, the only "same value on feature set S" rules that make mud/truck (D/K)
# family and read/cheap (D/P) not family are {articulator} and {manner, articulator}; nothing from manner/voicing/place.
# Own fixture: 15 codas and my own feature values, plus a BREAK variant table using a standard distinctive-feature set
# ([labial], [coronal], [dorsal], [continuant], [voice], [nasal]) to see whether any rule other than a lips split fits.
from itertools import combinations
C = {  # manner, voicing, place, coarse place, articulator
 "P": ("stop", 0, "bilabial", "labial", "lips"), "B": ("stop", 1, "bilabial", "labial", "lips"),
 "T": ("stop", 0, "alveolar", "coronal", "tongue"), "D": ("stop", 1, "alveolar", "coronal", "tongue"),
 "K": ("stop", 0, "velar", "dorsal", "tongue"), "G": ("stop", 1, "velar", "dorsal", "tongue"),
 "F": ("fric", 0, "labiodental", "labial", "lips"), "V": ("fric", 1, "labiodental", "labial", "lips"),
 "S": ("fric", 0, "alveolar", "coronal", "tongue"), "Z": ("fric", 1, "alveolar", "coronal", "tongue"),
 "SH": ("fric", 0, "postalveolar", "coronal", "tongue"), "M": ("nasal", 1, "bilabial", "labial", "lips"),
 "N": ("nasal", 1, "alveolar", "coronal", "tongue"), "NG": ("nasal", 1, "velar", "dorsal", "tongue"),
 "L": ("approx", 1, "alveolar", "coronal", "tongue")}
FEATS = ["manner", "voicing", "place", "coarse", "articulator"]
def fits(table, feats, S):
    same = lambda a, b: all(table[a][feats.index(f)] == table[b][feats.index(f)] for f in S)
    return same("D", "K") and not same("D", "P")
subsets = [S for r in range(1, len(FEATS) + 1) for S in combinations(FEATS, r)]
good = [S for S in subsets if fits(C, FEATS, S)]
print(len(C), "codas,", len(subsets), "rules; fitting:", good)
mvp = [S for S in good if set(S) <= {"manner", "voicing", "place"}]
split = sorted(a for a in C if all(C[a][FEATS.index(f)] == C["D"][FEATS.index(f)] for f in good[0])) if good else []
print("family of D under", good[0] if good else None, ":", split)
SF = ["labial", "coronal", "dorsal", "cont", "voice", "nasal"]
T2 = {"D": (0, 1, 0, 0, 1, 0), "K": (0, 0, 1, 0, 0, 0), "P": (1, 0, 0, 0, 0, 0)}
sub2 = [S for r in range(1, len(SF) + 1) for S in combinations(SF, r)]
good2 = [S for S in sub2 if fits(T2, SF, S)]
print("BREAK standard features, fitting rules:", good2)
ok = set(good) == {("articulator",), ("manner", "articulator")} and not mvp and all("labial" in S for S in good2)
print("RESULT: %s own 15-coda table: fitting rules %s, none from manner/voicing/place; standard feature set: %d fitting rules, all include [labial] (the same lips split)" % ("PASS" if ok else "FAIL", good, len(good2)))
