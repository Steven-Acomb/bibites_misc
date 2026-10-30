# NeuronBox v2 runs

**Terms used below:**
- **"The box":** everything NeuronBox v2 adds to Easy Herbivore. That is the
  36 sine neurons L1N1–L3N12 (3 layers of 12) and their 1,224 synapses, all
  starting at weight 0. It excludes Easy Herbivore's own 15 synapses and its
  Hidden0/Hidden1.
- **"Box push":** the input an output neuron currently receives from L3,
  i.e. Σ weight × L3 neuron value.

## Shelved: carnivore (2026-10-22)

`NeuronBox_v2_Carnivore.bb8template` (built with `make_neuronbox.py --carnivore`)
was checked in-game: brain intact and it eats meat.

Steve's plan for later:
- Build a world like the herbivore one, but spawning meat instead of plants.
- Gradually lower the meat spawn rate.
- Gradually raise the rate of random bibite spawns.
- Goal: evolve an actual predator.

Meanwhile the herbivore run (test 2) continues.

## Test 2, hex phase (from 2026-10-25)

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
