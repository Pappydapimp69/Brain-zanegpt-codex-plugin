# Does the Stonewake cinematic cut (film20, 26 s) follow measured trailer pacing?
# Reference: Redfern US Horror Trailers SL data (Zenodo 4479068, 50 trailers, 6762 shots), re-run this session:
# mean ASL 1.09 s, median cuts/min 61.1, median shot length by third 0.96 / 0.79 / 0.54, by tenth ... 0.42 (9th) then 0.77 (10th).
import statistics as st
REF_ASL, REF_CPM, REF_THIRDS = 1.09, 61.1, (0.96, 0.79, 0.54)
# film20 shot list from render(t) dispatch: (start, end, name)
SHOTS = [(0, 3.6, 'establish'), (3.6, 6.2, 'eye'), (6.2, 7.6, 'card1'), (7.6, 8.8, 'forest'), (8.8, 10.0, 'cave'),
         (10.0, 11.2, 'desert'), (11.2, 12.6, 'battle'), (12.6, 14.0, 'card2'), (14.0, 17.6, 'titan stands'),
         (17.6, 19.6, 'hero'), (19.6, 20.4, 'silence'), (20.4, 21.2, 'strike'), (21.2, 26.0, 'logo+button')]
T = SHOTS[-1][1]; L = [round(b - a, 2) for a, b, _ in SHOTS]
asl = T / len(L); cpm = len(L) / T * 60
thirds = [[], [], []]
for (a, b, n), d in zip(SHOTS, L): thirds[min(2, int((a + b) / 2 / T * 3))].append(d)
med = [st.median(t) for t in thirds]
print(f"1) ASL {asl:.2f}s vs ref {REF_ASL}; cuts/min {cpm:.0f} vs ref {REF_CPM}")
print(f"2) median shot by third: {med[0]:.2f} / {med[1]:.2f} / {med[2]:.2f}  (ref {REF_THIRDS})  third shots: {thirds}")
body = [(n, d) for (a, b, n), d in zip(SHOTS, L) if n != 'logo+button']
longest = max(body[2:], key=lambda x: x[1])   # after the opening: the longest hold in the body of the cut
lpos = next((a + b) / 2 / T for a, b, n in SHOTS if n == longest[0])
print(f"3) longest shot after the opening: {longest[0]} {longest[1]:.1f}s at {lpos:.0%} of the runtime (ref: shots shortest at 80-90%)")
# 4) does the shortening ratio first->last third match? ref 0.54/0.96 = 0.56
ratio = med[2] / med[0]; print(f"4) last/first third ratio {ratio:.2f} vs ref {REF_THIRDS[2]/REF_THIRDS[0]:.2f}")
hook = next(a for a, b, n in SHOTS if n == 'eye')   # the eye opening is the hook ("it was never a mountain")
print(f"5) hook (eye opens) lands at {hook}s vs the 3 s thumbstop window")
res = [asl > 1.7 * REF_ASL, med[2] >= med[1], 0.5 < lpos < 0.75, ratio > REF_THIRDS[2] / REF_THIRDS[0], hook > 3]
print(("RESULT: PASS" if all(res) else "RESULT: FAIL") + f" film20 ASL {asl:.1f}s ({asl/REF_ASL:.1f}x ref), {cpm:.0f} cuts/min vs {REF_CPM:.0f}; thirds {med[0]:.1f}/{med[1]:.1f}/{med[2]:.1f} flat into the climax (ref falls .79->.54); longest body shot '{longest[0]}' {longest[1]}s at {lpos:.0%}; hook at {hook}s > 3 s")
