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
