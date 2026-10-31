"""Build NeuronBox v2: Easy Herbivore plus a dense, recurrent sine "box" that
starts behavior-neutral and is meant to be filled in by weight drift.

Box structure (every synapse starts at weight 0, enabled):
  - every input            -> every L1 neuron
  - L(k)                   -> L(k+1), all pairs
  - last layer             -> every output
  - every hidden neuron    -> itself (self-loop)
  - last layer             -> L1 (top-down recurrence)
  - every output           -> L1 (feedback of the bibite's own actions)
Every path into an output passes through a last-layer -> output synapse, so
with those at 0 the bibite behaves exactly like Easy Herbivore.

See docs/brain_mechanics.md for why this works (same-tick feed-forward,
previous-tick recurrence, bias before activation).

--carnivore applies the 2025 NeuronBox_Complete_Carnivore edits to the base
first: plant edges rewired to their meat equivalents, GreenBibite->Want2Eat
mirrored to +0.843, Diet 0.899, MouthMusclesWAG 1.5, StomachWAG 2.0.

Usage:
  python tools/make_neuronbox.py <Easy Herbivore.bb8template> <layout.bb8template> <out.bb8template>
      [--layers 3] [--width 12] [--mutations 10] [--sigma 0.0005] [--carnivore]

<layout> supplies brain-viewer positions for the standard nodes (e.g. the
hand-arranged NeuronBox_Complete).
"""

import argparse

from bibite import INPUTS, OUTPUTS, SINE, Template


PLANT_TO_MEAT = {"PlantAngle": "MeatAngle", "PlantCloseness": "MeatCloseness",
                 "NPlants": "NMeats"}


def make_carnivore(t):
    """Mirror Easy Herbivore onto meat, as NeuronBox_Complete_Carnivore did."""
    desc = {n["Index"]: n["Desc"] for n in t.nodes}
    for s in t.synapses:
        src, dst = desc[s["NodeIn"]], desc[s["NodeOut"]]
        if src in PLANT_TO_MEAT:
            s["NodeIn"] = t.node(PLANT_TO_MEAT[src])["Index"]
        elif (src, dst) == ("GreenBibite", "Want2Eat"):
            # Exact mirror of Easy Herbivore's -0.842978239. The 2025 template
            # had +0.3829782, a hand-editing slip.
            s["Weight"] = -s["Weight"]
    genes = t.data["genes"]
    genes["Diet"] = 0.899495
    genes["MouthMusclesWAG"] = 1.5
    genes["StomachWAG"] = 2.0


def build(base_path, layout_path, out_path, layers, width, mutations, sigma,
          carnivore=False):
    t = Template.load(base_path)
    t.add_missing_inputs()
    t.copy_anchors_from(Template.load(layout_path))
    if carnivore:
        make_carnivore(t)

    # Hidden-node anchor y shares units with the input column (slots ~1..32).
    box = []
    for k in range(layers):
        x = 0.25 + 0.5 * k / max(layers - 1, 1)
        box.append([t.add_node(f"L{k + 1}N{i + 1}", SINE,
                               anchor=(x, 2.0 + 29.0 * i / max(width - 1, 1)))
                    for i in range(width)])

    first, last = box[0], box[-1]
    for src in INPUTS:
        for dst in first:
            t.connect(src, dst, 0.0)
    for lower, upper in zip(box, box[1:]):
        for src in lower:
            for dst in upper:
                t.connect(src, dst, 0.0)
    for src in last:
        for dst in OUTPUTS:
            t.connect(src, dst, 0.0)
    for layer in box:
        for n in layer:
            t.connect(n, n, 0.0)
    if layers > 1:
        for src in last:
            for dst in first:
                t.connect(src, dst, 0.0)
    for src in OUTPUTS:
        for dst in first:
            t.connect(src, dst, 0.0)

    genes = t.data["genes"]
    genes["BrainAverageMutation"] = mutations
    genes["BrainMutationSigma"] = sigma
    # As in v1: keep the body nearly fixed so evolution works on the brain.
    genes["AverageMutationNumber"] = 1.0
    genes["MutationAmountSigma"] = 0.01
    genes["ColorR"] = genes["ColorG"] = genes["ColorB"] = 0.5

    base = ("Easy Herbivore mirrored onto meat (as NeuronBox_Complete_Carnivore)"
            if carnivore else "Easy Herbivore")
    t.rename("NeuronBox_v2_Carnivore" if carnivore else "NeuronBox_v2", (
        f"Brain evolution starter. {base} plus {layers} hidden sine layers "
        f"of {width}: inputs->L1, layer->layer, L{layers}->outputs, self-loops, "
        f"L{layers}->L1 and outputs->L1, all at weight 0 (behaves exactly like "
        f"its base until weights drift). Built by tools/make_neuronbox.py."))
    t.save(out_path)
    return t


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("base")
    p.add_argument("layout")
    p.add_argument("out")
    p.add_argument("--layers", type=int, default=3)
    p.add_argument("--width", type=int, default=12)
    p.add_argument("--mutations", type=float, default=10.0,
                   help="brain mutations per birth; the game caps this at 10")
    p.add_argument("--sigma", type=float, default=0.0005)
    p.add_argument("--carnivore", action="store_true")
    a = p.parse_args()
    t = build(a.base, a.layout, a.out, a.layers, a.width, a.mutations, a.sigma,
              a.carnivore)
    print(f"wrote {a.out}: {len(t.nodes)} nodes, {len(t.synapses)} synapses")
