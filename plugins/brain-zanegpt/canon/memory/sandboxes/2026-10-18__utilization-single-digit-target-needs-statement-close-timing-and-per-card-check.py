# Sandbox: kernel PERSONAL-FINANCE/credit/utilization-ratio (30% = warning line, single digits = target,
# reported figure = statement balance) composed with two memory entries.
# Model: 2 cards, limits 5000 + 1000. Daily spend deterministic. Statement closes day 30, due day 55.
LIM = {"A": 5000, "B": 1000}
def reported(spend_per_day, pay_day, pay_amt, card):
    bal = 0
    for d in range(1, 31):               # cycle days 1..30, statement closes end of day 30
        bal += spend_per_day[card]
        if d == pay_day: bal = max(0, bal - pay_amt)
    return bal                            # balance reported to bureau at close
def util(spend, pay_day, pay):
    rep = {c: reported(spend, pay_day if c in pay else 0, pay.get(c, 0), c) for c in LIM}
    agg = sum(rep.values()) / sum(LIM.values())
    per = {c: rep[c] / LIM[c] for c in LIM}
    return agg, per
spend = {"A": 50, "B": 30}               # 1500 + 900 per cycle
# Scenario 1: no payment before close -> agg
a1, p1 = util(spend, 0, {})
# Scenario 2: pay everything on due date (day 55, after close) == same as 1 by construction
a2, p2 = util(spend, 0, {})
# Scenario 3: pay 1000 on A and 800 on B at day 29 (pre-close)
a3, p3 = util(spend, 29, {"A": 1000, "B": 800})
# Scenario 4: BREAK: aggregate under 30% while one card is far above it
a4, p4 = util({"A": 10, "B": 30}, 0, {})  # A 300/5000=6%, B 900/1000=90% ; agg=1200/6000=20%
# Scenario 5: same aggregate as 4 spread evenly (20% each)
a5, p5 = util({"A": 20, "B": 4}, 0, {})  # A 600/5000=12%? compute below
print("S1 no pay:", round(a1,3), {k: round(v,2) for k,v in p1.items()})
print("S2 pay after close:", round(a2,3))
print("S3 pre-close pay:", round(a3,3), {k: round(v,2) for k,v in p3.items()})
print("S4 skewed:", round(a4,3), {k: round(v,2) for k,v in p4.items()})
print("S5 other:", round(a5,3), {k: round(v,2) for k,v in p5.items()})
# Iteration 2: first run paid 1000/800 -> exactly 10.0% (NOT single digit). Scan payment size for the single-digit cutoff.
need = None
for extra in range(0, 1001, 50):
    ag, _ = util(spend, 29, {"A": 1000 + extra, "B": 800 + extra // 5})
    if ag < 0.10:
        need = (extra, round(ag, 3)); break
print("S6 min extra payment for <10%:", need)
ok = (a1 == a2 == 0.4 and a3 == 0.1 and need is not None and a4 < 0.30 and max(p4.values()) >= 0.9)
print("RESULT: %s statement-close timing: %.0f%% unpaid vs %.1f%% pre-close (boundary, not single digit; needs +%s); skewed cards agg %.0f%% but worst card %.0f%%"
      % ("PASS" if ok else "FAIL", a1*100, a3*100, need[0] if need else "?", a4*100, max(p4.values())*100))
