"""Sandbox: 28 days of promoting one free browser game across 3 communities with different rules.
Kernels exercised: DISTRIBUTION reddit-containment (dedicated threads vs standalone posts),
DISTRIBUTION itch-devlog-cadence (batch, dont drip, give first), DISTRIBUTION where-to-post-a-free-browser-game
(communities differ in rules/size). Rules are inputs (assumed); the sandbox tests the composed accounting.
 A thread-only (size 50k): standalone promo removed; promo allowed only inside the weekly feedback thread
 B ratio  (size 200k): promo removed unless promos <= 10 pct of your own contributions so far
 C open   (size 20k): anything allowed, but a promo within 3 days of the previous one is removed as spam
 2 removals in a community = ban for the rest of the run."""
DAYS = 28
COMM = {"A": 50, "B": 200, "C": 20}
def run(strategy):
    st = {c: dict(promos=0, other=0, removed=0, banned=False, last=-99, survived=0) for c in COMM}
    for day in range(DAYS):
        for c, s in st.items():
            if s["banned"]: continue
            if strategy["give_first"] and day % 1 == 0:
                s["other"] += strategy["helpful_per_day"]
            if strategy["cadence"] == "drip":
                promo, kind = True, "standalone"
            elif strategy["cadence"] == "batch":
                promo, kind = day % 7 == 6, ("thread" if strategy["use_threads"] else "standalone")
            if not promo: continue
            if c == "A": ok = kind == "thread"
            elif c == "B": ok = (s["promos"] + 1) <= 0.10 * (s["other"] + s["promos"] + 1)
            else: ok = day - s["last"] >= 3
            s["promos"] += 1; s["last"] = day
            if ok: s["survived"] += 1
            else:
                s["removed"] += 1
                if s["removed"] >= 2: s["banned"] = True
    reach = sum(s["survived"] * COMM[c] for c, s in st.items())
    return st, reach
STRATS = {
 "drip, no give-first": dict(cadence="drip", give_first=False, use_threads=False, helpful_per_day=0),
 "batch weekly + give-first + threads": dict(cadence="batch", give_first=True, use_threads=True, helpful_per_day=3),
 "batch weekly + give-first, standalone in A (BREAK)": dict(cadence="batch", give_first=True, use_threads=False, helpful_per_day=3),
 "batch weekly, no give-first, threads": dict(cadence="batch", give_first=False, use_threads=True, helpful_per_day=0),
}
res = {}
for name, s in STRATS.items():
    st, reach = run(s); res[name] = (st, reach)
    print("%-52s reach %5dk | %s" % (name, reach, {c: (v["survived"], v["removed"], "BAN" if v["banned"] else "") for c, v in st.items()}))
d, b, brk, nogf = (res[k] for k in STRATS)
ok = (b[1] > d[1] and b[1] > brk[1] and b[1] > nogf[1]
      and all(not v["banned"] for v in b[0].values())
      and d[0]["A"]["banned"] and d[0]["B"]["banned"]
      and brk[0]["A"]["survived"] == 0 and brk[0]["A"]["banned"]
      and nogf[0]["B"]["survived"] == 0)
print("RESULT: %s weekly batch + give-first + dedicated thread reached %dk with no bans versus %dk and bans in A and B for daily dripping; standalone posts in the thread-only community die even with give-first (%dk), and batching without give-first loses community B entirely (%dk)" % ("PASS" if ok else "FAIL", b[1], d[1], brk[1], nogf[1]))
