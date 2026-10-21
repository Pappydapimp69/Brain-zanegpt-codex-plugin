"""Sandbox T2: do trending songs tie a sound named in the lyrics to the Style field more than controls do?

Kernel under test: a-sound-named-in-the-lyric-is-written-into-the-style-as-a-returning-motif (filed
2026-10-01 from the owner's "Please remain on the line"). Data: data/suno.sqlite (English Now/Weekly
board songs vs same-creator non-trending controls, age <= 10 days, contest/verified excluded, Latin lyrics).
A song is "coherent" if any sound word appearing in its lyric text (not brackets) also appears in its tags.
Deterministic given the database snapshot; stdlib only.

PREDICTION (written before the first run):
  P1 |board share - control share| < 10 points (lyric/style craft traits do not separate board songs, as in suno E18)
  P2 fewer than 25% of board songs show any lyric-to-style sound tie
  P3 break: among songs that DO name a sound in the lyric, board songs tie it to Style at least
     15 points more often than controls (would contradict P1 on the subset that matters)
"""
import json
import os
import re
import sqlite3
from datetime import datetime

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "data", "suno.sqlite")
SOUNDS = ["piano", "guitar", "drum", "drums", "bass", "violin", "strings", "bell", "bells", "chime", "horn", "trumpet",
          "sax", "saxophone", "organ", "flute", "harp", "synth", "808", "choir", "whistle", "clap", "claps", "snare",
          "banjo", "fiddle", "accordion", "ukulele", "cello", "radio", "siren", "rain", "thunder", "bird", "birds",
          "heartbeat", "music box", "music", "hum", "humming", "static", "vinyl", "record", "bassline", "beat"]
TAG_RE = re.compile(r"\[[^\]]*\]")


def lyric_text(lyr):
    return " ".join(l for l in TAG_RE.sub(" ", lyr or "").lower().split("\n"))


def has(word, text):
    return re.search(r"\b" + re.escape(word) + r"\b", text) is not None


con = sqlite3.connect(DB)
last = con.execute("SELECT MAX(run_ts) FROM runs").fetchone()[0]
lt = datetime.fromisoformat(last.replace("Z", "+00:00"))


def load(where):
    out = {}
    for sid, created, handle, title, contest, verified, tags, lyr in con.execute(
            "SELECT song_id, created, handle, title, contest, verified, tags, lyrics FROM songs WHERE " + where):
        try:
            age = (lt - datetime.fromisoformat(created.replace("Z", "+00:00"))).days
        except Exception:
            continue
        if age > 10 or contest or verified or not re.fullmatch(r"[\x00-\x7F’‘“”—–…\s]*", (lyr or "")[:600]):
            continue
        key = (handle, " ".join((title or "").lower().split()[:3]))
        if key in out:
            continue
        lt_ = lyric_text(lyr)
        tg = (tags or "").lower()
        named = [w for w in SOUNDS if has(w, lt_)]
        tied = [w for w in named if has(w, tg)]
        out[key] = (bool(named), bool(tied))
    return list(out.values())


board = load("song_id IN (SELECT song_id FROM snapshots WHERE board IN ('English/Now','English/Weekly'))")
ctrl = load("first_board='control' AND song_id NOT IN (SELECT song_id FROM snapshots WHERE board!='control')")
share = lambda rows: sum(t for _, t in rows) / len(rows)
sub = lambda rows: [r for r in rows if r[0]]
sb, sc = share(board), share(ctrl)
nb, nc = sub(board), sub(ctrl)
ssb, ssc = share(nb) if nb else 0, share(nc) if nc else 0
res = [("P1 |diff| < 10 pts", abs(sb - sc) < 0.10, f"board {sb:.0%} (n {len(board)}) vs control {sc:.0%} (n {len(ctrl)})"),
       ("P2 board tie share < 25%", sb < 0.25, f"{sb:.0%}"),
       ("P3 break: subset gap >= 15 pts", ssb - ssc >= 0.15, f"names-a-sound subset: board {ssb:.0%} (n {len(nb)}) vs control {ssc:.0%} (n {len(nc)})")]
for n, ok, d in res:
    print(f"{n}: {'PASS' if ok else 'FAIL'}  {d}")
k = sum(ok for _, ok, _ in res)
print(("RESULT: PASS " if k == 3 else "RESULT: FAIL ") + f"{k}/3; tie share board {sb:.0%} vs control {sc:.0%}; "
      f"subset naming a sound: board {ssb:.0%} (n {len(nb)}) vs control {ssc:.0%} (n {len(nc)})")
