# Composes: every-video-gets-its-own-joke-and-script (name swapped into one template reads mass-produced),
# fake-ad-kernel-source-check (audit labels), invented-name-check-exact-match-misses-lookalikes.
from difflib import SequenceMatcher
REAL = ["Candy Crush Saga","Royal Match","Clash of Clans","Homescapes","Coin Master","Gardenscapes"]
LOOK = ["Candy Crash Saga","Royal Matches","Clash of Clan","Home Scapes","Coin Masters","Garden Scapes"]  # near-copies
CLEAN = ["Turnip Tango","Moss Bandit","Pocket Lantern","Gravel Opera","Velvet Hatchling","Static Orchard"]
GENERIC = {"saga","match","clash","home","coin","master","garden"}
def edit_hit(n):
    return any(SequenceMatcher(None,n.lower(),r.lower()).ratio()>=0.85 for r in REAL)
def exact_hit(n): return n in REAL
def word_overlap(n): return any(set(n.lower().split())&set(r.lower().split()) for r in REAL)
def distinct_hit(n):
    rw={w for r in REAL for w in r.lower().split()}-GENERIC
    return any(w in rw for w in n.lower().split()) or edit_hit(n)
print("exact on lookalikes", sum(map(exact_hit,LOOK)),"/6")
print("edit on lookalikes", sum(map(edit_hit,LOOK)),"/6; on clean", sum(map(edit_hit,CLEAN)),"/6")
print("distinct on lookalikes", sum(map(distinct_hit,LOOK)),"/6; on clean", sum(map(distinct_hit,CLEAN)),"/6")
TEMPLATE = "Pull the pin. The hero fails. Red stamp FAIL. Download {g} now. 99% of players cannot beat level 3."
swapped = [TEMPLATE.format(g=g) for g in CLEAN]
own = ["A goat files taxes inside {g}; the audit is the boss fight.",
       "Grandma's cursor eats the screen in {g} until the jingle stops.",
       "Two snails race for the fake store card in {g}. Neither finishes.",
       "In {g} the tutorial hand quits and the player must teach it.",
       "A bridge sells itself to the highest bidder in {g}.",
       "The loading bar in {g} confesses it was never loading."]
owned=[s.format(g=g) for s,g in zip(own,CLEAN)]
def strip(s,g): return s.replace(g,"@")
def mean_sim(xs):
    v=[SequenceMatcher(None,strip(a,g1),strip(b,g2)).ratio() for i,(a,g1) in enumerate(zip(xs,CLEAN)) for b,g2 in list(zip(xs,CLEAN))[i+1:]]
    return sum(v)/len(v)
sw,ow=mean_sim(swapped),mean_sim(owned)
print("mean script similarity after name strip: swapped %.2f own %.2f"%(sw,ow))
SOURCE=["popular externalization","social proof","false urgency","fake gameplay","bait-and-switch"]
KERNEL=["borrowed fame","social proof","false urgency","fake gameplay","bait-and-switch"]
bad=sum(k!=s for k,s in zip(KERNEL,SOURCE)); print("label mismatches",bad,"/5")
ok = sw>=0.99 and ow<0.5 and sum(map(exact_hit,LOOK))==0 and sum(map(edit_hit,LOOK))>=5 and sum(map(edit_hit,CLEAN))==0 and bad==1
print(("RESULT: PASS" if ok else "RESULT: FAIL"),"swapped sim %.2f own %.2f; exact 0/6 edit %d/6 on lookalikes, %d/6 on clean; labels %d/5"%(sw,ow,sum(map(edit_hit,LOOK)),sum(map(edit_hit,CLEAN)),bad))
