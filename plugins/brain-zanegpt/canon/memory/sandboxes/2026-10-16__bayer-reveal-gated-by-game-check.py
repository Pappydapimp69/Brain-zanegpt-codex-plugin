# Sandbox: Bayer 4x4 reveal (17 levels) driven by a game-of-scene beat sheet.
# A beat advances the reveal only if it is derived from the game (heightens it).
# Naive rule: any beat with a new noun advances it.
B = [[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]
def build(n):
    if n == 1: return [[0]]
    h = build(n//2); m = []
    for r in range(n):
        m.append([4*h[r%(n//2)][c%(n//2)] + [[0,2],[3,1]][r//(n//2)][c//(n//2)] for c in range(n)])
    return m
assert build(4) == B
def tone(level):  # count of lit cells for a level 0..16
    return sum(1 for r in B for v in r if v < level)
assert sorted(set(tone(l) for l in range(17))) == list(range(17))
# beat = (name, derived_from_game, new_noun)
SHEETS = {
 "heighten":   [("a",1,0),("b",1,0),("c",1,0),("d",1,0),("reveal",1,0)],
 "jump":       [("a",1,0),("b",1,0),("x",0,1),("y",0,1),("reveal",1,0)],
 "stock":      [("a",1,0),("s1",0,1),("s2",0,1),("c",1,0),("reveal",1,0)],
}
def run(sheet, rule, step):
    lvl = 0; early = 0
    for i,(n,d,nn) in enumerate(sheet):
        last = i == len(sheet)-1
        adv = (d and not nn) if rule == "derived" else bool(d or nn)
        if last: lvl = 16
        elif adv: lvl = min(15, lvl+step)
        if lvl == 16 and not last: early += 1
    return lvl, early
def distinct_states(sheet, rule, step):
    lvl=0; seen={0}
    for i,(n,d,nn) in enumerate(sheet):
        adv = (d and not nn) if rule=="derived" else bool(d or nn)
        if i==len(sheet)-1: lvl=16
        elif adv: lvl=min(15,lvl+step)
        seen.add(lvl)
    return len(seen)
# Prediction: with step 4, naive-any-noun rule closes the gap early in 0 of 3 sheets
# (cap 15) but flattens the ramp: jump/stock sheets advance on 4 non-game beats, so the
# ramp hits the cap (15) before the final beat in 2/3 sheets; derived rule never does.
capped = {}
for rule in ("naive","derived"):
    c = 0
    for name,sh in SHEETS.items():
        lvl=0
        for i,(n,d,nn) in enumerate(sh[:-1]):
            adv = (d and not nn) if rule=="derived" else bool(d or nn)
            if adv: lvl=min(15,lvl+4)
        if lvl==15: c+=1
        print(rule,name,"pre-reveal level",lvl,"early_close",run(sh,rule,4)[1])
    capped[rule]=c
print("capped sheets naive",capped["naive"],"derived",capped["derived"])
# Break scenario: a heighten beat that also adds a noun; derived rule skips it (mislabels)
brk = [("a",1,0),("b",1,1),("c",1,0),("d",1,0),("reveal",1,0)]
lvl=0
for n,d,nn in brk[:-1]:
    if d and not nn: lvl=min(15,lvl+4)
print("break: heighten-with-noun sheet, derived rule pre-reveal level", lvl, "(true heightens: 4 -> would be 15)")
ok = capped["naive"] > capped["derived"] and lvl == 12
print("RESULT: %s naive capped %d/3 sheets vs derived %d/3; derived under-advances noun-bearing heighten (12 vs 15)" % ("PASS" if ok else "FAIL", capped["naive"], capped["derived"]))
