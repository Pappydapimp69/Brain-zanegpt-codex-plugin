"""Sandbox: does the Eisenhower urgent/important attribution claim hold when traced?

Claims exercised:
  K1 ideas:TIME-MANAGEMENT/prioritization/eisenhower-matrix/... : the popular
     'seldom' wording is not what Eisenhower said (1954 speech: 'never'), and he
     credited an unnamed former college president.
  K2 ideas:RESEARCH/corroboration/trace-sources-to-independent-roots-...: count
     distinct documented ROOTS, not citing sources.
  K3 ideas:TIME-MANAGEMENT/deadlines/parkinsons-law/...: popular phrase vs the
     primary text (verbatim present, scope different).

PREDICTION (written before first run):
  S1 naive count of sources pairing Eisenhower with the 'seldom' form = 3;
     root-traced count of PRIMARY texts containing that form = 0 (only 1 traced
     chain, Pitt -> speech, and the speech text lacks 'seldom').
  S2 tracer on a synthetic echo chain (6 echoes of 1 root vs 2 independent
     roots) ranks the 2-root claim higher; naive count ranks the echo claim higher.
  S3 (BREAK) a verbatim-wording check PASSES the Parkinson popular phrase against
     its primary text (phrase present) although the kernel says the popular
     USE is wrong; so verbatim matching alone cannot detect scope misuse.
     Expect verbatim=True, and scope markers (officials/staff) present while the
     phrase is introduced as 'a commonplace observation'.
  S4 origin of the Eisenhower sentence: chain depth to documented root = 1 hop,
     origin = UNRESOLVED (no name for the former college president).
Offline: reads optional saved page text from SNAP_DIR (default below); embedded
excerpts are the fallback. No RNG, no timing, no network.
"""
import os, re, sys

SNAP_DIR = os.environ.get("SNAP_DIR", "/tmp/claude-0/trainrun3/pass1/src")

def norm(s):
    s = s.replace("“", '"').replace("”", '"').replace("’", "'")
    return re.sub(r"\s+", " ", s).strip().lower()

def snap(name):
    p = os.path.join(SNAP_DIR, name)
    if os.path.exists(p):
        return norm(open(p, errors="replace").read())
    return None

# --- records from the Quote Investigator page (cited real source) -----------
QI = "quoteinvestigator.com/2014/05/09/urgent"
SPEECH = ('i have two kinds of problems, the urgent and the important. the urgent '
          'are not important, and the important are never urgent.')
RECORDS = [
 # id, year, text, quoted?, derived_from, kind
 dict(id="speech1954", year=1954, kind="primary-transcript", derived_from=None,
      text=SPEECH),
 dict(id="loma1954_pitt", year=1954, kind="secondhand-recollection",
      derived_from="speech1954",
      text="the things that are urgent are seldom important and the things that are important are seldom urgent"),
 dict(id="lecarre1962", year=1962, kind="novel-half-quote", derived_from=None,
      text="what is important is seldom urgent"),
 dict(id="winnipeg1973", year=1973, kind="unquoted-paraphrase", derived_from=None,
      text="the really important matters were seldom urgent, and that the most urgent matters were seldom important"),
 dict(id="csm1975", year=1975, kind="unquoted-paraphrase", derived_from=None,
      text="important matters were seldom urgent and most urgent matters were seldom important"),
]
ATTRIBUTES_TO_EISENHOWER = {"speech1954", "loma1954_pitt", "winnipeg1973", "csm1975"}

def has_seldom_form(t):
    return bool(re.search(r"seldom", t)) and "urgent" in t and "important" in t

def root_of(rec, by_id):
    seen = 0
    while rec["derived_from"]:
        rec = by_id[rec["derived_from"]]; seen += 1
    return rec, seen

def run():
    ok = []
    by_id = {r["id"]: r for r in RECORDS}
    qi = snap("qi.txt")
    checked = 0
    if qi:
        for r in RECORDS:
            if r["kind"] in ("primary-transcript", "secondhand-recollection", "novel-half-quote",
                             "unquoted-paraphrase"):
                assert norm(r["text"]) in qi, "excerpt not found in snapshot: " + r["id"]
                checked += 1
    print("snapshot excerpt checks:", checked if qi else "skipped (embedded only)")
    print("unnamed-president marker in snapshot:",
          ("unnamed" in qi and "former college president" in qi) if qi else "n/a")

    # S1
    seldom_claims = [r for r in RECORDS if r["id"] in ATTRIBUTES_TO_EISENHOWER and has_seldom_form(r["text"])]
    naive = len(seldom_claims)
    roots = {}
    for r in seldom_claims:
        root, hops = root_of(r, by_id)
        roots.setdefault(root["id"], []).append(r["id"])
    traced_roots = {k: v for k, v in roots.items() if by_id[k]["kind"] == "primary-transcript"}
    primary_with_seldom = [k for k in traced_roots if has_seldom_form(by_id[k]["text"])]
    untraced = [k for k in roots if by_id[k]["kind"] != "primary-transcript"]
    print("S1 naive seldom-attribution count:", naive, "| traced to a primary root:",
          sum(len(v) for v in traced_roots.values()), "| untraced:", len(untraced),
          "| primary roots whose text has seldom-form:", len(primary_with_seldom))
    ok.append(("S1", naive == 3 and len(primary_with_seldom) == 0
               and sum(len(v) for v in traced_roots.values()) == 1))
    # the transcript uses 'never'
    ok.append(("S1b", "important are never urgent" in SPEECH and "seldom" not in SPEECH))

    # S2 synthetic echo chain
    syn = [dict(id="wiki", derived_from=None)] + [dict(id="e%d" % i, derived_from="wiki") for i in range(6)]
    syn += [dict(id="primaryA", derived_from=None), dict(id="primaryB", derived_from=None)]
    sid = {r["id"]: r for r in syn}
    def score(ids):
        rs = {root_of(sid[i], sid)[0]["id"] for i in ids}
        return len(ids), len(rs)
    echo_claim = ["wiki"] + ["e%d" % i for i in range(6)]
    indep_claim = ["primaryA", "primaryB"]
    n_e, r_e = score(echo_claim); n_i, r_i = score(indep_claim)
    print("S2 echo claim naive/roots = %d/%d ; independent claim naive/roots = %d/%d" % (n_e, r_e, n_i, r_i))
    ok.append(("S2", n_e > n_i and r_i > r_e))

    # S3 BREAK: verbatim check on Parkinson
    pk = snap("pk.txt")
    popular = "work expands so as to fill the time available for its completion"
    if pk:
        verb = popular in pk
        intro_commonplace = "commonplace observation that " + popular in pk
        scope_marks = sum(pk.count(w) for w in ("civil servants", "officials", "staff"))
        named_law_is_staff = "parkinson's law" in pk and "the number of the officials" in pk
    else:
        verb, intro_commonplace, scope_marks, named_law_is_staff = True, True, 1, True
    print("S3 parkinson popular phrase verbatim:", verb, "| introduced as commonplace:",
          intro_commonplace, "| staff-scope markers:", scope_marks, "| named law about staff:", named_law_is_staff)
    # the verbatim check says 'attribution fine'; a scope check is a different test
    ok.append(("S3", verb and intro_commonplace and scope_marks >= 3 and named_law_is_staff))
    print("S3 verdict: verbatim check alone passes the phrase; only a scope/introduction check flags it")

    # S4 origin
    depth = root_of(by_id["loma1954_pitt"], by_id)[1]
    origin_unresolved = (qi is None) or ("former college president" in qi and "unnamed" in qi)
    print("S4 chain depth to documented root:", depth, "| origin of the sentence: UNRESOLVED" if origin_unresolved else "| origin named")
    ok.append(("S4", depth == 1 and origin_unresolved))

    bad = [k for k, v in ok if not v]
    summary = "S1 naive=%d primary_with_seldom=%d; S2 echo %d/%d vs indep %d/%d; S3 verbatim-passes-but-scope-differs; S4 depth=%d origin unresolved; failed=%s" % (
        naive, len(primary_with_seldom), n_e, r_e, n_i, r_i, depth, bad or "none")
    print("RESULT: %s %s" % ("PASS" if not bad else "FAIL", summary))

run()
