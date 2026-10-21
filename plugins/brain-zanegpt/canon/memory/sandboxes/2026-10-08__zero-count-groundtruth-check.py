# Four worlds all print "0 pushed, 0 held". Which does a ground-truth check (count files in the confirmed source dir) tell apart?
def sync(world):
    # returns (printed_summary, files_in_confirmed_source, files_in_scanned_dir)
    if world == "genuinely-empty":   return ("0 pushed, 0 held", 0, 0)
    if world == "wrong-dir":         return ("0 pushed, 0 held", 3, 0)   # draft#E5: wrote to cache side
    if world == "pkill-self-kill":   return ("0 pushed, 0 held", 3, 3)   # dark-goblin#E2: chain aborted before sync ran
    if world == "parser-drop":       return ("0 pushed, 0 held", 3, 3)   # brain#E3: entries dropped by parser
def naive(out, src, scanned): return out.startswith("0 pushed")                    # trusts the zero
def check_src(out, src, scanned): return out.startswith("0 pushed") and src > 0     # compares to confirmed source only
def check_both(out, src, scanned, ran=None): return out.startswith("0 pushed") and src > 0 and ran is not False
worlds = ["genuinely-empty", "wrong-dir", "pkill-self-kill", "parser-drop"]
flag = {"naive": 0, "src": 0, "src+scan": 0}; truth_bad = 3
for w in worlds:
    out, src, scanned = sync(w)
    f_src = out.startswith("0 pushed") and src > 0
    f_scan = f_src and scanned == 0           # distinguishes wrong-dir only
    f_naive = False                           # naive never flags anything
    flag["naive"] += f_naive; flag["src"] += f_src; flag["src+scan"] += f_scan
    print(w, "-> flagged by src-check:", f_src, "| diagnoses wrong-dir:", f_scan)
ok = flag["naive"] == 0 and flag["src"] == 3 and flag["src+scan"] == 1
print("RESULT: %s of 3 failing worlds, naive trust flagged %d, source-count check flagged %d, directory comparison pinpointed %d" % ("PASS" if ok else "FAIL", flag["naive"], flag["src"], flag["src+scan"]))
