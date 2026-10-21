# Beats ramp in severity 1..5. A beat is funny (value = severity) only if severity <= framing distance d
# (benign violation); a beat above d is harm and scores -2. Compare three writers over d=1..5.
def sketch(sched, d): return sum(s if s<=d else -2 for s in sched)
GOBIG=[1,2,3,4,5,5]; MILD=[1,1,2,2,2,2]
def card(d, stated=None):
    c = d if stated is None else stated        # card states a harm ceiling
    return [min(s,c) for s in GOBIG]
rows=[]; wins=0
for d in range(1,6):
    g,m,c=sketch(GOBIG,d),sketch(MILD,d),sketch(card(d),d)
    rows.append((d,g,m,c)); print(f"d={d} gobig={g} mild={m} card={c}")
    wins += c>=max(g,m)
over=[sketch(card(d,min(5,d+2)),d) for d in range(1,6)]   # BREAK: ceiling misstated 2 too high
under=[sketch(card(d,max(1,d-1)),d) for d in range(1,6)]
exact=[r[3] for r in rows]
print("misstated +2:",over,"understated -1:",under,"exact:",exact)
ok = wins==5 and sum(over)<sum(exact) and sum(under)<sum(exact) and rows[4][3]==rows[4][1] and rows[0][3]>rows[0][1]
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" card>=best at {wins}/5 distances; exact sum {sum(exact)} vs +2 misstated {sum(over)} vs -1 understated {sum(under)}")
