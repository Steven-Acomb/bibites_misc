"""Build BrainProbe: Easy Herbivore plus side circuits that reveal how the game
evaluates a brain. Read the probe node values in the brain viewer.

The game drops hidden nodes that lack a path from an input and a path to an
output (self-loops don't count; weight-0 synapses do). So every probe node is
fed from TimeAlive (weight 0 where it shouldn't matter) and every readout gets
a weight-0 synapse into Herding. Behavior stays exactly Easy Herbivore's.

Easiest readout: save the bibite in-game; the .bb8 records each node's Value.

Usage: python tools/make_probe.py <Easy Herbivore.bb8template> <layout.bb8template> <out.bb8template>

<layout> supplies brain-viewer positions for the standard nodes (e.g. the
hand-arranged NeuronBox_Complete).
"""

import math
import sys

from bibite import LINEAR, SINE, Template

GAIN = 10.0  # amplifies the timing differences so they're readable at 2 decimals


def build(base_path, layout_path, out_path):
    t = Template.load(base_path)
    t.rename("BrainProbe", "Easy Herbivore + diagnostic side circuits "
             "(no effect on behavior). See tools/make_probe.py.")
    t.copy_anchors_from(Template.load(layout_path))

    # Timing: does a signal cross a chain of hidden nodes in one brain tick,
    # or advance one node per tick? Each D_* node is GAIN * (TimeAlive arriving
    # directly - TimeAlive arriving through a chain), so it reads 0 when the
    # chain adds no delay and grows with every tick of lag.
    f1 = t.add_node("F1", LINEAR, anchor=(0.25, 0.10))
    f2 = t.add_node("F2", LINEAR, anchor=(0.35, 0.10))
    f3 = t.add_node("F3", LINEAR, anchor=(0.45, 0.10))
    # Same chain, but created in reverse so its Index order runs backwards.
    r3 = t.add_node("R3", LINEAR, anchor=(0.45, 0.25))
    r2 = t.add_node("R2", LINEAR, anchor=(0.35, 0.25))
    r1 = t.add_node("R1", LINEAR, anchor=(0.25, 0.25))
    d_f1 = t.add_node("D_F1", LINEAR, anchor=(0.60, 0.05))
    d_f3 = t.add_node("D_F3", LINEAR, anchor=(0.60, 0.15))
    d_r3 = t.add_node("D_R3", LINEAR, anchor=(0.60, 0.25))
    for a, b in [("TimeAlive", f1), (f1, f2), (f2, f3),
                 ("TimeAlive", r1), (r1, r2), (r2, r3)]:
        t.connect(a, b, 1.0)
    for d, end in [(d_f1, f1), (d_f3, f3), (d_r3, r3)]:
        t.connect("TimeAlive", d, GAIN)
        t.connect(end, d, -GAIN)

    # Bias: is baseActivation added before the activation function?
    # Reads sin(0.5) = 0.48 if so, 0.50 if added after.
    bias = t.add_node("Bias_sin0.5", SINE, bias=0.5, anchor=(0.25, 0.45))

    # Sine self-loops: x -> sin(w*x + 0.1). The 0.1 bias kicks it off zero.
    loops = []
    for i, w in enumerate([0.5, 2.0, 3.0]):
        s = t.add_node(f"Loop_w{w}", SINE, bias=0.1, anchor=(0.35 + 0.1 * i, 0.45))
        t.connect(s, s, w)
        loops.append(s)

    # Counter: x -> x + 1 each brain tick if loops feed back last tick's value.
    counter = t.add_node("Counter", LINEAR, bias=1.0, anchor=(0.65, 0.45))
    t.connect(counter, counter, 1.0)

    for node in [bias, *loops, counter]:
        t.connect("TimeAlive", node, 0.0)
    for readout in [d_f1, d_f3, d_r3, bias, *loops, counter]:
        t.connect(readout, "Herding", 0.0)

    t.save(out_path)


def loop_prediction(w, bias=0.1, steps=200):
    """Iterate x -> sin(w*x + bias); return the last few values."""
    x, xs = 0.0, []
    for _ in range(steps):
        x = math.sin(w * x + bias)
        xs.append(x)
    return [round(v, 3) for v in xs[-4:]]


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2], sys.argv[3])
    print(f"wrote {sys.argv[3]}")
    for w in [0.5, 2.0, 3.0]:
        print(f"Loop_w{w}: expected to settle into {loop_prediction(w)} (last 4 ticks)")
