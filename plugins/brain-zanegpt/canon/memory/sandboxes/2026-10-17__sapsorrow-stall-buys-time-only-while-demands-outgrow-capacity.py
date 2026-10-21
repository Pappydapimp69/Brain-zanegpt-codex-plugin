"""Sandbox: The StoryTeller, "Sapsorrow" (1988) -- stalling with escalating impossible demands.

Episode (Wikipedia, The Storyteller TV series): the ring law says Sapsorrow must marry the king;
she stalls by asking for three gowns, "as pale as the moon", "as sparkling as the stars",
"as golden as the sun"; her father provides all three and she has to flee on the wedding night.
Grimms' Allerleirauh (sun, moon, stars, a mantle of every fur) and Perrault's Donkeyskin
(time, moon, sun, then the gold-making donkey's hide) run the same stall and the king meets
every demand each time.

Claim under test: escalating demands buy time only while each demand grows faster than the
other side's capacity to meet it grows (demand growth d > capacity growth g). When d <= g,
each further demand buys less time than the one before, the total time is capped at
t0 / (1 - d/g) however many demands are made, and the demands only raise the price he pays.
A demand above his absolute ceiling ends the stall in a refusal instead.

Model (deterministic, stdlib): demand k costs c0 * d^k units; the king mobilises more makers as
he goes, so his rate on demand k is r0 * g^k units/day; demand k takes (c0/r0) * (d/g)^k days.
c0 = 10 units, r0 = 1 unit/day, so t0 = 10 days. Her escape needs T = 40 days to be ready.
The stall "works" if the time bought reaches T before the demands run out.

PREDICTION (written before the first run):
  S1 tale-like, d=2, g=2, 3 gowns: 10+10+10 = 30 days < 40 -> stall falls short; price 70.
  S2 demands outrun, d=3, g=1.5, 3 gowns: 10+20+40 = 70 days >= 40 -> works; price 130.
  S3 capacity outruns, d=1.5, g=3, 3 gowns: 10+5+2.5 = 17.5 days -> short; price 47.5.
  S3b same, 10 demands: about 19.98 days (cap 20), price about 1133 -> only the price rose.
  S4 ceiling 60 units, d=3, g=1.5: third demand (90) refused after 30 days -> stall ends in refusal.
  S5 BREAK same three demands as S2 in DESCENDING order (90, 30, 10) against g=1.5:
     90 + 20 + 4.44 = 114.4 days > 70 ascending -> escalation is not what buys the time.
  S6 static king g=1, d=3: ascending and descending both 130 days (order irrelevant).
Added after the first run, prediction written before rerun:
  S7 descending 90,30,10 against the ceiling of 60: refused at demand 1 after 0 days, while
     ascending (S4) banked 30 days first -> ascending order pays only when a ceiling may be near.
Added after the ZaneGPT check, prediction written before rerun:
  S8 d>g is not enough: d=3, g=1.5, ceiling 25 -> refused at demand 2 after 10 days, short of 40.
  S9 unseen ceiling: averaged over ceilings 5,10,...,120 (24 equally likely), ascending 10,30,90
     averages about 37.1 days, descending 90,30,10 about 33.4 -> escalating wins only when the
     ceiling is unknown, and loses (70 vs 114.4) once he is known to have no ceiling in range.
"""

C0, R0, NEED = 10.0, 1.0, 40.0


def stall(costs, g, ceiling=None):
    """Return (days bought, price paid, refused_at or None)."""
    days = price = 0.0
    for k, c in enumerate(costs):
        if ceiling is not None and c > ceiling:
            return days, price, k + 1
        days += c / (R0 * g ** k)
        price += c
    return days, price, None


def ascending(d, n):
    return [C0 * d ** k for k in range(n)]


def report(name, costs, g, ceiling=None):
    days, price, refused = stall(costs, g, ceiling)
    if refused:
        verdict = f"refused at demand {refused}"
    else:
        verdict = "works" if days >= NEED else "short"
    print(f"{name:<44} days={days:7.2f} price={price:8.1f} -> {verdict}")
    return days, price, refused


results = {}
results["S1"] = report("S1 tale-like d=2 g=2 (3 gowns)", ascending(2, 3), 2)
results["S2"] = report("S2 demands outrun d=3 g=1.5", ascending(3, 3), 1.5)
results["S3"] = report("S3 capacity outruns d=1.5 g=3", ascending(1.5, 3), 3)
results["S3b"] = report("S3b capacity outruns, 10 demands", ascending(1.5, 10), 3)
cap = (C0 / R0) / (1 - 1.5 / 3)
print(f"    S3 cap on time from any number of demands = {cap:.2f} days")
results["S4"] = report("S4 ceiling 60, d=3 g=1.5", ascending(3, 3), 1.5, ceiling=60)
results["S5"] = report("S5 BREAK descending 90,30,10 g=1.5", list(reversed(ascending(3, 3))), 1.5)
results["S7"] = report("S7 descending with ceiling 60, g=1.5", list(reversed(ascending(3, 3))), 1.5, ceiling=60)
results["S8"] = report("S8 d>g but ceiling 25", ascending(3, 3), 1.5, ceiling=25)
ceilings = list(range(5, 121, 5))
avg_up = sum(stall(ascending(3, 3), 1.5, c)[0] for c in ceilings) / len(ceilings)
avg_down = sum(stall(list(reversed(ascending(3, 3))), 1.5, c)[0] for c in ceilings) / len(ceilings)
print(f"S9 unknown ceiling 5..120: ascending avg {avg_up:.2f} days, descending avg {avg_down:.2f} days")
results["S6a"] = report("S6 static king g=1 ascending d=3", ascending(3, 3), 1)
results["S6b"] = report("S6 static king g=1 descending d=3", list(reversed(ascending(3, 3))), 1)

close = lambda a, b: abs(a - b) < 0.05
checks = [
    close(results["S1"][0], 30) and results["S1"][0] < NEED and close(results["S1"][1], 70),
    close(results["S2"][0], 70) and results["S2"][0] >= NEED and close(results["S2"][1], 130),
    close(results["S3"][0], 17.5) and close(results["S3"][1], 47.5),
    close(results["S3b"][0], 19.98) and results["S3b"][0] < cap and abs(results["S3b"][1] - 1133.3) < 1,
    results["S4"][2] == 3 and close(results["S4"][0], 30),
    close(results["S5"][0], 114.44) and results["S5"][0] > results["S2"][0],
    results["S7"][2] == 1 and results["S7"][0] == 0,
    results["S8"][2] == 2 and close(results["S8"][0], 10),
    abs(avg_up - 37.1) < 0.1 and abs(avg_down - 33.4) < 0.1 and avg_up > avg_down,
    close(results["S6a"][0], 130) and close(results["S6b"][0], 130),
]
print("checks:", checks)
if all(checks):
    print("RESULT: PASS d>g buys 70 days, d=g 30 (short of 40), d<g caps at 20 days while price climbs to 1133; "
          "ceiling refuses demand 3; BREAK: descending order buys 114.4 days vs 70, so the time comes from "
          "cost over capacity, not from escalating, unless a ceiling is near (descending is refused at once, 0 days vs 30); d>g under a ceiling of 25 still stops at 10 days; "
          f"over an unknown ceiling escalating averages {avg_up:.1f} days vs {avg_down:.1f} largest-first")
else:
    print("RESULT: FAIL prediction mismatch, see checks")
