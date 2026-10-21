"""Sandbox: does wiring examples into doctest catch API drift, and what does it miss?
Deterministic, stdlib only. Models an API at v1 and v2 (v2 renames a kwarg and
changes a default), docs as tutorial (examples), how-to, and reference (prose)."""
import doctest, types

API_V1 = '''
def resize(w, h, keep_ratio=True):
    return (w, h) if not keep_ratio else (w, w * h // w)
'''
API_V2 = '''
def resize(w, h, preserve_ratio=False):
    return (w, h) if not preserve_ratio else (w, w * h // w)
'''
# tutorial doc: executable examples. reference doc: prose claims only.
TUTORIAL = """
>>> resize(4, 3)
(4, 3)
>>> resize(4, 3, keep_ratio=False)
(4, 3)
"""
HOWTO_ONLY_ONE_EXAMPLE = """
>>> resize(10, 5)
(10, 5)
"""
REFERENCE_PROSE = "resize(w, h, keep_ratio=True): keep_ratio defaults to True."

def load(src):
    m = types.ModuleType("api"); exec(src, m.__dict__); return m

def run_doctest(text, mod):
    parser = doctest.DocTestParser()
    test = parser.get_doctest(text, dict(mod.__dict__), "doc", None, 0)
    runner = doctest.DocTestRunner(verbose=False, optionflags=doctest.ELLIPSIS)
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        res = runner.run(test)
    return res.failed, res.attempted

def copy_first_reader(text, mod):
    """Reader skips prose, copies examples; succeeds if every example runs w/o exception."""
    ok = 0
    for line in text.splitlines():
        if line.startswith(">>> "):
            try: eval(line[4:], dict(mod.__dict__)); ok += 1
            except Exception: return False
    return ok > 0

def prose_check(text, mod):
    """Nothing executes prose: a checker can only 'pass' it. Returns True always."""
    return True

v1, v2 = load(API_V1), load(API_V2)
results = {}
# S1: docs and API in sync (v1) -> doctest clean
results["S1_sync_v1_failed"] = run_doctest(TUTORIAL, v1)[0]
# S2: API drifts to v2, doctest wired -> must fail loudly
f2 = run_doctest(TUTORIAL, v2)
results["S2_drift_v2_failed"] = f2[0]
# S3: no CI wiring: copy-first reader on stale docs fails on v2 anyway, reference prose still 'passes'
results["S3_reader_v2_ok"] = copy_first_reader(TUTORIAL, v2)
results["S3_prose_flagged_by_check"] = not prose_check(REFERENCE_PROSE, v2)
# S4 BREAK: drift that the examples never touch (default flip) -> doctest with only
# the default-free example passes while behaviour changed
f4 = run_doctest(HOWTO_ONLY_ONE_EXAMPLE, v2)
results["S4_default_flip_doctest_failed"] = f4[0]
# the same default flip observable: keep_ratio default semantic differs
results["S4_actual_behaviour_changed"] = v1.resize(4, 3) != v2.resize(4, 3) or \
    v1.resize.__defaults__ != v2.resize.__defaults__
for k, v in results.items(): print(k, v)

caught = results["S2_drift_v2_failed"] >= 1
reader_blocked = results["S3_reader_v2_ok"] is False
prose_blind = results["S3_prose_flagged_by_check"] is False
silent_gap = results["S4_default_flip_doctest_failed"] == 0 and results["S4_actual_behaviour_changed"]
ok = results["S1_sync_v1_failed"] == 0 and caught and reader_blocked and prose_blind and silent_gap
print("RESULT: %s doctest caught example drift (%d fails) and the copy-first reader breaks on stale docs, "
      "but reference prose is never checked and an example that avoids the changed default passes silently"
      % ("PASS" if ok else "FAIL", results["S2_drift_v2_failed"]))
