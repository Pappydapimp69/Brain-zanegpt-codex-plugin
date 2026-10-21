# Deterministic model: MFA factor tiers vs attacker capabilities.
# Factor accepts a login attempt given (attacker capability, user behaviour).
def sms_code(a, o): return a["relay"] or a["has_code"]
def totp(a, o): return a["relay"] or a["has_code"]
def push(a, o): return a["relay"] and o["tap"] or a["bomb"] and o["fatigue_taps"]
def push_numbermatch(a, o):
    # number shown on the LOGIN page; user must type it. Bomber has no page in front of user.
    return a["relay"] and o["tap"]  # relay shows the real number to the victim -> still works
def fido(a, o, origin="evil.example", rp="bank.example"):
    return origin == rp  # assertion bound to origin: lookalike gets nothing usable
def session_theft(factor_ok_for_victim, a):
    # after a legit FIDO login, a stolen session cookie bypasses ANY factor
    return a["steal_cookie"]
O = dict(tap=True, fatigue_taps=True)
attackers = {
 "relay(AitM page)": dict(relay=True, bomb=False, has_code=False, steal_cookie=False),
 "push-bomb only":   dict(relay=False, bomb=True, has_code=False, steal_cookie=False),
 "stolen-code replay (no relay)": dict(relay=False, bomb=False, has_code=True, steal_cookie=False),
}
factors = {"sms":sms_code,"totp":totp,"push":push,"push+numbermatch":push_numbermatch,"fido":fido}
res = {}
for an,a in attackers.items():
    for fn,f in factors.items():
        res[(an,fn)] = bool(f(a,O))
        print(f"{an:34s} {fn:18s} breached={res[(an,fn)]}")
# stacking same-class controls (sms AND push) vs relay: both relayable
stack = all(res[("relay(AitM page)",x)] for x in ("sms","push"))
print("stack sms+push breached by relay:", stack)
# BREAK attempt: FIDO + cookie theft
ck = dict(relay=False,bomb=False,has_code=False,steal_cookie=True)
print("fido but cookie theft breached:", session_theft(True, ck))
ok = (res[("relay(AitM page)","fido")] is False
      and res[("relay(AitM page)","sms")] and res[("relay(AitM page)","push+numbermatch")]
      and res[("push-bomb only","push")] and not res[("push-bomb only","push+numbermatch")]
      and stack and session_theft(True, ck))
print("RESULT: %s fido blocks relay (0/3 attackers), sms/totp/push fall to relay, numbermatch stops bomb only, stacking same-class stays breached, cookie theft bypasses fido" % ("PASS" if ok else "FAIL"))
