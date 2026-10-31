# How the game runs a bibite brain (measured)

Verified 2026-10-21 on game v0.6.3.1 with `bibites/probes/BrainProbe.bb8template`
(built by `tools/make_probe.py`). Evidence: saved bibites
`Brainprobe_brainprobe_saved0.bb8` and `_saved1.bb8` from the game's `Bibites\` folder.

| Fact | Evidence |
|---|---|
| **Feed-forward signals cross any depth in the same brain tick.** Nodes are evaluated in dependency order, not list (Index) order. | After 1 tick, chains F1→F2→F3 and R1→R2→R3 (R created in reverse Index order) all equal the input; difference nodes read exactly 0. |
| **Cycles feed back the previous tick's value.** | Self-loop sine nodes settle exactly at the fixed points of x → sin(w·x + b): w=0.5 → 0.1974, w=2.0 → 0.9273 (latch); w=3.0 keeps bouncing (LastInput = 3·x_prev + 0.1). |
| **`baseActivation` is a bias added before the activation function.** | Sine node with bias 0.5 and zero input reads sin(0.5) = 0.4794, LastInput 0.5. |
| **Brain tick rate ≈ 20 Hz** in a default world. | Linear node with bias 1 + self-loop 1 counted 176 after 8.75 s alive. |
| **Culling:** on load the game deletes hidden nodes lacking a path from an input *and* a path to an output. Weight-0 synapses count; self-loops do not. | Probe v1 (no output links) lost all probe nodes; v2 lost the nodes with no input-side edges. |
| **TimeAlive input is in minutes.** | Input 0.1442 at ~8.65 s alive. |
| **Saved `.bb8` files record live state**: each node's `Value`, `LastInput`, `LastOutput`; `clock.timeAlive`. Easiest way to read a brain. | — |
| **Version-0.6 files get RotationSpeed inserted on load** at Index 5, shifting every later node (biases, types, synapse endpoints). A file that already has RotationSpeed must say version "0.6.2" or it gets inserted twice. | NeuronBox_v2 first build: Accelerate's bias landed on Rotate → spun in place; save showed 87 nodes and a duplicate Want2Attack. |
| **Hidden-node anchor y uses input-slot units (~1–32)**, not 0–1; x is 0 (inputs) … 1 (outputs). | v2 first build with y in 0–1 piled every hidden node at the top. |
| **`BrainAverageMutation` is capped at 10** (brain mutations per birth). | NeuronBox_v2 template set 40; the spawned bibite had 10. No bibite in the 2025 run exceeded 10. |
| **Want2Attack is bite strength (sigmoid, 0–1).** Below 0.15 there is no attack. Above it, the bibite bites anything in or entering its mouth, and keeps draining a target it bit last tick. The game's default activation is 0.1618. With bias 0 and no inputs (Easy Herbivore and both v2 templates), it sits at 0.5, so they always bite at half strength. | In-game tooltip (screenshot 2026-10-31). |
| **Layout (`nodeAnchors`) lives only in templates**, keyed by node Inov; in-game rearranging isn't saved to `.bb8`. The game renumbers node Inovs on load. | — |

## Self-loop regimes for a sine neuron, x → sin(w·x + input)

| w | behavior |
|---|---|
| 0 – 1 | leaky: decays toward its input |
| 1 – ~2.26 | bistable latch near ±0.9 (1-bit memory) |
| > ~2.26 | period-doubling / chaos; at 20 Hz this is flicker, i.e. noise |

Slow rhythms instead come from sine of the time inputs (TimeAlive, Minute, Tic):
weight w from TimeAlive into a sine neuron gives a period of 2π/w minutes.

## Feeding mechanics (from the game's code)

Read 2026-10-31 from the decompiled `BibitesAssembly.dll` (v0.6.3.1,
`BibiteMouth`, `NEATBrain.UpdateSenses`, `FieldOfView`). The decompiled
source is kept locally only (git-ignored `research_private/`); this is a
paraphrase.

**Mouth size and jaws**
- Throat width = √(throat organ area), which comes from ThroatWAG.
- Jaw area = body area × the jaw's share (MouthMusclesWAG); jaw mass is
  proportional to jaw area.
- Jaw strength = bitingPressure × (jaw area × metabolic rate)^(jawMusclesSizingPower / 2).
- Bite period = √(throat width × jaw mass / jaw strength) × 70 × bitePeriodFactor.
  The bite timer fills up to one period and doesn't bank beyond it.
- The mouth's catch zone is wider for herbivores: its length is 7 − 8 × Diet
  when Diet < 0.5, and 3 otherwise.

**Each tick, for each object in the mouth (nearest first):**
- **Swallow attempt.** The bibite tries to swallow if Want2Eat > 0.15 and
  the bite timer is full. Mouth opening = Want2Eat × throat width.
  - A pellet with radius ≤ opening/4 is swallowed whole and doesn't use up
    the bite timer.
  - A pellet with radius ≤ opening/2 is swallowed whole but uses one bite
    period.
  - A larger pellet can't be swallowed.
  - A whole live bibite can be swallowed if its body length ≤ the opening
    (half the opening costs a bite period). The swallower gets its stomach
    contents plus its energy as meat.
  - **Swallowing never needs Want2Attack.**
- **Bite.** If swallowing didn't happen (or wasn't attempted) and
  Want2Attack > 0.15, the bibite bites, once per bite period.
  - Bite force = jaw strength × Want2Attack.
  - The chunk size comes from force / (opening × the material's
    cohesiveness), limited by the target's radius.
  - **Pellets:** the opening is the Want2Eat mouth opening. If Want2Attack >
    Want2Eat the chunk is ripped off as a separate pellet; otherwise it goes
    into the stomach.
  - **Live bibites:** the opening is Want2Attack × throat width, scaled by
    the target's internals-to-effective-radius ratio. The target's armor
    strength is subtracted from the first bite's force, and there is no
    damage if bite force ≤ armor.
  - Damage = bitingDamageFactor × target max health × chunk area / target
    body area.
  - While a bite continues on the same target, each tick deals damage ×
    dt / (5 × bite period), with no wait. The meat produced goes into the
    stomach if it fits.
  - A bibite with 50+ kills whose total victim area ≥ 50 × its own area
    becomes a "Reaper".
- **Vomit.** Want2Eat < −0.15 makes the bibite vomit, once per bite period.

**Inputs (`NEATBrain.UpdateSenses`)**
- Red/Green/BlueBibite = the raw ColorR/G/B genes of a bibite in view
  (selected in `FieldOfView`). They are **not** normalized by brightness.
- Speed = normalized velocity.
- Minute = clock chrono time / 60.
- TimeAlive = time alive / 60.
- NBibites/NPlants/NMeats = count in view / 4.
- PheroSense = tanh(sum / 5).
- BibiteCloseness/Angle and PlantCloseness/Angle are weighted
  *concentrations* over everything in view, not just the nearest object.
