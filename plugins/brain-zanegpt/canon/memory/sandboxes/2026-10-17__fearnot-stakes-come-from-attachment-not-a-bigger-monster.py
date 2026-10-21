"""Fearnot (The StoryTeller, from Grimm KHM 4, the youth who went forth to learn fear).
Deterministic, stdlib. A scene threatens one target (the hero or his sweetheart) through a channel:
'fight' (something he can beat) or a channel strength cannot touch ('parting', 'curse'). Stakes = loss chance x value of the
target to the hero (a product, so a zero on either side vetoes the scene). The hero wins any fight up to his
strength; above it he loses the share (size - strength) / size. A fully immune hero has infinite strength."""
INF = float("inf")
def loss_chance(scene, strength, beside_her=True):
    target, channel, size = scene
    if channel != "fight":
        return size                                   # size is the chance itself; strength cannot touch it
    if target == "sweetheart" and not beside_her:
        return 1.0                                    # nobody there to fight for her
    return 0.0 if size <= strength else (size - strength) / size
def stakes(scene, strength=INF, values=None, beside_her=True):
    values = values or {"hero": 10, "sweetheart": 10}
    return loss_chance(scene, strength, beside_her) * values[scene[0]]
sizes = [1, 10, 100, 1000]
s1 = [stakes(("hero", "fight", s)) for s in sizes]
s2 = stakes(("sweetheart", "fight", 1000))
s3 = stakes(("sweetheart", "parting", 0.3))
s4 = stakes(("sweetheart", "fight", 1), beside_her=False)
s5 = stakes(("sweetheart", "curse", 0.5), beside_her=True)
b1 = stakes(("hero", "fight", 1000), strength=100)
b2 = [stakes(sc, values={"hero": 10, "sweetheart": 0}) for sc in [("sweetheart", "parting", 0.3), ("sweetheart", "fight", 1000)]]
b2 += [stakes(("hero", "fight", s)) for s in sizes]
print(f"1) monsters of size {sizes} at the immune hero: stakes {s1}")
print(f"2) size-1000 monster at the sweetheart, hero beside her: stakes {s2}")
print(f"3) a parting he cannot fight (chance 0.3, value 10): stakes {s3:.1f}")
print(f"4) a size-1 monster at the sweetheart while he is away: stakes {s4:.1f}")
print(f"5) a curse on the sweetheart while he stands beside her (chance 0.5): stakes {s5:.1f}")
print(f"BREAK a) hero wins fights only up to 100, size-1000 monster: stakes {b1:.1f} (vs attachment {s3:.1f})")
print(f"BREAK b) no attachment (sweetheart value 0): max stakes over every scene {max(b2)}")
ok = max(s1) == 0 and s2 == 0 and abs(s3 - 3.0) < 1e-9 and s4 == 10 and abs(s5 - 5.0) < 1e-9 and abs(b1 - 9.0) < 1e-9 and max(b2) == 0
print(("RESULT: PASS " if ok else "RESULT: FAIL ") + f"for a fully immune hero bigger monsters give stakes {max(s1)} up to size 1000 and "
      f"a monster at his sweetheart while he guards her gives {s2}; only a loss his strength cannot reach gives stakes (parting {s3:.1f}, smallest monster while he is away {s4:.1f}, curse while he guards her {s5:.1f}); "
      f"with immunity capped at 100 a size-1000 monster gives {b1:.1f}, and with no attachment nothing gives stakes")
