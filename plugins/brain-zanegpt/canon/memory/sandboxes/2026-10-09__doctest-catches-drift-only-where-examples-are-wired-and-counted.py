"""Sandbox: kernel ideas:DOCUMENTATION/executable-docs/doctest (+ sibling doc-rot, memory sandbox-resolver-starves-tutorial/E2).
Uses the REAL stdlib doctest module on an API that changes between v1 and v2 while its documentation does not.
Prediction (before run): unrun docs detect 0 of 4 stale examples; doctest over the module docstrings detects the stale docstring examples (3 of 3);
a stale README example and a stale plain-fence (no >>> prompt) example stay undetected unless the README is wired in AND uses prompts (so 1 of 5 stays hidden even with testfile);
a module with zero examples reports 0 failed (vacuous pass) so the 'attempted > 0' per-file check is needed. Deterministic, stdlib only."""
import doctest, types, os, tempfile

V2 = '''
def area(w, h):
    """Rectangle area (v2 now returns a float).
    >>> area(2, 3)
    6
    """
    return float(w * h)

def label(n):
    """Label text (v2 changed the prefix).
    >>> label(5)
    'n=5'
    """
    return "num:%d" % n

def keys(d):
    """Sorted keys (v2 returns a tuple).
    >>> keys({'b': 1, 'a': 2})
    ['a', 'b']
    """
    return tuple(sorted(d))

def undocumented(x):
    return x
'''
README = """# Usage
Call area like this:

>>> area(2, 3)
6

and in plain fenced form (no prompt):

    area(2, 3)  # returns 6
"""
EMPTY = '''
def f(x):
    """Does a thing; example is prose only: f(2) returns 4"""
    return x * 3
'''

def load(name, src):
    m = types.ModuleType(name); exec(compile(src, name, "exec"), m.__dict__); m.__doc__ = m.__doc__; return m

def run_mod(m):
    f = doctest.DocTestFinder(); r = doctest.DocTestRunner(verbose=False, optionflags=0)
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        for t in f.find(m, m.__name__, globs=dict(m.__dict__)): r.run(t)
    return r.failures, r.tries

# the doctest finder needs source lines for exec'd modules; docstrings come from __doc__ so it works
m2 = load("v2mod", V2)
stale_total = 4  # 3 docstring examples + 1 README example (plus 1 plain fence = 5 stale claims)
# S1 no checking at all
detected_unrun = 0
# S2 doctest over module docstrings
fail2, tries2 = run_mod(m2)
# S3 README wired via doctest.testfile
d = tempfile.mkdtemp(); p = os.path.join(d, "README.txt"); open(p, "w").write(README)
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    r3 = doctest.testfile(p, module_relative=False, globs=dict(m2.__dict__), optionflags=0)
# S4 vacuous pass: module whose example is prose only
me = load("emptymod", EMPTY); failE, triesE = run_mod(me)
# S5 fragility: dict repr / whitespace false failure and its flag fix
frag = types.ModuleType("frag"); frag.__doc__ = ">>> print(  'a   b')\na b\n"
r5 = doctest.DocTestRunner(optionflags=0)
with contextlib.redirect_stdout(io.StringIO()):
    for t in doctest.DocTestFinder().find(frag, "frag"): r5.run(t)
r5n = doctest.DocTestRunner(optionflags=doctest.NORMALIZE_WHITESPACE)
with contextlib.redirect_stdout(io.StringIO()):
    for t in doctest.DocTestFinder().find(frag, "frag"): r5n.run(t)
print("S1 unrun docs detect:", detected_unrun, "of 5 stale claims")
print("S2 module doctest: tries=%d failed=%d (stale docstring examples caught)" % (tries2, fail2))
print("S3 README via testfile: attempted=%d failed=%d (plain fence invisible: 1 stale claim never attempted)" % (r3.attempted, r3.failed))
print("S4 prose-only module: failed=%d attempted=%d -> vacuous pass" % (failE, triesE))
print("S5 whitespace-only mismatch: failed=%d, with NORMALIZE_WHITESPACE failed=%d" % (r5.failures, r5n.failures))
caught = fail2 + r3.failed
hidden = 5 - caught
ok = detected_unrun == 0 and fail2 == 3 and r3.failed == 1 and hidden == 1 and failE == 0 and triesE == 0 and r5.failures == 1 and r5n.failures == 0
print("RESULT: %s doctest caught %d of 5 stale claims (3 docstring + 1 wired README); 1 plain-fence claim hidden; unrun docs caught 0; zero-example file passes with failed=0 attempted=0; whitespace-only mismatch fails until NORMALIZE_WHITESPACE"
      % ("PASS" if ok else "FAIL", caught))
