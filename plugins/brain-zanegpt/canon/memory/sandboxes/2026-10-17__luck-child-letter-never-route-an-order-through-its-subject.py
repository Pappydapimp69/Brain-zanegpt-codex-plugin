"""The Luck Child: a death order carried by the person it condemns.

Deterministic, stdlib only, no randomness. An issuer sends an order that harms
its subject to an executor. The letter passes 3 stops; every route over a
world's stop types is enumerated (4 types -> 64 routes, 3 types -> 27).

Stop types:
  empty / inn  nobody opens the letter
  kind_den     robbers who read travellers' letters and rewrite an order that
               harms someone standing in front of them (only if the subject
               is the carrier); cannot forge a seal
  forger_den   the same, and can forge the issuer's hand and seal
  ally_den     knows the subject by name and rewrites a harmful order about
               him whoever carries it; cannot forge

Carriers: the subject who can read (rewrites it himself first), the subject
who cannot read (the boy in the tale), or a neutral courier.
Seal: none, or tamper-evident (a rewrite by a non-forger is detected).
Tamperers: rational (only rewrite when they can beat the seal) or naive.
Outcome per route: silent (rewritten order executed), detected, or intact.

PREDICTION (written before the first run; also in sbx2_J/predictions.txt):
  base world: subject literate no seal 64/64 silent; subject illiterate no seal
  56/64; neutral no seal 0/64; either subject with seal (rational) 37/64,
  detected 0; neutral with seal 0/64; subject illiterate, seal, naive: silent
  28, detected 28, intact 8. No-forger world (27): subject illiterate 19/27,
  with seal 0/27, neutral 0/27. BREAK ally world: neutral no seal 37/64,
  neutral with seal 0/64, subject illiterate no seal 56/64. Empty-route world
  (8): subject illiterate 0/8, subject literate 8/8.
  ADDED BEFORE RUN 2 (run 1 matched every prediction): BREAK forger-ally world
  (an ally by name who can also forge): neutral courier with seal 37/64.
  ADDED BEFORE RUN 3 (after the first ZaneGPT check): in that world the
  subject with a seal also gets 37/64, equal to the neutral courier.
"""
from itertools import product

FORGERS = {"forger_den", "forger_ally"}
READERS = {"kind_den", "forger_den", "ally_den", "forger_ally"}
ALLIES = {"ally_den", "forger_ally"}


def deliver(route, carrier, seal, rational=True):
    subject_present = carrier in ("subject_lit", "subject_illit")
    state, broken = "harm", False

    def tamper(can_forge):
        nonlocal state, broken
        if not seal or can_forge:
            state = "rewritten"
        elif not rational:
            state, broken = "rewritten", True

    if carrier == "subject_lit":
        tamper(can_forge=False)
    for stop in route:
        if state != "harm" or stop not in READERS:
            continue
        motive = subject_present or stop in ALLIES
        if motive:
            tamper(can_forge=stop in FORGERS)
    if state == "rewritten":
        return "detected" if broken else "silent"
    return "intact"


def tally(types, carrier, seal, rational=True):
    out = {"silent": 0, "detected": 0, "intact": 0}
    routes = list(product(types, repeat=3))
    for r in routes:
        out[deliver(r, carrier, seal, rational)] += 1
    return out, len(routes)


checks = []


def check(label, got, want):
    ok = got == want
    checks.append(ok)
    print(f"{'ok ' if ok else 'BAD'} {label}: {got} (predicted {want})")
    return got


BASE = ["empty", "inn", "kind_den", "forger_den"]
NOFORGER = ["empty", "inn", "kind_den"]
ALLY = ["empty", "inn", "kind_den", "ally_den"]
EMPTY = ["empty", "inn"]
FALLY = ["empty", "inn", "kind_den", "forger_ally"]


def silent(types, carrier, seal, rational=True):
    return tally(types, carrier, seal, rational)[0]["silent"]


print("== 1) base world: who carries it, and is it sealed")
a = check("subject literate, no seal", silent(BASE, "subject_lit", False), 64)
b = check("subject illiterate, no seal", silent(BASE, "subject_illit", False), 56)
c = check("neutral courier, no seal", silent(BASE, "neutral", False), 0)
d = check("subject literate, seal", silent(BASE, "subject_lit", True), 37)
e = check("subject illiterate, seal", silent(BASE, "subject_illit", True), 37)
check("detected, subject illiterate, seal, rational", tally(BASE, "subject_illit", True)[0]["detected"], 0)
check("neutral courier, seal", silent(BASE, "neutral", True), 0)

print("== 2) naive tamperers: the seal turns tampering into detection")
n = check("subject illiterate, seal, naive", tally(BASE, "subject_illit", True, rational=False)[0],
          {"silent": 28, "detected": 28, "intact": 8})

print("== 3) no forger on any route (27 routes)")
check("subject illiterate, no seal", silent(NOFORGER, "subject_illit", False), 19)
check("subject illiterate, seal", silent(NOFORGER, "subject_illit", True), 0)
check("neutral courier, no seal", silent(NOFORGER, "neutral", False), 0)

print("== 4) BREAK: an ally who knows the subject by name sits on some routes")
f = check("neutral courier, no seal", silent(ALLY, "neutral", False), 37)
check("neutral courier, seal", silent(ALLY, "neutral", True), 0)
check("subject illiterate, no seal", silent(ALLY, "subject_illit", False), 56)

print("== 5) empty routes: carrying it is harmless unless the subject can read")
g = check("subject illiterate, no seal", silent(EMPTY, "subject_illit", False), 0)
check("subject literate, no seal", silent(EMPTY, "subject_lit", False), 8)

print("== 6) BREAK: one party both knows the name and can forge")
h = check("neutral courier, seal", silent(FALLY, "neutral", True), 37)
hs = check("subject illiterate, seal (carrier choice stops mattering)", silent(FALLY, "subject_illit", True), 37)

if all(checks):
    print(f"RESULT: PASS subject carrier gets {b}/64 silent rewrites unsealed ({a}/64 if he reads), "
          f"neutral courier {c}/64; a seal cuts the subject case only to {e}/64 while forgers exist "
          f"(naive tamperers: 28 silent, 28 detected); BREAK: an ally who knows the name rewrites "
          f"{f}/64 for a neutral courier, which only the seal stops; "
          f"an ally who can also forge beats neutral courier plus seal {h}/64, "
          f"the same as the sealed subject {hs}/64")
else:
    print(f"RESULT: FAIL {checks.count(False)} of {len(checks)} predictions missed")
