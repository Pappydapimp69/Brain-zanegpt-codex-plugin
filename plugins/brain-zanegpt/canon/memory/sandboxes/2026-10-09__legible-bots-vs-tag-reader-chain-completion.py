"""Sandbox: does restricting bots to interface-visible info change a design verdict?
Kernels: gamedesign/simulation/play-the-legible-game, gamedesign/discoverability/assert-every-bound-verb...
Memory:  sandbox-kernel-system-narrative/E1 (staged selector, not-recently-shown placement).
Deterministic: seeded LCG, all parameters explicit."""
NPCS = 5; DAYS = 6; BUDGET = 4; CHAIN_NPC = 3; NEED = 3

class Lcg:
    def __init__(s, seed): s.x = (seed * 2654435761 + 12345) % 2**32
    def f(s):
        s.x = (s.x * 1664525 + 1013904223) % 2**32
        return s.x / 2**32

# 6 beats per NPC: (name, criteria needed over 3 facts, specificity=len(criteria))
BEATS = [("b%d" % i, tuple(j for j in range(3) if (i >> j) & 1 and i < 6)) for i in range(6)]

FIT = {'b0':0.05,'b1':0.22,'b2':0.41,'b3':0.58,'b4':0.77,'b5':0.93}
def select(facts, recent, lru, tension):
    ok = [b for b in BEATS if all(facts[c] for c in b[1])]
    ms = max(len(b[1]) for b in ok)
    top = [b for b in ok if len(b[1]) == ms]               # specificity stage
    if lru == "between":
        f = [b for b in top if b[0] not in recent]; top = f or top
    t = tension
    best = min(abs(FIT[b[0]] - t) for b in top)             # best tension fit (continuous -> usually unique)
    top = [b for b in top if abs(FIT[b[0]] - t) == best]
    if lru == "after":
        f = [b for b in top if b[0] not in recent]; top = f or top
    return sorted(top)[0]                                   # lexical tie-break

def play(policy, seed, attach=0.0, bed=BUDGET, lru="between"):
    r = Lcg(seed); trust = [0]*NPCS; recent = [[] for _ in range(NPCS)]
    mood = 5; last = None; done = False
    for day in range(DAYS):
        for a in range(min(bed, BUDGET)):
            facts = [(day + a + k) % 2 == 0 or r.f() < .5 for k in range(3)]
            if policy == "tag":
                n = CHAIN_NPC
            else:
                if last is not None and r.f() < attach: n = last
                elif day >= 6 and mood <= 2: n = CHAIN_NPC   # late self-interest keyed to VISIBLE mood
                else: n = int(r.f() * NPCS)
            b = select(facts, recent[n][-3:], lru, ((mood * 7 + day) % 10) / 10)
            if b[0] not in recent[n][-3:]: trust[n] += 1
            recent[n].append(b[0]); last = n; mood = max(0, mood - (1 if r.f() < .3 else 0))
            if n == CHAIN_NPC and trust[n] >= NEED: done = True
    return done

def rate(**kw):
    return sum(play(seed=s, **kw) for s in range(300)) / 300

print("S1 tag-reader bot, LRU between :", rate(policy="tag"))
print("S2 tag-reader bot, LRU after   :", rate(policy="tag", lru="after"))
res = {}
for lru in ("between", "after"):
    for att in (0.0, 0.5, 0.8):
        res[(lru, att)] = rate(policy="human", attach=att, bed=3, lru=lru)
        print("S3 legible human lru=%s attach=%.1f bed=3: %.3f" % (lru, att, res[(lru, att)]))
print("S4 legible, no bedtime-limit    :", rate(policy="human", attach=.5, bed=4))
# verb guard (sibling kernel assert-every-bound-verb): tautology test
hint = "move gather give trade"
help_text = "Walk with arrows. Chop wood or mine stone. Offer items to friends.\nKeys: move gather give trade"
strip = "\n".join(l for l in help_text.split("\n") if not l.startswith("Keys:"))
naive = [v for v in hint.split() if v not in help_text]
real = [v for v in hint.split() if v not in strip]
print("S5 verb guard naive misses:", naive, " stripped misses:", real)
tag = res[("between", 0.5)]
ok = rate(policy="tag") > 0.95 and tag < 0.5 and naive == [] and len(real) == 4
print("RESULT: %s tag-bot %.2f vs legible %.3f (attach0.5,lru between); lru-after attach.8 %.3f; naive verb guard misses %d, stripped %d"
      % ("PASS" if ok else "FAIL", rate(policy="tag"), tag, res[("after", .8)], len(naive), len(real)))
