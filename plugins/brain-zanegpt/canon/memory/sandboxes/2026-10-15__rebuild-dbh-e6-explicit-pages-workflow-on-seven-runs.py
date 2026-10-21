"""Rebuild of local dbh E6 (Pages 'building' for hours = the dynamic
pages-build-deployment run queued with no jobs; fix: an explicit deploy
workflow, check environment branch policy). Not blind: I audited this entry
earlier in the session. A sandbox cannot make GitHub's builder stick, so this
rebuild tests the FIX side on independent real data: every Actions run of
Pappydapimp69/Seven, fetched through the GitHub API on 2026-10-15 and embedded
below as (workflow, event, conclusion, run seconds, queue seconds) - 68 runs,
2026-08-29 to 2026-10-11. Seven deploys with an explicit upload-pages-artifact
workflow (.github/workflows/deploy.yml), never the dynamic builder.
PREDICTION (written before running): no run is queued for more than 5 min
(the dbh failure mode is hours queued); >= 95% of SEVEN deploy runs succeed;
every run completes within 5 min; 0 runs are the dynamic pages-build-deployment.
"""
import sys
print("python", sys.version.split()[0])
RUNS = [('SEVEN', 'push', 'success', 24, 0), ('SEVEN', 'push', 'success', 25, 0), ('SEVEN', 'push', 'success', 21, 0), ('SEVEN', 'push', 'success', 20, 0), ('SEVEN', 'push', 'success', 26, 0), ('SEVEN', 'push', 'success', 25, 0), ('SEVEN', 'push', 'success', 23, 0), ('SEVEN', 'push', 'success', 23, 0), ('SEVEN', 'push', 'success', 23, 0), ('SEVEN', 'push', 'success', 25, 0), ('SEVEN', 'push', 'success', 18, 0), ('SEVEN', 'push', 'success', 21, 0), ('SEVEN', 'push', 'success', 46, 0), ('SEVEN', 'push', 'success', 24, 0), ('SEVEN', 'push', 'success', 23, 0), ('SEVEN', 'push', 'success', 28, 0), ('SEVEN', 'push', 'success', 22, 0), ('SEVEN', 'push', 'success', 24, 0), ('SEVEN', 'push', 'success', 22, 0), ('SEVEN', 'push', 'success', 21, 0), ('SEVEN', 'push', 'success', 23, 0), ('SEVEN', 'push', 'success', 19, 0), ('SEVEN', 'push', 'success', 24, 0), ('SEVEN', 'push', 'success', 21, 0), ('SEVEN', 'push', 'success', 28, 0), ('SEVEN', 'push', 'failure', 10, 0), ('SEVEN', 'push', 'success', 24, 0), ('SEVEN', 'push', 'success', 37, 0), ('SEVEN', 'push', 'success', 21, 0), ('SEVEN', 'push', 'success', 22, 0), ('SEVEN', 'push', 'success', 23, 0), ('SEVEN', 'push', 'success', 23, 0), ('SEVEN', 'push', 'success', 24, 0), ('SEVEN', 'push', 'success', 22, 0), ('SEVEN', 'push', 'success', 26, 0), ('SEVEN', 'push', 'success', 23, 0), ('SEVEN', 'push', 'success', 49, 0), ('SEVEN', 'push', 'success', 23, 0), ('SEVEN', 'push', 'success', 23, 0), ('SEVEN', 'push', 'success', 25, 0), ('SEVEN', 'push', 'success', 33, 0), ('SEVEN', 'push', 'success', 24, 0), ('SEVEN', 'push', 'success', 25, 0), ('SEVEN', 'push', 'success', 28, 0), ('SEVEN', 'push', 'success', 24, 0), ('SEVEN', 'push', 'success', 20, 0), ('SEVEN', 'push', 'success', 22, 0), ('SEVEN', 'push', 'success', 22, 0), ('SEVEN', 'push', 'success', 27, 0), ('SEVEN', 'push', 'success', 25, 0), ('SEVEN', 'push', 'success', 24, 0), ('SEVEN', 'push', 'success', 21, 0), ('SEVEN', 'push', 'success', 23, 0), ('SEVEN', 'push', 'success', 23, 0), ('SEVEN', 'push', 'success', 23, 0), ('SEVEN', 'push', 'success', 26, 0), ('SEVEN', 'push', 'success', 27, 0), ('SEVEN', 'push', 'success', 25, 0), ('SEVEN', 'push', 'success', 24, 0), ('SEVEN', 'push', 'success', 20, 0), ('SEVEN', 'push', 'success', 26, 0), ('SEVEN', 'push', 'success', 24, 0), ('SEVEN', 'push', 'success', 24, 0), ('SEVEN', 'push', 'success', 22, 0), ('SEVEN', 'push', 'success', 24, 0), ('SEVEN', 'push', 'success', 24, 0), ('MIRAGE', 'push', 'failure', 10, 0), ('MIRAGE', 'push', 'failure', 10, 0)]
seven = [r for r in RUNS if r[0] == "SEVEN"]
ok = sum(r[2] == "success" for r in seven)
maxq = max(r[4] for r in RUNS); maxrun = max(r[3] for r in RUNS)
dynamic = sum(1 for r in RUNS if r[0].lower().startswith("pages"))
fails = [r for r in RUNS if r[2] != "success"]
print(f"runs {len(RUNS)}; SEVEN deploys {len(seven)}, success {ok} ({ok/len(seven):.1%}); max queue {maxq}s; max run {maxrun}s; dynamic builder runs {dynamic}; failures {fails}")
c = [maxq <= 300, ok / len(seven) >= 0.95, maxrun <= 300, dynamic == 0]
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} {sum(c)}/4; explicit workflow: {ok}/{len(seven)} SEVEN deploys succeeded, max queue {maxq}s, max run {maxrun}s, 0 dynamic-builder runs; the stuck-builder half is not reproducible here")
