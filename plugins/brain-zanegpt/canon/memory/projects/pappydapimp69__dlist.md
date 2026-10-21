# Pappydapimp69/Dlist — lessons

Project: Pappydapimp69/Dlist. Newest first.

---

## E7 — locomotion active tail holds inside the turn entered by lag
- Date: 2026-10-21
- Project: Pappydapimp69/Dlist
- Tags: [locomotion][animation][physics][gamedev][sandbox]
- What: With the tail ACTIVELY used for balance (the owner's decision on the open tail-side
  tension), the best controller for a turning Herrerasaurus holds the tail on the INSIDE of
  the turn and enters that hold by letting the tail keep its world heading while the body
  yaws (lag timing), through a critically damped 3 Hz command filter. It lowers the steady
  roll moment about the support line by 11 percent at sprint (2432 vs 2752 N m straight) and
  40 percent at walk (598 vs 997), never needs more leg yaw torque than a straight tail, and
  an outside hold or any flick strategy roughly doubles to quadruples the peak leg yaw torque.
- Why built: Loop-4 lesson dlist/E5 showed a PASSIVE tail ends outside a fast turn and a
  path tail ends inside, which left the side open; the owner ruled the tail is actively used
  for balance, so the side, the hold angle as a function of speed and yaw rate, and the entry
  and exit timing had to be chosen by what actually stabilises the body.
- Design: A deterministic planar multibody sandbox: body 205 kg (CoM 0.33 m ahead of the
  hip at 1.10 m, yaw inertia 75 kg m^2) on the demo's speeds 1.5, 3.4 and 7.4 m/s at its
  maximum turn rates (2.43, 2.08, 1.35 rad/s) with its 0.125 s yaw smoothing; the loop-4 tail
  chain (6 links, 2.86 m, 45 kg) with a PD servo at the base joint and passive mid joints, the
  distal three 5x stiffer. It scores six strategies on peak and steady roll moment about the
  support line, peak and steady leg yaw torque, and settling at entry and exit.
- Got right: Inside wins on roll at every speed because holding the tail mass inward moves
  the centre of mass toward the turn (gravity moment m_t*g*d*sin(phi)); the leg yaw torque is
  nearly side-independent in a steady turn (668 vs 633 to 700 N m at sprint), so roll decides
  the side. Bending stays at the base: the base joint carries 65 to 75 percent of the bend.
- Where/why it failed: Run 1 sent step commands into the servo and produced impulsive
  torques of 1e5 to 1e7 N m that swamped every comparison; commands must be filtered. My
  prediction that the entry reaction torque would cut peak leg yaw clearly was wrong: inside
  beats straight by only 1 to 4 percent. The sprint slalom built to break the winner does break
  a plain inside hold (peak leg yaw 4568 vs straight 3491 N m), and the tail swing settles
  slower than a straight tail (1.33/1.43 s vs 0.77/0.78 s at sprint).
- Fix: Use lag timing, which survives the slalom (2986 N m, below straight), with
  hold = asin(min(sin 0.5, 0.49 * v * |yawRate|)) rad on the inside, commanded as
  min(hold, |yaw - yawAtTurnStart|) so the tail swings only as fast as the body turns, reset
  when the turn direction flips, followed by a critically damped 3 Hz filter; on exit the
  same formula returns the tail as the yaw rate decays.
- Why this fix: Lag timing makes the tail swing through the body's own yaw rather than ahead
  of it, so its angular momentum barely changes at entry and on each slalom flip, while the
  inside hold keeps the roll gain; the 0.49 factor is m*h/(m_t*d*g) for this rig, which makes
  the gravity moment of the tail match the centripetal roll load until the range cap.
- Rule of thumb: An actively balancing tail should sit on the inside of a turn, at
  asin(min(sin(phi_max), m*h*v*|yawRate|/(m_t*d*g))), swung in no faster than the body yaws
  (min(hold, yaw since turn start)) through a critically damped filter; step commands, outside
  holds and flicks multiply peak leg yaw torque two to four times.
- Provenance (verified/assumed): Verified first-hand with the deterministic sandbox below;
  speeds, turn rates, yaw smoothing and tail length come from demos/skin-test/index.html, and
  the tail chain matches dlist/E5.
- Caveats: Body mass split, body yaw inertia, tail range cap phi_max 0.5 rad and servo gains
  are assumed values. The roll check is quasi-3D (heights on a planar model), and the body is
  modelled without rolling or leaning, so roll moment is what foot placement and body lean
  must still carry, as in dlist/E4. With soft 1 Hz mid joints inside still wins on roll
  (2544 vs 2743 N m) but the base carries only 39 percent of the bend.
- Composed: dlist/E5, dlist/E4,
  ideas:MOTION/physics/critically-damped-spring-not-fixed-duration-tween
- Sandbox: sandboxes/2026-10-21__locomotion-active-tail-holds-inside-the-turn-entered-by-lag.py
- Prediction: Written before the first run: inside hold lowers steady roll by about 200 N m
  (about 7 percent at sprint, 20 percent at walk) and outside raises it by the same; steady
  hip hold torque is straight-worst and inside equals outside; swinging inward during the
  yaw ramp clearly lowers peak leg yaw against straight, and flick-outside-first raises it;
  winner inside with lag entry; a sprint slalom pushes the inside hold's peak leg yaw above
  straight. Side, winner and the flick and outside penalties held; the roll gain was larger
  (11 and 40 percent); the yaw benefit was only 1 to 4 percent; the slalom broke only the
  plain inside hold, not the lag-timed one.
- Observed: RESULT: PASS active tail wins INSIDE entered by lag: sprint steady roll 2432 vs
  straight 2752 vs outside 3066 N m, peak leg yaw 1662 vs straight 1682 vs outside 3555; walk
  steady roll 598 vs 997; base bend share 0.65; slalom break holds for lag timing (peak leg
  yaw 2986 vs straight 3491) but breaks a plain inside hold (4568); settle in/out 1.33/1.43 s.
  Flick strategies peak at 5002 to 6553 N m roll and 6124 to 7275 N m leg yaw; phi_max 0.7
  lowers sprint steady roll further to 2289 N m.
- Scenarios: 1) six strategies (inside hold, inside with lag entry, outside hold, flick in then
  hold out, flick out then hold in, straight) at 1.5, 3.4 and 7.4 m/s; 2) phi_max 0.3, 0.5 and
  0.7 at sprint; 3) soft 1 Hz mid joints at sprint; 4) BUILT TO BREAK the winner: a sprint
  slalom with yaw rate flipping +/-1.35 rad/s every 0.5 s.
- Link: session claude.ai/code/session_017uyNQEczEfzSRfCLiYvMTe (owner decision on the tail-side tension, active balance)

## E6 — locomotion predictive foot target must predict heading too
- Date: 2026-10-21
- Project: Pappydapimp69/Dlist
- Tags: [locomotion][animation][gamedev][sandbox]
- What: In a procedural gait whose swing foot eases (smoothstep) toward a landing target that
  is re-evaluated every frame, the foot's world velocity at touchdown equals the target's
  world velocity, because smoothstep has zero slope at the end. Predicting the landing point
  as body + offset + velocity * remaining swing time makes the target stand still on a
  straight path (0.000 m/s skid against 7.48 m/s with no prediction). The same prediction
  still skids in turns, at omega * |offset| (1.05 m/s in the Herrerasaurus demo's sprint turn,
  1.31 m/s in its walk turn), and under acceleration (0.43 m/s), for two separate reasons.
- Why built: The demo plants feet with exactly this velocity-times-remaining prediction, and
  the next round adds sharper turns and a sprint posture, so it needed to be known where
  the prediction still lets a foot skate on touchdown before adding more motion on top.
- Design: A deterministic sandbox reproduces the demo's swing and landing formula (neutral
  ball offset, stance-centring term 0.5 * v * duty * T, the 1.1 Hz cadence floor, smoothstep
  easing) on a body path with constant acceleration and yaw rate, and measures the foot's
  touchdown speed for no prediction, velocity-only prediction (the demo) and full prediction
  of the body's future position and heading. It reruns the sprint turn with the longer
  stance from the Froude duty (dlist/E2) and Alexander stride (dlist/E3).
- Got right: Velocity times remaining time is the right core: on straight paths at walk and
  sprint it cancels the target's drift exactly (0.000 m/s), and adding the predicted heading
  (rotate the body offset to the heading the body will have at touchdown, and move along the
  arc) cancels the turn skid to 0.000 m/s at both turn rates.
- Where/why it failed: Velocity-only prediction leaves the body-attached offset rotating with
  the body, so the target moves at omega * |offset| at touchdown, 1.05 m/s at sprint and 1.31
  m/s at walk, and 1.24 m/s once the longer E2/E3 stance is used. My pre-run prediction also
  missed the acceleration case: the stance-centring term uses the current speed, so the
  target creeps forward at 0.5 * a * duty * T, 0.43 m/s at 3 m/s^2.
- Fix: Predict heading as well as position (offset rotated by the heading at touchdown, body
  moved along the predicted arc), and freeze the speed in the stance-centring term at
  lift-off. With both, touchdown skid is 0.006 m/s or less in every tested case.
- Why this fix: Both errors come from parts of the target that change with time and were not
  predicted (heading and speed), so predicting or freezing those parts makes the target
  stationary in the world, which is the property smoothstep needs; neither fix changes
  where the foot lands on a straight path at constant speed.
- Rule of thumb: An eased swing foot lands with its target's world velocity, so predict
  everything the target depends on: velocity*remaining fixes straight paths only; a turn
  needs the heading predicted too (else skid omega*|offset|, 1.05 m/s here), and acceleration
  needs the stance-centring speed frozen at lift-off (else 0.5*a*duty*T).
- Provenance (verified/assumed): Verified first-hand with the deterministic sandbox below,
  whose swing, landing, duty, stride and turn-rate formulas were copied from
  demos/skin-test/index.html. The touchdown speed is measured by finite difference over the
  final millisecond of swing.
- Composed: dlist/E2, dlist/E3
- Sandbox: sandboxes/2026-10-21__locomotion-predictive-foot-target-must-predict-heading-too.py
- Prediction: Written before the first run: without the velocity term the foot touches down
  at about body speed (7.4 m/s at sprint), with it about zero; under 3 m/s^2 acceleration
  still about zero; in the sprint turn about 1.0 m/s and in the walk turn about 1.3 m/s with
  velocity-only prediction, and about zero with heading predicted. All held except
  acceleration (0.43 m/s, run 1 printed RESULT: FAIL); run 2 adds the frozen-speed fix.
- Observed: RESULT: PASS no prediction skids at 7.48 m/s at sprint touchdown, velocity
  prediction 0.000; accel skids 0.426 until the centring speed is frozen at lift-off (0.006);
  in turns velocity-only still skids 1.05 m/s sprint / 1.31 walk (= omega*|offset|), 1.24 with
  E2/E3 stance; heading prediction 0.000/0.000.
- Scenarios: 1) sprint straight 7.4 m/s; 2) walk straight 1.5 m/s; 3) accelerating 3 m/s^2 at
  4 m/s, and 3b) the same with centring speed frozen; 4) BUILT TO BREAK the claim that velocity
  prediction avoids foot sliding: sprint turn at 1.35 rad/s; 5) walk turn at 2.43 rad/s; 6) the
  sprint turn with the Froude duty and Alexander stride stance from dlist/E2 and dlist/E3.
- Link: session claude.ai/code/session_017uyNQEczEfzSRfCLiYvMTe (brain train combined, LOCOMOTION loop 5)

## E5 — locomotion passive tail swings outside a turn path tail inside
- Date: 2026-10-21
- Project: Pappydapimp69/Dlist
- Tags: [locomotion][animation][physics][gamedev][sandbox]
- What: A procedural dinosaur tail in a turn has two physically different answers for which
  side it ends on. A tail placed along the hip's own path sits on the INSIDE of the turn
  (0.73 m at the demo's sprint radius of 5.48 m). A passive spring-and-damper tail chain
  lags to the inside only for the first fraction of a second, while the yaw rate ramps in,
  and then settles OUTSIDE (1.23 m at 7.4 m/s and 1.35 rad/s), because the hip's centripetal
  acceleration of about 10 m/s^2 swings it out. So the familiar idea of a brief outward lag
  on a sharp turn has the wrong sign for a passive tail.
- Why built: The Herrerasaurus demo's next round wants a stiffer tail with lag in turns; its
  current tail target is -0.22 * yawRate on one spring (stiffness 38, damping 8.5), which
  always curls the tail inward, and the plan needed to know what a physically lagging tail
  would do before tuning lag by eye.
- Design: A planar 6-link tail chain (2.86 m, 45 kg tapering) on a prescribed accelerating
  hip, with full multibody equations of motion solved per step and semi-implicit Euler
  integration, driven through a left turn whose yaw rate ramps with the demo's 0.125 s
  smoothing. It is compared with a kinematic path-following tail. It also tests distal
  stiffening (distal three joints five times stiffer), per-joint critical damping, and
  explicit vs semi-implicit Euler at a coarse 2 ms step.
- Got right: Distal stiffening does move bending toward the base: the two base joints carry
  27 percent of the bending in a uniform tail and 44 percent with the distal joints five times
  stiffer, which is the mechanical reading of the herrerasaurid elongated distal
  prezygapophyses. Semi-implicit Euler stays bounded where explicit Euler diverges.
- Where/why it failed: The claim to test was that tail inertia gives a brief OUTWARD lag on
  sharp turns; the passive chain gives the opposite order (inside first at t+0.03 s, up to
  0.53 m, first outside at t+0.60 s). Separately, setting every joint to critical damping
  (zeta 1) does not stop the coupled chain overshooting: the tip still swings 24 percent past
  its steady outward position, so single-spring critical damping does not carry over to a
  chain.
- Fix: Decide the side on purpose. For a tail that reads as following the body, keep the
  path-style inside target. For physical lag, drive the tail from the hip's lateral
  acceleration (v * yawRate) as well as yaw rate, so it swings outside at speed after a
  short inside lag, and tune overshoot on the whole chain, not per joint.
- Why this fix: The sandbox shows the two motions come from different terms: yaw angular
  acceleration gives the inside lag, centripetal acceleration v * omega gives the outward
  swing. A target built only from yawRate, as in the demo, cannot produce the speed-dependent
  outward swing, and it gives about the same curl at walk (where a passive tail stays near
  straight, -0.03 m) as at sprint.
- Rule of thumb: A passive tail lags inside a turn only briefly, then swings outside by
  about v*omega/stiffness; a path-following tail sits inside (0.73 m at R 5.5 m); pick one on
  purpose, drive outward swing from v*yawRate, and tune damping on the whole chain, since
  per-joint critical damping still overshot 24 percent.
- Provenance (verified/assumed): Verified first-hand with the deterministic sandbox below.
  The demo's tail spring, yaw smoothing, turn-rate limits and tail length were read from
  demos/skin-test/index.html. The elongate distal caudal prezygapophyses of herrerasaurids
  are confirmed through search summaries of Novas 1994 (J Vert Paleontol 13:400) and Novas
  1986, where they overlap the posterior half of the preceding vertebra; reading them as a
  five-times distal stiffness is this sandbox's modelling choice.
- Caveats: Tail mass, stiffness (1 Hz) and damping (zeta 0.3) are assumed values, and the
  chain is passive with no muscle control. Real cheetah tails are used actively in turns
  (Patel and Braae 2013; Patel and Boje 2015), and a source for which side a running
  theropod or cheetah tail sits on in a steady turn was not found.
- Composed: ideas:MOTION/physics/critically-damped-spring-not-fixed-duration-tween,
  ideas:PHYSICS/integration/semi-implicit-euler-conserves-what-explicit-euler-leaks
- Sandbox: sandboxes/2026-10-21__locomotion-passive-tail-swings-outside-a-turn-path-tail-inside.py
- Prediction: Written before the first run: the path-following tip sits inside by about
  L^2/(2R) = 0.74 m; the passive chain lags INSIDE briefly at turn onset and then settles
  OUTSIDE at sprint, the opposite of the brief-outward-lag claim; distal stiffening raises the
  base-two-joint bend share by at least 15 points. The integrator and per-joint damping
  scenarios were added after the first run for the kernel check.
- Observed: RESULT: PASS path-following tail sits 0.73 m inside at sprint R; passive tail lags
  INSIDE first (t=1.03s) then settles OUTSIDE -1.234 m, so the 'brief outward lag' is the
  wrong sign; walk steady -0.030 m; distal x5 stiffening moves base-joint bend share
  0.27->0.44; per-joint critical damping still overshoots 24%; explicit Euler inf vs
  semi-implicit 2.99 rad (fine-step reference 2.67 rad).
- Scenarios: 1) path-following tail at sprint and walk turn radii; 2) passive chain at sprint
  (7.4 m/s, 1.35 rad/s), BUILT TO BREAK the brief-outward-lag claim; 3) passive chain at walk
  (1.5 m/s, 2.43 rad/s); 4) a stiff 4 Hz tail at walk, built to break the outside-at-steady
  result (it stays outside but only 5 cm); 5) distal stiffening x5; 6) per-joint critical
  damping; 7) explicit vs semi-implicit Euler, undamped, 2 ms step, against a 0.1 ms reference.
- Link: session claude.ai/code/session_017uyNQEczEfzSRfCLiYvMTe (brain train kernel, LOCOMOTION loop 4)
- Cited-by: 2026-10-21 · projects/pappydapimp69__dlist.md#E7 · compatible · sandboxes/2026-10-21__locomotion-active-tail-holds-inside-the-turn-entered-by-lag.py · observed RESULT: PASS active tail wins INSIDE entered by lag: sprint steady roll 2432 vs straight 2752 vs outside 3066 N m, peak leg yaw 1662 vs straight 1682 vs outside 3555; walk steady roll 598 vs 997; base bend share 0.65; slalom break holds fo… · session claude.ai/code/session_017uyNQEczEfzSRfCLiYvMTe (owner decision on the tail-side tension, active balance)

## E4 — locomotion horizontal biped leans with its feet not its trunk
- Date: 2026-10-21
- Project: Pappydapimp69/Dlist
- Tags: [locomotion][animation][gamedev][physics][sandbox]
- What: For a horizontal-bodied biped balanced over the hip (theropod, bird-like rig), the
  usual sprint posture cues (pitch the trunk forward, straighten and lower the neck,
  straighten the tail as a counterweight) each move the fore-aft centre of mass by under
  2 cm, while accelerating at the demo's 3.0 m/s^2 needs the support 0.34 m behind the
  centre of mass (lean line 17 degrees from vertical). The physical lean of such an animal
  lives in where the feet are planted, not in how the trunk is posed.
- Why built: The Herrerasaurus demo's next round plans a walk-to-sprint posture change, and
  the question was whether posing the trunk, neck and tail can carry the balance story or
  whether foot placement must change too, before tuning any pose curves by eye.
- Design: A deterministic sandbox spreads assumed mass fractions (tail 12 to 25 percent,
  head plus neck 6 to 12 percent, legs 15 percent) along the demo's own joint chains, then
  measures fore-aft centre-of-mass shifts for rigid pitch about the hip, neck extension to
  level and tail straightening; it then applies the di Prampero acceleration lean
  (support behind the centre of mass by h*a/g) and checks it against the heel-lift leg reach
  and Alexander stride with Froude duty from dlist/E3 and dlist/E2.
- Got right: The balance arithmetic is robust to the unknown mass split: over nine splits the
  worst shift is 1.09 cm per 10 degrees of rigid pitch, neck extension is 1.03 cm, and the
  largest posture shift of all (1.68 cm) is 5 percent of the 0.34 m offset an acceleration of
  3 m/s^2 needs, so posture can be styled freely without breaking balance.
- Where/why it failed: My pre-run picture was wrong in shape: I expected rigid pitch to be
  second order (under 1 cm) and neck extension first order (about 2 cm); both came out at
  about 1 cm. The tail claim only holds for a nearly straight tail: straightening the demo
  tail (6.4 degree droop) cancels 3 to 14 percent of the neck shift, but a tail starting 30
  degrees drooped cancels 163 percent. The reach check also shows the demo's 3.0 m/s^2 is not
  sustainable everywhere: the shifted stance only fits up to 2.08, 2.15 and 1.22 m/s^2 at 2, 5
  and 7 m/s.
- Fix: Express acceleration and braking by shifting the planted-foot window backward (or
  forward) by h*a/g relative to the centre of mass, about 0.11 m per 1 m/s^2 for this rig,
  and cap acceleration by what the leg can reach at that speed; keep trunk pitch, neck and
  tail pose as a separate style layer driven by speed or intent.
- Why this fix: The foot window is the only lever large enough (tens of centimetres) to move
  the support under a level body, it reuses the reach model already verified, and keeping
  posture separate means a pose tweak cannot silently unbalance the animal, since no pose in
  the tested range moves the centre of mass more than 1.7 cm.
- Rule of thumb: In a level-bodied biped, put acceleration lean in the feet: plant the support
  h*a/g behind the centre of mass (0.34 m at 3 m/s^2) and cap a by leg reach; trunk pitch,
  neck and tail poses move it under 2 cm, so they are style, and tail straightening only
  rebalances a tail that starts well drooped.
- Provenance (verified/assumed): Verified first-hand with the deterministic sandbox below;
  joint positions and pelvis motion are copied from demos/skin-test/index.html, and the
  result holds across nine swept segment mass splits. The acceleration lean angle
  alpha = arctan(g/a) is from di Prampero et al. 2005, J Exp Biol 208:2809, and running birds
  pitching further forward with speed is from Abourachid et al. 2011 (Zoology), both checked
  through search summaries.
- Caveats: The segment mass fractions are a swept guess rather than a Herrerasaurus mass
  model. A search for running birds lowering the neck with speed found no source, so the
  neck pose is treated as a style choice here.
- Composed: dlist/E2, dlist/E3
- Sandbox: sandboxes/2026-10-21__locomotion-horizontal-biped-leans-with-its-feet-not-its-trunk.py
- Prediction: Written before the first run: rigid pitch of 10 degrees moves the centre of mass
  under 1 cm; neck extension about 2 cm forward; demo tail straightening under 20 percent of
  that; a 30 degree drooped tail comparable to the neck; acceleration of 3.0 m/s^2 needs
  0.36 m and braking 6.5 m/s^2 needs 0.78 m; heel-lift reach caps acceleration near 2 m/s^2 at
  3 to 5 m/s. Run 1 printed RESULT: FAIL (pitch 1.09 cm), run 2 tests the surviving claim.
- Observed: RESULT: PASS posture moves CoM <= 1.68 cm (0.050 of the 0.34 m support offset a=3
  m/s^2 needs): pitch 1.09 cm per 10 deg, neck extension +1.03 cm vs demo-tail straightening
  cancels 0.03-0.14 of it, a 30-deg-drooped tail cancels 1.63 (break holds); reach caps a at
  2.08/2.15/1.22 m/s^2 at 2/5/7 m/s. Braking at 6.5 m/s^2 needs support 0.73 m ahead.
- Scenarios: 1) rigid pitch of +5, +10 and -10 degrees over nine mass splits; 2) neck extension
  vs straightening the demo tail over the same splits; 3) BUILT TO BREAK the tail claim: a tail
  starting 30 degrees drooped, then straightened; 4) support offset for +1, +3 and -6.5 m/s^2;
  5) reach-limited acceleration at 1, 2, 3, 5 and 7 m/s.
- Link: session claude.ai/code/session_017uyNQEczEfzSRfCLiYvMTe (brain train combined, LOCOMOTION loop 3)
- Cited-by: 2026-10-21 · projects/pappydapimp69__dlist.md#E7 · compatible · sandboxes/2026-10-21__locomotion-active-tail-holds-inside-the-turn-entered-by-lag.py · observed RESULT: PASS active tail wins INSIDE entered by lag: sprint steady roll 2432 vs straight 2752 vs outside 3066 N m, peak leg yaw 1662 vs straight 1682 vs outside 3555; walk steady roll 598 vs 997; base bend share 0.65; slalom break holds fo… · session claude.ai/code/session_017uyNQEczEfzSRfCLiYvMTe (owner decision on the tail-side tension, active balance)

## E3 — locomotion alexander stride needs a stance reach check
- Date: 2026-10-21
- Project: Pappydapimp69/Dlist
- Tags: [locomotion][animation][gamedev][sandbox]
- What: Driving a procedural theropod's stride from speed with Alexander's dynamic-similarity
  law, stride/h = 2.3 * (v^2/(g*h))^0.3 with h = hip height, gives a sprint stride of 4.33 m at
  7.4 m/s where the demo's linear stride 0.9 + 0.33v gives 3.34 m, so the demo spins its legs
  at 2.21 Hz instead of 1.71 Hz. Taking the longer stride exposes a second limit: the foot must
  reach the whole STANCE length (duty * stride), and a two-bone leg IK with a fixed metatarsus
  cannot reach it at toe-off.
- Why built: The Herrerasaurus demo needs stride and cadence that read as a real animal at
  every speed, and the duty factor from the earlier Froude-keyed schedule (dlist/E2) has to be
  combined with a stride rule without the IK leg popping straight or the foot sliding.
- Design: A deterministic sandbox copies the demo's leg geometry (thigh 0.522 m, shin 0.539 m,
  metatarsus 0.230 m, hip 1.14 m), its pelvis drop and bob, and its landing rule (stance spans
  neutral +/- half of duty * stride). It checks that the sourced solved form
  v = 0.25 g^0.5 stride^1.67 h^-1.17 is the inverse of the stride law, compares strides, and
  measures IK overreach over the stance with a fixed metatarsus and with full heel lift (the
  metatarsus allowed to rotate so the ankle aims at the hip).
- Got right: Alexander's law in Froude form is size-free and invertible: inverting it gives
  coefficient 0.2495 against the published 0.25 with a 0.62 percent worst round-trip error, so
  the same function can both drive a gait from speed and read speed back from a trackway.
- Where/why it failed: My first-run prediction was wrong twice. The shipped demo already
  overreaches at sprint toe-off by 3.5 cm (I predicted 15 cm, ignoring the pelvis bob), and
  I predicted that even heel lift could not reach an Alexander stride with Froude duty 0.36;
  it can, with 2.2 cm to spare. What really breaks is the fixed metatarsus: with it the
  Alexander sprint stance overreaches 14.5 cm at toe-off and the reachable duty cap is 0.225,
  and the cap first binds at 1.2 m/s.
- Fix: Use Alexander's stride law for stride and cadence, and let the metatarsus rotate during
  stance (heel lift toward toe-off) instead of holding its rest angle; then cap duty at the
  reach limit, duty <= reach_cap(stride), computed from the leg chain, so a later stride or
  speed retune cannot silently straighten the leg.
- Why this fix: Heel lift adds the metatarsus to the usable reach (1.061 m to 1.291 m) right
  where the stance needs it, behind the hip at toe-off, and the sandbox shows it keeps the
  Froude duty reachable at every speed from 1.0 to 7.4 m/s, while shortening stride instead
  would bring back the high cadence.
- Rule of thumb: When a speed law sets stride, check stance length (duty * stride) against leg
  reach at toe-off, not stride; a fixed metatarsus IK is what overreaches first (duty cap 0.225
  at 7.4 m/s here), and stance heel lift restores reach (cap 0.375) without shortening stride.
- Provenance (verified/assumed): Verified first-hand with the deterministic sandbox below,
  using geometry and formulas copied from demos/skin-test/index.html. Alexander's law
  (Alexander 1976, Nature 261:129-130) is confirmed through its published solved form with the
  0.25, 1.67 and -1.17 constants found in secondary teaching sources by search; the primary
  paper's full text was not reachable from this session, which is why the sandbox checks the
  two forms against each other. Real-animal heel-lift kinematics are named as a design choice.
- Composed: dlist/E2
- Sandbox: sandboxes/2026-10-21__locomotion-alexander-stride-needs-a-stance-reach-check.py
- Prediction: Written before the first run: inverse coefficient about 0.249 with round trip
  within 1 percent; Alexander stride 1.30 m at 1.0 m/s, 2.71 m at 3.4 m/s, 4.33 m at 7.4 m/s;
  sprint cadence 1.71 Hz vs demo 2.22 Hz; demo sprint overreach about 15 cm at toe-off; and
  Alexander stride plus Froude duty overreaching both ends even with full heel lift, with a
  reachable duty near 0.3. The first two held; the overreach magnitude and the heel-lift case
  came out wrong (run 1 printed RESULT: FAIL), and run 2 tests the surviving claim.
- Observed: RESULT: PASS stride law inverts to 0.25 coef within 0.62%; sprint stride alexander
  4.33 m vs demo 3.34 m (cadence 1.71 vs 2.21 Hz); demo toe-off overreach +0.035 m;
  alexander+froude duty with fixed metatarsus overreaches +0.145 m at toe-off (duty cap 0.225,
  binds from 1.2 m/s), with heel lift reaches (margin 0.022 m, cap 0.375).
- Scenarios: 1) solved-form inverse round trip at five speeds; 2) Alexander vs demo stride and
  cadence from 1.0 to 7.4 m/s; 3) the demo as shipped at sprint (fixed metatarsus); 4) BUILT TO
  BREAK the claim: Alexander stride with Froude duty 0.36 at 7.4 m/s, fixed metatarsus vs full
  heel lift; 5) reach-capped duty swept from 1.0 to 7.4 m/s for both foot models.
- Link: session claude.ai/code/session_017uyNQEczEfzSRfCLiYvMTe (brain train combined, LOCOMOTION loop 2)
- Cited-by: 2026-10-21 · projects/pappydapimp69__dlist.md#E4 · compatible · sandboxes/2026-10-21__locomotion-horizontal-biped-leans-with-its-feet-not-its-trunk.py · observed RESULT: PASS posture moves CoM <= 1.68 cm (0.050 of the 0.34 m support offset a=3 m/s^2 needs): pitch 1.09 cm per 10 deg, neck extension +1.03 cm vs demo-tail straightening cancels 0.03-0.14 of it, a 30-deg-drooped tail cancels 1.63 (break… · session claude.ai/code/session_017uyNQEczEfzSRfCLiYvMTe (brain train combined, LOCOMOTION loop 3)
- Cited-by: 2026-10-21 · projects/pappydapimp69__dlist.md#E6 · compatible · sandboxes/2026-10-21__locomotion-predictive-foot-target-must-predict-heading-too.py · observed RESULT: PASS no prediction skids at 7.48 m/s at sprint touchdown, velocity prediction 0.000; accel skids 0.426 until the centring speed is frozen at lift-off (0.006); in turns velocity-only still skids 1.05 m/s sprint / 1.31 walk (= omega*… · session claude.ai/code/session_017uyNQEczEfzSRfCLiYvMTe (brain train combined, LOCOMOTION loop 5)

## E2 — locomotion walk run switch by froude not top speed fraction
- Date: 2026-10-21
- Project: Pappydapimp69/Dlist
- Tags: [locomotion][animation][gamedev][physics][sandbox]
- What: A procedural biped gait (Herrerasaurus skin-test demo) sets its duty factor as a
  straight lerp over fraction of top speed, duty = lerp(0.64, 0.38, v/7.4). The duty factor
  only falls below 0.5 (first aerial phase) at 3.98 m/s, which for a 1.15 m leg is Froude
  number 1.41, so the animal shows a walking footfall pattern far past the speed where a
  rigid-leg walk can physically exist.
- Why built: The demo needs one gait clock that blends walk to sprint for a 5.2 m theropod
  with a 1.15 m hind limb, and the duty-factor curve decides when both feet leave the ground,
  which is what reads as running to a player.
- Design: A deterministic sandbox models two legs offset by half a cycle to get support
  fractions from duty factor, then a point mass vaulting over a rigid leg with energy
  conservation across the stance arc to find the highest midstance speed with a non-negative
  leg force, and finally runs the demo's own duty and stride formulas against that ceiling.
- Got right: Duty factor is the right single knob: the sandbox confirms aerial fraction is
  exactly max(0, 1 - 2*duty) and double support is max(0, 2*duty - 1), so 0.5 is a hard
  boundary between walking and running footfalls with no third case for two legs.
- Where/why it failed: Tying duty to v / top_speed puts the 0.5 crossing wherever the game's
  speed cap happens to be. The rigid-leg ceiling is Fr = 1 only for a vanishing stance arc;
  with a real stance half-angle th0 the leg force goes negative first at the ends of stance,
  giving Fr_mid <= 3cos(th0) - 2 (0.60 at 30 degrees, 0.67 at the demo's 27 degrees). The
  demo walks with negative leg force from 2.83 to 3.98 m/s, and its non-sprint top speed of
  3.4 m/s is Fr 1.02 with duty 0.52.
- Fix: Drive duty factor from Froude number Fr = v^2 / (g * leg_length), centred so duty
  passes 0.5 at Fr about 0.5 (the measured walk-run switch in humans and other bipeds), for
  example duty = 0.5 + 0.14 * tanh((0.5 - Fr) / 0.25). For the demo's 1.15 m leg that puts
  the switch at 2.38 m/s instead of 3.98 m/s.
- Why this fix: Froude number makes the switch size-independent (dynamic similarity), so
  the same curve works for a 0.25 m leg (switch 1.11 m/s), a human 0.9 m leg (2.10 m/s) and
  the 1.15 m theropod (2.38 m/s) with no per-species retuning, and it stays below the
  finite-arc pendulum ceiling instead of above it.
- Rule of thumb: Schedule a biped's duty factor on Froude number v^2/(g*leg), crossing 0.5
  near Fr 0.5, never on fraction of top speed; a rigid-leg walk fails below Fr 1 once the
  stance arc is real, since leg force first goes negative at stance ends (Fr_mid <= 3cos(th0)-2).
- Provenance (verified/assumed): Verified first-hand with the deterministic sandbox below
  (support fractions, pendulum ceiling by bisection, demo formulas read from
  demos/skin-test/index.html). The Fr about 0.5 walk-run switch across bipeds and the
  Fr = 1 inverted-pendulum ceiling were checked against published sources found by search
  (Kram et al. 1997 J Exp Biol 200:821; Usherwood 2005 Biol Lett; Hancock et al. 2007 on
  tinamous, Fr 0.4 to 0.6). The tanh curve shape is a design choice, not a measured curve.
- Composed: N/A
- Sandbox: sandboxes/2026-10-21__locomotion-walk-run-switch-by-froude-not-top-speed-fraction.py
- Prediction: Aerial fraction equals max(0, 1 - 2*duty); demo duty crosses 0.5 at 3.98 m/s
  = Fr 1.41; rigid-leg ceiling Fr 1.00 at zero arc; with a finite arc the ceiling follows
  3cos(th0) - 2, about 0.60 at 30 degrees and about 0.67 at the demo's 27 degrees; Froude-0.5
  switch at 2.37 m/s for L = 1.15 m and 2.10 m/s for a 0.9 m human leg.
- Observed: RESULT: PASS aerial phase iff duty<0.5; ceiling Fr=1 only at zero arc,
  3cos(th0)-2 otherwise (0.60 at 30 deg); demo duty crosses 0.5 at 3.98 m/s = Fr 1.41,
  walking-impossible band 2.83-3.98 m/s; Froude-0.5 switch is 2.38 m/s. Ceiling Fr_mid
  0.954/0.819/0.673/0.598/0.457 at 10/20/27/30/35 degrees.
- Scenarios: 1) support fractions at duty 0.70/0.55/0.50/0.45/0.38; 2) rigid-leg ceiling with
  a vanishing stance arc (Fr 1.000); 3) BUILT TO BREAK the Fr = 1 ceiling: finite stance
  half-angles 10 to 35 degrees, where the ceiling drops to 0.46 to 0.95; 4) the demo's own
  duty and stride schedule from 0 to 7.4 m/s; 5) the Froude schedule at three leg lengths.
- Link: session claude.ai/code/session_017uyNQEczEfzSRfCLiYvMTe (brain train newdomain, LOCOMOTION seed)
- Cited-by: 2026-10-21 · projects/pappydapimp69__dlist.md#E3 · compatible · sandboxes/2026-10-21__locomotion-alexander-stride-needs-a-stance-reach-check.py · observed RESULT: PASS stride law inverts to 0.25 coef within 0.62%; sprint stride alexander 4.33 m vs demo 3.34 m (cadence 1.71 vs 2.21 Hz); demo toe-off overreach +0.035 m; alexander+froude duty with fixed metatarsus overreaches +0.145 m at toe-of… · session claude.ai/code/session_017uyNQEczEfzSRfCLiYvMTe (brain train combined, LOCOMOTION loop 2)
- Cited-by: 2026-10-21 · projects/pappydapimp69__dlist.md#E4 · compatible · sandboxes/2026-10-21__locomotion-horizontal-biped-leans-with-its-feet-not-its-trunk.py · observed RESULT: PASS posture moves CoM <= 1.68 cm (0.050 of the 0.34 m support offset a=3 m/s^2 needs): pitch 1.09 cm per 10 deg, neck extension +1.03 cm vs demo-tail straightening cancels 0.03-0.14 of it, a 30-deg-drooped tail cancels 1.63 (break… · session claude.ai/code/session_017uyNQEczEfzSRfCLiYvMTe (brain train combined, LOCOMOTION loop 3)
- Cited-by: 2026-10-21 · projects/pappydapimp69__dlist.md#E6 · compatible · sandboxes/2026-10-21__locomotion-predictive-foot-target-must-predict-heading-too.py · observed RESULT: PASS no prediction skids at 7.48 m/s at sprint touchdown, velocity prediction 0.000; accel skids 0.426 until the centring speed is frozen at lift-off (0.006); in turns velocity-only still skids 1.05 m/s sprint / 1.31 walk (= omega*… · session claude.ai/code/session_017uyNQEczEfzSRfCLiYvMTe (brain train combined, LOCOMOTION loop 5)

## E1 — shader uniform array must alias sim state
- Date: 2026-10-20
- Project: Pappydapimp69/Dlist
- Tags: [gamedev][shaders][state][testing]
- What: A three.js skin shader read wet and mud levels from uniform float arrays
  (one value per body-height band), while the sim wrote those levels into its own
  separate Float32Arrays, so the shader saw zeros forever and no effect ever drew.
- Why built: The Herrerasaurus skin test needed wetness, wet mud, dried crust and
  flaking to vary up the body by wading depth, driven by sim timers (8 s dry, 30 s walk).
- Design: Sim state owns per-band arrays; material uniforms hold Float32Array values
  uploaded each frame by three.js; the fragment shader interpolates bands by bind-pose
  height.
- Got right: The sim logic and timers were correct: a headless state probe showed wet
  0.83 after leaving water, mud cover 1.0, dry reaching 1.0 at 8 s and flake rising
  after 30 s walked, and flake particles spawned on schedule.
- Where/why it failed: The uniform objects were created with their own new
  Float32Arrays and nothing copied sim values into them, so every state-level check
  passed while the rendered skin never changed; only reading screenshots exposed it.
- Fix: Make the sim arrays BE the uniform arrays (state fields reference
  skinU.uWet.value etc.), so three.js uploads the live values with no copy step.
- Why this fix: Aliasing removes the copy step entirely, so there is no second writer
  or forgotten sync to drift; three.js re-uploads array uniforms every render anyway.
- Rule of thumb: When sim state drives a shader uniform array, alias the same typed
  array instead of copying, and verify the effect in a rendered frame, because a
  state probe passes even when the GPU never receives the values.
- Provenance (verified/assumed): verified first-hand in headless Chromium (SwiftShader):
  state probe correct and screenshots unchanged before the fix; wet gloss and mud crust
  visible in screenshots after aliasing the arrays.
- Composed: N/A
- Link: Pappydapimp69/Dlist commit 9c7260d (demos/skin-test/index.html); session_017uyNQEczEfzSRfCLiYvMTe

