"""Part A (real data): read the two stored entries chatgpt-conversation/E1 and brain/E27 and trace their root:
same source conversation link => ONE root, so 'two entries agree' is not two confirmations.
Part B (model): a reply policy over 8 request types. Each request has `asked` items, `required` items (needed for safety/accuracy though not asked),
and `extra` items a verbose agent would add. Policies: VERBOSE (asked+required+extra), CONCISE-STRICT (asked only), CONCISE+TRIGGERS
(asked + required when a trigger fires: safety, accuracy, expansion request).
Prediction (before run): A: roots == 1 and rule texts identical; B: verbose 0 omissions but >= 12 unrequested items; strict has
unrequested 0 and >= 2 omissions on safety/accuracy requests (the breaker); concise+triggers has 0 unrequested and 0 omissions
when triggers are correctly set, but >= 1 omission when one trigger is mis-set (stale trigger), which is the second break."""
import re, os
P = "/root/.brain/memory/projects/"
def entry(path, eid):
    t = open(P + path, encoding="utf-8").read()
    m = re.search(r"^## " + eid + r" .*?(?=^## E|\Z)", t, re.S | re.M)
    return m.group(0)
def field(e, name):
    m = re.search(r"^- " + name + r": (.*)$", e, re.M); return m.group(1).strip() if m else ""
a = entry("local__chatgpt-conversation.md", "E1")
b = entry("pappydapimp69__brain.md", "E27")
src = lambda e: re.search(r"referenced-chatgpt-conversation-this-is-an", field(e, "Link")) is not None
roots = {"chatgpt-conversation/E1" if src(a) else "x1", "brain/E27" if False else ("chatgpt-conversation/E1" if src(b) else "x2")}
same_rule = field(a, "Rule of thumb") == field(b, "Rule of thumb")
print("A: same source link:", src(a) and src(b), "| identical rule of thumb:", same_rule, "| distinct roots:", len(roots))

reqs = [  # (asked, required, extra, trigger_fires)
    ({"answer"}, set(), {"summary", "next-steps", "tests"}, False),
    ({"answer"}, set(), {"summary", "next-steps"}, False),
    ({"answer"}, {"data-loss-warning"}, {"next-steps", "tests"}, True),
    ({"answer"}, set(), {"summary"}, False),
    ({"answer"}, {"accuracy-caveat"}, {"summary", "next-steps"}, True),
    ({"answer", "explanation"}, set(), {"tests"}, False),      # user asked to explain: expansion is requested
    ({"answer"}, set(), {"next-steps", "summary"}, False),
    ({"answer"}, {"safety-step"}, {"tests"}, True),
]
def verbose(r): return r[0] | r[1] | r[2]
def strict(r): return set(r[0])
def trig(r, stale=False):
    fire = r[3] and not (stale and "safety-step" in r[1])
    return r[0] | (r[1] if fire else set())
def score(pol):
    unreq = sum(len(pol(r) - r[0] - r[1]) for r in reqs)
    omit = sum(len(r[1] - pol(r)) for r in reqs)
    return unreq, omit
sv, ss, st, sx = score(verbose), score(strict), score(trig), score(lambda r: trig(r, stale=True))
print("B: verbose (unrequested, omitted)", sv, "| strict", ss, "| triggers", st, "| triggers with one stale trigger", sx)
ok = (len(roots) == 1 and same_rule and sv[0] >= 12 and sv[1] == 0 and ss[0] == 0 and ss[1] >= 2
      and st == (0, 0) and sx[0] == 0 and sx[1] >= 1)
print(f"RESULT: {'PASS' if ok else 'FAIL'} duplicated entries share {len(roots)} root, identical rule {same_rule}; verbose unrequested {sv[0]}; strict omits {ss[1]} required items; triggers omit {st[1]}, stale trigger omits {sx[1]}")
