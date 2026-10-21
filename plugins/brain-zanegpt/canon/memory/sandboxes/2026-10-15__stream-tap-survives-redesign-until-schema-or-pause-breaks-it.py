"""Hand-written model (not a real browser, page or TTS vendor) of automating a TTS web UI.

Claim under test (ideas:VOICE/automation/intercept-the-stream-not-the-dom): a selector scraper breaks when
the page's markup is redesigned, while tapping the page's own data stream (WebSocket audio messages) and
detecting completion by a silence/buffer heuristic survives. Pushed until it stops holding:
  - a redesign that ALSO changes the stream schema (message type / field rename),
  - a take whose internal dramatic pause is longer than the silence threshold,
  - DOM waits: fixed sleep vs observer, and insertion-based vs visibility-based (pocketzane#E2) when the
    redesign pre-renders the 'done' toast hidden.
Prediction (written before the first run): v1 both methods capture 100%; v2 (markup redesign, same
stream) selector scraper 0%, stream tap 100%; v3 (schema rename) stream tap 0% captured and, unless it
checks for unknown message types, reports success; silence threshold 400 ms truncates a take with a
600 ms pause to under 60% of its audio, threshold must exceed the longest pause; fixed 1000 ms sleep
fails on >=1 of 6 render delays; insertion-wait on a pre-rendered hidden toast fires at t=0 (false).
Pure stdlib, deterministic."""

CHUNK_MS = 100

def make_take(pause_ms_list, words=6, word_ms=400):
    """Audio as 100 ms frames of amplitude; words are loud (0.6), pauses between words silent."""
    frames = []
    for w in range(words):
        frames += [0.6] * (word_ms // CHUNK_MS)
        if w < words - 1:
            p = pause_ms_list[w] if w < len(pause_ms_list) else 100
            frames += [0.0] * (p // CHUNK_MS)
    return frames

def stream(frames, schema="v1", tail_silence_frames=10):
    """The page's own WebSocket traffic: one message per frame, then trailing silence padding, then done."""
    msgs = [{"type": "status", "state": "queued"}]
    for i, a in enumerate(frames + [0.0] * tail_silence_frames):
        if schema in ("v1", "v2"):
            msgs.append({"type": "audio", "seq": i, "pcm": a})
        else:  # v3: vendor renamed the message type and payload field
            msgs.append({"type": "audio_chunk", "seq": i, "samples": a})
    msgs.append({"type": "status", "state": "done"} if schema != "v3" else {"type": "job", "phase": "complete"})
    return msgs

def dom(version, audio_frames, t):
    """Rendered markup at time t (ms) as a flat list of nodes. v1 plain classes; v2 hashed CSS-module classes,
    extra wrappers, and a 'done' toast pre-rendered hidden from t=0, made visible when finished."""
    finished = t >= 1800
    nodes = []
    if version == "v1":
        nodes.append({"tag": "div", "cls": "spinner", "visible": not finished})
        if finished:
            nodes.append({"tag": "audio", "cls": "audio-player", "src": len(audio_frames), "visible": True})
            nodes.append({"tag": "div", "cls": "toast-done", "visible": True})
    else:
        nodes.append({"tag": "div", "cls": "Loader_x93kd", "visible": not finished})
        nodes.append({"tag": "div", "cls": "Toast_k2j1", "visible": finished})  # pre-rendered, hidden
        if finished:
            nodes.append({"tag": "div", "cls": "Wrap_a81z", "visible": True})
            nodes.append({"tag": "audio", "cls": "Player_p0q7", "src": len(audio_frames), "visible": True})
    return nodes

def selector_scraper(version, frames):
    """Built against v1: wait for .spinner to vanish, read audio.audio-player."""
    for t in range(0, 5000, 100):
        nodes = dom(version, frames, t)
        spin = [n for n in nodes if n["cls"] == "spinner" and n["visible"]]
        player = [n for n in nodes if n["tag"] == "audio" and n["cls"] == "audio-player"]
        if not spin and player:
            return player[0]["src"]
    return 0

def stream_tap(msgs, silence_ms=400, strict=False):
    """Collect audio frames from the stream; declare done after silence_ms of silence once audio began.
    strict=True raises on any message type the tap does not know."""
    got, silent, started = [], 0, False
    known = {"audio", "status"}
    for m in msgs:
        if m["type"] not in known:
            if strict:
                return got, "error:unknown-type:" + m["type"]
            continue
        if m["type"] != "audio":
            continue
        a = m["pcm"]
        got.append(a)
        if a > 0.05:
            started, silent = True, 0
        elif started:
            silent += CHUNK_MS
            if silent >= silence_ms:
                return got, "done-by-silence"
    return got, "stream-ended"

def loud(frames):
    return sum(1 for a in frames if a > 0.05)

# ---- Scenario 1/2/3: capture across versions
take = make_take([200, 200, 200, 200, 200])
L = loud(take)
rows = {}
for v in ("v1", "v2", "v3"):
    scrap = selector_scraper(v, take)
    scr_frac = loud(take) / L if scrap == len(take) else 0.0
    got, how = stream_tap(stream(take, v))
    got_s, how_s = stream_tap(stream(take, v), strict=True)
    rows[v] = (scr_frac, loud(got) / L, how, how_s)
    print(f"{v}: selector scraper captured {scr_frac:.0%}; stream tap captured {loud(got)/L:.0%} ({how}); strict tap -> {how_s}")

# ---- Scenario 4: silence threshold vs internal dramatic pause
pause_take = make_take([200, 200, 600, 200, 200])
Lp = loud(pause_take)
sweep = {}
for thr in (300, 400, 500, 600, 700, 800):
    got, how = stream_tap(stream(pause_take, "v1"), silence_ms=thr)
    sweep[thr] = loud(got) / Lp
print("pause take (longest internal pause 600 ms) captured by threshold:", {k: f"{v:.0%}" for k, v in sweep.items()})
# latency cost: silence threshold is added after the true end (trailing silence in stream is 1000 ms)
min_safe = min(t for t, f in sweep.items() if f == 1.0)
print(f"smallest safe threshold {min_safe} ms = longest pause {600} ms + one chunk")

# ---- Scenario 5: DOM waits (the part that cannot be avoided). Element ready at delay d.
delays = [300, 700, 950, 1200, 1800, 2500]
sleep_ms = 1000
sleep_fail = sum(1 for d in delays if d > sleep_ms)
sleep_waste = sum(sleep_ms - d for d in delays if d <= sleep_ms)
observer_wait = sum(delays)
print(f"fixed sleep {sleep_ms} ms: fails {sleep_fail}/6 renders, wastes {sleep_waste} ms on the rest; observer waits exactly {observer_wait} ms total, fails 0")

# ---- Scenario 6: insertion-based vs visibility-based completion wait on v2 (toast pre-rendered hidden)
def insertion_wait(version):
    seen0 = {n["cls"] for n in dom(version, take, 0)}
    for t in range(0, 5000, 100):
        if any("oast" in n["cls"] for n in dom(version, take, t)):
            return t if "Toast_k2j1" not in seen0 or t > 0 else 0
    return None
def visibility_wait(version):
    for t in range(0, 5000, 100):
        if any("oast" in n["cls"] and n["visible"] for n in dom(version, take, t)):
            return t
    return None
iv1, iv2 = insertion_wait("v1"), insertion_wait("v2")
vv1, vv2 = visibility_wait("v1"), visibility_wait("v2")
print(f"done-toast wait (true finish 1800 ms): insertion v1 {iv1} v2 {iv2}; visibility v1 {vv1} v2 {vv2}")

ok = (rows["v1"][0] == 1 and rows["v1"][1] == 1 and rows["v2"][0] == 0 and rows["v2"][1] == 1
      and rows["v3"][1] == 0 and rows["v3"][2] != "error" and rows["v3"][3].startswith("error")
      and sweep[400] < 0.6 and min_safe == 700 and sleep_fail >= 1 and iv2 == 0 and vv2 == 1800)
print("RESULT:", "PASS" if ok else "FAIL",
      f"redesign: scraper {rows['v2'][0]:.0%} vs stream tap {rows['v2'][1]:.0%}; schema rename: tap {rows['v3'][1]:.0%} reported '{rows['v3'][2]}' (strict: {rows['v3'][3]}); "
      f"silence 400 ms on a 600 ms pause keeps {sweep[400]:.0%}, safe from {min_safe} ms; sleep 1000 fails {sleep_fail}/6; "
      f"hidden pre-rendered toast: insertion fires at {iv2} ms, visibility at {vv2} ms")
