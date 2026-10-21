"""Prediction (before run): toy generational collector, young-gen size Y swept 64..131072 objects.
Workload A (weak generational hypothesis holds): 1 in 20 objects is long-lived, rest die within 20 allocations.
 -> throughput rises with Y and flattens, max pause rises about linearly with Y, footprint rises, promptness (mean dead-to-
 reclaimed delay) worsens ~Y/2: no single Y wins all four. Workload B (hypothesis broken: every object long-lived): bigger Y
 buys NO throughput (gc cost per allocation stays constant) yet still costs pause/footprint.
 RAM cliff: when young gen exceeds the RAM headroom, touches hit SSD latency (150 us vs 100 ns, 1500x) so throughput collapses:
 I predict the best-throughput Y in workload A is the largest size that still fits RAM, not the largest swept size.
Deterministic, no RNG, costs in model nanoseconds (assumed constants, not measured)."""
ALLOC_NS = 100.0        # mutator cost per allocation (one RAM reference, latency-numbers kernel)
COPY_NS = 200.0         # copy one survivor
FIXED_NS = 50_000.0     # fixed per-collection overhead (stop, root scan)
SSD_NS, RAM_NS = 150_000.0, 100.0
RAM_HEADROOM = 16384    # objects of young gen that fit in RAM; beyond it, touches page
N = 2_000_000
def run(Y, long_every, life=20):
    pause_max = 0.0; gc_ns = 0.0; mut_ns = 0.0; promoted = 0; delay_sum = 0.0; dead = 0
    n = 0
    while n < N:
        batch = min(Y, N - n)
        # live survivors at collection: long-lived objects plus the last `life` short ones still alive
        long_cnt = (batch + long_every - 1) // long_every if long_every > 1 else batch
        recent = 0 if long_every == 1 else min(batch, life)
        live = long_cnt + recent
        pause = FIXED_NS + COPY_NS * live
        pause_max = max(pause_max, pause); gc_ns += pause; promoted += long_cnt
        resident = min(batch, RAM_HEADROOM); paged = batch - resident
        mut_ns += ALLOC_NS * batch; gc_ns += SSD_NS * paged   # useful work is the allocs; each paged touch is SSD-latency overhead
        # promptness: a short object that dies after `life` waits until collection: avg wait ~ (batch - life)/2
        shorts = batch - long_cnt
        delay_sum += shorts * max(0, (batch - life) / 2); dead += shorts
        n += batch
    thr = mut_ns / (mut_ns + gc_ns)
    return dict(Y=Y, thr=thr, pause=pause_max / 1000, foot=Y + promoted, prompt=(delay_sum / dead) if dead else 0.0)
SIZES = [64, 256, 1024, 4096, 16384, 32768, 131072]
A = [run(Y, 20) for Y in SIZES]; B = [run(Y, 1) for Y in SIZES]
for name, rows in (("A weak-gen", A), ("B all-long", B)):
    for r in rows: print(name, "Y=%-6d thr=%.4f maxpause=%9.1fus footprint=%8d promptness=%9.1f" % (r["Y"], r["thr"], r["pause"], r["foot"], r["prompt"]))
bestA = max(A, key=lambda r: r["thr"])["Y"]
inRam = [r for r in A if r["Y"] <= RAM_HEADROOM]
thrB = [r["thr"] for r in B if r["Y"] <= RAM_HEADROOM]
ok = (bestA == RAM_HEADROOM
      and all(inRam[i]["thr"] < inRam[i + 1]["thr"] for i in range(len(inRam) - 1))
      and all(inRam[i]["pause"] < inRam[i + 1]["pause"] for i in range(len(inRam) - 1))
      and all(inRam[i]["prompt"] < inRam[i + 1]["prompt"] for i in range(len(inRam) - 1))
      and B[4]["thr"] - B[3]["thr"] < 0.02 and B[4]["thr"] < 0.4
      and A[-1]["thr"] < 0.2 * A[4]["thr"])
print("RESULT: %s best-throughput Y=%d (RAM headroom %d); A thr %.3f->%.3f in RAM, collapses to %.3f at Y=131072; B thr 4096->16384 gain %.4f; pause %.0f->%.0f us" %
      ("PASS" if ok else "FAIL", bestA, RAM_HEADROOM, inRam[0]["thr"], inRam[-1]["thr"], A[-1]["thr"], B[4]["thr"] - B[3]["thr"], inRam[0]["pause"], inRam[-1]["pause"]))
