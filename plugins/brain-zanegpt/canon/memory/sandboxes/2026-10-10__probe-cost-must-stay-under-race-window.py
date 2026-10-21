# Deterministic virtual-clock model of a stale-read race plus a rAF-style loop. No RNG, no real timing.
WORKER_DONE=40   # worker publishes result at t=40
MAIN_READ=35     # main reads at t=35 -> stale (bug) in free run
def run(probe_cost=0, breakpoint_pause=0):
    t=MAIN_READ+probe_cost+breakpoint_pause   # a probe delays the read by its cost
    return "fresh" if t>=WORKER_DONE else "STALE"
free=run()
print("free run:",free)
bp=run(breakpoint_pause=1000)          # human stops at the read; wall time passes
pr0=run(probe_cost=1)                  # light print
pr_heavy=run(probe_cost=6)             # heavy logging (formatting, IO) shifts the read past 40
print("breakpoint:",bp,"light print:",pr0,"heavy print:",pr_heavy)
# threshold: smallest probe cost that hides the bug
hide=min(c for c in range(0,100) if run(probe_cost=c)=="fresh")
print("smallest hiding probe cost:",hide)
# E36 pattern: loop that reschedules LAST dies on first throw; reschedule-first survives
def loop(reschedule_first, throw_at=5, frames=10):
    logs=[]
    f=0;alive=True
    while alive and f<frames:
        if reschedule_first: nxt=True
        try:
            logs.append(f)               # print probe: one line per frame
            if f==throw_at: raise RuntimeError
            nxt=True
        except RuntimeError:
            nxt=reschedule_first
        alive=nxt; f+=1
    return logs
last=loop(False); first=loop(True)
print("reschedule-last log ends at",last[-1],"; reschedule-first log ends at",first[-1])
# a print probe localizes the death (last log line = throw frame) with zero perturbation of this loop
ok=(free=="STALE" and bp=="fresh" and pr0=="STALE" and pr_heavy=="fresh" and hide==5
    and last[-1]==5 and first[-1]==9)
print(f"RESULT: {'PASS' if ok else 'FAIL'} free run STALE; breakpoint hides the race; light print keeps it but cost>={hide} ticks also hides it; print log pins the loop death at frame 5 (reschedule-last) vs frame 9 (reschedule-first)")
