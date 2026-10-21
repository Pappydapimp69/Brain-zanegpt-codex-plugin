"""Sandbox (train kernel B, declare SYSTEM/seeded-rng): save the generator's full
state words, not a {seed, count} pair. Composed with seven E1 (a callback that
draws a data-dependent number of times makes a 'counted' roll total wrong) and
the-game-prologue E1 (hash game state with sorted keys or equal states hash
differently).
Deterministic: sfc32 implemented here; no ambient randomness, no timing (cost
is counted in generator steps, not seconds).
"""
import hashlib
import json

M = 0xFFFFFFFF


class Sfc32:
    def __init__(self, a, b, c, d):
        self.s = [a & M, b & M, c & M, d & M]
        self.steps = 0

    def next(self):
        a, b, c, d = self.s
        t = (a + b + d) & M
        d = (d + 1) & M
        a = b ^ (b >> 9)
        b = (c + (c << 3)) & M
        c = ((c << 21) | (c >> 11)) & M
        c = (c + t) & M
        self.s = [a, b, c, d]
        self.steps += 1
        return t

    @classmethod
    def from_seed(cls, seed):
        g = cls(0x9E3779B9, 0x243F6A88, 0xB7E15162, seed)
        for _ in range(12):
            g.next()
        g.steps = 0
        return g


def play(g, turns, counted):
    """Each turn: one visible roll (counted) plus a crit callback that draws
    (turn % 3) extra times -- the hidden draws seven E1 warns about."""
    for t in range(turns):
        g.next()
        counted[0] += 1
        for _ in range(t % 3):
            g.next()           # hidden: not added to the counted total


def stable_hash(state):
    return hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()[:12]


def naive_hash(state):
    return hashlib.sha256(json.dumps(state).encode()).hexdigest()[:12]


def main():
    seed, turns = 1234, 3000
    g = Sfc32.from_seed(seed)
    counted = [0]
    play(g, turns, counted)
    true_steps = g.steps
    expected_next = Sfc32(*g.s).next()

    # save A: full state words
    a = Sfc32(*list(g.s))
    a_next, a_cost = a.next(), 0
    # save B: {seed, count} with the COUNTED total (misses hidden draws)
    b = Sfc32.from_seed(seed)
    for _ in range(counted[0]):
        b.next()
    b_next, b_cost = b.next(), counted[0]
    # save C: {seed, count} with the TRUE total (break case: correct but slow)
    c = Sfc32.from_seed(seed)
    for _ in range(true_steps):
        c.next()
    c_next, c_cost = c.next(), true_steps
    print(f"true draws {true_steps}, counted {counted[0]}")
    print(f"state words : next matches {a_next == expected_next}, restore cost {a_cost} steps")
    print(f"seed+counted: next matches {b_next == expected_next}, restore cost {b_cost} steps")
    print(f"seed+true   : next matches {c_next == expected_next}, restore cost {c_cost} steps")

    s1 = {"turn": turns, "rng": list(g.s), "party": ["a", "b"]}
    s2 = {"party": ["a", "b"], "rng": list(g.s), "turn": turns}   # same state, built in another order
    print(f"golden hash equal states: naive {naive_hash(s1) == naive_hash(s2)}, sorted {stable_hash(s1) == stable_hash(s2)}")
    checks = [
        ("state-words restore matches the next roll with 0 replay steps", a_next == expected_next and a_cost == 0),
        ("seed+count with the counted total (hidden draws missed) diverges", b_next != expected_next),
        ("break case: seed+count with the true total matches, but costs every draw", c_next == expected_next and c_cost == true_steps),
        ("naive JSON hash splits two equal states; a sorted-key hash does not",
         naive_hash(s1) != naive_hash(s2) and stable_hash(s1) == stable_hash(s2)),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; true {true_steps} counted {counted[0]}; "
          f"words cost 0 match; counted diverges; true-count cost {c_cost}; sorted hash stable")


if __name__ == "__main__":
    main()
