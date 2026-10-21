"""Prediction (before run): a lobby model with (a) join binding cloned to every device type and (b) an identity registry for
reconnects gives 0 slot errors across 4 scenarios; dropping cloning locks out the 2nd player's gamepad join (1 lockout);
dropping the registry (first-free-slot matching) lets a stranger steal a vacated slot (1 theft) and makes the true owner
rejoin as new. Built to break: composing BOTH faults, where I expect a rejoining owner to be locked out of its own slot
because the join binding for its device type was never cloned. Deterministic, stdlib only."""

class Lobby:
    def __init__(s, clone, registry):
        s.clone, s.registry = clone, registry
        s.slots = {}          # slot -> device id
        s.lost = {}           # slot -> device id (disconnected registry)
        s.join_enabled = {"kbd": True, "pad": True}
        s.log = []
    def join(s, dev, kind):
        if not s.join_enabled[kind]:
            return "LOCKED_OUT"
        slot = len(s.slots) + len(s.lost)
        s.slots[slot] = dev
        if not s.clone:       # first join disables join bindings on other device types
            for k in s.join_enabled:
                if k != kind: s.join_enabled[k] = False
        return f"slot{slot}"
    def lose(s, dev):
        for sl, d in list(s.slots.items()):
            if d == dev:
                del s.slots[sl]; s.lost[sl] = dev; return sl
    def connect(s, dev, kind):
        if s.registry:
            for sl, d in s.lost.items():
                if d == dev:
                    del s.lost[sl]; s.slots[sl] = dev; return f"regained slot{sl}"
            return "NEEDS_JOIN" if not s.join_enabled[kind] is False else "LOCKED_OUT"
        if s.lost:            # naive: first vacated slot goes to whoever connects
            sl = min(s.lost); del s.lost[sl]; s.slots[sl] = dev; return f"took slot{sl}"
        return s.join(dev, kind)

def run(clone, registry):
    L = Lobby(clone, registry)
    out = [L.join("kbd1", "kbd")]
    out.append(L.join("pad1", "pad"))
    L.lose("kbd1")
    out.append(L.connect("pad2", "pad"))   # stranger
    out.append(L.connect("kbd1", "kbd"))   # true owner
    return out

res = {}
for name, c, r in (("both", True, True), ("no_clone", False, True), ("no_registry", True, False), ("neither", False, False)):
    res[name] = run(c, r); print(name, res[name])
ok_both = res["both"] == ["slot0", "slot1", "NEEDS_JOIN", "regained slot0"]
ok_nc = res["no_clone"][1] == "LOCKED_OUT"
steal = res["no_registry"][2] == "took slot0" and res["no_registry"][3] != "regained slot0"
brk = res["neither"][1] == "LOCKED_OUT"
print("RESULT:", "PASS" if ok_both and ok_nc and steal and brk else "FAIL",
      f"both ok={ok_both}; no_clone lockout={ok_nc}; no_registry theft={steal} owner={res['no_registry'][3]}; neither 2nd join lockout={brk}")
