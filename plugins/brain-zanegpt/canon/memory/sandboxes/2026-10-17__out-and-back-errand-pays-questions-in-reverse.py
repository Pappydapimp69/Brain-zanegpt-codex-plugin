"""Out-and-back errand from Grimm KHM 29 ("The Devil with the Three Golden Hairs",
the source of Jim Henson's The StoryTeller: "The Luck Child"). Deterministic, stdlib.
Stops on a line: fountain town (1), tree town (2), ferry (3), the far end (4).
Each stop asks a question on the way out; answers are learned at the far end.
Measures: open questions per beat (withheld outcomes = tension), closure order,
share of rewards in the final third of beats, and whether a teller is trapped
by an answer that turns a service against the one who still needs it."""
STOPS = [("fountain", 1, 2), ("tree", 2, 2), ("ferry", 3, 0)]   # name, position, reward (asses of gold)
FAR = 4

def run(route, answers_at, ferry_answer_before_crossing=False, stops=None):
    """route: list of positions visited in order. answers_at: 'far' (learned at FAR)
    or 'arrival' (known on first arrival). Returns beats, closure order, rewards, trapped."""
    asked, closed, beats, rewards, order, known = set(), set(), [], [], [], False
    trapped = None
    stops = stops or STOPS
    for t, pos in enumerate(route):
        if pos == FAR or answers_at == "arrival":
            known = True
        for name, p, rew in stops:
            if p != pos:
                continue
            if name not in asked:
                asked.add(name)
                if answers_at == "arrival":          # answered on the spot
                    closed.add(name); order.append(name); rewards.append((t, rew))
            elif known and name not in closed:
                if name == "ferry" and ferry_answer_before_crossing:
                    trapped = "boy"                   # next to ask for the crossing takes the oar: him
                closed.add(name); order.append(name); rewards.append((t, rew))
        beats.append(len(asked - closed))
    return beats, order, rewards, trapped

out_back = [0, 1, 2, 3, 4, 3, 2, 1, 0]
one_way = [0, 1, 2, 3, 4]
S = {}
S["1 out-and-back (the tale)"] = run(out_back, "far")
S["2 same content, answers on arrival"] = run(out_back, "arrival")
S["3 one-way route"] = run(one_way, "far")
S["4 BREAK: ferry answered before crossing"] = run(out_back, "far", ferry_answer_before_crossing=True)
# 5) control: pay in FORWARD order on the way home (a loop route that passes the stops again in the
#    same order), same content -- does the reverse order itself add tension?
S["5 control: paid in forward order (loop)"] = run([0, 1, 2, 3, 4, 1, 2, 3, 0], "far")
# 6) the trap-prone service is the FIRST stop out: reverse order answers it last; hold-until-past
#    still means answer after crossing -- do the two clauses conflict?
ferry_first = [("ferry", 1, 0), ("tree", 2, 2), ("fountain", 3, 2)]
S["6 ferry first, answered after crossing"] = run(out_back, "far", stops=ferry_first)
S["7 ferry first, answered before crossing"] = run(out_back, "far", True, stops=ferry_first)
for k, (b, o, r, tr) in S.items():
    n = len(b); last = [x for x in r if x[0] >= n * 2 / 3]
    share = sum(x[1] for x in last) / max(1, sum(x[1] for x in r))
    print(f"{k:42s} open/beat={b} tension={sum(b)} close={o} reward_in_final_third={share:.2f} trapped={tr}")
# the oar's next taker: whoever next asks to cross after the boy is safe; the boy's story of gold
# on the far bank sends the greediest listener to the ferry first
listeners = {"queen": 0.2, "miller": 0.4, "king": 0.95}
lure = 0.9
goes = sorted([n for n, gr in listeners.items() if gr >= lure], key=lambda n: -listeners[n])
oar = goes[0] if goes else None
b1, o1, r1, _ = S["1 out-and-back (the tale)"]; b2 = S["2 same content, answers on arrival"][0]
b3 = S["3 one-way route"][0]; tr4 = S["4 BREAK: ferry answered before crossing"][3]
b5, o5 = S["5 control: paid in forward order (loop)"][:2]
tr6, tr7 = S["6 ferry first, answered after crossing"][3], S["7 ferry first, answered before crossing"][3]
print(f"forward-order control tension {sum(b5)} vs reverse {sum(b1)}; ferry-first trapped: after={tr6} before={tr7}")
ok = (sum(b5) == sum(b1) and tr6 is None and tr7 == "boy" and o1 == ["ferry", "tree", "fountain"] and max(b1) == 3 and b1.index(3) == 3 and sum(b2) == 0
      and b3[-1] == 3 and tr4 == "boy" and S["1 out-and-back (the tale)"][3] is None and oar == "king")
print(f"next to take the oar: {oar}")
print(("RESULT: PASS " if ok else "RESULT: FAIL ") +
      f"the return leg makes the tension (12 vs {sum(b2)} answered on arrival, {b3[-1]} left open one-way); the ORDER does not "
      f"(forward-order payment also scores {sum(b5)}): reverse is just what a straight road forces; the trap answer is safe only after "
      f"the crossing wherever the ferry sits (ferry-first: before traps the boy, after is safe); told after, the lure hands the oar to the {oar}")
