"""Gap (no Brain lessons on content warnings that don't spoil; SEVEN's open
list). Published input: Bridgland, Jones & Bellet 2023 (Clinical Psychological
Science, 12-study meta-analysis): warnings did not reduce distress after the
content and reliably raised anticipatory anxiety; avoidance effects were mixed.
So a warning's useful job is an informed CHOICE (skip, filter), not emotional
preparation - and the cost to measure is how much it spoils.
Exact information model, no rng. A run of SEVEN-like play has 6 disturbing
content types; each is present in a run with p = 0.5 and, if present, falls on
one of 7 days uniformly (independent). Warning schemes:
 S1 one game-wide list of every type the game CAN contain (same every run)
 S2 a per-run list of the types present this run
 S3 per-day warnings ('tonight contains X')
 S4 S1 plus per-type filters the player can switch off (control, no new info)
Spoil = mutual information between the warning and the run (bits); since each
warning is a function of the run, MI = H(warning).
Break case: a type whose mere EXISTENCE is the design's twist (SEVEN: someone
in your party is not who they say). A game-wide list naming it spoils the
premise even though it carries 0 bits about any run: the player's prior that
the game has an impostor (assumed 0.2) jumps to 1.
PREDICTION (written before running): S1 0 bits; S2 6 bits; S3 14.4 bits = the
whole run's entropy (fully spoils timing); S4 0 bits; break case 2.32 bits of
premise surprise removed by S1, so the twist type needs a neutral umbrella word
(e.g. 'deception', 'paranoia') whose prior is already high.
"""
import math, sys
print("python", sys.version.split()[0])
K, D, P = 6, 7, 0.5
def H(ps): return -sum(p * math.log2(p) for p in ps if p > 0)
h_type_full = H([1 - P] + [P / D] * D)            # presence + day
run_entropy = K * h_type_full
spoil = {"S1": 0.0, "S2": K * H([P, 1 - P]), "S3": K * h_type_full, "S4": 0.0}
for k, v in spoil.items(): print(f"{k}: {v:.2f} bits of {run_entropy:.2f} in a run")
prior = 0.2
premise = math.log2(1 / prior)
umbrella_prior = 0.8   # assumed: a horror game 'contains deception' is expected
premise_umbrella = math.log2(1 / umbrella_prior)
print(f"break: naming the twist type removes {premise:.2f} bits of premise surprise; a neutral umbrella word with prior {umbrella_prior} removes {premise_umbrella:.2f}")
c = [spoil["S1"] == 0, abs(spoil["S2"] - 6) < 1e-9, abs(spoil["S3"] - 14.4) < 0.05, spoil["S3"] == run_entropy, spoil["S4"] == 0, abs(premise - 2.32) < 0.01]
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} S1 0, S2 {spoil['S2']:.1f}, S3 {spoil['S3']:.2f} (= run entropy {run_entropy:.2f}), S4 0 bits; twist named game-wide removes {premise:.2f} bits of premise surprise, umbrella word {premise_umbrella:.2f}")
