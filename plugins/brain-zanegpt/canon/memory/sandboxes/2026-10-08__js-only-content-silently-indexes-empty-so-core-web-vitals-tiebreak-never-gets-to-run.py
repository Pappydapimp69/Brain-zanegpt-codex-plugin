"""Prediction (before run): in a deterministic two-phase indexer (crawl raw HTML -> render queue -> render with a step budget -> index),
(1) an SSR page is indexed with its full content at first pass; (2) a client-rendered page is indexed EMPTY at first pass and gets content only after
its render-queue delay; (3) a render timeout or a script error leaves it empty FOREVER with no error surfaced (silent fallback, like a missing sprite key);
(4) ranking = relevance then Core Web Vitals as tiebreak, so a CSR page that never rendered (relevance 0) loses to a slower SSR page, while between two equally relevant pages the faster one wins.
Break: raise the render budget above the page's script cost and the CSR page must catch up (the failure is conditional, not inherent)."""
QUERY = {"vegan", "lasagna"}

def page(name, mode, words, script_cost, js_error=False, lcp=2.5):
    return dict(name=name, mode=mode, words=set(words), cost=script_cost, err=js_error, lcp=lcp)

def raw_html(p):            # what the first pass sees
    return p["words"] if p["mode"] == "ssr" else set()

def rendered(p, budget):    # what the render phase sees
    if p["mode"] == "ssr": return p["words"]
    if p["err"] or p["cost"] > budget: return set()   # silent: nothing signals failure
    return p["words"]

def index_at(p, step, queue_delay, budget):
    content = raw_html(p)
    if step >= queue_delay: content = rendered(p, budget) or content
    return content

def rank(pages, step, queue_delay, budget):
    sc = []
    for p in pages:
        rel = len(QUERY & index_at(p, step, queue_delay, budget))
        sc.append((rel, -p["lcp"], p["name"]))        # relevance first, CWV only as tiebreak
    return [n for _, _, n in sorted(sc, reverse=True)]

W = ["vegan", "lasagna", "recipe"]
ssr_slow = page("ssr_slow", "ssr", W, 0, lcp=4.8)
csr_fast = page("csr_fast", "csr", W, 5, lcp=1.2)
csr_heavy = page("csr_heavy", "csr", W, 50, lcp=1.2)
csr_err = page("csr_err", "csr", W, 5, js_error=True, lcp=1.2)
ssr_fast = page("ssr_fast", "ssr", W, 0, lcp=1.5)
checks = []
Q, B = 10, 20
checks.append(("1 ssr full at step0", index_at(ssr_slow, 0, Q, B) == set(W)))
checks.append(("2 csr empty at step0, full after queue", index_at(csr_fast, 0, Q, B) == set() and index_at(csr_fast, Q, Q, B) == set(W)))
checks.append(("3a heavy script times out forever", all(index_at(csr_heavy, s, Q, B) == set() for s in (Q, 100, 10000))))
checks.append(("3b script error empty forever", index_at(csr_err, 10000, Q, B) == set()))
checks.append(("4a never-rendered fast page loses to slow ssr", rank([csr_heavy, ssr_slow], 100, Q, B)[0] == "ssr_slow"))
checks.append(("4b equal relevance: faster wins", rank([ssr_slow, ssr_fast], 0, Q, B)[0] == "ssr_fast"))
checks.append(("4c before queue delay ssr beats csr despite worse CWV", rank([csr_fast, ssr_slow], 0, Q, B)[0] == "ssr_slow"))
checks.append(("5 BREAK: budget above cost rescues heavy csr, then CWV decides", index_at(csr_heavy, Q, Q, 60) == set(W) and rank([csr_heavy, ssr_slow], Q, Q, 60)[0] == "csr_heavy"))
for n, ok in checks: print(("ok   " if ok else "FAIL ") + n)
good = all(ok for _, ok in checks)
print("RESULT: %s %d/%d checks; csr page is empty until queue delay %d, empty forever when cost>budget or script errors, and CWV never rescues relevance 0; budget 60 > cost 50 rescues it" % ("PASS" if good else "FAIL", sum(ok for _, ok in checks), len(checks), Q))
