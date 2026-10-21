"""The True Bride: one standing trap on the pursuit path takes both villains.

The StoryTeller "The True Bride": the Thought Lion builds the troll a palace with a
room/door that opens onto nothing; the troll, inspecting it, falls to his death.
Later the troll's daughter chases the lovers, is misled by their scent and voices,
and falls into the same room.

Model: a palace graph. A standing trap stays armed after a fall; a one-shot trap
seals after its first victim. Villain 1 (troll) inspects every room (BFS order).
Villain 2 (daughter) chases the lovers: she follows a lure (scent/voices) if one is
placed, otherwise the lovers' own trail; an informed chaser (who saw the first fall)
steps around a known trap. The lovers' own escape route is checked for crossing the
trap too.
Measured: catches per trap built, author-added steps needed to make the second
catch happen (detour length), and allies exposed to the trap.
Deterministic, stdlib only.
"""
from collections import deque

EDGES = [("gate", "hall"), ("hall", "east"), ("hall", "west"),
         ("west", "door"), ("east", "garden"), ("garden", "road")]
G = {}
for a, b in EDGES:
    G.setdefault(a, []).append(b)
    G.setdefault(b, []).append(a)
for n in G:
    G[n].sort()


def bfs_path(src, dst, avoid=()):
    prev = {src: None}
    q = deque([src])
    while q:
        u = q.popleft()
        if u == dst:
            break
        for v in G[u]:
            if v not in prev and v not in avoid:
                prev[v] = u
                q.append(v)
    if dst not in prev:
        return None
    path, u = [], dst
    while u is not None:
        path.append(u)
        u = prev[u]
    return path[::-1]


def inspect_order(src="gate"):
    seen, q, order = {src}, deque([src]), []
    while q:
        u = q.popleft()
        order.append(u)
        for v in G[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    return order


def walk(path, trap, armed):
    """Return (caught, still_armed)."""
    if armed and trap in path:
        return True, armed
    return False, armed


def scenario(name, trap="door", standing=True, lure=None, informed=False, lovers_bypass=True):
    armed = True
    traps_built = 1
    catches = 0
    # villain 1: the troll inspects every room of his new palace
    troll_path = inspect_order()
    caught, _ = walk(troll_path, trap, armed)
    if caught:
        catches += 1
        if not standing:
            armed = False
    # lovers escape gate -> road; a trap on their own route exposes them unless bypassed
    lovers_route = bfs_path("gate", "road")
    exposure = 1 if (trap in lovers_route and not lovers_bypass) else 0
    # villain 2: the daughter chases by lure if any, else by the lovers' trail
    goal = lure if lure else "road"
    avoid = (trap,) if informed else ()
    chase = bfs_path("gate", goal, avoid=avoid)
    if chase is None:  # informed chaser refuses the lure that leads into the known trap
        chase = bfs_path("gate", "road", avoid=avoid)
    caught2, _ = walk(chase, trap, armed)
    if not caught2 and chase[-1] != "road":
        # the lure led nowhere (trap sealed): she resumes the chase from there
        chase = chase + bfs_path(chase[-1], "road", avoid=avoid)[1:]
    detour = 0
    if caught2:
        catches += 1
    elif armed and not informed:
        # steps the author must add to bring her to the trap and back to her route
        to_trap = bfs_path("hall", trap)  # forced steps out from her route to the trap
        detour = len(to_trap) - 1 if to_trap else 0
    setups = traps_built if catches == 2 else traps_built + 1
    second = "caught" if caught2 else ("reaches lovers" if chase[-1] == "road" else "stops")
    print(f"{name:<50} catches={catches} setups={setups} detour={detour} "
          f"exposure={exposure} second_villain={second} chase={'-'.join(chase)}")
    return catches, setups, detour, exposure, chase[-1]


def main():
    r1 = scenario("1) standing trap + lure at door (episode)", lure="door")
    r2 = scenario("2) one-shot trap (seals after first fall)", standing=False, lure="door")
    r3 = scenario("3) standing trap off pursuit path, no lure")
    r4 = scenario("4) BREAK informed chaser (saw first fall), lure", lure="door", informed=True)
    r5 = scenario("5) chokepoint trap at hall, no lure, no bypass", trap="hall", lovers_bypass=False)

    checks = [
        ("1) 2 catches, 1 setup, 0 detour", r1[:3] == (2, 1, 0)),
        ("2) one-shot: 1 catch, 2 setups, chaser reaches lovers", r2[:2] == (1, 2) and r2[4] == "road"),
        ("3) off-path: 1 catch, 2-step detour", r3[0] == 1 and r3[2] == 2),
        ("4) BREAK informed: 1 catch", r4[0] == 1),
        ("5) chokepoint: 2 catches, 0 detour, 1 ally exposure", r5[:4] == (2, 1, 0, 1)),
    ]
    for label, ok in checks:
        print(("ok   " if ok else "MISS ") + label)
    if all(ok for _, ok in checks):
        print("RESULT: PASS standing trap on the lured pursuit path: 2 catches from 1 trap, 0 added steps; "
              "one-shot needs 2 setups; off-path needs a 2-step detour; informed chaser escapes; "
              "chokepoint catches both but exposes the lovers")
    else:
        print("RESULT: FAIL " + "; ".join(l for l, ok in checks if not ok))


if __name__ == "__main__":
    main()
