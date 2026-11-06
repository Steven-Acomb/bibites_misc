# NeuronBox v2 runs

**Terms used below:**
- **"The box":** everything NeuronBox v2 adds to Easy Herbivore. That is the
  36 sine neurons L1N1–L3N12 (3 layers of 12) and their 1,224 synapses, all
  starting at weight 0. It excludes Easy Herbivore's own 15 synapses and its
  Hidden0/Hidden1.
- **"Box push":** the input an output neuron currently receives from L3,
  i.e. Σ weight × L3 neuron value.

## Planned: carnivore phase (on the roadmap, not cancelled)

`NeuronBox_v2_Carnivore.bb8template` (built with `make_neuronbox.py --carnivore`)
was checked in-game on 2026-10-22: brain intact, eats meat.

Steve's plan, once the herbivores have reached a reasonable point:
1. Pause the herbivore run.
2. Create a mirrored world for the carnivores whose zones spawn meat
   instead of plants.
3. Let them evolve there while slowly lowering the meat zones' fertility
   and raising the spawn rate of random virgin bibites.
4. Goal: real predators, later co-evolving with the herbivores.

**GreenBibite → Want2Eat.** In Easy Herbivore this is −0.843: a bibite eats
less when the nearest bibite is green. Steve calls it the devs' "green flag"
(literally) that evolution is working, and both runs' winners turned green
to exploit it. The 2025 carnivore flipped the sign but had +0.3829782, which
looks like a hand-editing slip (0.84 → 0.38). On 2026-10-31 the v2
carnivore was rebuilt with the exact mirror, +0.842978239.
Checked whether 0.383 was engineered against the output function. Want2Eat
is TanH with bias 1.228, so it outputs 0.842 with no green in view.
- At full green, 0.383 gives 0.923 and the mirror gives 0.969. Tanh
  saturates near 1, so the two behave almost alike.
- No transfer-function logic explains 0.383; the matching digit tail
  (…29782) points to a slip.

**2026-10-31 carnivore rebuild:**
- BibiteAngle → Rotate was flipped to +0.127 (turn toward bibites),
  matching every official hunting template.
- GreenBibite → Want2Eat stays at +0.843.
- Want2Attack and mouth size are left as is until we understand what those
  values do in-game.

**The game's own carnivore templates, for comparison (2026-10-31).**
Official templates Squalus nova, Vulture, Scorpion, Parasite and Seeker
shooter, plus Nigel in v0.5 format. Squalus nova is described as having
evolved to kill.

| | Squalus nova (shark) | Parasite | Seeker shooter | Nigel | Vulture (scavenger) | v2 carnivore |
|---|---|---|---|---|---|---|
| BibiteAngle → Rotate | **+11.3** | +2.5 | +0.77 (off) | +1.26 (concentration angle) | none (BibiteCloseness → Rotate −0.69) | −0.127 (inherited) |
| GreenBibite → Want2Eat | **+1.27** | — | — | — | — | +0.843 |
| Want2Attack inputs | bias +5, Tic −15 | BibiteCloseness +3.5, MeatCloseness +5.7, Fullness −5.8 | MeatCloseness +2.8, bias −2.8 | bibite concentration +2.7 | Speed +1.1, hidden +1 | none (bias 0 → constant 0.5) |
| Mouth muscles | 7.6 | 2.1 | 6.4 | — | 9.0 | 1.5 |

Every one that hunts steers toward bibites, and every carnivore wires
Want2Attack to something. Squalus, Vulture and Easy Herbivore all share the
Want2Eat bias of 1.228, which suggests a common dev-made base.

## Reference: sweeps in the 2025 NeuronBox 1 run

Steve: a lucky descendant line taking over from a rough starting species is
expected behavior, the system finding a lower energy state, and it keeps
happening for a long time. The 2025 run confirms it.

For each `Neuron_Box_Test_1_*` save on the A: drive, the most recent species
that every living herbivore descends from:

| Save | Sim h | Gen max | Common ancestor from gen | Generations back |
|---|---|---|---|---|
| 07-19 13:00 | 72 | 76 | 37 | ~39 |
| 07-20 | 131 | 137 | 89 | ~48 |
| 07-23 | 277 | 289 | 194 | ~95 |
| 07-26 15:00 | 359 | 357 | 285 | ~72 |
| 07-31 | 467 | 478 | 378 | ~100 |
| 08-08 | 630 | 638 | 538 | ~100 |
| 08-11 | 679 | 676 | 609 | ~67 |
| 09-07 (final) | 878 | 875 | 817 | ~58 |

- The whole population coalesced within ~40–100 generations at every point.
  Sweeps never stopped.
- Both runs make ~1 generation per sim-hour.
- v2 at 10-30 (gen 62: 97% from gen 36) is in line with 2025 at a similar
  stage (gen 41: 90% from gen 17).

**Ancestry depth over time (2026-11-01).** Measured at species
resolution from each save's species tree:
- **Whole population:** how many generations back everyone alive shares one
  ancestor species.
- **Pairwise:** the mean over random pairs of how far back each pair shares
  an ancestor.

| Run / save | Alive | Gen median | Whole population | Pairwise mean |
|---|---|---|---|---|
| 2025 07-19 | 308 | 71 | 34 | 19 |
| 2025 07-20 | 310 | 127 | 38 | 31 |
| 2025 07-23 | 537 | 283 | 89 | 54 |
| 2025 07-26 | 533 | 352 | 67 | 48 |
| 2025 07-31 | 1052 | 468 | 90 | 55 |
| 2025 08-08 | 1256 | 623 | 85 | 66 |
| 2025 08-11 | 1127 | 669 | 60 | 42 |
| 2025 08-24 | 1037 | 690 | 81 | 44 |
| 2025 09-07 | 1256 | 870 | 53 | 48 |
| v2 10-26 | 529 | 43 | 43 (seed) | 30 |
| v2 10-30 | 626 | 53 | 52 (seed) | 18 |
| v2 11-01 | 515 | 64 | 28 | 14 |

- In 2025, pairwise depth roughly doubled over the first ~300 generations
  (~20–30 → ~50), then held at ~42–66 for the rest of the run, while the
  population grew ~4×.
- Pairwise depth (~50 generations) is far below the census population
  (500–1,250). Pure neutral drift in a population that size would give a
  depth on the order of the population size, so takeovers are much faster
  than drift alone would produce. That is consistent with selection and/or
  very uneven reproduction.
- Sudden drops mark takeovers: 2025 08-08 → 08-11 (66 → 42) and v2
  10-30 → 11-01 (18 → 14).

**"Adapted enough?" signals (2026-11-01).**

**The 2025 run was not fixed-settings.**
- Mutation settings changed several times: background variance, synapse
  vs neuron share, relativity.
- Meat decay was changed repeatedly.
- Carnivores were added at 07-26, and a plant zone ("Zone 1") at 07-27.
- So its population rise (~300 → ~1,250) is partly the added food, not
  only adaptation. It can't calibrate plateau timing cleanly.
- The one clean stretch is 07-20 → 07-26, with no settings changes:
  herbivores went 310 → 533 while standing plant energy fell 435 → 215 kE
  (1,405 → 405 E per herbivore), a real efficiency gain over gens ~127–352.

**v2, standing plant food in zones, with fixed settings since the hex swap:**

| Save | Sim h | Gen median | Alive | Plant energy on ground (kE) | Per bibite (E) |
|---|---|---|---|---|---|
| p4 | 29.0 | 34 | 485 | 1,145 | 2,360 |
| p10 | 40.9 | 40 | 432 | 775 | 1,795 |
| 10-26 | 44.8 | 43 | 529 | 640 | 1,210 |
| 10-28 | 54.0 | 46 | 572 | 680 | 1,185 |
| 10-30 | 64.4 | 53 | 626 | 485 | 775 |
| 11-01 | 77.6 | 64 | 515 | 455 | 885 |

Still trending down, so not plateaued.

**Correction (2026-11-01):** a pellet's `amount` is material, not energy.
Plant material holds 5 E per unit and meat 10 (world material settings), so
these tables now show energy, ×5 the earlier figures.
- The earlier claim that ungrazed pellets "hold only 20% of their size" was
  wrong: they are full size, and an ungrazed zone sits at its whole biomass
  cap.
- `run_stats.py`'s zone food % was numerically right all along and now uses
  the real conversion.

**The game's own log (`tools/game_log.py`, 2026-11-01).** Every save's
`data.bin` holds the game's statistics, logged every 60 sim-seconds from the
start of the world and downsampled with age. It's a regular series that
doesn't depend on when saves happen.

Bibite share of total energy, where the total is bibites + plants + meat +
free (unspawned) biomass:

| v2 sim h | 31 | 39 | 47 | 55 | 63 | 71 | 75 |
|---|---|---|---|---|---|---|---|
| bibite share | 28.1% | 28.5% | 31.5% | 34.1% | 35.3% | 32.4% | 31.7% |

| 2025 sim h | 168 | 216 | 288 | 336 | 432 | 528 | 624 | 720 | 816 | 864 |
|---|---|---|---|---|---|---|---|---|---|---|
| bibite share | 17.5% | 22.2% | 26.9% | 27.2% | 30.4% | 34.5% | 34.2% | 31.2% | 31.4% | 32.5% |

- The 2025 run rose to ~31–35% by ~430 h and then held there for the rest
  of the run, through its settings changes.
- 2025's 384 h point (88.8 ME total, 4,528 bibites) is the 07-26 mass
  carnivore spawn.
- **v2 per doubling of time since the hex swap** (mean share): 34.9–41.0 h
  29.0%, 41.0–53.2 h 30.3%, 53.2–77.6 h 32.6%. Gains per doubling are +1.3
  then +2.3 points, not shrinking, so still climbing.

**New readouts (2026-11-01).**

`game_log.py --since <h> --genes` gives the doubling table and per-gene
trends from the game's log.
The reader was verified against the in-game Stats panel on 2026-11-01.
Values and times match exactly at the 1h, 10h and 2-day views, for Biomass
and Entities Count. Point i of each resolution level sits (i+1) steps
before the save, as the game draws it.
The gene log was verified against the Gene Analysis panel the same day
(Jaw Muscles WAG at 1 h, 2 h, 4 h and 3d0h ago). Bin counts and
percentages match exactly, e.g. 158 of 551 (28.7%) at 1 h and 100 of 584
(17.1%) at 72 h. Times now follow the panel's rule, and only the points the
panel shows are kept. Decoded gene medians match the save's bibites
within histogram resolution: MouthMusclesWAG 8.18 vs 8.19, ViewRadius 194
vs 196. A gene at exactly 0 reads slightly above 0.

v2 since the hex swap (28.8 → 77.6 h), most-moved genes (net change as % of
the gene's range, directionality):

| Gene | Net change | Directionality |
|---|---|---|
| ColorB | −64% | 0.66 |
| MouthMusclesWAG | +55% | 0.95 |
| PheroSense | +44% | 1.00 |
| EyeOffset | −44% | 0.66 |
| LayTime | +34% | 0.95 |
| StomachWAG | +34% | 1.00 |
| ViewRadius | +23% | 0.97 |
| SizeRatio | −15% | 0.62 |
| SpeedRatio | 0% | 0.00 |

**Hidden vs expressed** (`run_stats.py` sweep), the strongest input per
bibite, median:

| Save | Own state: outputs / L3 | Surroundings: outputs / L3 |
|---|---|---|
| p4 | 0.0014 / 0.013 | 0.0005 / 0.0036 |
| 10-30 | 0.026 / 0.087 | 0.0039 / 0.013 |
| 11-01 | 0.028 / 0.098 | 0.0065 / 0.021 |

Outputs stay ~0.3× the L3 response in all three, so internal structure is
growing in step with expression. There is no sign yet of unused internal
state piling up.

**11-06 save (166.7 h, gen 122–139; +89 sim h since 11-01, ~0.75 sim h per
real hour).**

- **Population:** 960 alive, up from 515.
- **Energy:** bibite share per doubling since 29.0 h is 28.6 → 32.7 → 31.6
  → 35.1% (+4.0, −1.1, +3.5). Older windows rely on coarse log points.
  Still climbing.
- **Brains** (sweep, median per bibite):
  - Own state 0.106 at outputs (was 0.028); surroundings 0.021 (was
    0.0065); inside L3 0.28 / 0.053.
  - Input-dependent push: median 0.058, max 0.20; 600 of 960 are above 0.05.
  - Top surroundings inputs: Phero2Angle, Phero3Angle.
  - Wiring: every kind has a mean |w| of ~0.07–0.10. No latches; the
    largest self-loop is +0.46.
- **Bodies, since 29 h** (gene log, directionality in brackets):
  - SizeRatio 1.19 → 0.50 (0.84); HatchTime 21 → 71 (0.77).
  - Living bibites' HatchTime/BroodTime median is now 0.83, about double
    11-01's newborns, so babies are much bigger.
  - MouthMusclesWAG is back down to ~3.6 (from ~8.2 on 11-01).
  - HerdCohesionWeight 0.55 → 3.44 (0.92); HerdSeparationDistance 13 → 62.
  - BrainAverageMutation 8.2 → 1.8 (median 1.6; 187 bibites at 0).
- **Newborns:** median age at death is 2.4 min (was 1.7). The last hour had
  3,911 births with 960 alive, ~4 per bibite per hour (was ~7).
- **Want2Lay:** bias −0.86, output median 0.302; 38 of 960 are holding eggs.
- **Lineage:** everyone descends from 13203 *pizamampfus* (gen 57), and 50%
  from 15101 *lacerdus* (gen 110). The top species are now genus
  *Godopedrus*: 15796 *leo* (240) and 15742 *leventianus* (178).
- **Species tied to zones:** 1.09× (mixed).

**What the strongest responses actually do (11-06).**

Method: sweep each key input over its typical range and compute each
output's *actual* value through its activation function, including Easy
Herbivore's own wiring and biases. Medians over 200 bibites.

- **Real behavior changes are small.** The largest is ~0.02 in output units,
  even though the pre-activation pushes are ~0.1.
  - Outputs mostly sit where their activation is flat: Want2Eat is tanh at
    ~0.84, and the pheromone outputs are ReLU, often at 0.
  - So my earlier "~0.1 push = visible behavior" rule of thumb overstated
    it.
- **Pheromone inputs:** changes of ≤0.004, and the direction is shared by
  only 50–64% of bibites, i.e. essentially random per bibite. There is no
  common pheromone-driven behavior yet.
- **The one consistent effect:** older bibites heal more. TimeAlive → Want2Heal
  is +0.013, in the same direction for 87% of bibites. TimeAlive → Grab is
  +0.013 (75%).
- **One curve shift, now handled by `run_stats.py`:** evolution raised
  Accelerate's bias from 1.13 to 1.88, which is near tanh saturation. The
  added layers' steady −0.25 pushes it back onto the steep part, so Easy
  Herbivore's own "brake near plants" reflex got stronger (−0.35 → −0.51
  across PlantCloseness 0→1).
  - This is a real behavior change, but not new sensing.
  - The behavior report credits the added layers only beyond a sweep with
    them frozen, so offsets like this aren't counted as sensing.
- **Pheromone production is rising regardless:** 295/196/70 of 960 bibites
  produce channels 2/3/1, and there are 1,687 spots in the world (504 on
  11-01). It doesn't depend on the inputs above, so it presumably comes from
  output biases or constant pushes (inferred).

**Newborn mortality (2026-11-01).**

From the game's log at 77.6 h, last hour:
- 3,453 births and 3,454 deaths, with ~515 alive.
- Age at death: q25 1.1 min, median 1.7 min, q75 3.6 min.
- The median age at death has risen from 0.5 min (48 h earlier) to 1.7 min.

So nearly every bibite dies within minutes of hatching.

Recently dead newborns (≤3.2 min) in the 10-28 / 10-30 / 11-01 saves:
- 779 of 786 died with zero energy (starvation). Only 5% had been attacked.
- Median age at death was 0.86 min.

Birth size decides it. The size at birth scales with HatchTime/BroodTime
(`BibiteGenes.RootOfMaturityAtBirth`). Newborns in the saves by that ratio:

| HatchTime/BroodTime | Newborns | Already dead | Median size |
|---|---|---|---|
| < 0.2 | 193 | 89% | 0.025 |
| 0.2–0.3 | 325 | 71% | 0.079 |
| 0.3–0.4 | 267 | 68% | 0.119 |
| 0.4–0.5 | 164 | 59% | 0.146 |
| ≥ 0.5 | 187 | 47% | 0.194 |

"Already dead" is a snapshot of bodies in the saves, not a survival rate,
but the gradient is clear.

Blind bibites (view angle < 20°) turned up 18 times across 21 saves, at
most 5 at once. All were ≤3.2 min old and none laid eggs: a recurring
mutation, not a lineage. With 84% of dead bodies being newborns, the data
can't show that blindness itself kills.

**Egg laying is near its decision threshold (2026-11-01).**

How laying works (`BibiteEggLayingOrgan`): EggProduction > 0.15 builds
eggs, and a finished egg is laid only while Want2Lay ≥ 0.25. Eggs are laid
behind the parent, and babies hatch where the egg lies.

In the templates Want2Lay is a sigmoid with bias 0, so 0.5: always lay.

At 11-01:
- The Want2Lay bias has drifted to a median of −0.81 (range −1.18 to +0.26).
- The output is a median 0.294 (range 0.227–0.548), just above the 0.25
  threshold. 15 of 515 bibites are currently below it, holding their eggs.
- The gap from the median to the threshold is ~0.22 in pre-activation
  units. Current input-dependent pushes are 0.02–0.07 (max).

Sitting near a threshold means small, food-dependent signals could switch
laying on and off, e.g. "lay where food is". Given 84% newborn starvation
(above), that would have a large payoff, and it is a candidate for the
first sensing-driven behavior.

**Watch:** the Want2Lay response to PlantCloseness/NPlants in the sweep, and
food density around eggs vs random spots.

**Input-dependent push in the 2025 run** (herbivores, same measurement as
`run_stats.py`; v1 has 2 added layers, so its input→output paths are 3
weights long, not 4):

| Save | Gen max | Median | p90 | Max | Above 0.1 |
|---|---|---|---|---|---|
| 07-20 | 137 | 0.053 | 0.094 | 0.15 | 20 of 310 |
| 07-26 | 357 | 0.166 | 0.250 | 0.44 | 462 of 533 |
| 08-08 | 638 | 0.303 | 0.463 | 0.69 | 1206 of 1256 |
| 09-07 | 875 | 0.313 | 0.503 | 0.79 | 1233 of 1256 |

In the final save's top 40 bibites, the push depends mostly on Speed, then
TimeAlive, Minute, Maturity, LifeRatio, Tic, EnergyRatio and Fullness.
External senses barely register (PlantCloseness ~0.1, against ~17 for Speed,
summed). So v1's added layers became controllers of internal state (speed,
age, time, energy), not processors of what the bibite sees.

**Sensitivity sweep (2026-10-30).** The input-dependent push compares
inputs at their saved values against zero, which underrates inputs that
happen to be 0 at save time. A fairer test: sweep each input over its
5th–95th percentile range in the population and measure the biggest change
at any output, from the added layers only.

| Input | Range in 2025 final | 2025 final (gen 875) median / p90 | v2 at 10-30 (gen 62) median / p90 |
|---|---|---|---|
| TimeAlive | 0.5–67 | 0.30 / 0.59 | 0.023 / 0.038 |
| Speed | 1–9.8 | 0.31 / 0.55 | 0.006 / 0.013 |
| Minute | 0–3.9 | 0.19 / 0.38 | 0.008 / 0.014 |
| Maturity | 0.1–4 | 0.11 / 0.19 | 0.010 / 0.020 |
| Fullness | 0–0.96 | 0.063 / 0.15 | 0.002 / 0.004 |
| PlantCloseness | 0–1 | 0.029 / 0.051 | 0.001 / 0.002 |
| NPlants | 0–0.25 | 0.025 / 0.040 | 0.001 / 0.002 |
| NBibites | 0–0.25 | 0.019 / 0.035 | — |
| PlantAngle | −0.09–0.07 | 0.009 / 0.015 | 0.001 / 0.002 |

- Even measured fairly, v1's external senses stayed ~10× weaker than its
  internal/time inputs after 875 generations.
- Part of the reason is the inputs' real ranges. TimeAlive and Speed span
  ~0–67 and ~1–10, while senses span ≤1. PlantAngle spans only ±0.09,
  because Easy Herbivore's own PlantAngle→Rotate reflex keeps the nearest
  plant nearly straight ahead.

## Test 2, hex phase (from 2026-10-25)

Settings changes and their sim times are in [settings_log.md](settings_log.md).

**The switch (sim time 28.8 h):**
- Food zones were hot-swapped to the 7-zone hexagon. Each zone is radius
  1/3 and only one of fertility, biomass or pellet size differs from the
  others, along one of the three lines through the Center.
- Totals were matched to the old world: 1.339 ME, 2.13 kE/s, ~6.7k pellets.
  All other settings are unchanged.
- Swapping deleted the old zones' pellets. Steve refilled by temporarily
  raising spawn rates and hand-spawning food, then cutting it back. That
  boomed the population from 546 to 731.
- `p4` (29.0 h) is the clean start of this phase.

`python tools/run_stats.py <save>` prints a per-zone table for this world.
Note: the world size setting (20 ku) is a radius.

**Correction (2026-10-26):** saves also contain bibites that have died but
not yet been removed (`body.dead`), about 30–40% of the saved bibites.
Before this fix, `run_stats.py` counted them as alive, so every population
count and per-zone count logged before 10-26 is too high. That includes the
pre-hex test 2 numbers below, e.g. "956 bibites" at 10-22 was 691 alive. The
table below is recomputed with living bibites only.

| Save | Sim h | Alive | Gen max | Species tied to zones | Brains vs own zone | Input-dependent push (median / max / count >0.01) |
|---|---|---|---|---|---|---|
| p4 | 29.0 | 485 | 38 | 1.35× | 0.979 | 0.0008 / 0.006 / 0 |
| p5 | 30.8 | 331 | 40 | 1.64× | 0.959 | 0.0011 / 0.011 / 1 |
| p6 | 32.4 | 320 | 43 | 1.63× | 0.971 | 0.0013 / 0.010 / 0 |
| p7 | 33.2 | 345 | 43 | 1.39× | 0.953 | 0.0017 / 0.012 / 1 |
| p8 | 36.0 | 344 | 44 | 1.31× | 0.967 | 0.0024 / 0.022 / 15 |
| p9 | 37.9 | 393 | 47 | 1.41× | 0.978 | 0.0028 / 0.022 / 36 |
| p10 | 40.9 | 432 | 50 | 1.61× | 0.954 | 0.0034 / 0.019 / 31 |
| 10-26 | 44.8 | 529 | 56 | 1.41× | 0.967 | 0.0048 / 0.040 / 62 |
| 10-27 | 48.3 | 575 | 59 | 1.69× | 0.935 | 0.0061 / 0.031 / 133 |
| 10-28 | 54.0 | 572 | 56 | 1.26× | 0.957 | 0.0086 / 0.070 / 247 |
| 10-30 | 64.4 | 626 | 62 | 1.26× | 0.970 | 0.0115 / 0.050 / 375 |
| 11-01 | 77.6 | 515 | 68 | 1.07× | 0.961 | 0.0187 / 0.068 / 473 |

Notes:
- p8→p9 ran overnight in the background at ~0.19 sim h per real hour
  (Windows throttling). In focus with throttling disabled, ~0.65–0.8.
- Input-dependent push is the steady trend: the median grew ~6× from p4 to
  10-26 (gen max 38→56).
- Species-zone tie and brain-zone numbers fluctuate between saves with no
  clear trend yet.
- Zone gene patterns flip between saves (e.g. East_Middle mouth muscles).
  At 10-26 the biggest mouths are in East_South (5.3) and West_South (5.1).
- 10-26 → 10-27 ran 3.5 sim h in ~11.4 real h (~0.31 sim h per real hour).
- **Two body plans at 10-27:**
  - Big mouth, fast and lean: species 12274 and its offshoot 12401 (created
    at 44.8 h). Mouth muscles ~7.7, speed ~1.6, size ~0.9, view ~190. Mostly
    on the west side (West_Middle, West_North, West_South).
  - Small mouth, bigger and slower: 12242. Mouth ~2.0, speed ~1.1, size
    ~1.2. Mostly in West_North, East_North and Center.
- Mouth muscles by zone are 7.5 in West_Middle (small pellets) against 2.8 in
  East_Middle (big pellets), even excluding 12401. East_Middle has few
  residents (39) and 84% of its food left.
- **10-28: the big-mouth line swept.**
  - 12401 has 181 of 572. 12242 (small mouth) is down to 1 bibite, and only
    55 bibites have mouth muscles below 4.
  - Mouth muscles are ~7 in every zone, and species-zone tie fell to 1.26×.
  - Run speed 10-27 → 10-28: 5.6 sim h in ~25 real h.
- **10-28: what the input-dependent push responds to.** For the top 5
  bibites, nearly all of it comes from TimeAlive and Maturity. Those inputs
  grow large (TimeAlive in minutes, up to ~85; Maturity up to ~13), so even
  tiny weights from them add up. These are age-dependent behaviors, not
  reactions to food or other bibites. Most common output carrying it:
  Herding (103 of the 247 bibites above 0.01), then Want2Eat (35) and
  PhereOut1 (34).
- **10-30: a single-ancestor sweep.**
  - 97% of living bibites (606 of 626) descend from species 12401
    *Printzilonum martinezfelixis*. It appeared at sim 44.8 h, generation 36,
    as an offshoot of 12274, the big-mouth line.
  - Tracing ancestry back from the current population: at 48 h one line was
    already the ancestor of 94%. The descendants have since split into 61
    species (equivalent to ~15 equally common ones).
  - 12401's founder versus its parent's species snapshot:
    - Diet 0.03 → 0, ClockSpeed 0.95 → 2.2, BroodTime 33 → 66,
      GrowthMaturityExponent 0.04 → 0.48, BrainMutationSigma 0.031 → 0.0003.
    - It also differs in 100 weights and 39 biases.
    - The snapshots are of single individuals, so this can't say which
      change mattered.
  - Since 10-28 standing food fell in every zone; East_Middle (big pellets)
    dropped from 92% to 43% as its residents rose 49 → 65. Median size went
    from ~0.95 to ~0.82.
  - Run speed 10-28 → 10-30: 10.4 sim h in ~53.5 real h.
- **11-01:**
  - Everyone descends from 12401. 99% descend from 12720 *textexae* (54.2 h,
    gen 46), and 59% from 13203 *pizamampfus* (69.0 h, gen 57), which is the
    top species (241 of 515).
  - Sensitivity sweep, median per bibite, own state vs surroundings:
    10-30: 0.026 vs 0.0039. 11-01: 0.0275 vs 0.0065. Surroundings grew ~1.7×
    while own state stayed flat. Two points only, so watch it.
  - Top surroundings inputs: Phero3Angle, MeatAngle, PlantCloseness.
  - Mouth muscles ~8 and size ~0.75 in every zone.
  - Run speed: 13.2 sim h in ~42 real h.

## Test 2 (started 2026-10-21, ~15 h at max speed)

World: the 2025 run settings saved as a scenario. That means zero brain costs,
weights and biases only (add/remove/toggle/type-change all 0), synapse/neuron
mutation split 0.6/0.4, background mutation chance 20 with variance 0.05, and
brainTPS 2. Seeded with a few NeuronBox_v2 copies. World saves:
`Savefiles/Neuron_Box_test_2_10-21-2026.zip` and `..._10-22-2026.zip`.

`ademinemesius_test2_2026-10-22.bb8` is the dominant species (11322) at the
10-22 save.

Population at the 10-22 save: 956 bibites in 38 species. Generations run 8–23
(median 18). Lifetimes are long; this bibite was ~2.5 sim-hours old.

- **The box is still dormant.** About 270 of the 1,224 box synapses are
  non-zero, but the largest is only ~0.1–0.19. The most any box path pushes
  into any output is 0.02 (median 0.005). An input reaches an output only by
  crossing four box weights in a row, so the signal is their product
  (e.g. 0.05⁴ ≈ 6e-6).
- **Real change so far is body and base network:**
  - Size and speed went up, view radius went up, and the clock slowed.
  - A few Easy Herbivore biases and weights moved slightly. For example,
    Minute→Hidden0 went from 5.79 to 6.07 and Accelerate's bias from 1.13 to 1.21.
  - The 5 disabled synapses all come from Easy Herbivore itself. No new
    toggles happened.
- **Mutation genes:**
  - BrainMutationSigma's median went from 0.0005 to 0.0048. 274 bibites
    (including this one) have it at 0, but brains still differ between them
    (all 536 members of species 11322 have distinct brains), so it isn't frozen.
  - BrainAverageMutation sits at 7–10.

**2026-10-22 ~06:40, settings change, run resumed:**
- Background Mutation Variance went from 5% to 10%.
- Mutation Value Relativity went from 50% to 25%.

Per the in-game tooltip, a lower relativity makes mutation size depend less
on a gene's current value, so genes stuck near 0 can climb back out. That
matters here: BrainMutationSigma had hit 0 in 274 bibites.

At x100 the game showed 20 tps and sim/real x0.51.

### 10-24 save (resumed from an autosave after a PC crash)

Numbers from `python tools/run_stats.py <save.zip>`:

- **Population:** 570 bibites in 59 species, down from 956 in 38.
  Generations 18–37 (median 32), so about 14 generations since 10-22.
- **Mutation genes:**
  - BrainMutationSigma median 0.0128 (was 0.0048). 185 bibites are at 0.
  - AverageMutationNumber median 1.49 (was 0.31).
- **Box weights:** median 442 non-zero box synapses (was 270). The largest
  box weight per bibite has a median of 0.30 (was 0.10) and a max of 0.54.
- **Box push on outputs:** median 0.032 (was 0.005), max 0.24. The max is a
  Want2Attack push in species 11690; Herding and Want2Lay also reach ~0.2.
- **But it's constant, not sensing.**
  - In the strongest case, L3N9's own bias (sin(−0.52) ≈ −0.49) times the
    −0.51 L3N9→Want2Attack weight adds a fixed +0.25. That offsets
    Want2Attack's bias, which has drifted to −0.415.
  - To find how much of the push comes from inputs, I re-ran one tick of the
    box with real inputs and again with inputs zeroed. The input-driven part
    is at most 0.006 (median 0.0005) across all 570.
  - So the box currently acts as extra output bias. The input→L1→L2→L3→output
    paths are still too weak to matter.

The 10-24 save file itself is gone, and the autosaves only keep the last 26.
Steve: almost no game time passed in it, so nothing real was lost.

### 10-25 save (~28.5 h game time; autosave every 10 min had stalled the overnight run, now disabled)

- **Population:** 533 bibites in 56 species, generations 20–38. That's only
  about one generation past 10-24.
- **Added layers:** median 449 non-zero synapses; the largest |weight| per
  bibite has a median of 0.30 and a max of 0.56. Basically unchanged from 10-24.
- **Push on outputs:** median 0.031, max 0.24 (−0.24 into Herding,
  species 11726).
  - The input-dependent part is at most 0.007 (median 0.0005).
  - `run_stats.py` now reports this split.
- **Diet:** trending to pure herbivore. Median 0.011, and 240 bibites are at
  exactly 0.

**Diversity at 10-25:**
- **Species:** 56 living, but most hold only a handful of bibites; it's
  equivalent to ~19 equally common species (inverse Simpson). All descend from
  the founder 11320, and splits that still have descendants are mostly from
  the last ~10 sim-hours.
- **Brains:**
  - Bibites in different species are about twice as far apart in weights as
    bibites in the same species (median distance 2.0 vs 1.1).
  - About 28% of the drift from the template is shared by the whole
    population; the rest happened after lines split.
  - Of the 1,260 added parameters, 864 vary noticeably between bibites (SD
    above 0.02). Only 2 have one value shared across the population.
- **Turnover is heavy:**
  - Of the 38 species alive on the 10-22 morning, only 3 have living
    descendants. One of them (11322) accounts for 74% of today's population.
  - Of the 55 alive on the 10-22 afternoon, 16 have living descendants, and
    one (11580) accounts for 64%.
  - This window included the boom-and-settle population drop, which kills
    lines on its own.
