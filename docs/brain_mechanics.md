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
| **Layout (`nodeAnchors`) lives only in templates**, keyed by node Inov; in-game rearranging isn't saved to `.bb8`. The game renumbers node Inovs on load. | — |

## Self-loop regimes for a sine neuron, x → sin(w·x + input)

| w | behavior |
|---|---|
| 0 – 1 | leaky: decays toward its input |
| 1 – ~2.26 | bistable latch near ±0.9 (1-bit memory) |
| > ~2.26 | period-doubling / chaos; at 20 Hz this is flicker, i.e. noise |

Slow rhythms instead come from sine of the time inputs (TimeAlive, Minute, Tic):
weight w from TimeAlive into a sine neuron gives a period of 2π/w minutes.
