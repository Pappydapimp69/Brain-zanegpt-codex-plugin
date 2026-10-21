"""Sandbox: API with 6 documented behaviours drifts in v2 (stdlib doctest, deterministic).
Docs A: prose reference only. Docs B: worked examples run by doctest in CI (drift fixed when caught).
A 'developer' copies each doc claim into a call and we count calls that work against v2."""
import doctest, types
def make_api(v):
    ns = {}
    src = '''
def resize(img, width, height=None): return (width, height or width)           # v1 default: square
def fmt(x, places=2): return round(x, places)
def tag(name, *, upper=False): return name.upper() if upper else name
def retry(fn, tries=3): return tries
def clamp(x, lo, hi): return max(lo, min(hi, x))
def join(a, b, sep=","): return a + sep + b
'''
    if v == 2:
        src = src.replace("height=None): return (width, height or width)", "height=None): return (width, height or 0)")  # default drift (A)
        src = src.replace("def retry(fn, tries=3)", "def retry(fn, tries=5)")                                                      # default drift (B)
        src = src.replace("def tag(name, *, upper=False)", "def tag(name, *, case='keep')").replace("name.upper() if upper else name", "name.upper() if case=='upper' else name")  # rename (C)
    exec(src, ns); return ns
PROSE = {  # claim -> callable(api) that a developer would write from the prose
 'resize square default': lambda a: a['resize'](None, 4) == (4, 4),
 'fmt places': lambda a: a['fmt'](1.2345, 2) == 1.23,
 'tag upper kw': lambda a: a['tag']('x', upper=True) == 'X',
 'retry default 3': lambda a: a['retry'](None) == 3,
 'clamp': lambda a: a['clamp'](9, 0, 5) == 5,
 'join sep': lambda a: a['join']('a', 'b') == 'a,b',
}
def works(claim, a):
    try: return bool(PROSE[claim](a))
    except TypeError: return False
v2 = make_api(2)
prose_ok = sum(works(c, v2) for c in PROSE)
# Docs B: doctest examples for 4 of the 6 behaviours (resize, fmt, tag, clamp); retry & join defaults unexercised
EX = {'resize square default': ">>> resize(None, 4)\n(4, 4)\n", 'fmt places': ">>> fmt(1.2345, 2)\n1.23\n",
      'tag upper kw': ">>> tag('x', upper=True)\n'X'\n", 'clamp': ">>> clamp(9, 0, 5)\n5\n"}
def doctest_fails(api):
    p = doctest.DocTestParser(); failed = attempted = 0; bad = []
    for c, txt in EX.items():
        t = p.get_doctest(txt, dict(api), c, None, 0)
        r = doctest.DocTestRunner(verbose=False); import io, contextlib
        with contextlib.redirect_stdout(io.StringIO()): r.run(t)
        attempted += r.tries
        if r.failures: failed += 1; bad.append(c)
    return failed, attempted, bad
failed, attempted, bad = doctest_fails(v2)
# CI catches the 2 drifted exercised claims; maintainer fixes the examples -> developer copies the fixed example.
fixed_examples_ok = sum(1 for c in EX if c not in bad) + len(bad)  # fixed examples always work by construction of CI
copy_ok_B = 4 + sum(works(c, v2) for c in ('retry default 3', 'join sep'))  # unexercised claims stay as prose
print(f"v2 drift: doctest attempted {attempted}, failing {failed} {bad}")
print(f"prose-only copy success {prose_ok}/6; examples+CI copy success {copy_ok_B}/6 (retry default unexercised)")
a1 = make_api(1); v1_prose = sum(works(c, a1) for c in PROSE)
print(f"control v1: prose copy success {v1_prose}/6")
ok = (v1_prose == 6 and prose_ok == 3 and failed == 2 and attempted == 4 and copy_ok_B == 5)
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" v1 prose 6/6; v2 prose {prose_ok}/6; doctest caught {failed}/2 exercised drifts; examples+CI copy {copy_ok_B}/6 (unexercised retry default still wrong)")
