# Sandbox: how is abandonment-by-walking-forward made FELT with no prompt?
# Exact enumeration (no RNG). States at the moment the lead takes camp down:
#   behind = someone missing in THIS area (the move abandons them)
#   ahead  = someone missing in the NEXT area (the move does not)
#   none   = nobody missing
# Evidence the player can have at that moment:
#   A) the dawn call this morning (real p_n, floored; false 0.3, any bearing)
#   B) a call as camp comes down: real whenever the move would abandon someone,
#      false at rate fk otherwise (so a call alone never says posterior 1.0)
# "Felt" = informed (P heard | behind) high AND posterior P(behind | heard)
# high but < 0.99 (1.0 would be an announcement, i.e. a prompt in disguise).

def p_call(n):           # the game's dawn call: fades 0.15/night, floor 0.5
    return max(0.5, 1 - 0.15 * (n - 1))

NIGHTS = [1, 2, 3, 4]
FD = 0.3                 # dawn false-call rate (game value)

def evaluate(q, a, fk, r=1.0):
    none = 1 - q - a
    pd = sum(p_call(n) for n in NIGHTS) / len(NIGHTS)
    # A: dawn only
    heard_A = {"behind": pd, "ahead": pd, "none": FD}
    # B: dismantle call only
    heard_B = {"behind": r, "ahead": fk, "none": fk}
    # C: the camp-down call comes from the SAME bearing as this morning's call.
    # A real voice holds its bearing; two false calls agree 1 time in 8.
    heard_C = {"behind": pd * r, "ahead": pd * fk / 8, "none": FD * fk / 8}
    prior = {"behind": q, "ahead": a, "none": none}
    out = {}
    for name, h in (("A", heard_A), ("B", heard_B), ("C", heard_C)):
        num = prior["behind"] * h["behind"]
        den = sum(prior[s] * h[s] for s in prior)
        out[name] = {"informed": h["behind"], "posterior": num / den if den else 0.0,
                     "false_alarm": (prior["ahead"] * h["ahead"] + prior["none"] * h["none"]) / (1 - q)}
    return out

scen = [
    ("1) prior 0.2, ahead 0.15, fk 0.3", 0.2, 0.15, 0.3),
    ("2) prior 0.4, ahead 0.15, fk 0.3", 0.4, 0.15, 0.3),
    ("3) prior 0.2, ahead 0.30, fk 0.3", 0.2, 0.30, 0.3),
    ("4) BREAK: fk 0 (a call only when real)", 0.2, 0.15, 0.0),
    ("5) BREAK: fk 1 (a call every time)", 0.2, 0.15, 1.0),
]
ok = True
for label, q, a, fk in scen:
    o = evaluate(q, a, fk)
    print(f"{label}: A informed {o['A']['informed']:.3f} post {o['A']['posterior']:.3f} | "
          f"B informed {o['B']['informed']:.3f} post {o['B']['posterior']:.3f} | "
          f"C informed {o['C']['informed']:.3f} post {o['C']['posterior']:.3f} falseAlarm {o['C']['false_alarm']:.4f}")
    if label.startswith(("1", "2", "3")):
        ok &= o["C"]["informed"] >= 0.75 and 0.9 < o["C"]["posterior"] < 0.995 and o["B"]["informed"] == 1.0
    elif "fk 0" in label:
        ok &= o["B"]["posterior"] >= 0.999 and o["C"]["posterior"] >= 0.999   # an announcement
    else:
        ok &= abs(o["B"]["posterior"] - q) < 1e-9   # the camp-down call alone says nothing

print(("RESULT: PASS" if ok else "RESULT: FAIL") +
      " camp-down call on the dawn bearing: posterior 0.9-0.995, informed 0.775, in 3/3; alone it is weak (0.46-0.69); fk=0 announces; fk=1 alone says nothing")
