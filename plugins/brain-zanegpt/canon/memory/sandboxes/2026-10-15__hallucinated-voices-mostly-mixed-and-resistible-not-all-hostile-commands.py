"""Gap (SEVEN's open list: disturbing voice content). Published input:
McCarthy-Jones, Trauer, Mackinnon, Sims, Thomas & Copolov, Schizophrenia
Bulletin 40(1):231-235 (PMC3885292), N = 199 voice hearers (81% schizophrenia):
abusive 61%, derogatory 67%, threatening 63%; helpful 45%, guiding 49%,
affirming 37%; commands 67% (25% never), of whom 76% could resist; second-person
address 73%, third-person 65%; running commentary 55%; voices known or mixed
69%, anonymous 31%; 70% like people who had spoken to them before.
Question for a game's voice layer: what mix and what control rules match these
proportions? Exact arithmetic (Frechet bounds on co-occurrence from marginals;
no joint table was published), no rng.
PREDICTION (written before running): at least 5% (and possibly up to 45%) of
hearers have BOTH abusive and helpful voices, so an all-hostile voice layer
contradicts a large share of reports; hearers who get commands AND can resist
are about 51% of all, while at most about 16% of all hear commands they cannot
resist - so a voice that takes control of the player is the minority case;
second-person address is the commonest form (73%) but third-person commentary
(65%) is nearly as common, so a layer with only 'you' lines misses most of it.
Break case: a design where every voice line is a command that overrides input
- its share of 'commands you cannot resist' (100%) against the reported <= 16%.
"""
import sys
print("python", sys.version.split()[0])
P = dict(abusive=.61, derog=.67, threat=.63, helpful=.45, guiding=.49, affirm=.37, cmd=.67, resist=.76,
         second=.73, third=.65, comment=.55, known=.69)
lo = lambda a, b: max(0.0, a + b - 1); hi = lambda a, b: min(a, b)
both_ab_help = (lo(P["abusive"], P["helpful"]), hi(P["abusive"], P["helpful"]))
both_derog_guide = (lo(P["derog"], P["guiding"]), hi(P["derog"], P["guiding"]))
cmd_resist = P["cmd"] * P["resist"]; cmd_no = P["cmd"] * (1 - P["resist"])
both_forms = (lo(P["second"], P["third"]), hi(P["second"], P["third"]))
only_second_max = P["second"] - both_forms[0]
print(f"abusive AND helpful: {both_ab_help[0]:.2f}..{both_ab_help[1]:.2f}; derogatory AND guiding {both_derog_guide[0]:.2f}..{both_derog_guide[1]:.2f}")
print(f"commands and can resist {cmd_resist:.3f} of all; commands cannot resist {cmd_no:.3f} of all (upper share; 'resist' asked of command hearers)")
print(f"second AND third person address: {both_forms[0]:.2f}..{both_forms[1]:.2f}; second-person only at most {only_second_max:.2f}")
override_design = 1.0
print(f"break: an all-override voice layer makes 'commands you cannot resist' {override_design:.0%} of voice experience vs reported {cmd_no:.0%} of hearers")
c = [both_ab_help[0] >= 0.05, abs(cmd_resist - 0.51) < 0.01, cmd_no <= 0.17, P["second"] > P["third"], only_second_max <= 0.35]
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} {sum(c)}/5; abusive+helpful {both_ab_help[0]:.2f}-{both_ab_help[1]:.2f} of hearers; resistible commands {cmd_resist:.2f}, irresistible {cmd_no:.2f}; both address forms >= {both_forms[0]:.2f}; all-override layer 100% vs {cmd_no:.0%}")
