# NeuronBox v2 runs

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
