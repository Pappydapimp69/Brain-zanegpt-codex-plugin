"""Sandbox L2: causal ledger + relay-token payoff on a real story song ("Did You Eat?").

Kernels: ideas:SONGWRITING/outline-tooling/causal-ledger-checker-for-story-songs (typed payoffs plus
reachability to the last beat) and ideas:SONGWRITING/narrative/relay-token-payoff (every payoff plants
the next setup). Ledger hand-annotated from the lyric sheet: each token is SET in one beat and PAID in
later beats. A token reaches the ending if it is paid in the final chorus/outro, or paid in a beat that
sets a token which itself reaches the ending (relay). Deterministic, stdlib only.

PREDICTION (set from a hand trace of the ledger before the code ran; the code checks the trace):
  P1 reach: 11 of 18 setups reach the ending (61%), below the 80% a tight story song should hit
  P2 relay: at least 60% of beats that pay something also set a token that is later paid
  P3 break: deleting the bridge beat (Suno sometimes skips or garbles a bridge) drops reach below 30%
  P4 the dangling setups are exactly coat, bus, clock, heart, sunday, truth, rent
"""
BEATS = ["intro", "v1", "pre1", "ch1", "v2", "pre2", "ch2", "bridge", "final", "outro"]
END = {"final", "outro"}
SET = {  # token: beat where it is planted
    "ritual": "intro", "phone": "v1", "time615": "v1", "bubble": "v1", "coat": "v1", "bus": "v1",
    "fine": "v1", "age": "v1", "nightline": "pre1", "clock": "ch1", "twowords": "ch1", "rent": "v2",
    "typeslow": "v2", "soup": "pre2", "heart": "pre2", "truth": "ch2", "sunday": "bridge", "slower": "bridge",
}
PAID = {  # token: beats that pay it off
    "ritual": ["pre1", "ch1", "ch2", "final", "outro"], "phone": ["v2", "bridge"], "time615": ["final"],
    "bubble": ["bridge"], "fine": ["v2", "ch2"], "age": ["v2"], "nightline": ["ch1"], "twowords": ["ch2", "final"],
    "rent": ["ch2"], "typeslow": ["bridge"], "soup": ["bridge"], "slower": ["final"],
}


def reach(removed=()):
    beats = [b for b in BEATS if b not in removed]
    tokens = [t for t, b in SET.items() if b in beats]
    paid = {t: [b for b in PAID.get(t, []) if b in beats] for t in tokens}
    sets_in = {b: [t for t in tokens if SET[t] == b] for b in beats}
    memo = {}

    def ok(t, seen=()):
        if t in memo:
            return memo[t]
        if t in seen:
            return False
        r = False
        for b in paid[t]:
            if b in END or any(ok(u, seen + (t,)) for u in sets_in[b] if u != t):
                r = True
                break
        memo[t] = r
        return r

    good = [t for t in tokens if ok(t)]
    return tokens, good


tokens, good = reach()
dangling = sorted(set(tokens) - set(good))
paying_beats = sorted({b for t in PAID for b in PAID[t]})
relay = [b for b in paying_beats if any(SET[t] == b and PAID.get(t) for t in SET)]
t2, g2 = reach(removed=("bridge",))
r1, r3 = len(good) / len(tokens), len(g2) / len(t2)
res = [
    ("P1 reach 11/18", len(good) == 11 and len(tokens) == 18, f"{len(good)}/{len(tokens)} = {r1:.2f}"),
    ("P2 relay >= 60%", len(relay) / len(paying_beats) >= 0.60, f"{len(relay)}/{len(paying_beats)} paying beats also plant a paid token"),
    ("P3 break: no bridge < 30%", r3 < 0.30, f"{len(g2)}/{len(t2)} = {r3:.2f}"),
    ("P4 dangling set", dangling == sorted(["coat", "bus", "clock", "heart", "sunday", "truth", "rent"]), ", ".join(dangling)),
]
for n, okk, d in res:
    print(f"{n}: {'PASS' if okk else 'FAIL'}  {d}")
k = sum(okk for _, okk, _ in res)
lost = sorted(set(good) - set(g2) - {"sunday", "slower"})
print(("RESULT: PASS " if k == 4 else "RESULT: FAIL ") +
      f"{k}/4; reach {len(good)}/{len(tokens)} ({r1:.0%}); relay {len(relay)}/{len(paying_beats)}; "
      f"without bridge {len(g2)}/{len(t2)} ({r3:.0%}), lost {', '.join(lost)}; dangling {', '.join(dangling)}")
