#!/usr/bin/env python3
"""Sandbox: does 'no license file => all rights reserved' hold against primary texts?

NOT LEGAL ADVICE. This models only what can be checked mechanically:
  (a) quoted primary-source rules (Berne Convention Art. 5(2), 9(1), 9(2);
      GitHub 'Licensing a repository'; GPL-2 s.4; GPL-3 s.8) are present
      verbatim in short excerpts EMBEDDED in this file (reproducible anywhere,
      no network, no local source files), and
  (b) OPTIONAL, environment-dependent: real license texts act as explicit
      GRANTS (a text with no grant grants nothing), and the copyleft/permissive
      split is detectable. This part needs the system license directory
      (default /usr/share/common-licenses, override with env var LIC_DIR). If the
      directory is missing it prints SKIPPED and everything else still runs.
  (c) five no-license controls and the snippet-reuse verdict need no files.
It cannot decide the law (implied licenses, fair use, jurisdiction).

PREDICTION (written before the first run):
  P1: grant classifier finds copy+modify+distribute grants in 12 of the 14
      distinct real license files in /usr/share/common-licenses (misses
      expected on wording: LGPL-3 grants by reference to GPL-3, plus one more).
  P2: 0 of 5 no-license controls (empty file, 'All rights reserved' notice,
      public-README, view-only text with negation, informal 'free to use') grant anything.
  P3: copyleft detector flags exactly the GPL/LGPL/MPL/GFDL files (10) and not
      Apache-2.0, BSD, CC0-1.0.
"""
import os, re, sys

LIC_DIR = os.environ.get("LIC_DIR", "/usr/share/common-licenses")
fails = []
def check(name, ok, info=""):
    print(("ok   " if ok else "FAIL ") + name + (" -- " + info if info else ""))
    if not ok: fails.append(name)

def norm(s):
    s = s.replace("&#x27;", "'").replace("\u2019", "'")
    return re.sub(r"\s+", " ", s).lower()

# ---- (a) primary-source quotes, EMBEDDED (reproducible anywhere) ---------
# Each excerpt is a short verbatim passage (whitespace normalised) copied from
# the source named in its note, at authoring time (2026-10-09).
BERNE_NOTE = ("WIPO Lex, Berne Convention for the Protection of Literary and Artistic "
              "Works (Paris Act), https://www.wipo.int/wipolex/en/text/283698, fetched as raw HTML")
EXCERPTS = {
    "berne_5_2": ("(2) The enjoyment and the exercise of these rights shall not be subject to any "
                  "formality; such enjoyment and such exercise shall be independent of the "
                  "existence of protection in the country of origin of the work.",
                  BERNE_NOTE + ", Article 5(2)"),
    "berne_9_1": ("(1) Authors of literary and artistic works protected by this Convention shall "
                  "have the exclusive right of authorizing the reproduction of these works, in "
                  "any manner or form.",
                  BERNE_NOTE + ", Article 9(1)"),
    "berne_9_2": ("(2) It shall be a matter for legislation in the countries of the Union to permit "
                  "the reproduction of such works in certain special cases, provided that such "
                  "reproduction does not conflict with a normal exploitation of the work and does "
                  "not unreasonably prejudice the legitimate interests of the author.",
                  BERNE_NOTE + ", Article 9(2)"),
    "github_default": ("However, without a license, the default copyright laws apply, meaning that "
                       "you retain all rights to your source code and no one may reproduce, "
                       "distribute, or create derivative works from your work.",
                       "GitHub Docs, 'Licensing a repository' (docs.github.com, repositories / "
                       "customizing your repository), fetched as raw HTML"),
    "gpl2_s4": ("4. You may not copy, modify, sublicense, or distribute the Program except as "
                "expressly provided under this License. Any attempt otherwise to copy, modify, "
                "sublicense or distribute the Program is void, and will automatically terminate "
                "your rights under this License.",
                "GNU GPL version 2 text, /usr/share/common-licenses/GPL-2, section 4"),
    "gpl3_s8": ("8. Termination. You may not propagate or modify a covered work except as "
                "expressly provided under this License. Any attempt otherwise to propagate or "
                "modify it is void, and will automatically terminate your rights under this "
                "License",
                "GNU GPL version 3 text, /usr/share/common-licenses/GPL-3, section 8 "
                "(Termination; the default prohibition sits in s.8 of this text, not s.9)"),
}
QUOTES = [  # (label, excerpt key, exact phrase that must appear in that excerpt)
    ("Berne 5(2) no formality", "berne_5_2",
     "enjoyment and the exercise of these rights shall not be subject to any formality"),
    ("Berne 9(1) exclusive reproduction right", "berne_9_1",
     "shall have the exclusive right of authorizing the reproduction of these works, in any manner or form"),
    ("Berne 9(2) special-case exceptions", "berne_9_2",
     "to permit the reproduction of such works in certain special cases"),
    ("GitHub default rule", "github_default",
     "without a license, the default copyright laws apply, meaning that you retain all rights to your source code and no one may reproduce, distribute, or create derivative works from your work"),
    ("GPL-2 s.4 default prohibition", "gpl2_s4",
     "you may not copy, modify, sublicense, or distribute the program except as expressly provided under this license"),
    ("GPL-3 s.8 default prohibition", "gpl3_s8",
     "you may not propagate or modify a covered work except as expressly provided under this license"),
]
print("embedded excerpts (no external files needed): %d" % len(EXCERPTS))
for label, key, phrase in QUOTES:
    text, note = EXCERPTS[key]
    print("  source of %s: %s" % (key, note))
    check("quote: " + label, phrase in norm(text))

# ---- (b) grant classifier (needed by controls too) -----------------------
MARKER = re.compile(r"(hereby grants?|grants? (to )?you|permission is hereby granted|you may|"
                    r"is permitted|are permitted|permitted provided|licen[cs]e to|permission to|"
                    r"you are free to|hereby grant)", re.I)
NEG = re.compile(r"(may not|not permitted|no one may|must not|shall not|cannot|may only view)", re.I)
ACTIONS = {
    "copy": re.compile(r"\b(cop(y|ies|ying)|reproduc\w*|duplicat\w*)\b", re.I),
    "modify": re.compile(r"\b(modif\w*|adapt\w*|derivative|alter\w*|chang\w*)\b", re.I),
    "distribute": re.compile(r"\b(distribut\w*|redistribut\w*|propagat\w*|convey\w*|give away|publish\w*|sell)\b", re.I),
}
def grants(text):
    got = set()
    for s in re.split(r"(?<=[.;:])\s+", re.sub(r"\s+", " ", text)):
        if MARKER.search(s) and not NEG.search(s):
            for a, rx in ACTIONS.items():
                if rx.search(s): got.add(a)
    return got

COPYLEFT = re.compile(
    r"(license the (entire|whole) work|as a whole under the terms|under precisely this license|"
    r"licensed? as a whole|(entire|whole) work.{0,120}this license|"
    r"source code form.{0,120}under the terms of this license|"
    r"made available under the terms of this license|"
    r"distributed under the terms of this license|governed by the terms and conditions of this license|"
    r"license (the )?(entire )?work as a whole under this license)", re.I)
def copyleft(text):
    return bool(COPYLEFT.search(re.sub(r"\s+", " ", text)))

# ---- (b') OPTIONAL corpus part: 14 real license files --------------------
corpus_ran = os.path.isdir(LIC_DIR)
full, partial, cl, files = [], [], [], []
if corpus_ran:
    files = sorted(f for f in os.listdir(LIC_DIR) if not os.path.islink(os.path.join(LIC_DIR, f)))
    print("real license files (symlinks excluded): %d -> %s" % (len(files), " ".join(files)))
    for f in files:
        t = open(os.path.join(LIC_DIR, f), encoding="utf-8", errors="replace").read()
        g = grants(t)
        (full if g == set(ACTIONS) else partial).append((f, sorted(g)))
        if copyleft(t): cl.append(f)
    print("full 3-action grant:", [f for f, _ in full])
    print("partial:", partial)
    print("copyleft flagged:", cl)
    check("P1 grant coverage == 12 of 14 (prediction)", len(files) == 14 and len(full) == 12,
          "observed %d of %d" % (len(full), len(files)))
else:
    print("SKIPPED corpus part (P1 grant coverage, P3 copyleft split): license directory "
          "not found: %s (set LIC_DIR to a directory of license texts to run it)" % LIC_DIR)

# ---- no-license controls (scenario built to BREAK the claim at the margins)
CONTROLS = {
    "empty (no LICENSE file)": "",
    "notice only": "Copyright (c) 2026 Alice. All rights reserved.",
    "public README": "This repository is public. Anyone can view and read the source.",
    "view-only with negation": "You may view the source. You may not copy, modify, or distribute it.",
    "informal intent (BREAK: law may imply a license)": "Free to use! Public code, do whatever you like with it.",
}
zero = 0
for name, t in CONTROLS.items():
    g = grants(t)
    print("control %-52s grants=%s" % (name, sorted(g)))
    zero += (not g)
check("P2 controls granting nothing == 5 of 5 (prediction)", zero == 5, "observed %d of 5" % zero)

# fair-use sibling: no grant != decided. The model must say 'undecidable', never 'allowed'.
def verdict(license_text, use):
    g = grants(license_text)
    if use in g: return "GRANTED"
    return "NO GRANT (exceptions such as fair use / 9(2) special cases are a separate, case-by-case question this model cannot decide)"
v = verdict("", "copy")
print("snippet reuse, no license ->", v)
check("no-license snippet reuse is never 'GRANTED'", v.startswith("NO GRANT") and "case-by-case" in v)

# permissive vs copyleft split (sibling kernel) -- corpus part only
if corpus_ran:
    expect_cl = {f for f in files if re.match(r"(GPL|LGPL|MPL|GFDL)", f)}
    check("P3 copyleft set == GPL/LGPL/MPL/GFDL (10), not Apache/BSD/CC0 (prediction)",
          set(cl) == expect_cl and not ({"Apache-2.0", "BSD", "CC0-1.0"} & set(cl)),
          "flagged=%d expected=%d symdiff=%s" % (len(cl), len(expect_cl), sorted(set(cl) ^ expect_cl)))
else:
    print("SKIPPED P3 copyleft split (corpus part not run)")

# summary
if corpus_ran:
    corpus_txt = "corpus=RAN grants-full=%d/%d copyleft=%d" % (len(full), len(files), len(cl))
else:
    corpus_txt = "corpus=SKIPPED (P1,P3 not evaluated; embedded excerpts and controls only)"
print("RESULT: %s %s controls-zero=%d/5 (failed checks: %s)" % (
    "PASS" if not fails else "FAIL", corpus_txt, zero, "; ".join(fails) or "none"))
