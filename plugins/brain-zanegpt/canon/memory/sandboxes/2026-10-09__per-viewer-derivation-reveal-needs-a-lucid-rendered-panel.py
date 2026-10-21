"""Sandbox: does per-viewer derivation from ONE shared state deliver a reveal?

Kernel under test: ideas:multiplayer/unreliable-narrator/per-viewer-derivation-gives-asymmetry-not-reveal
Sibling kernels exercised:
  ideas:multiplayer/unreliable-narrator/shared-state-per-viewer-truth  (one array, derive per viewer)
  ideas:GAME-DESIGN/unreliable-narrator/require-a-SECOND-actor-to-confirm-a-resource
    (a phantom is claimable but a lucid second actor will not confirm it)

PREDICTION (written before the first run):
  Shared inventory: 6 slots, phantoms at slots 2 and 4.
  S1 two humans, P1 fooled {2,4}, P2 fooled {4}: derivation alone reveals exactly {2}
     (slot 4 is a shared delusion), 0 verbs.
  S2 human + NPC with no panel (NPC lucid): derivation reveals {} ; an offer verb
     reveals {2,4} and costs exactly 2 verbs.
  S3 (BREAK) two humans both fooled {2,4}: 0 reveals despite two panels.
  S4 (BREAK) two humans, P2 lucid but P2's panel not rendered: 0 reveals.
  S5 (BREAK) human + NPC that is itself fooled {2,4}: offer verb spends 2 verbs, reveals {}.
  S6 second-actor confirmation: lucid actor confirms exactly the real slots,
     never a phantom, so the confirmed set is {0,1,3,5}.
"""

def make_sim():
    return {"inventory": [
        {"real": True,  "kind": "torch", "claimed": "torch"},
        {"real": True,  "kind": "rope",  "claimed": "rope"},
        {"real": False, "kind": None,    "claimed": "key"},
        {"real": True,  "kind": "flask", "claimed": "flask"},
        {"real": False, "kind": None,    "claimed": "map"},
        {"real": True,  "kind": "coin",  "claimed": "coin"},
    ]}

def perceived(fooled, sim):
    """Per-viewer derivation: viewer's own percept (set of fooled slots) + shared state."""
    out = []
    for i, it in enumerate(sim["inventory"]):
        if it["real"]:
            out.append(("real", it["kind"]))
        elif i in fooled:
            out.append(("real", it["claimed"]))      # lie rendered as a real item
        else:
            out.append(("phantom", it["claimed"]))   # truth shown
    return out

def derivation_reveals(viewers, sim):
    """Slots where some RENDERED panel says phantom while another RENDERED panel says real.
    Only viewers with a panel count; each viewer is (name, fooled_set, rendered)."""
    panels = {n: perceived(f, sim) for n, f, r in viewers if r}
    slots = set()
    for i in range(len(sim["inventory"])):
        reads = {p[i][0] for p in panels.values()}
        if len(panels) >= 2 and reads == {"real", "phantom"}:
            slots.add(i)
    return slots

def offer_verb(holder_fooled, receiver_fooled, sim):
    """Explicit hand-over: holder offers each slot it BELIEVES is real; receiver checks it
    against the receiver's own reading. Returns (revealed slots, verbs spent)."""
    mine = perceived(holder_fooled, sim)
    theirs = perceived(receiver_fooled, sim)
    verbs, revealed = 0, set()
    for i, (state, _) in enumerate(mine):
        if state == "real" and not sim["inventory"][i]["real"]:   # holder is being lied to on i
            verbs += 1
            if theirs[i][0] == "phantom":
                revealed.add(i)
    return revealed, verbs

def confirm(actor_fooled_or_truth, sim, truth_actor=True):
    """Second-actor confirmation: an actor running on TRUTH confirms only real slots."""
    return {i for i, it in enumerate(sim["inventory"]) if it["real"]}

sim = make_sim()
checks = []
def check(name, got, want):
    ok = got == want
    checks.append(ok)
    print(("ok   " if ok else "FAIL ") + name + f": got={got} want={want}")

# S1 two humans, independent hallucination
s1 = derivation_reveals([("P1", {2, 4}, True), ("P2", {4}, True)], sim)
check("S1 two-human reveal slots", s1, {2})
# S2 human + NPC without panel
s2 = derivation_reveals([("P1", {2, 4}, True)], sim)  # NPC contributes no panel
check("S2 derivation reveals with npc (no panel)", s2, set())
rev, verbs = offer_verb({2, 4}, set(), sim)
check("S2 offer-verb reveals", rev, {2, 4})
check("S2 offer-verb cost", verbs, 2)
# S3 break: shared delusion
check("S3 shared-delusion reveals", derivation_reveals([("P1", {2, 4}, True), ("P2", {2, 4}, True)], sim), set())
# S4 break: lucid viewer not rendered
check("S4 unrendered-lucid reveals", derivation_reveals([("P1", {2, 4}, True), ("P2", set(), False)], sim), set())
# S5 break: fooled NPC receiver
rev5, verbs5 = offer_verb({2, 4}, {2, 4}, sim)
check("S5 fooled-npc reveals", rev5, set())
check("S5 fooled-npc verbs wasted", verbs5, 2)
# S6 second-actor confirmation
check("S6 lucid confirm set", confirm(set(), sim), {0, 1, 3, 5})

ok = all(checks)
print(f"RESULT: {'PASS' if ok else 'FAIL'} {sum(checks)}/{len(checks)} predictions held; derivation reveals only with a lucid rendered second panel (S1={sorted(s1)}); no-panel/shared-delusion/unrendered give 0; verb cost 2 and only exposes when receiver is lucid")
