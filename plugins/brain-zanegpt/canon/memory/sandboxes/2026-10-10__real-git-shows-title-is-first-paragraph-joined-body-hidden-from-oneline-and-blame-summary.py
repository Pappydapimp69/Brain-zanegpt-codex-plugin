"""Prediction (before run), real git binary in a temp repo:
 1) --oneline/%s/blame summary/format-patch Subject all show ONLY the title, the body only via %b / full message.
 2) BREAK: a message whose first paragraph spans 3 lines (no blank line) makes %s the 3 lines JOINED by spaces, longer than 50 chars -
    the 50-char convention is not enforced by git, only the blank-line split is.
 3) git blame --porcelain 'summary' equals the title of the commit that last touched the line (not the body).
 4) a path in .gitignore is absent from git ls-files after 'git add -A' while the source file is present.
Deterministic: fixed dates, identity, no global config. stdlib only (subprocess + tempfile)."""
import os, subprocess, tempfile

env = dict(os.environ, GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_SYSTEM="/dev/null",
           GIT_AUTHOR_NAME="a", GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_NAME="a", GIT_COMMITTER_EMAIL="a@x",
           GIT_AUTHOR_DATE="2026-01-01T00:00:00Z", GIT_COMMITTER_DATE="2026-01-01T00:00:00Z")
d = tempfile.mkdtemp(prefix="gitsb_")
def g(*a, inp=None):
    return subprocess.run(["git", "-C", d, *a], env=env, input=inp, capture_output=True, text=True, check=True).stdout

g("init", "-q"); g("config", "commit.gpgsign", "false")
open(d + "/.gitignore", "w").write("build/\n")
os.makedirs(d + "/build"); open(d + "/build/out.bin", "w").write("generated\n")
open(d + "/app.py", "w").write("x = 1\n")
g("add", "-A")
title = "Add retry to fetch loop"
body = "The upstream drops the first request after idle, so retry once.\nWithout this the nightly job silently loses a day."
g("commit", "-q", "-F", "-", inp=title + "\n\n" + body + "\n")
open(d + "/app.py", "a").write("y = 2\n")
g("add", "-A")
g("commit", "-q", "-F", "-", inp="line one of a long first paragraph that keeps going\nline two continues with no blank line\nline three ends it\n\nreal body\n")

res = {}
oneline = g("log", "--oneline").splitlines()
res["oneline_has_title"] = any(l.endswith(title) for l in oneline)
res["oneline_hides_body"] = not any("nightly" in l for l in oneline)
res["body_via_b"] = "nightly job" in g("log", "--format=%b", "HEAD~1")
res["title_len"] = len(title)
joined = g("log", "-1", "--format=%s")
res["joined_title"] = joined.strip()
res["joined_len"] = len(joined.strip())
res["joined_over_50"] = res["joined_len"] > 50
patch = g("format-patch", "-1", "HEAD~1", "--stdout")
subj = [l for l in patch.splitlines() if l.startswith("Subject:")][0]
res["patch_subject_title_only"] = subj == "Subject: [PATCH] " + title
res["patch_body_below"] = "nightly job" in patch
blame = g("blame", "--porcelain", "app.py")
summaries = [l.split(" ", 1)[1] for l in blame.splitlines() if l.startswith("summary ")]
res["blame_summaries"] = summaries
res["blame_summary_is_title"] = summaries[0] == title and "nightly" not in " ".join(summaries)
tracked = g("ls-files").split()
res["ignored_untracked"] = "build/out.bin" not in tracked and "app.py" in tracked
print(res)
ok = (res["oneline_has_title"] and res["oneline_hides_body"] and res["body_via_b"] and res["joined_over_50"]
      and res["patch_subject_title_only"] and res["patch_body_below"] and res["blame_summary_is_title"]
      and res["ignored_untracked"] and "line one" in joined and "line three" in joined)
print("RESULT:", "PASS" if ok else "FAIL",
      "title_len=%d joined_title_len=%d subject_title_only=%s blame_first=%r ignored_untracked=%s" % (
      res["title_len"], res["joined_len"], res["patch_subject_title_only"], summaries[0], res["ignored_untracked"]))
