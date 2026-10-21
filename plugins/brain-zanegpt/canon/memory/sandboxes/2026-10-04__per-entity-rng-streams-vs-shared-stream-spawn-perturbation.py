"""Prediction (before run): with one shared LCG stream, spawning an extra unrelated entity before a fight changes that fight's
damage roll in most of 8 seeds (>=5/8); giving each entity its own stream derived from (seed, entity id) changes it in 0/8.
Built to break: per-entity streams must still break if two entities get the SAME derived id (collision), changing the fight roll
in at least 1 of 8 seeds when the colliding entity is drawn from first. Deterministic, stdlib only."""
M = 2**31 - 1
def lcg(s): return (s * 48271) % M
def mix(seed, eid): return lcg(lcg(seed * 1000003 + eid * 7919 + 1) or 1)

def shared(seed, spawn_extra):
    s = lcg(seed or 1)
    if spawn_extra:
        s = lcg(s)               # unrelated entity consumes one draw at spawn
    s = lcg(s)                   # the fight's damage roll
    return s % 20

def per_entity(seed, spawn_extra, extra_id=99, fight_id=7):
    if spawn_extra:
        e = mix(seed, extra_id); e = lcg(e)   # extra entity draws from its own stream
    f = mix(seed, fight_id)
    f = lcg(f)
    return f % 20

def _collide(seed, spawn_extra):
    st = {7: mix(seed, 7)}                      # both entities map to id 7 -> one shared state
    if spawn_extra:
        st[7] = lcg(st[7])
    st[7] = lcg(st[7])
    return st[7] % 20

seeds = range(1, 9)
a = sum(shared(s, False) != shared(s, True) for s in seeds)
b = sum(per_entity(s, False) != per_entity(s, True) for s in seeds)
c = sum(_collide(s, False) != _collide(s, True) for s in seeds)
print(f"shared_changed={a}/8 per_entity_changed={b}/8 collision_changed={c}/8")
ok = a >= 5 and b == 0 and c >= 1
print("RESULT:", "PASS" if ok else "FAIL", f"shared_changed={a}/8 per_entity_changed={b}/8 collision_changed={c}/8")
