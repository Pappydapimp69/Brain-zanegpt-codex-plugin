"""The Soldier and Death (The StoryTeller, from the Russian tale collected by Afanasyev, retold by Arthur Ransome).
Deterministic, stdlib. The soldier wants a final resting place. A place takes him if its own rule admits him and, when it
holds a grudge, he has not beaten it. Map: earth -> death (if Death takes him), earth -> hell gate (always) -> hell (if the
devils admit him); at the hell gate the devils hand over souls and a map to heaven's gate -> heaven (if heaven's rule admits
him, or a key fires from inside). The key is the sack handed to a holder who must shout "Into the sack, soldier!" once
inside. Heaven's gate wipes memory; a key fires if its holder still remembers after the gate or the key fires by itself.
Exits = terminal places reachable by BFS from earth. No exit reachable = he wanders the earth."""
from collections import deque
TERMINALS = ("death", "hell", "heaven")
def admits(place, won, rules, grudges):
    return rules[place] and not (grudges[place] and place in won)
def key_fires(holders, gate_wipes_memory=True):
    return any(h["self_firing"] or not gate_wipes_memory for h in holders)
def exits(won, holders, rules=None, grudges=None, gate_wipes_memory=True):
    rules = rules or {"death": True, "hell": True, "heaven": False}        # heaven: "no place for you here"
    grudges = grudges or {"death": True, "hell": True, "heaven": False}
    edges = {"earth": ["death", "hell_gate"], "hell_gate": ["hell", "heaven_gate"], "heaven_gate": ["heaven"]}
    def open_edge(a, b):
        if b in TERMINALS and b != "heaven":
            return admits(b, won, rules, grudges)
        if b == "heaven":
            return admits("heaven", won, rules, grudges) or key_fires(holders, gate_wipes_memory)
        return True
    seen, q = {"earth"}, deque(["earth"])
    while q:
        a = q.popleft()
        for b in edges.get(a, []):
            if b not in seen and open_edge(a, b):
                seen.add(b); q.append(b)
    return sorted(t for t in TERMINALS if t in seen)
forgetful = {"self_firing": False}
self_fire = {"self_firing": True}
canon_won = {"hell", "death"}                       # beat the devils at cards and in the sack; trapped Death in the sack
s1 = exits(canon_won, [forgetful])
s2 = exits(canon_won, [forgetful] * 250)          # hand a sack to every one of the 250 souls
s3 = exits(canon_won, [self_fire])
s4 = exits({"hell"}, [forgetful])                   # never traps Death
s5 = [len(exits(w, [])) for w in (set(), {"hell"}, {"hell", "death"})]
s6 = exits(canon_won, [forgetful], gate_wipes_memory=False)   # a heaven that keeps memory
s7 = exits(set(), [forgetful])                      # control: wins no contest (loses or never plays), grudges on
b1 = exits(canon_won, [forgetful], grudges={"death": False, "hell": False, "heaven": False})
print(f"1) canon: beat devils and Death, heaven refuses, one forgetful holder -> exits {s1} ({'wanders' if not s1 else 'rests'})")
print(f"2) sack copies handed to all 250 souls, all forgetful -> exits {s2}")
print(f"3) one holder whose key fires on entry without memory -> exits {s3}")
print(f"4) soldier never traps Death, only beats the devils -> exits {s4}")
print(f"5) exits left after winning 0 / 1 / 2 contests (heaven refusing, no key): {s5}")
print(f"6) same canon, but the gate does not wipe memory -> exits {s6}")
print(f"7) control: soldier wins no contest, grudges on, one forgetful holder -> exits {s7}")
print(f"BREAK) beaten gatekeepers hold no grudge -> exits {b1} despite winning every contest")
ok = (s1 == [] and s2 == [] and s3 == ["heaven"] and s4 == ["death"] and s5 == [2, 1, 0]
      and s6 == ["heaven"] and s7 == ["death", "hell"] and b1 == ["death", "hell"])
print(("RESULT: PASS " if ok else "RESULT: FAIL ") + f"each contest won against a grudge-holding gatekeeper closes that exit "
      f"(exits {s5} after 0/1/2 wins; winning none leaves {s7}); with heaven refusing, the soldier's last exit is the handed-off key, and it fires for "
      f"neither 1 nor 250 holders who forget at the gate ({s1}, {s2}) but does for one self-firing key or a gate that keeps "
      f"memory ({s3}, {s6}); BREAK: gatekeepers without grudges leave {b1} open, so the no-exit ending needs grudges")
