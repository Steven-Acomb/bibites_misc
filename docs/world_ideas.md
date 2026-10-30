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
- Current settings, for reference: `worldWrapping` is on and `voidAvoidance`
  is off. Worth knowing what the rim actually does to a bibite before relying
  on void risk.
