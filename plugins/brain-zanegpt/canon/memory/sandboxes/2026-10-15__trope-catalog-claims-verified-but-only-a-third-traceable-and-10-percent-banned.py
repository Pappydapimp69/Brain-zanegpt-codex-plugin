# Sandbox: 20-trope catalog + anti-template rule + source-check rule. Stdlib only, deterministic.
from itertools import combinations
from math import comb
CATALOG = [  # (trope, example named in kernel, banned-in-real-ads)
 ("pull-the-pin","Playrix",0),("fail ad","",0),("lever/slider dungeon","Hero Wars",0),
 ("bigger-number-wins dungeon","Hero Wars",0),("numbered barrels/gates squad","Evony",0),
 ("fast merge-army battle","Top War",0),("save the King","Royal Match",0),
 ("cinematic resource fantasy","Gold and Goblins",0),("crook-to-boss transformation","Mafia City",0),
 ("15-second soap drama","Lily's Garden",0),("pretty-to-ugly makeover","Project Makeover",0),
 ("betrayal-then-rebuild","Family Island",0),("celebrity skit","Coin Master",0),
 ("live-action TV spot","Game of War",0),("creator sponsorship read","RAID",0),
 ("only 1% can solve caption","",0),("unfinished satisfying sort","Water Sort",0),
 ("choose-your-story","",0),("won-real-money testimonial","social casino",1),
 ("sexualised reveal","",1)]
# kernel Source line names: ASA Playrix 2020; ASA Top Games 2024 (Evony); BBB Project Makeover;
# aftermath Hero Wars; knowyourmeme Mafia City; wbur Lily's Garden; udonis (generic, names none)
SOURCED = {"Playrix","Evony","Project Makeover","Hero Wars","Mafia City","Lily's Garden"}
n = len(CATALOG); banned = sum(b for *_,b in CATALOG)
traceable = sum(1 for t,e,b in CATALOG if e in SOURCED)
print("tropes", n, "banned", banned, "example-traceable to Source line", traceable)
# claim 'each verified': checks
ok_each = traceable == n
# P(batch of k distinct tropes drawn uniformly contains a banned one)
def p_banned(k): return 1 - comb(n-banned,k)/comb(n,k)
for k in (1,5,8,10): print("k",k,"P(banned)",round(p_banned(k),3))
# exact check by enumeration k=8 (125970 combos)
bad = sum(1 for c in combinations(range(n),8) if any(CATALOG[i][2] for i in c))
print("enum k=8", round(bad/comb(n,8),3))
safe = [c for c in CATALOG if not c[2]]
# anti-template: distinct trope per video caps at len(safe); 19th video must repeat
print("max distinct-trope safe batch", len(safe))
# BREAK scenario: removing banned tropes shifts the cap; a 20-video batch cannot be distinct and safe
print("20-video distinct batch safe?", len(safe) >= 20)
checks = [not ok_each, traceable<=8, abs(bad/comb(n,8)-p_banned(8))<1e-9, len(safe)==18, p_banned(8)>0.6]
print("checks", checks)
print(("RESULT: PASS" if all(checks) else "RESULT: FAIL"),
 f"traceable {traceable}/20 (claim 'each verified' fails); banned 2/20; P(banned in 8 distinct)={p_banned(8):.3f}; safe distinct cap 18")
