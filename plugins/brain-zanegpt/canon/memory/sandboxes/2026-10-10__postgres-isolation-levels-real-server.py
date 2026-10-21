"""Real PostgreSQL 16 (scratch initdb, unix socket) driven by interleaved psql sessions. Deterministic, stdlib only.
Prediction (before first run): default level is read committed. On-call write skew (two doctors, each checks
count>=2 then goes off call): READ COMMITTED -> 0 on call; REPEATABLE READ -> 0 on call (kernel table: serialization
anomaly still possible); SERIALIZABLE -> second commit fails with SQLSTATE 40001, 1 on call. Non-repeatable read:
RC re-read differs, RR same. BREAK scenarios: SELECT FOR UPDATE on the checked rows keeps >=1 on call even at READ
COMMITTED (fix without raising the level); OFFSET paging with one statement per page under RC skips a row when another
session deletes a row before the cursor (memory august-10/E29), while one REPEATABLE READ transaction does not."""
import os, subprocess, tempfile, threading, queue, shutil, time, sys

PGBIN = [d for d in (f"/usr/lib/postgresql/{v}/bin" for v in ("16", "15", "17", "14")) if os.path.isdir(d)][0]
D = tempfile.mkdtemp(prefix="pgsb"); os.chmod(D, 0o755); shutil.chown(D, "postgres")
DATA = os.path.join(D, "data"); PORT = "54329"
def as_pg(*a, **k): return subprocess.run(["runuser", "-u", "postgres", "--", *a], capture_output=True, text=True, **k)
as_pg(f"{PGBIN}/initdb", "-D", DATA, "-A", "trust", "-U", "postgres")
as_pg(f"{PGBIN}/pg_ctl", "-D", DATA, "-o", f"-p {PORT} -k {D} -c listen_addresses=''", "-l", os.path.join(D, "log"), "-w", "start")

class S:
    def __init__(self, name):
        self.n = 0; self.q = queue.Queue(); self.name = name
        self.p = subprocess.Popen([f"{PGBIN}/psql", "-X", "-q", "-t", "-A", "-h", D, "-p", PORT, "-U", "postgres", "-d", "postgres"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        threading.Thread(target=self._rd, daemon=True).start()
    def _rd(self):
        for line in self.p.stdout: self.q.put(line.rstrip("\n"))
    def send(self, sql):
        self.n += 1; self.mark = f"__DONE{self.n}__"
        self.p.stdin.write(sql.strip() + f"\n\\echo {self.mark}\n"); self.p.stdin.flush()
    def wait(self, timeout=8):
        out = []; end = time.time() + timeout
        while time.time() < end:
            try: l = self.q.get(timeout=0.2)
            except queue.Empty: continue
            if l == self.mark: return out
            out.append(l)
        return out + ["__TIMEOUT__"]
    def run(self, sql): self.send(sql); return self.wait()
    def close(self): self.p.stdin.close(); self.p.wait(timeout=5)

def fresh(a):
    a.run("DROP TABLE IF EXISTS oncall; CREATE TABLE oncall(doc text primary key, on_call boolean); "
          "INSERT INTO oncall VALUES ('alice',true),('bob',true);")

def skew(level, lock=False):
    a, b, c = S("a"), S("b"), S("c"); fresh(c)
    sel = "SELECT doc FROM oncall WHERE on_call FOR UPDATE;" if lock else "SELECT count(*) FROM oncall WHERE on_call;"
    a.run(f"BEGIN ISOLATION LEVEL {level};"); b.run(f"BEGIN ISOLATION LEVEL {level};")
    ra = a.run(sel); ra = [str(len(ra))] if lock else ra; b.send(sel)                       # with FOR UPDATE b blocks here until a finishes
    time.sleep(0.4); blocked = (not lock) and False
    a.run("UPDATE oncall SET on_call=false WHERE doc='alice';"); ea = a.run("COMMIT;")
    rb = b.wait()                                      # b's count (for lock case: after a commits)
    cnt_b = str(len([x for x in rb if x in ("alice", "bob")])) if lock else (rb[0] if rb and rb[0].strip().isdigit() else "?")
    ub = b.run("UPDATE oncall SET on_call=false WHERE doc='bob';") if (cnt_b.isdigit() and int(cnt_b) >= 2) else ["(b saw <2, skipped)"]
    eb = b.run("COMMIT;")
    final = c.run("SELECT count(*) FROM oncall WHERE on_call;")[0]
    err = " ".join(x for x in ub + eb if "ERROR" in x)
    for s in (a, b, c): s.close()
    return dict(final=int(final), a_saw=ra[0], b_saw=cnt_b, err=err)

def nonrep(level):
    a, b = S("a"), S("b"); fresh(b)
    a.run(f"BEGIN ISOLATION LEVEL {level};"); r1 = a.run("SELECT on_call FROM oncall WHERE doc='alice';")[0]
    b.run("UPDATE oncall SET on_call=false WHERE doc='alice';"); r2 = a.run("SELECT on_call FROM oncall WHERE doc='alice';")[0]
    a.run("COMMIT;"); a.close(); b.close(); return r1, r2

def paging(level_single_txn):
    a, b = S("a"), S("b")
    b.run("DROP TABLE IF EXISTS items; CREATE TABLE items(id int primary key); INSERT INTO items SELECT generate_series(1,20);")
    seen = []
    if level_single_txn: a.run("BEGIN ISOLATION LEVEL REPEATABLE READ;")
    seen += a.run("SELECT id FROM items ORDER BY id LIMIT 5 OFFSET 0;")
    b.run("DELETE FROM items WHERE id=2;")               # a row before the cursor goes away between pages
    seen += a.run("SELECT id FROM items ORDER BY id LIMIT 5 OFFSET 5;")
    if level_single_txn: a.run("COMMIT;")
    keyset = []
    a2 = a.run("SELECT id FROM items WHERE id > 5 ORDER BY id LIMIT 5;")
    a.close(); b.close()
    ids = [int(x) for x in seen]; missing = sorted(set(range(1, 11)) - {2} - set(ids))
    return ids, missing

try:
    d = S("d"); default = d.run("SHOW default_transaction_isolation;")[0]; d.close()
    rc, rr, ser, lk = skew("READ COMMITTED"), skew("REPEATABLE READ"), skew("SERIALIZABLE"), skew("READ COMMITTED", lock=True)
    n_rc, n_rr = nonrep("READ COMMITTED"), nonrep("REPEATABLE READ")
    p_rc, p_rr = paging(False), paging(True)
    for k, v in dict(default=default, skew_rc=rc, skew_rr=rr, skew_ser=ser, skew_rc_forupdate=lk, nonrep_rc=n_rc, nonrep_rr=n_rr, page_rc=p_rc, page_rr=p_rr).items(): print(k, v)
    ok = (lk["b_saw"] == "1" and default == "read committed" and rc["final"] == 0 and rr["final"] == 0 and ser["final"] == 1 and "could not serialize" in ser["err"] and lk["final"] >= 1 and n_rc[0] != n_rc[1] and n_rr[0] == n_rr[1]
          and p_rc[1] != [] and p_rr[1] == [])
    print("RESULT:", "PASS" if ok else "FAIL", f"default={default}; on-call left RC={rc['final']} RR={rr['final']} SER={ser['final']} RC+FOR UPDATE={lk['final']}; "
          f"nonrepeatable RC={n_rc} RR={n_rr}; offset-page rows missed RC={p_rc[1]} RR-txn={p_rr[1]}")
finally:
    as_pg(f"{PGBIN}/pg_ctl", "-D", DATA, "-m", "immediate", "stop"); shutil.rmtree(D, ignore_errors=True)
