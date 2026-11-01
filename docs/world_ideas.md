# World ideas for evolving sensing

Goal: behavior driven by what the bibite sees, without changing the
NeuronBox v2 structure. The structure can already express it: every input
feeds every L1 neuron.

**Why surroundings lose so far** (measured, see
`bibites/neuronbox_v2/runs/README.md`):
1. **Scale.** A weight's effect is weight × the input's range. TimeAlive and
   Speed span tens of units, while senses span ≤1.
2. **Little reward for seeing better.** Easy Herbivore's reflexes already
   steer toward the nearest plant. PlantAngle only ranges ±0.09 because the
   PlantAngle→Rotate reflex keeps food straight ahead.

The 2025 run's senses stayed ~10× weaker than its own-state inputs after 875
generations. Track this with the "surroundings" lines of `tools/run_stats.py`.

## Steve's plans

- **Predators.** `NeuronBox_v2_Carnivore.bb8template` already exists. The
  plan: a meat world, gradually less meat and more random bibite spawns,
  until real predators evolve; then they co-evolve with the herbivores.
- **Reduce the amount of plants.**
- **Make the Center zone barren**, for diversity and because handling
  empty, risky areas is itself a selection pressure that rewards sensing.
- **The full staged plan (2026-11-01):**
  1. Herbivores to plateau.
  2. Step the Center down to barren, then plateau again.
  3. A meat-mirror hex world for carnivores: plateau, then lower global
     fertility and possibly raise virgin spawns until near-pure predators
     evolve.
  4. Bring the predators into the herbivore world with the Center as a
     normal meat zone, plateau, then ramp the Center back down to void. The
     result is a ring world with predator/prey dynamics.
- **Way down the road:** turn pheromone production cost off.
- **After the ring world is done:** try the settings animators (new since
  the 2025 run).
- **Population size stays.** It's already near what the game can
  meaningfully support, from Steve's experience.
- **Design intent:** every choice so far aims to push the plateau as high as
  possible, e.g. free brains, so behavioral improvements keep paying after
  bodies settle.

## Claude's suggestions (2026-10-30, unverified hypotheses)

1. **Danger you have to see coming.** Predators make BibiteCloseness,
   BibiteAngle and AttackedDamage worth reacting to, and the base wiring has
   no avoidance reflex. They need to be an effective threat: the 2025 run had
   5–20% carnivores from gen 357 and bibite-sensing stayed small
   (NBibites ~0.02).
2. **Food you have to choose between within view.** Different food values
   side by side, so turning toward the right one beats turning toward the
   nearest. The hex zones vary by zone, not within view.
3. **Food that isn't where it was.** Slowly moving zones or patchy,
   short-lived food, so habits fail and seeing wins. Probably weaker than #1,
   since the base reflex already chases visible food.

### Claude's input on Steve's plans

**Reducing plants:**
- Stronger selection overall: finding food matters more when it's scarce.
- Fewer bibites as a side effect. That means faster sim ticks (more
  generations per real hour) but fewer lines at once.
- Uniformly thinner food mostly rewards *searching* while nothing is in
  view, and internal rhythms (time and speed controllers) can solve that
  without sensing. Making food **patchier** (clumps with empty space between)
  likely rewards seeing more: a clump in view is worth turning to, empty
  space is worth leaving.
- Lower it gradually, as in the predator plan, to avoid a crash during AFK
  runs.

**Barren Center:**
- It creates an area where the right move depends on what you see:
  NPlants/PlantCloseness at 0 means turn back or keep going.
  - Easy Herbivore has no reflex for "no plant in view", since PlantAngle→Rotate
    does nothing then.
  - So that response has to come from new wiring, and the added layers are
    the obvious place.
- No input senses the world edge or "void" directly. Bibites would have to
  infer emptiness from absent food and bibites.
- Diversity:
  - The six outer zones still touch their neighbours in a ring. Removing the
    Center removes the hub that links all of them, so opposite zones are
    3 hops apart instead of 2.
  - Whether that measurably slows sweeps is unknown. One run can't separate
    it from noise; see the 2025 sweep baseline.
- Removing the Center also removes 1/7 of the plants unless the other zones
  get it back, so it doubles as a first step of "reducing plants".

## Claude's suggestions for raising the practical plateau (2026-11-01)

**The ceiling.** The brain is a discrete-time recurrent network (3 sine
layers, self-loops, L3→L1 and output→L1 feedback), so in practice a
finite-state controller. Its building blocks:
- **Latches:** a sine self-loop with weight ~1–2.26 holds 1 bit.
- **Leaky memories:** self-loop weight < 1.
- **Oscillators:** weight > 2.26, or the feedback loops.
- **Clocks:** sine of TimeAlive or Minute.

What evolution actually finds is likely well below that ceiling, because
each step has to pay. World-only levers, roughly in order of impact:

1. **Make memory and modes pay.** Pure reflexes are nearly optimal when food
   sits still in view. Situations where the right action depends on the
   past or on something out of view:
   - food beyond view range (patchy food, barren areas);
   - food that moves or changes over time (zone movement, settings
     animators);
   - intermittent danger (predators);
   - delayed choices (see the egg-laying threshold in the runs README).
2. **Pheromones as external memory.** A trail stores information in the
   world. It outlasts any internal latch and is shared, so brain plus
   environment can do more than the brain alone.
3. **Gradual changes.** Each intermediate step needs a reward. Abrupt harsh
   changes mostly select for blunt survival traits.
4. **More search** (population, mutation step size) would help, but
   population is at the game's practical limit (Steve). Larger mutation
   steps also break working circuits more often, and infant mortality is
   already 84%.

### Research notes from the game's code (decompiled v0.6.3.1)

**Pheromones** (`BibitePheromoneOrgan`, `PheromoneSpot`, `Pherosense`):

- **Production.** PhereOut1–3 are ReLU outputs. Once a second, if
  Σ output × production rate > 0.05, the bibite drops a spot with strength
  output × `pheromoneProductionStrength`. The spot also records the
  depositor's facing direction.
  - Energy cost = Σ strength × `pheromoneProductionCost` per drop.
  - In this world: rate 10, cost 0.01, so full output on one channel costs
    0.1 E/s.
- **Decay.** Strength drops linearly by 0.25 per second. A full-output
  spot lasts ~40 s at rate 10, up to ~400 s at the maximum rate of 100.
  So **the production rate setting also sets how long trails last.**
- **Sensing.** It covers all directions within the PheroSense gene's radius;
  it is not limited to the view cone.
  - Each spot counts as strength ÷ distance.
  - Inputs are PheroSense = tanh(Σ / 5), the angle to the strength-weighted
    centre, and the averaged heading of the depositors (Phero*Heading).
- **Already in use at 11-01:**
  - 116 of 515 bibites produce channel 3 (blue) and ~30 each produce red
    and green; 504 spots in the world.
  - The PheroSense radius gene rose +44% since the hex swap
    (directionality 1.00).
  - Phero3Angle is the top "surroundings" input in the sweep.
- **Related settings:** the "Prevent Red/Green/Blue Pheromone Production"
  toggles, and `enableRedDeath` (off; when on it injects red pheromone near
  a shrinking safe radius).

**Settings animators** (`SettingsChanger`, `SettingsChangerManager`):

- An animator multiplies the base value of one or more settings by a curve
  over **sim time**.
  - The curve is a spline: points (t, factor) with an interpolation type
    and ease.
  - It has a start time and an optional repeat. Repeating cycles forever;
    non-repeating animators are deleted after their last point.
- **What can be animated:** every numeric field of every **zone**:
  - fertility, biomass density, pellet size, movement speed;
  - position X/Y, radius (relative/absolute), inside radius;
  - rectangle width/height.

  An animated setting is locked from manual editing while animated. I found
  no global (non-zone) settings in the animatable list.
- **Saved** in the world's settings under `settingsChangers`. The loader
  reads it only from files of version ≥ 0.6.3.3.
  - **⚠ Test before relying on this.** Saves record the game version, and
    Steve's saves say `0.6.3.1`. If that's what this build writes, animators
    might be silently dropped when a save is reloaded.
  - To test: make a throwaway animator, save, reload, and see whether it
    survives. (Unverified reading of `SerializationHelper.DeserializeScenario`.)
- **Ideas these enable:**
  - seasons (cycling fertility per zone, possibly out of phase between
    zones);
  - drifting or resizing zones;
  - a gradual ramp, e.g. the barren-Center step-down as one smooth
    animator instead of manual steps.

**Zone options** (`ZoneSettings`):
- **Movement:** None, Free (wanders), or Locked to Target (follows another
  zone), with a speed.
- **Distributions:** Flat circle, Center-to-edge, Edge-to-center, Ring
  (density 0 at the edges), Flat ring, Rectangle.

## Void settings are deliberate (Steve, 2026-10-31)

- **`voidAvoidance` off.** When on, an automatic safeguard overrides bibite
  behavior to keep them inside fertile zones, like bowling-lane gutter guards.
- **`worldWrapping` on.** No artificial "dies if it crosses this line" edge.
  Hard hazards like that can be added deliberately in controlled places, and
  Steve is choosing not to.
- **The void's real danger is starvation.** That leaves room for interesting
  adaptations: crossing the void (fat stores plus smart turning) versus
  avoiding it, possibly as different strategies in different lines.
