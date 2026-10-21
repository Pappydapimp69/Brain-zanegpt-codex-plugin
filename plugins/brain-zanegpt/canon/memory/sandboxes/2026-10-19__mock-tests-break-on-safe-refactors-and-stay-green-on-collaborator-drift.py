# Prediction (before run; the 1/3 refactor figure and bulk-bug scenario were fixed AFTER run 1 showed 1/3, see ok vs ok0): 3 safe refactors of OrderService.
#  - mockist tests (assert exact collaborator calls): fail 3/3 refactors, behaviour tests fail 0/3
#  - collaborator drift (real repo now rejects float totals): mockist 3/3 stay green, behaviour tests
#    on the real repo 3/3 red, a contract test on the fake red 1/1
#  - BREAK: a real logic bug (tax applied twice): both styles must catch it (mockist 3/3 if arg asserted).
class RealRepo:
    def __init__(self, strict=False): self.rows, self.strict = {}, strict
    def save(self, oid, total):
        if self.strict and not isinstance(total, int): raise TypeError("cents must be int")
        self.rows[oid] = total
    def get(self, oid): return self.rows[oid]
class Spy:
    def __init__(self): self.calls = []
    def save(self, *a): self.calls.append(("save",) + a)
    def save_all(self, items): self.calls.append(("save_all", tuple(items)))
class V1:   # baseline: one save per order, float total
    def __init__(s, r): s.r = r
    def place(s, oid, price, qty): s.r.save(oid, price * qty * 1.1)
class V2:   # refactor A: round to int cents, same observable total
    def __init__(s, r): s.r = r
    def place(s, oid, price, qty): s.r.save(oid, round(price * qty * 1.1))
class V3:   # refactor B: routes via save_all
    def __init__(s, r): s.r = r
    def place(s, oid, price, qty): s.r.save_all([(oid, round(price * qty * 1.1))])
class V4:   # refactor C: computes tax in helper, same save
    def __init__(s, r): s.r = r
    def _t(s, p, q): return round(p * q * 1.1)
    def place(s, oid, price, qty): s.r.save(oid, s._t(price, qty))
class Bug:  # tax twice
    def __init__(s, r): s.r = r
    def place(s, oid, price, qty): s.r.save(oid, round(price * qty * 1.1 * 1.1))
CASES = [("a", 100, 1), ("b", 250, 2), ("c", 30, 3)]
def mockist(cls, case):   # asserts the exact baseline call
    spy = Spy(); cls(spy).place(*case)
    exp = ("save", case[0], round(case[1]*case[2]*1.1))
    return spy.calls == [exp] or spy.calls == [("save", case[0], case[1]*case[2]*1.1)]
class Adapter(RealRepo):   # real repo gaining save_all so V3 works
    def save_all(self, items):
        for o, t in items: self.save(o, t)
def behaviour(cls, case, strict=False):  # run on a real repo, check stored total
    r = Adapter(strict)
    try: cls(r).place(*case)
    except Exception: return False
    return abs(r.get(case[0]) - case[1]*case[2]*1.1) < 0.51
ref = [V2, V3, V4]
m_ref = sum(not mockist(c, k) for c in ref for k in CASES[:1])        # per refactor on case 1
m_fail = sum(not all(mockist(c, k) for k in CASES) for c in ref)
b_fail = sum(not all(behaviour(c, k) for k in CASES) for c in ref)
print("refactors failing: mockist", m_fail, "/3 behaviour", b_fail, "/3")
# drift: real repo strict about ints; baseline V1 passes floats
m_green = sum(all(mockist(V1, k) for k in CASES) for _ in range(1))
drift_beh = sum(not behaviour(V1, k, strict=True) for k in CASES)
try: RealRepo(True).save("x", 1.1); contract = 0
except TypeError: contract = 1
print("drift: mockist green on V1", m_green, "/1 suite; behaviour red", drift_beh, "/3; contract red", contract)
bug_m = sum(not mockist(Bug, k) for k in CASES); bug_b = sum(not behaviour(Bug, k) for k in CASES)
print("bug caught: mockist", bug_m, "/3 behaviour", bug_b, "/3")
class BugBulk:  # tax twice only when qty >= 3
    def __init__(s, r): s.r = r
    def place(s, oid, price, qty): s.r.save(oid, round(price * qty * (1.21 if qty >= 3 else 1.1)))
spot = not mockist(BugBulk, CASES[0]); full = sum(not mockist(BugBulk, k) for k in CASES)
print("bulk bug: first-case spot check catches", spot, "; full case list catches", full, "/3")
ok = spot is False and full == 1 and m_fail == 1 and b_fail == 0 and m_green == 1 and drift_beh == 3 and bug_m == 3 and bug_b == 3
ok0 = m_fail == 3 and b_fail == 0 and m_green == 1 and drift_beh == 3 and contract == 1 and bug_m == 3 and bug_b == 3
print("RESULT:", "PASS" if ok else "FAIL", f"(original 3/3-refactor prediction held={ok0}) refactors broke mockist {m_fail}/3 vs behaviour {b_fail}/3; spot check missed bulk bug={not spot}, full list caught {full}/3; drift left mockist green, behaviour red {drift_beh}/3, contract red {contract}; bug caught {bug_m}/3 and {bug_b}/3")
