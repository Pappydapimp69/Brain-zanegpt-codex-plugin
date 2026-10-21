# Composes companion-planting-claim-keyed-grading (grade by plant,target,setting) with
# the brainwork binding-rate lesson (log a rate per level; a pinned 0 or 1 means non-binding).
CLAIMS = [  # (plant, target, setting, true_grade)
 ("marigold","nematode","bed","strong"),("marigold","aphid","bed","weak"),("marigold","whitefly","greenhouse","moderate"),
 ("marigold","nematode","pot","weak"),("basil","aphid","bed","weak"),("basil","hornworm","bed","moderate"),
 ("basil","aphid","greenhouse","weak"),("nasturtium","aphid","bed","strong"),("nasturtium","aphid","pot","moderate"),
 ("garlic","aphid","bed","moderate"),("garlic","beetle","bed","weak"),("garlic","beetle","greenhouse","weak"),
]
def by_plant(c):  # majority-grade per plant, ties -> first seen
    g = {}
    for p,_,_,t in c: g.setdefault(p,[]).append(t)
    return {p: max(sorted(set(v)), key=v.count) for p,v in g.items()}
pl = by_plant(CLAIMS)
key = {(p,t,s):g for p,t,s,g in CLAIMS}
mis_plant = sum(1 for p,t,s,g in CLAIMS if pl[p] != g)
mis_key = sum(1 for p,t,s,g in CLAIMS if key[(p,t,s)] != g)
# binding rate analog: share of a plant's claims whose grade differs from the plant's modal grade
def bind(plant):
    rows=[g for p,_,_,g in CLAIMS if p==plant]; return sum(g!=pl[plant] for g in rows)/len(rows)
rates = {p: round(bind(p),2) for p in pl}
print("grades per plant", {p: len({g for q,_,_,g in CLAIMS if q==p}) for p in pl})
print("misgraded per-plant", mis_plant, "claim-keyed", mis_key, "of", len(CLAIMS))
print("non-binding rate by plant", rates)
# BREAK scenario: duplicate key with conflicting grade must be detected, not silently overwritten
dup = CLAIMS + [("garlic","beetle","bed","strong")]
seen={}; conflicts=0
for p,t,s,g in dup:
    k=(p,t,s)
    if k in seen and seen[k]!=g: conflicts+=1
    seen[k]=g
print("key conflicts detected", conflicts)
pinned = [p for p,r in rates.items() if r in (0.0,1.0)]
ok = mis_key==0 and mis_plant>=4 and conflicts==1 and pinned==[]
print(("RESULT: PASS" if ok else "RESULT: FAIL"), "misgraded per-plant", mis_plant, "claim-keyed", mis_key, "conflicts", conflicts, "pinned plants", pinned)
