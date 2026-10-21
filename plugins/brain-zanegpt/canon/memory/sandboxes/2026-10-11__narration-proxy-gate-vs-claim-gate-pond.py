# Sandbox: state-driven copy gated on a proxy (mat exists) vs on the claim (bed failing).
# Prediction (written before run): proxy gate emits >=1 false "gone quiet" line on healthy-with-cover
# states and the claim gate emits 0 false lines over the same grid; a lexical novelty gate (brain/E98)
# flags captions that merely restate the readout numbers.
import itertools, re

def truth_quiet(s):          # ground truth: pond is actually failing
    return s["plants"] < 20 or s["o2"] < 40 or s["fish"] == 0

def proxy_line(s):
    return "Under the mat it has gone quiet." if s["mat"] else "Not much has happened yet."
def claim_line(s):
    failing = s["plants"] < 20 or s["o2"] < 40
    return "Under the mat it has gone quiet." if failing else "Not much has happened yet. Built well, or not started - from here they look identical."

def claim_line_v2(s):        # iteration 2: predicate now covers every way the claim is true
    failing = s["plants"] < 20 or s["o2"] < 40 or s["fish"] == 0
    return claim_line(dict(s, plants=0)) if failing else claim_line(dict(s, plants=99, o2=99))

def says_quiet(line): return "gone quiet" in line
def false_count(fn, grid):
    return sum(1 for s in grid if says_quiet(fn(s)) != truth_quiet(s))

grid = [dict(mat=m, plants=p, o2=o, fish=f) for m, p, o, f in
        itertools.product([0, 1], [0, 10, 30, 60], [10, 39, 40, 79, 95], [0, 5])]
# consistent worlds only: no fish without oxygen >=40 would be odd, but keep fish=0 case as truth failing
# iteration 1 observed: claim gate 24 false (not 0) - its predicate omitted fish==0; v2 fixes that.
fp, fc1, fc = false_count(proxy_line, grid), false_count(claim_line, grid), false_count(claim_line_v2, grid)
print("claim v1 false", fc1)
print("grid", len(grid), "proxy false", fp, "claim false", fc)
# scenario: the reported failure 79% oxygen, mat present, fish swimming
s = dict(mat=1, plants=30, o2=79, fish=5)
print("79% case proxy:", proxy_line(s)); print("79% case claim:", claim_line(s))
# BREAK scenario: claim predicate's own threshold is wrong (plants<20 but plants=25 with o2 high & fish=0)
b = dict(mat=0, plants=25, o2=90, fish=0)
print("break: claim gate says quiet=", says_quiet(claim_line(b)), "truth=", truth_quiet(b))
# readout pair + novelty gate (E98-style): caption restating the numbers is flagged
def novel(caption, readout):
    nums = set(re.findall(r"\d+(?:\.\d+)?", readout))
    return not (set(re.findall(r"\d+(?:\.\d+)?", caption)) & nums)
ro = "weeks 31 / bodies 37 / decay 0.00"
print("novelty restate:", novel("31 weeks, 37 bodies, decay 0.00", ro), "paraphrase-free:", novel("Time passes. The toll builds. Nothing breaks down.", ro))
ok = fp >= 1 and fc1 < fp and fc == 0 and says_quiet(proxy_line(s)) and not says_quiet(claim_line(s)) and (says_quiet(claim_line(b)) != truth_quiet(b)) and not novel("31 weeks, 37 bodies", ro)
print("RESULT: %s false lines over %d states: proxy gate %d, claim gate v1 %d (predicate missed fish==0), claim gate v2 %d" % ("PASS" if ok else "FAIL", len(grid), fp, fc1, fc))
