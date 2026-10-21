"""Loop 5 sandbox: what share of SEVEN's hallucination episodes are AUDITORY,
computed from its own code (src/state.js pickHallucinationKind, seven-0.34),
against the share in real psychosis (filled from the research digest).
Kinds: PHANTOM_MARKER (visual object), DOUBLED_PARTY (visual person / presence),
FALSE_ANCHOR (visual/instrument), WRONG_WAY (misperception of a real instrument),
CHORUS (voices). Player: flat 1/5 each. Companion: weights 1 + 2*trait
(wander, wander, chatty, selfCare, flat 1), traits from the five templates;
selfCare is uniform 0..1 (integrated on a 101-point grid); the +/-0.15 trait
jitter is symmetric and ignored (weights are linear, so it only nudges ratios).
Exact arithmetic, no RNG.
Then: a REWEIGHTED mix that keeps every kind reachable (each >= 0.05) but makes
voices the majority, and how many distinct visual episodes a 20-episode run
would then contain (scarcer visuals, per seven E56, wear out slower).
"""
TEMPLATES = {
    "VOSS": (0.4, 0.5), "IREN": (0.8, 0.35), "HALDER": (0.5, 0.8),
    "NKEM": (1.0, 0.4), "PAO": (0.6, 0.95),
}  # (chatty, wander)


def companion_chorus_share(chatty, wander):
    acc = 0.0
    pts = [i / 100 for i in range(101)]
    for sc in pts:
        w = {"marker": 1 + 2 * wander, "wrong": 1 + 2 * wander, "chorus": 1 + 2 * chatty,
             "anchor": 1 + 2 * sc, "doubled": 1}
        acc += w["chorus"] / sum(w.values())
    return acc / len(pts)


def main(real_aud):
    player = 1 / 5
    comp = {n: companion_chorus_share(c, w) for n, (c, w) in TEMPLATES.items()}
    mean_comp = sum(comp.values()) / len(comp)
    for n, v in comp.items():
        print(f"{n:6s}: voices share {v:.3f}")
    print(f"player {player:.3f}; companion mean {mean_comp:.3f}; real psychosis auditory ~{real_aud:.2f}")
    # reweight: voices take real_aud, others share the rest equally, floor 0.05
    rest = (1 - real_aud) / 4
    new = {"chorus": real_aud, "marker": rest, "wrong": rest, "anchor": rest, "doubled": rest}
    visual_now = 3 / 5 * 20
    visual_new = (new["marker"] + new["anchor"] + new["doubled"]) * 20
    print(f"reweighted mix: voices {new['chorus']:.2f}, each other kind {rest:.3f}; visual episodes per 20: "
          f"{visual_now:.1f} -> {visual_new:.1f}")
    checks = [
        (f"SEVEN's player mix is under half the real auditory share ({player:.2f} vs {real_aud:.2f})", player < real_aud / 2),
        (f"even the chattiest companion (NKEM) stays below the real share ({comp['NKEM']:.3f})", comp["NKEM"] < real_aud),
        ("the reweighted mix keeps every kind reachable (each >= 0.05)", min(new.values()) >= 0.05),
        ("break case: reweighting cuts visual episodes per 20 by at least half", visual_new <= visual_now / 2 + 1e-9),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; player voices {player:.2f}, "
          f"companion mean {mean_comp:.3f}, NKEM {comp['NKEM']:.3f}, real ~{real_aud:.2f}; visuals per 20 "
          f"{visual_now:.1f} -> {visual_new:.1f}")


if __name__ == "__main__":
    import sys
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 0.55)
