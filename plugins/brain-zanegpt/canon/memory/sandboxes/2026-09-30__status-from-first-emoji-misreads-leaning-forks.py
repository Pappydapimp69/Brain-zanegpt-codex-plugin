"""Sandbox: reading a ledger entry's status as the first status mark ANYWHERE
in the block (checked in 🔴🟡🟢⚪ order) vs the first mark on its `Lean:` line.
Deterministic; stdlib only. Mirrors Brain's entry_status before/after fix."""
import re
MARKS = ("🔴", "🟡", "🟢", "⚪")

def old(b):
    return next((m for m in MARKS if m in b), "")

def new(b):
    for line in b.splitlines():
        if re.match(r"\s*Lean\s*:", line):
            hits = [(line.find(m), m) for m in MARKS if m in line]
            if hits:
                return min(hits)[1]
            break
    return old(b)

cases = [
    ("1 leaning, history mentions a transition", "🟡",
     "### T1 · x\nLean: 🟡 leaning — act.\nUpdates:\n- moved 🔴→🟡 after review\n"),
    ("2 resolved, original lean kept for the record", "🟢",
     "### T2 · x\nLean: 🟢 resolved (evidence). Original lean: 🔴 open — deferred.\n"),
    ("3 BREAK: no Lean line, status in heading", "🟡",
     "### 🟡 leaning · tradeoff · y\nBody mentions a past 🔴 state.\n"),
    ("4 plain open", "🔴", "### T4 · x\nLean: 🔴 open\n"),
]
bad_old = bad_new = 0
for name, want, block in cases:
    o, n = old(block), new(block)
    bad_old += o != want
    bad_new += n != want
    print(f"{name:48} want {want} old {o} new {n}")
print(f"RESULT: {'PASS' if bad_new == 0 and bad_old == 2 else 'FAIL'} "
      f"old misreads {bad_old}/4, new misreads {bad_new}/4")
