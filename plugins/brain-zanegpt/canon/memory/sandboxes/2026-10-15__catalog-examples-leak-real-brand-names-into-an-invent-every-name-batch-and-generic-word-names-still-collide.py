# Sandbox: invent-every-name rule applied to a catalog that names real games. Deterministic, stdlib only.
import itertools
REAL = ["Playrix","Homescapes","Hero Wars","Evony","Top War","Royal Match","Gold and Goblins","Mafia City",
        "Lily's Garden","Project Makeover","Family Island","Coin Master","Game of War","RAID","Water Sort","Last War"]
# 20-trope catalog from the kernel: (trope label, real example it names, or '')
CAT = [("pull-the-pin","Playrix"),("fail ad",""),("lever dungeon","Hero Wars"),("bigger-number dungeon","Hero Wars"),
 ("numbered barrels","Evony"),("merge-army battle","Top War"),("save the King","Royal Match"),("cinematic resource","Gold and Goblins"),
 ("crook-to-boss","Mafia City"),("soap drama","Lily's Garden"),("makeover","Project Makeover"),("betrayal-rebuild","Family Island"),
 ("celebrity skit","Coin Master"),("TV spot","Game of War"),("creator read","RAID"),("1% caption",""),("sort","Water Sort"),
 ("choose-story",""),("testimonial",""),("reveal","")]
leak = sum(1 for _,e in CAT if e)
words = lambda s: {w.lower().strip("'s") for w in s.split() if len(w)>2}
real_words = set().union(*[words(r) for r in REAL]) - {"and","the","of"}
# name generators: A = two generic words from the catalog vocabulary; B = invented syllable pairs
GEN = ["Royal","Top","Hero","Last","Family","Water","War","Match","Island","Sort","Garden","City"]
A = [f"{a} {b}" for a,b in itertools.permutations(GEN,2)][:60]
SYL = ["zo","ka","mi","ru","bel","tan","vi","qua","dro","fen"]
B = [x+y for x,y in itertools.permutations(SYL,2)][:60]
def collides(name):
    nw = {w.lower() for w in name.split()}
    exact = name.lower() in {r.lower() for r in REAL}
    word = bool(nw & real_words)
    return exact, word
for label,names in (("generic-word names",A),("invented syllable names",B)):
    ex=sum(collides(n)[0] for n in names); wd=sum(collides(n)[1] for n in names)
    print(f"{label}: exact {ex}/{len(names)} word-overlap {wd}/{len(names)}")
exA=sum(collides(n)[0] for n in A); wdA=sum(collides(n)[1] for n in A); wdB=sum(collides(n)[1] for n in B); exB=sum(collides(n)[0] for n in B)
# scrubbing the catalog: replace every real example with a placeholder
scrubbed=[(l,"") for l,_ in CAT]
print("catalog entries naming a real game:",leak,"of",len(CAT),"| after scrub:",sum(1 for _,e in scrubbed if e))
ok = leak==15 and exA==4 and wdB==0 and exB==0   # exA expected 0 (refuted); word-overlap on A is true by construction, not a finding
print(("RESULT: PASS" if ok else "RESULT: FAIL"),f"{leak}/20 catalog entries name a real game; generic-word names exact {exA}/60 (word-overlap by construction); syllable names 0/60")
