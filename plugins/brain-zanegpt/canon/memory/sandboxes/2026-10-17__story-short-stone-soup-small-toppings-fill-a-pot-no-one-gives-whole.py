"""Sandbox: The StoryTeller, "A Story Short" (1988) -- stone soup.

Episode (Wikipedia, The Storyteller TV series): the begging Storyteller picks up a stone, tricks
the castle cook into helping make soup from it; the stone goes into a cauldron of water and the
cook slowly adds other ingredients to improve the flavour; when the cook realises he has been
swindled he demands the Storyteller be boiled. The fable (Wikipedia, Stone Soup): travellers say
the stone soup only needs a little garnish, and each villager adds one ingredient until the pot is
a full meal nobody would have handed over whole.

Claim under test: asking for one small topping at a time for something visibly underway collects a
full pot that a single full request never gets, because each yes raises how far along the pot looks
and so the next person's willingness. The worthless seed (the stone) only has to carry the first asks.
It cannot buy an item bigger than anyone's top willingness.

Model (deterministic, stdlib): a full pot is worth M = 12 units. Asks go in a fixed order; an ask for
an item of cost c gets a yes iff c <= base + k * p, where p = (seed + real units given) / M is how far
along the pot looks. base = 0.8, k = 4, so top willingness (p = 1) is 4.8. A refused item is skipped
and the next ask is made (one pass). The stone's seed is perceived as 2 units and is worth 0.

PREDICTION (written before the first run):
  S1 tale: stone, toppings cheap-first [1,1,2,2,3,3]: full pot 12/12, 6 yeses.
  S2 no stone, same toppings: first ask refused (0.8 < 1), and every other too -> 0/12.
  S3 full request, stone in pot, one ask for 12: refused (1.47 < 12) -> 0/12;
     S3b full request split into 6 equal asks of 2 with nothing underway: all refused -> 0/12.
  S4 stone, toppings dear-first [3,3,2,2,1,1]: only the two 1s -> 2/12.
  S5 stone seen through after 3 yeses (seed drops to 0): the next 2 still given, both 3s refused -> 6/12.
  S6 BREAK: stone, [1,1,2,2,6] (meat worth half the pot): meat refused (6 > top willingness 4.8) -> 6/12.
Added after the ZaneGPT check, prediction written before rerun:
  S7 ladder gap, base constants, stone, [1,1,4,3,3]: the 4 is refused at p=4/12 (2.13) and so is
     everything after -> 2/12.
  S8 threshold 0.4 + 4p: stone cheap-first 2/12, no stone 0/12, dear-first 2/12 (ladder breaks at the 2s).
  S9 threshold 1.5 + 2p: stone cheap-first 6/12, no stone 2/12, dear-first 2/12.
  Across all three threshold settings the stone never does worse than no stone and cheapest-first never
  worse than dearest-first, but the full pot appears only under 0.8 + 4p.
"""

M, BASE, K, SEED = 12.0, 0.8, 4.0, 2.0


def brew(items, seed=SEED, reveal_after=None, base=None, k=None):
    base = BASE if base is None else base
    k = K if k is None else k
    real, yeses = 0.0, 0
    for c in items:
        s = 0.0 if (reveal_after is not None and yeses >= reveal_after) else seed
        willing = base + k * (s + real) / M
        if c <= willing + 1e-9:
            real += c
            yeses += 1
    return real, yeses


def report(name, items, **kw):
    real, yeses = brew(items, **kw)
    print(f"{name:<48} pot={real:4.1f}/{M:.0f} yeses={yeses}")
    return real, yeses


cheap = [1, 1, 2, 2, 3, 3]
r = {}
r["S1"] = report("S1 tale: stone, cheap toppings first", cheap)
r["S2"] = report("S2 no stone, same toppings", cheap, seed=0.0)
r["S3"] = report("S3 full request (one ask for 12), stone in pot", [12])
r["S3b"] = report("S3b 6 equal asks of 2, nothing underway", [2] * 6, seed=0.0)
r["S4"] = report("S4 stone, dear toppings first", list(reversed(cheap)))
r["S5"] = report("S5 stone seen through after 3 yeses", cheap, reveal_after=3)
r["S6"] = report("S6 BREAK stone, meat worth 6 last", [1, 1, 2, 2, 6])
r["S7"] = report("S7 ladder gap [1,1,4,3,3], stone", [1, 1, 4, 3, 3])
for tag, b, kk in (("S8", 0.4, 4.0), ("S9", 1.5, 2.0)):
    r[tag + "s"] = report(f"{tag} {b}+{kk}p stone cheap-first", cheap, base=b, k=kk)
    r[tag + "n"] = report(f"{tag} {b}+{kk}p no stone cheap-first", cheap, seed=0.0, base=b, k=kk)
    r[tag + "d"] = report(f"{tag} {b}+{kk}p stone dear-first", list(reversed(cheap)), base=b, k=kk)
print(f"    top willingness at a full-looking pot = {BASE + K:.1f}")

checks = [
    r["S1"] == (12, 6),
    r["S2"] == (0, 0),
    r["S3"] == (0, 0) and r["S3b"] == (0, 0),
    r["S4"] == (2, 2),
    r["S5"] == (6, 4),
    r["S6"] == (6, 4),
    r["S7"][0] == 2,
    (r["S8s"][0], r["S8n"][0], r["S8d"][0]) == (2, 0, 2),
    (r["S9s"][0], r["S9n"][0], r["S9d"][0]) == (6, 2, 2),
]
print("checks:", checks)
if all(checks):
    print("RESULT: PASS stone + cheap toppings fills 12/12 where no stone, a full ask or 6 equal asks get 0; "
          "dear-first gets 2/12; seeing through the stone after 3 yeses stalls at 6/12; "
          "BREAK: a 6-unit meat above top willingness 4.8 is never given, pot stops at 6/12; "
          "a ladder gap (a 4 after two 1s) stalls at 2/12; under 0.4+4p and 1.5+2p the pot reaches only 2/12 and 6/12, "
          "the stone and cheapest-first never worse but the full pot depends on every step being affordable")
else:
    print("RESULT: FAIL prediction mismatch, see checks")
