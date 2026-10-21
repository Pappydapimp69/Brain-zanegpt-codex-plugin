"""Apply the Roman 're-encode and compare' canonical rule to abacus rod states.
Soroban rod: heaven 0..1 (x5), earth 0..4. Suanpan rod: heaven 0..2, earth 0..5.
Multi-rod numbers: place values 10^k, per-rod value 5h+e. Stdlib only, deterministic."""
from itertools import product

def rod_states(hmax, emax):
    return [(h, e) for h in range(hmax + 1) for e in range(emax + 1)]

def value(state):                      # state = tuple of (h, e) per rod, most significant first
    v = 0
    for h, e in state:
        v = v * 10 + 5 * h + e
    return v

def encode(v, rods):                   # greedy canonical: standard decimal digits, 5 -> heaven bead
    if v >= 10 ** rods:
        return None
    out = []
    for _ in range(rods):
        out.append(divmod(v % 10, 5))
        v //= 10
    return tuple(reversed(out))

def canonical(state):
    return encode(value(state), len(state)) == state

results = {}
for name, (hm, em) in {"soroban 1+4": (1, 4), "suanpan 2+5": (2, 5)}.items():
    for rods in (1, 2, 3):
        states = list(product(rod_states(hm, em), repeat=rods))
        vals = {}
        for s in states:
            vals.setdefault(value(s), []).append(s)
        canon = sum(canonical(s) for s in states)
        multi = sum(1 for v in vals.values() if len(v) > 1)
        nocanon = sum(1 for v, ss in vals.items() if not any(canonical(s) for s in ss))
        results[(name, rods)] = (len(states), len(vals), canon, multi, nocanon)
        print(f"{name} x{rods} rods: states {len(states)}, values {len(vals)}, canonical states {canon}, values with 2+ spellings {multi}, values with no canonical spelling {nocanon}")

so = [results[("soroban 1+4", r)] for r in (1, 2, 3)]
su = [results[("suanpan 2+5", r)] for r in (1, 2, 3)]
sor_ok = all(s == v == c and m == 0 and n == 0 for s, v, c, m, n in so)
su_ok = su[0][2] == 10 and su[1][4] > 0 and su[2][2] == 1000
print(f"RESULT: {'PASS' if sor_ok and su_ok else 'FAIL'} soroban states==values==canonical at 1-3 rods; "
      f"suanpan 3 rods: {su[2][0]} states, {su[2][1]} values, only {su[2][2]} canonical, {su[2][3]} values with 2+ spellings, {su[2][4]} values with no canonical spelling")
