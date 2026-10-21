"""Sandbox: collective#E5 (default-deny gate) x pocketzane#E5/E6/E4 (silent no-op tags,
block-boundary reset, instrument the lowest primitive).  Stdlib only, no RNG, no timing.

PREDICTION (written before the first run):
  Engine: 12 working tags, 8 accept-but-ignore (dead) tags.  Corpus: each of 20 tags used 2x
  (40 uses; 16 dead uses, 24 working uses).
  S1 hand deny-list (knows 3 of 8 dead tags):          silent leaks = 10, false blocks = 0
  S2 hand allowlist (knows 10 of 12 working tags):     silent leaks = 0,  false blocks = 4
  S3 probe-derived allowlist (one canary per tag):     silent leaks = 0,  false blocks = 0
  S4 engine drift (one working tag dies, one dead tag starts working), policies NOT re-edited:
        hand allowlist leaks 2, hand deny-list leaks 12 and false-blocks 2,
        probe re-run: leaks 0, false blocks 0
  S5 directive declared once in a 4-block doc applies to 1/4 blocks; per-block re-declare = 4/4
  S6 BREAK: a once-per-block tag (works on first use per block only): a single-use canary probe
        admits it, so probe-allowlist still leaks 3 of 6 uses -> the rule must be narrowed to
        stateless tags; a two-use canary in one block catches it (leaks 0).
  The claim PASSes only if all six numbers match.
"""
W = ["laugh", "sigh", "whisper", "pause", "excited", "sad", "angry", "cheer", "cough", "gasp", "breath", "sing"]
D = ["building", "curious", "thoughtful", "smirk", "nervous", "proud", "tired", "shy"]
ALL = W + D


class Engine:
    def __init__(self, working, dead, once=()):
        self.working, self.dead, self.once = set(working), set(dead), set(once)

    def render(self, blocks):
        """per use -> (tag, 'effect'|'silent'|'error'); state resets at each block."""
        out = []
        for blk in blocks:
            seen = set()
            for t in blk:
                if t in self.working:
                    if t in self.once and t in seen:
                        out.append((t, "silent"))
                    else:
                        out.append((t, "effect"))
                    seen.add(t)
                elif t in self.dead:
                    out.append((t, "silent"))
                else:
                    out.append((t, "error"))
        return out

    def active_directive_blocks(self, blocks_decl):
        return [i for i, declared in enumerate(blocks_decl) if declared]


def corpus():
    blocks = [[] for _ in range(5)]
    for i, t in enumerate(ALL):
        blocks[i % 5].append(t)
        blocks[(i + 2) % 5].append(t)
    return blocks


def gate(blocks, admit):
    return [[t for t in b if admit(t)] for b in blocks]


def score(engine, blocks, admit):
    """leaks = admitted uses that do nothing; fb = blocked uses that would have worked."""
    leaks = sum(1 for _, o in engine.render(gate(blocks, admit)) if o == "silent")
    fb = 0
    for b in blocks:
        for t in b:
            if not admit(t) and t in engine.working:
                fb += 1
    return leaks, fb


def probe(engine, tags, uses=1):
    """canary: render the tag `uses` times in one fresh block; effect on every use = working."""
    ok = set()
    for t in tags:
        res = engine.render([[t] * uses])
        if all(o == "effect" for _, o in res):
            ok.add(t)
    return ok


results = {}
eng = Engine(W, D)
C = corpus()
assert sum(len(b) for b in C) == 40

deny = set(D[:3])
results["S1"] = score(eng, C, lambda t: t not in deny)
allow = set(W[:10])
results["S2"] = score(eng, C, lambda t: t in allow)
pa = probe(eng, ALL)
results["S3"] = score(eng, C, lambda t: t in pa)

# S4 drift: laugh dies, building starts working; hand policies unchanged
eng2 = Engine((set(W) - {"laugh"}) | {"building"}, (set(D) - {"building"}) | {"laugh"})
s4_allow = score(eng2, C, lambda t: t in allow)
s4_deny = score(eng2, C, lambda t: t not in deny)
pa2 = probe(eng2, ALL)
s4_probe = score(eng2, C, lambda t: t in pa2)
results["S4"] = (s4_allow, s4_deny, s4_probe)

# S5 directive coverage
decl_once = [True, False, False, False]
decl_each = [True, True, True, True]
s5 = (len(eng.active_directive_blocks(decl_once)), len(eng.active_directive_blocks(decl_each)))
results["S5"] = s5

# S6 break: once-per-block tag
eng3 = Engine(W, D, once=["pause"])
doc = [["pause", "pause"] for _ in range(3)]
p1 = probe(eng3, ["pause"], uses=1)
p2 = probe(eng3, ["pause"], uses=2)
s6_single = score(eng3, doc, lambda t: t in p1)
s6_double = score(eng3, doc, lambda t: t in p2)
results["S6"] = (s6_single, s6_double, sorted(p1), sorted(p2))

for k, v in results.items():
    print(k, v)

ok = True
ok &= results["S1"] == (10, 0)
ok &= results["S2"] == (0, 4)
ok &= results["S3"] == (0, 0)
ok &= s4_allow[0] == 2 and s4_deny == (12, 2) and s4_probe == (0, 0)
ok &= s5 == (1, 4)
ok &= s6_single[0] == 3 and s6_double[0] == 0
print("S4 detail: allow=%s deny=%s probe=%s" % (s4_allow, s4_deny, s4_probe))
print("RESULT: %s deny-list leaks %d/16 dead uses, hand allowlist blocks %d working uses, probe-derived allowlist 0/0; drift leaks allow=%d deny=%d probe=%d; directive 1/4->4/4; once-per-block break: single-use probe leaks %d, two-use probe %d"
      % ("PASS" if ok else "FAIL", results["S1"][0], results["S2"][1], s4_allow[0], s4_deny[0], s4_probe[0], s6_single[0], s6_double[0]))
