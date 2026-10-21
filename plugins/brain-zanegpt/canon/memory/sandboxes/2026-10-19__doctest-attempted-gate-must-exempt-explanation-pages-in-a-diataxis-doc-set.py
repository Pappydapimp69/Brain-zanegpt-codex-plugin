"""Sandbox: per-file 'attempted > 0' doctest gate over a four-quadrant (diataxis) doc set, real doctest runs (stdlib)."""
import doctest, io, contextlib
PAGES = {
 'tutorial/first-run':   ">>> add(2, 3)\n5\n>>> add(add(1, 1), 1)\n3\n",
 'howto/clamp-input':    ">>> clamp(9, 0, 5)\n5\n",
 'reference/api':        ">>> add(1, 1)\n2\n>>> clamp(-1, 0, 5)\n0\n>>> add.__name__\n'add'\n",
 'explanation/why-pure': "Functions here are pure because callers retry them; a pure add can be replayed safely.\nNo prompt lines on purpose.\n",
 'explanation/design':   "We keep clamp separate from add so each has one reason to change.\n",
 'reference/stale':      ">>> add(1, 1)\n3\n",   # one deliberately stale example
 'howto/prose-only':     "To clamp a value call clamp with low and high bounds.\n",   # howto forgot its example
}
def add(a, b): return a + b
def clamp(x, lo, hi): return max(lo, min(hi, x))
def run(txt, name):
    t = doctest.DocTestParser().get_doctest(txt, {'add': add, 'clamp': clamp}, name, None, 0)
    r = doctest.DocTestRunner(verbose=False)
    with contextlib.redirect_stdout(io.StringIO()): r.run(t)
    return r.tries, r.failures
res = {n: run(t, n) for n, t in PAGES.items()}
for n, (a, f) in res.items(): print(f"{n}: attempted {a} failed {f}")
naive = [n for n, (a, f) in res.items() if a == 0 or f > 0]                      # gate: attempted>0 and failed==0 for every file
quad = lambda n: n.split('/')[0]
smart = [n for n, (a, f) in res.items() if f > 0 or (a == 0 and quad(n) != 'explanation')]   # explanation exempt from attempted>0
true_bad = {'reference/stale', 'howto/prose-only'}
print(f"naive per-file gate flags {sorted(naive)}")
print(f"quadrant-aware gate flags {sorted(smart)}")
fp_naive = [n for n in naive if n not in true_bad]
ok = set(smart) == true_bad and len(fp_naive) == 2 and all(quad(n) == 'explanation' for n in fp_naive)
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" naive gate false-flags {len(fp_naive)} explanation pages of {len(naive)} flags; quadrant-aware gate flags exactly the {len(true_bad)} real defects (stale example, how-to with no example)")
