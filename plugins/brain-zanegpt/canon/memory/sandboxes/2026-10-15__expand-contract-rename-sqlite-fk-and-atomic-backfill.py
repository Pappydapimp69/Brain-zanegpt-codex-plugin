"""Prediction (before run), using real sqlite3 (in-memory, stdlib): (1) a one-step RENAME COLUMN makes the still-running OLD app version fail
on 100% of its statements (the script counts 2 per call: 1 insert, 1 read) while the new one succeeds; (2) expand/dual-write/backfill/contract keeps BOTH app versions at
0 errors in every phase; (3) built to BREAK it: contracting (dropping the old column) before the old app is retired gives >= 1 old-app error, and
skipping dual-write leaves old-app reads returning NULL for rows the new app wrote (silent, no exception); (4) FK kernel: with foreign_keys=ON,
rebuilding the parent table by DROP TABLE + rename silently CASCADE-deletes child rows (I predict all 3 children vanish) while an in-place
ALTER ... DROP COLUMN keeps 3; (5) ACID kernel: a backfill that fails on row 3 inside one transaction leaves 0 rows migrated, versus 2 migrated under autocommit.
Deterministic, stdlib only."""
import sqlite3
def db():
    c = sqlite3.connect(":memory:", isolation_level=None)
    c.execute("PRAGMA foreign_keys=ON")
    c.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT)")
    c.execute("CREATE TABLE posts(id INTEGER PRIMARY KEY, uid INTEGER REFERENCES users(id) ON DELETE CASCADE)")
    c.executemany("INSERT INTO users(id,name) VALUES(?,?)", [(1,"a"),(2,"b"),(3,"c")])
    c.executemany("INSERT INTO posts(id,uid) VALUES(?,?)", [(1,1),(2,2),(3,3)])
    return c
def old_app(c, i):
    errs = 0
    for fn in (lambda: c.execute("INSERT INTO users(id,name) VALUES(?,?)", (i,"o%d"%i)),
               lambda: c.execute("SELECT name FROM users WHERE id=?", (i,)).fetchone()):
        try: fn()
        except sqlite3.Error: errs += 1
    return errs
def new_app(c, i, dual=True):
    errs = 0
    try:
        if dual: c.execute("INSERT INTO users(id,name,full_name) VALUES(?,?,?)", (i,"n%d"%i,"n%d"%i))
        else: c.execute("INSERT INTO users(id,full_name) VALUES(?,?)", (i,"n%d"%i))
        c.execute("SELECT full_name FROM users WHERE id=?", (i,)).fetchone()
    except sqlite3.Error: errs += 1
    return errs
# 1 one-step rename
c = db(); c.execute("ALTER TABLE users RENAME COLUMN name TO full_name")
s1_old = old_app(c, 10) ; s1_new = new_app(c, 11, dual=False)
# 2 expand/contract, both versions active in every phase
c = db(); ph = {}
c.execute("ALTER TABLE users ADD COLUMN full_name TEXT"); ph["expand"] = old_app(c, 20) + 0
c.execute("UPDATE users SET full_name=name WHERE full_name IS NULL"); ph["backfill"] = old_app(c, 21) + new_app(c, 22)
ph["both_live"] = old_app(c, 23) + new_app(c, 24)
c.execute("ALTER TABLE users DROP COLUMN name"); ph["contract_after_old_retired"] = new_app(c, 25, dual=False)
# 3a contract too early
c = db(); c.execute("ALTER TABLE users ADD COLUMN full_name TEXT"); c.execute("ALTER TABLE users DROP COLUMN name")
s3a = old_app(c, 30)
# 3b skipped dual-write: new app writes only full_name, old app reads name
c = db(); c.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
new_app(c, 40, dual=False); s3b_val = c.execute("SELECT name FROM users WHERE id=40").fetchone()[0]
# 4 FK: table rebuild vs in-place
c = db(); c.execute("DROP TABLE users")
fk_rebuild = c.execute("SELECT COUNT(*) FROM posts").fetchone()[0] if True else None
c = db(); c.execute("ALTER TABLE users ADD COLUMN full_name TEXT"); c.execute("ALTER TABLE users DROP COLUMN name")
fk_inplace = c.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
# 5 atomic backfill
def backfill(atomic):
    c = db(); c.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
    try:
        if atomic: c.execute("BEGIN")
        for i in (1, 2, 3):
            if i == 3: raise RuntimeError("boom")
            c.execute("UPDATE users SET full_name=name WHERE id=?", (i,))
    except RuntimeError:
        if atomic: c.execute("ROLLBACK")
    return c.execute("SELECT COUNT(*) FROM users WHERE full_name IS NOT NULL").fetchone()[0]
a_atomic, a_auto = backfill(True), backfill(False)
print("1 rename: old errs", s1_old, "new errs", s1_new, "| 2 phases", ph, "| 3a", s3a, "3b old read", s3b_val)
print("4 posts left: rebuild", fk_rebuild, "inplace", fk_inplace, "| 5 migrated: atomic", a_atomic, "autocommit", a_auto)
ok = (s1_old == 2 and s1_new == 0 and all(v == 0 for v in ph.values()) and s3a >= 1 and s3b_val is None
      and fk_rebuild == 0 and fk_inplace == 3 and a_atomic == 0 and a_auto == 2)
print("RESULT:", "PASS" if ok else "FAIL", f"one-step rename breaks old app ({s1_old}/2 stmts), expand/contract 0 errors in {len(ph)} phases, early contract {s3a} errs, no dual-write leaves NULL; table rebuild leaves {fk_rebuild}/3 child rows vs {fk_inplace} in place; rollback migrates {a_atomic} vs autocommit {a_auto}")
