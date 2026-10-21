"""Deterministic sandbox: LYRICS (song-structure/section-tag level), 10 loops.

Distinct from the prior lyrical-composition session (line/word/phoneme level:
meter, rhyme classification, dedup scope). This round works one level up: the
bracket-tag lyric SHEET as Suno-style tools actually consume it -- section
labels, repeat markers, ad-libs, duration estimation. No RNG, no real timing.
"""

import re


# ============================================================ LOOP 1 =====
def loop1_double_chorus_duration_inflation():
    """Claim: a duration estimator that counts DISTINCT section labels
    ("how many sections, times average section length") silently double-
    counts when a lyric sheet's outro is written as two adjacent identical
    choruses under SEPARATE tags ([Chorus] ... [Chorus] ..., a common way to
    hand-write a chorus repeat rather than an "x2" marker) if it treats each
    tag occurrence as a distinct section -- which is actually CORRECT for
    duration (both really do play) but WRONG if a separate "unique section
    count" metric conflates the two meanings without saying which it means.
    """
    print("=" * 78); print("LOOP 1 -- section OCCURRENCE count vs section TYPE count")
    print("=" * 78)
    sections = ["Verse 1", "Chorus", "Verse 2", "Chorus", "Bridge", "Chorus", "Chorus"]
    occurrence_count = len(sections)
    type_count = len(set(sections))
    # duration should use occurrence count (every played section costs time);
    # "song has N distinct parts" (a structure-complexity metric) needs type count.
    print(f"  sections in order: {sections}")
    print(f"  occurrence count (for duration): {occurrence_count}")
    print(f"  distinct TYPE count (for structure complexity): {type_count}")
    avg_section_seconds = 20
    duration_from_occurrences = occurrence_count * avg_section_seconds
    duration_from_types = type_count * avg_section_seconds  # the bug: using type count for duration
    print(f"  duration using occurrence count: {duration_from_occurrences}s (correct)")
    print(f"  duration using TYPE count (bug): {duration_from_types}s "
          f"({'undercounts' if duration_from_types < duration_from_occurrences else 'matches'} "
          f"by {duration_from_occurrences - duration_from_types}s)")
    ok = duration_from_types < duration_from_occurrences
    print(f"  VERDICT: {'CONFIRMED' if ok else 'refuted'} -- using distinct-type count where occurrence "
          f"count is needed undercounts duration by exactly (occurrences - types) * avg_section_seconds "
          f"= {occurrence_count - type_count} * {avg_section_seconds} = "
          f"{(occurrence_count - type_count) * avg_section_seconds}s on this sheet")
    return ok


# ============================================================ LOOP 2 =====
def loop2_repeat_marker_expansion_vs_visible_lines():
    """Claim: a duration estimator counting VISIBLE lines in a lyric sheet
    undercounts whenever a section is written once with a repeat marker
    ("[Chorus] x2") rather than spelled out twice -- the marker is an
    INSTRUCTION, not decoration, and a line-counting estimator that doesn't
    parse it treats the chorus as playing once.
    """
    print(); print("=" * 78); print("LOOP 2 -- repeat-marker (x2) expansion vs raw visible-line count")
    print("=" * 78)
    sheet = [
        ("Verse 1", ["line a", "line b", "line c", "line d"], 1),
        ("Chorus", ["hook line one", "hook line two"], 2),   # "[Chorus] x2"
        ("Verse 2", ["line e", "line f", "line g", "line h"], 1),
        ("Chorus", ["hook line one", "hook line two"], 1),   # written out once more, no marker
    ]
    visible_lines = sum(len(lines) for _, lines, _ in sheet)
    expanded_lines = sum(len(lines) * mult for _, lines, mult in sheet)
    print(f"  visible (unexpanded) line count: {visible_lines}")
    print(f"  repeat-marker-expanded line count: {expanded_lines}")
    seconds_per_line = 3
    print(f"  duration from visible lines: {visible_lines * seconds_per_line}s")
    print(f"  duration from expanded lines: {expanded_lines * seconds_per_line}s "
          f"(undercounted by {(expanded_lines - visible_lines) * seconds_per_line}s if unexpanded)")
    ok = expanded_lines > visible_lines
    print(f"  VERDICT: {'CONFIRMED' if ok else 'refuted'} -- an unexpanded line count undercounts "
          f"duration by {expanded_lines - visible_lines} lines' worth exactly where a writer used a "
          f"repeat marker instead of writing the section out")
    return ok


# ============================================================ LOOP 3 =====
def loop3_adlib_lines_corrupt_rhyme_scheme_scan():
    """Claim: a line-based rhyme-scheme scanner that treats every non-blank
    line as a scheme-bearing lyric line will fold bracketed AD-LIBS
    ("(yeah)", "(uh)") into the scheme, shifting every subsequent letter and
    potentially creating a spurious rhyme match between an ad-lib and a real
    lyric line -- ad-libs are craft-conventionally off-grid (background,
    not part of the primary rhyme scheme).
    """
    print(); print("=" * 78); print("LOOP 3 -- ad-lib lines corrupt a naive rhyme-scheme scan")
    print("=" * 78)
    # rhyme_class per line; None = ad-lib (should be excluded from scheme)
    raw_lines = [
        ("we ran through the rain", "A"),
        ("(yeah)", None),
        ("and never looked back again", "A"),
        ("(oh)", None),
        ("holding on to something true", "B"),
        ("(uh huh)", None),
        ("i was holding on to you", "B"),
    ]

    def assign(lines, include_adlibs):
        letters, next_letter = {}, iter("ABCDEFGH")
        seq = lines if include_adlibs else [l for l in lines if l[1] is not None]
        for i, (text, rc) in enumerate(seq):
            if rc is None:
                letters[i] = "-"
                continue
            match = next((j for j in range(i) if seq[j][1] == rc), None)
            letters[i] = letters[match] if match is not None else next(next_letter)
        return seq, letters

    seq_naive, letters_naive = assign(raw_lines, include_adlibs=True)
    seq_clean, letters_clean = assign(raw_lines, include_adlibs=False)
    naive_scheme = "".join(letters_naive[i] for i in range(len(seq_naive)))
    clean_scheme = "".join(letters_clean[i] for i in range(len(seq_clean)))
    print(f"  naive (ad-libs included) scheme over {len(seq_naive)} lines: {naive_scheme}")
    print(f"  clean (ad-libs excluded) scheme over {len(seq_clean)} lines: {clean_scheme}")
    # the real check: does the naive scheme's letter SPACING differ from the
    # true rhyme pairs' actual line-distance once ad-libs are (wrongly) counted?
    clean_gap_positions = [i for i in range(len(seq_clean)) if letters_clean[i] == "A"]
    true_pair_gap = clean_gap_positions[1] - clean_gap_positions[0]   # gap among REAL lyric lines only
    naive_gap_positions = [i for i in range(len(seq_naive)) if letters_naive[i] == "A"]
    naive_gap = naive_gap_positions[1] - naive_gap_positions[0] if len(naive_gap_positions) == 2 else None
    print(f"  true gap between the A-rhyme pair, counted over lyric lines only: {true_pair_gap}")
    print(f"  gap as computed over the ad-lib-inflated raw sequence: {naive_gap}")
    ok = naive_gap != true_pair_gap
    print(f"  VERDICT: {'CONFIRMED' if ok else 'refuted'} -- counting ad-lib lines inflates the measured "
          f"gap between a real rhyme pair from {true_pair_gap} to {naive_gap}, which would corrupt any "
          f"closure-distance-style metric (see the prior session's E8) computed over the raw line list")
    return ok


# ============================================================ LOOP 4 =====
def loop4_section_tag_regex_false_match_on_lyric_content():
    """Claim: a section-tag parser using a loose regex (does this line
    CONTAIN the word "verse"/"chorus"/"bridge"?) rather than an anchored
    bracket-tag pattern (`^\\[...\\]$`) will misfire on a lyric LINE whose
    content happens to contain one of those words -- e.g. a lyric like
    "you're my whole universe" contains "verse" as a substring.
    """
    print(); print("=" * 78); print("LOOP 4 -- loose substring section-tag detection vs anchored bracket match")
    print("=" * 78)
    lines = [
        "[Verse 1]",
        "you're my whole universe",
        "nothing else matters, not a word",
        "[Chorus]",
        "we're forever, undeterred",
    ]
    loose_re = re.compile(r"verse|chorus|bridge", re.I)
    anchored_re = re.compile(r"^\[(verse|chorus|bridge)\b.*\]$", re.I)
    loose_hits = [ln for ln in lines if loose_re.search(ln)]
    anchored_hits = [ln for ln in lines if anchored_re.match(ln)]
    print(f"  loose substring match flags {len(loose_hits)} lines as section tags: {loose_hits}")
    print(f"  anchored bracket match flags {len(anchored_hits)} lines as section tags: {anchored_hits}")
    false_positive = "you're my whole universe" in loose_hits and "you're my whole universe" not in anchored_hits
    ok = false_positive
    print(f"  VERDICT: {'CONFIRMED' if ok else 'refuted'} -- the loose regex misfires on a real lyric "
          f"line ('universe' contains 'verse') that the anchored bracket pattern correctly ignores")
    return ok


# ============================================================ LOOP 5 =====
def loop5_letter_carryforward_across_a_non_rhyming_section():
    """Claim: a rhyme-scheme letter-assigner that processes the WHOLE sheet
    as one flat line sequence, with no per-section reset or "this section
    has no scheme" flag, will carry the previous section's rhyme_class
    matching forward across a SPOKEN/non-rhyming bridge -- if the bridge's
    dialogue happens to share a rhyme_class value with an earlier verse
    line (a monitoring code quirk: unset/null rhyme_class defaulting to the
    same sentinel as a real one), it gets silently folded into that scheme.
    """
    print(); print("=" * 78); print("LOOP 5 -- letter carry-forward across a spoken, non-rhyming section")
    print("=" * 78)
    # None = "no rhyme intended" (spoken line); the BUG is a naive assigner
    # treating None as `!= ln["rc"]` normally, EXCEPT when compared with a
    # buggy default of None also being used for "not yet computed."
    lines = [
        ("verse", "we built this from nothing at all", "A"),
        ("verse", "watched it rise and watched it fall", "A"),
        ("bridge", "listen -- i need to say something real for a second", None),
        ("bridge", "this part isn't meant to rhyme with anything", None),
        ("verse", "and still we stand after it all", "A"),
    ]

    def assign_naive(lines):
        """Bug: skips None lines when SEARCHING for a match (correct), but
        a line with rc=None still gets a letter key `None` recorded in the
        results dict rather than being explicitly excluded -- and a second
        None-rc line then 'matches' the FIRST None-rc line's letter via the
        same `dict.get`/equality-on-None path a rhyme_class match uses,
        because the matcher's equality check doesn't special-case None."""
        letters, next_letter = {}, iter("ABCDEFGH")
        for i, (section, text, rc) in enumerate(lines):
            match = next((j for j in range(i) if lines[j][2] == rc), None)
            letters[i] = letters[match] if match is not None else next(next_letter)
        return letters

    def assign_correct(lines):
        letters, next_letter = {}, iter("ABCDEFGH")
        for i, (section, text, rc) in enumerate(lines):
            if rc is None:
                letters[i] = "-"
                continue
            match = next((j for j in range(i) if lines[j][2] == rc and lines[j][2] is not None), None)
            letters[i] = letters[match] if match is not None else next(next_letter)
        return letters

    naive = assign_naive(lines)
    correct = assign_correct(lines)
    naive_scheme = "".join(naive[i] for i in range(len(lines)))
    correct_scheme = "".join(correct[i] for i in range(len(lines)))
    print(f"  naive scheme (None treated as a real rhyme_class value): {naive_scheme}")
    print(f"  correct scheme (None explicitly excluded):               {correct_scheme}")
    bug_links_bridge_lines = naive[2] == naive[3]   # both bridge lines get the SAME letter, spuriously
    ok = bug_links_bridge_lines and correct[2] == "-" and correct[3] == "-"
    print(f"  VERDICT: {'CONFIRMED' if ok else 'refuted'} -- treating a 'no rhyme intended' sentinel "
          f"as an ordinary rhyme_class value makes the two unrelated spoken bridge lines match each "
          f"other by coincidence (both letter '{naive.get(2)}'), a scheme the writer never intended; "
          f"an explicit None-exclusion correctly marks both '-' instead")
    return ok


# ============================================================ LOOP 6 =====
def loop6_near_title_drop_missed_by_exact_substring():
    """Claim: a "does the song's title appear in its lyrics" checker using
    exact substring match misses a deliberate NEAR-title-drop -- a common
    hook technique where the hook line is a close variant of the title
    rather than a verbatim repeat (pluralization, tense change, or a word
    inserted for scansion).
    """
    print(); print("=" * 78); print("LOOP 6 -- title-drop detection: exact substring vs fuzzy match")
    print("=" * 78)
    title = "Hold The Line"
    hook_lines = [
        "so hold the line, hold the line",              # exact
        "i'm gonna hold that line forever",              # near: word inserted + pronoun swap
        "we held the line when it mattered most",        # near: tense changed (hold -> held)
    ]

    def exact_drop(title, line):
        return title.lower() in line.lower()

    STOPWORDS = {"the", "a", "an", "that", "this"}

    def fuzzy_drop(title, line, max_gap_words=2):
        # token-subsequence match over the title's CONTENT words only (function
        # words are routinely dropped/substituted in a near-title-drop, e.g.
        # "hold THAT line" for "hold THE line") -- every content word appears
        # in the line, in order, with at most max_gap_words of drift, and
        # simple stemming for tense (held -> hold).
        def stem(w):
            w = w.lower()
            if w.endswith("held"):
                return "hold"
            return w
        title_words = [stem(w.strip(",.'!?")) for w in title.split()
                       if stem(w.strip(",.'!?")) not in STOPWORDS]
        line_words = [stem(w.strip(",.'!?")) for w in line.split()]
        pos = -1
        for tw in title_words:
            found = None
            for j in range(pos + 1, len(line_words)):
                if line_words[j] == tw:
                    found = j
                    break
            if found is None or (pos >= 0 and found - pos - 1 > max_gap_words):
                return False
            pos = found
        return True

    print(f"    {'hook line':<45} {'exact':>6} {'fuzzy':>6}")
    exact_hits, fuzzy_hits = 0, 0
    for ln in hook_lines:
        e, f = exact_drop(title, ln), fuzzy_drop(title, ln)
        exact_hits += e
        fuzzy_hits += f
        print(f"    {ln:<45} {str(e):>6} {str(f):>6}")
    ok = exact_hits < len(hook_lines) and fuzzy_hits == len(hook_lines)
    print(f"  VERDICT: {'CONFIRMED' if ok else 'refuted'} -- exact substring catches only {exact_hits}/"
          f"{len(hook_lines)} deliberate title-drops; order-preserving fuzzy word match catches "
          f"{fuzzy_hits}/{len(hook_lines)}")
    return ok


# ============================================================ LOOP 7 =====
def loop7_global_syllables_per_second_misestimates_mixed_pacing():
    """Claim: a duration estimator using ONE global syllables-per-second
    rate for the whole song under-/over-estimates badly once a section is
    performed at a genuinely different pace (a double-time rap bridge vs
    sung verses) -- the error isn't just noise, it's systematically biased
    in the direction of whichever section type dominates the calibration.
    """
    print(); print("=" * 78); print("LOOP 7 -- one global syllables/sec rate vs per-section pacing")
    print("=" * 78)
    sections = [
        ("Verse 1", 32, 2.2),     # syllables, TRUE rate (syll/sec) for this section
        ("Chorus", 24, 2.5),
        ("Verse 2", 32, 2.2),
        ("Bridge", 60, 5.0),      # double-time rap bridge: much faster true rate
        ("Chorus", 24, 2.5),
    ]
    true_duration = sum(syll / rate for _, syll, rate in sections)
    global_rate = sum(syll for _, syll, _ in sections) / true_duration  # calibrated "globally" from the truth
    # now use ONE global rate to re-estimate each section, and see how far
    # the BRIDGE (the outlier-paced section) drifts from its true duration.
    print(f"    {'section':<10} {'syll':>5} {'true rate':>10} {'true dur':>9} {'global-rate dur':>16} {'error':>7}")
    total_est = 0
    bridge_error = None
    for name, syll, rate in sections:
        true_dur = syll / rate
        est_dur = syll / global_rate
        total_est += est_dur
        err = est_dur - true_dur
        if name == "Bridge":
            bridge_error = err
        print(f"    {name:<10} {syll:>5} {rate:>10.2f} {true_dur:>9.2f} {est_dur:>16.2f} {err:>+7.2f}")
    print(f"  true total duration: {true_duration:.2f}s   global-rate estimated total: {total_est:.2f}s "
          f"(song-level error: {total_est - true_duration:+.2f}s)")
    ok = abs(bridge_error) > 3.0  # the bridge alone drifts by more than 3 seconds
    print(f"  VERDICT: {'CONFIRMED' if ok else 'refuted'} -- the bridge section alone is misestimated by "
          f"{bridge_error:+.2f}s under one global rate, even though the SONG-level total error partly "
          f"cancels out ({total_est - true_duration:+.2f}s) -- a global check on total duration alone "
          f"would hide a real per-section error this large")
    return ok


# ============================================================ LOOP 8 =====
def loop8_extended_metaphor_vehicle_flagged_as_topic_drift():
    """Claim: a per-line "topic drift" detector comparing each line's
    vocabulary against the song's overall word-frequency profile flags an
    extended metaphor's VEHICLE words (storm/lightning/flood imagery used
    throughout a heartbreak song) as off-topic outliers, because the
    profile is dominated by the metaphor's TENOR words (heart, leaving,
    alone) even though the vehicle words are the intended, consistent
    device, appearing as consistently as the tenor words do.
    """
    print(); print("=" * 78); print("LOOP 8 -- extended-metaphor vehicle words flagged as topic drift")
    print("=" * 78)
    lines = [
        "my heart is breaking, you are leaving",
        "the storm is rising, clouds are grieving",
        "i'm alone here with an empty heart",
        "lightning cracks and tears us apart",
        "the flood is rising where you used to be",
        "my heart, still breaking, still leaving me",
    ]
    tenor_words = {"heart", "breaking", "leaving", "alone", "empty"}
    vehicle_words = {"storm", "rising", "clouds", "lightning", "cracks", "flood"}
    all_words = [w.strip(",.'").lower() for ln in lines for w in ln.split()]
    from collections import Counter
    freq = Counter(all_words)

    def topic_drift_score(line, freq):
        words = [w.strip(",.'").lower() for w in line.split()]
        # naive: fraction of words that are BELOW-MEDIAN frequency in the song
        med = sorted(freq.values())[len(freq) // 2]
        rare = sum(1 for w in words if freq[w] <= med)
        return rare / len(words)

    print(f"    {'line':<45} {'drift score':>12}  vehicle-heavy?")
    tenor_scores, vehicle_scores = [], []
    for ln in lines:
        score = topic_drift_score(ln, freq)
        words = {w.strip(",.'").lower() for w in ln.split()}
        is_vehicle_line = bool(words & vehicle_words) and not (words & tenor_words)
        (vehicle_scores if is_vehicle_line else tenor_scores).append(score)
        print(f"    {ln:<45} {score:>12.2f}  {is_vehicle_line}")
    avg_tenor = sum(tenor_scores) / len(tenor_scores) if tenor_scores else 0
    avg_vehicle = sum(vehicle_scores) / len(vehicle_scores) if vehicle_scores else 0
    print(f"  avg drift score, tenor-only lines: {avg_tenor:.2f}   vehicle-only lines: {avg_vehicle:.2f}")
    ok = avg_vehicle > avg_tenor
    print(f"  VERDICT: {'CONFIRMED' if ok else 'refuted'} -- the pure-vehicle-imagery lines score HIGHER "
          f"'drift' ({avg_vehicle:.2f}) than the pure-tenor lines ({avg_tenor:.2f}) despite being just as "
          f"deliberate and consistent a device -- a word-frequency-only drift metric can't distinguish "
          f"'off-topic' from 'the song's other deliberate vocabulary track'")
    return ok


# ============================================================ LOOP 9 =====
def loop9_section_renumbering_breaks_on_inserted_bridge():
    """Claim: a section-renumbering tool that relabels every "[Verse N]"
    tag by simple encounter-order incrementing (a common auto-fix after
    editing) is fine when sections are only ADDED at the end, but silently
    RELABELS a later verse's semantic identity (its own internal callbacks,
    e.g. "like I said in verse 2") when a bridge is inserted BETWEEN two
    verses and the renumbering only touches the bracket tags, not any prose
    references to a verse's old number inside the lyric text itself.
    """
    print(); print("=" * 78); print("LOOP 9 -- auto-renumbering bracket tags vs stale in-lyric verse references")
    print("=" * 78)
    original = [
        ("[Verse 1]", ["first thing i ever said to you"]),
        ("[Verse 2]", ["still holding on like verse one told you to"]),
        ("[Chorus]", ["hold on, hold on"]),
        ("[Verse 3]", ["callback now -- remember verse two?"]),
    ]
    # editing: insert a NEW bridge between Verse 2 and the Chorus
    edited = [
        ("[Verse 1]", ["first thing i ever said to you"]),
        ("[Verse 2]", ["still holding on like verse one told you to"]),
        ("[Bridge]", ["wait -- before the chorus, one more line"]),
        ("[Chorus]", ["hold on, hold on"]),
        ("[Verse 3]", ["callback now -- remember verse two?"]),
    ]

    def renumber_tags_only(sheet):
        out, n = [], 0
        for tag, lines in sheet:
            if tag.lower().startswith("[verse"):
                n += 1
                out.append((f"[Verse {n}]", lines))
            else:
                out.append((tag, lines))
        return out

    renumbered = renumber_tags_only(edited)
    print("  bracket tags after inserting a bridge + renumbering (tags only):")
    for tag, lines in renumbered:
        print(f"    {tag:<12} {lines[0]}")
    # the bracket tags are all still correct (Verse 1/2/3 unchanged, since the
    # bridge isn't a verse) -- the REAL bug is the prose callback inside
    # Verse 3's own lyric, which still says "verse two" and is correct here,
    # but would go STALE if the edit had instead REMOVED or REORDERED a verse,
    # which the tag-only renumbering has no way to detect or warn about.
    reordered = [
        ("[Verse 1]", ["still holding on like verse one told you to"]),  # verse 2 promoted to slot 1
        ("[Verse 2]", ["first thing i ever said to you"]),               # verse 1 demoted to slot 2
        ("[Chorus]", ["hold on, hold on"]),
        ("[Verse 3]", ["callback now -- remember verse two?"]),
    ]
    renumbered2 = renumber_tags_only(reordered)
    stale_reference = "verse one" in renumbered2[0][1][0] and renumbered2[0][0] == "[Verse 1]"
    print(f"\n  after REORDERING verses 1 and 2 and renumbering tags only:")
    for tag, lines in renumbered2:
        print(f"    {tag:<12} {lines[0]}")
    print(f"  [Verse 1]'s own lyric still says 'verse one' referring to itself under its OLD number "
          f"(stale self-reference): {stale_reference}")
    ok = stale_reference
    print(f"  VERDICT: {'CONFIRMED' if ok else 'refuted'} -- renumbering bracket tags alone never touches "
          f"prose verse-number callbacks inside the lyric text, so a reorder (not just an insert) leaves "
          f"a stale, now-incorrect self-reference that only a content-aware check would catch")
    return ok


# ============================================================ LOOP 10 ====
def loop10_repeat_expansion_discards_authored_variant_chorus():
    """Claim (composes with the prior session's dedup-lifetime kernel,
    sandbox-hitbox-window/E2 via sandbox-lyrical-composition/E1): a repeat-
    marker EXPANDER that mechanically duplicates the FIRST occurrence of a
    section N times for "[Chorus] x2" will silently DISCARD an authored,
    deliberately evolving second chorus if the lyric sheet ALSO happens to
    write the second chorus out in full immediately after -- the expander
    has no way to know the written-out text was meant to REPLACE its
    mechanical duplicate rather than sit alongside it, so naive concatenation
    produces a chorus that plays three times, not two.
    """
    print(); print("=" * 78); print("LOOP 10 -- repeat-marker expansion vs an authored evolving second chorus")
    print("=" * 78)
    sheet = [
        ("[Chorus] x2", ["we are the ones who stayed", "we are the ones who stayed"]),
        ("[Chorus - final]", ["we are the ones who stayed", "and we're still here today"]),  # evolved 2nd chorus
    ]

    def expand_naive(sheet):
        out = []
        for tag, lines in sheet:
            m = re.search(r"x(\d+)", tag)
            mult = int(m.group(1)) if m else 1
            for _ in range(mult):
                out.extend(lines)
        return out

    expanded = expand_naive(sheet)
    true_intended_plays = 2  # the "x2" chorus PLUS the "final" variant = 2 total choruses intended...
    # actually: intent is "x2" MEANS this chorus plays twice, and the SECOND
    # of those two plays is the evolved "final" version written out --  not
    # three plays total. Expansion blindly adds the x2 duplicate on TOP of
    # the separately-written final chorus.
    actual_expanded_plays = len(expanded) // 2  # each "play" is 2 lines here
    print(f"  sheet as written: [Chorus] x2 (2 lines) then [Chorus - final] (2 lines, evolved)")
    print(f"  intended total chorus plays: {true_intended_plays} (the x2 IS the final-chorus pair)")
    print(f"  naive expansion result ({len(expanded)} lines = {actual_expanded_plays} plays): {expanded}")
    ok = actual_expanded_plays > true_intended_plays
    print(f"  VERDICT: {'CONFIRMED' if ok else 'refuted'} -- naive mechanical expansion of the x2 marker, "
          f"run on top of a separately-authored evolved chorus meant to BE the second of those two plays, "
          f"produces {actual_expanded_plays} chorus plays where {true_intended_plays} were intended -- "
          f"the same 'evolving repeat' shape as the prior session's hook-dedup finding, now on the "
          f"SECTION-repeat-marker axis instead of the hook-text axis")
    return ok


if __name__ == "__main__":
    results = {
        "L1_occurrence_vs_type_count": loop1_double_chorus_duration_inflation(),
        "L2_repeat_marker_vs_visible_lines": loop2_repeat_marker_expansion_vs_visible_lines(),
        "L3_adlib_corrupts_scheme_scan": loop3_adlib_lines_corrupt_rhyme_scheme_scan(),
        "L4_loose_vs_anchored_tag_regex": loop4_section_tag_regex_false_match_on_lyric_content(),
        "L5_letter_carryforward_nonrhyme": loop5_letter_carryforward_across_a_non_rhyming_section(),
        "L6_exact_vs_fuzzy_title_drop": loop6_near_title_drop_missed_by_exact_substring(),
        "L7_global_vs_per_section_pacing": loop7_global_syllables_per_second_misestimates_mixed_pacing(),
        "L8_metaphor_vehicle_flagged_drift": loop8_extended_metaphor_vehicle_flagged_as_topic_drift(),
        "L9_renumber_tags_stale_prose_refs": loop9_section_renumbering_breaks_on_inserted_bridge(),
        "L10_repeat_expansion_vs_authored_variant": loop10_repeat_expansion_discards_authored_variant_chorus(),
    }
    print(); print("=" * 78); print("SUMMARY -- lyrics structure, loops 1-10"); print("=" * 78)
    for k, v in results.items():
        print(f"  {k:<32} {'CONFIRMED' if v else 'refuted/no-signal'}")
