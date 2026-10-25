"""Summarize a NeuronBox world save: population, mutation genes, and how far
the added hidden layers (L1N1..L3N12 and their synapses) have drifted from
their all-zero start.

"Push on output" is, for an output, the input it currently receives
from L3 (sum of weight * that neuron's live Value); it stays ~0 until the
added layers start to matter.

Usage: python tools/run_stats.py <world save .zip> [more saves...]
"""

import collections
import json
import math
import statistics as st
import sys
import zipfile


def is_added(desc):
    return desc[0] == "L" and desc[1].isdigit()


def bibite_stats(b):
    nodes = {n["Index"]: n for n in b["brain"]["Nodes"]}
    nonzero, max_w, drive = 0, 0.0, collections.defaultdict(float)
    for s in b["brain"]["Synapses"]:
        a, c = nodes[s["NodeIn"]], nodes[s["NodeOut"]]
        if not (is_added(a["Desc"]) or is_added(c["Desc"])):
            continue
        if s["Weight"]:
            nonzero += 1
            max_w = max(max_w, abs(s["Weight"]))
        if is_added(a["Desc"]) and not is_added(c["Desc"]) and s["En"]:
            drive[c["Desc"]] += s["Weight"] * a["Value"]
    top = max(drive.items(), key=lambda kv: abs(kv[1]), default=("-", 0.0))
    return nonzero, max_w, top, input_driven(b)


def input_driven(b):
    """Largest part of any output's push from L3 that depends on the inputs.

    Recomputes one brain tick of L1..L3 twice, with the saved input values and
    with inputs zeroed, and returns the biggest difference at an output.
    Feed-forward edges use this tick's values, recurrent ones last tick's
    (the saved Values), matching docs/brain_mechanics.md.
    """
    nodes = {n["Index"]: n for n in b["brain"]["Nodes"]}
    saved = {n["Desc"]: n["Value"] for n in nodes.values()}
    kind = {n["Desc"]: n["archetype"] for n in nodes.values()}
    incoming = collections.defaultdict(list)
    for s in b["brain"]["Synapses"]:
        if s["En"] and s["Weight"]:
            incoming[nodes[s["NodeOut"]]["Desc"]].append(
                (nodes[s["NodeIn"]]["Desc"], s["Weight"]))
    added = [n for n in nodes.values() if is_added(n["Desc"])]
    added.sort(key=lambda n: (n["Desc"][1], int(n["Desc"][3:])))

    def push(zero_inputs):
        val = dict(saved)
        for n in added:
            layer = int(n["Desc"][1])
            x = n["baseActivation"]
            for src, w in incoming[n["Desc"]]:
                if kind[src] == 0:
                    x += w * (0.0 if zero_inputs else saved[src])
                elif is_added(src) and int(src[1]) == layer - 1:
                    x += w * val[src]
                else:
                    x += w * saved[src]
            val[n["Desc"]] = math.sin(x)
        return {o: sum(w * val[s] for s, w in src_list if is_added(s))
                for o, src_list in incoming.items() if kind[o] == 1}

    real, zero = push(False), push(True)
    return max((abs(real[o] - zero[o]) for o in real), default=0.0)


def spread(xs, fmt="{:.4g}"):
    xs = list(xs)
    return (f"min {fmt.format(min(xs))}  med {fmt.format(st.median(xs))}  "
            f"max {fmt.format(max(xs))}")


def summarize(path):
    z = zipfile.ZipFile(path)
    bibites = [json.loads(z.read(n).decode("utf-8-sig"))
               for n in z.namelist() if n.startswith("bibites/")]
    genes = [b["genes"]["genes"] for b in bibites]
    print(f"== {path}")
    species = collections.Counter(b["genes"]["speciesID"] for b in bibites)
    print(f"bibites {len(bibites)}  species {len(species)}  "
          f"top {species.most_common(3)}")
    print(f"generation            {spread((b['genes']['gen'] for b in bibites), '{}')}")
    print(f"age (sim min)         {spread(b['clock']['timeAlive'] / 60 for b in bibites)}")
    for k in ["BrainAverageMutation", "BrainMutationSigma",
              "AverageMutationNumber", "MutationAmountSigma", "Diet"]:
        xs = [g[k] for g in genes]
        print(f"{k:22}{spread(xs)}  zeros {sum(x == 0 for x in xs)}")
    stats = [bibite_stats(b) for b in bibites]
    print(f"nonzero added synapses  {spread((s[0] for s in stats), '{}')}  (of 1224)")
    print(f"largest added |weight|  {spread(s[1] for s in stats)}")
    print(f"largest push on output  {spread(abs(s[2][1]) for s in stats)}")
    print(f"  ...input-dependent    {spread(s[3] for s in stats)}  "
          f">0.01: {sum(s[3] > 0.01 for s in stats)}  >0.05: {sum(s[3] > 0.05 for s in stats)}")
    best = max(range(len(stats)), key=lambda i: abs(stats[i][2][1]))
    out, val = stats[best][2]
    print(f"strongest: bibite gen {bibites[best]['genes']['gen']} species "
          f"{bibites[best]['genes']['speciesID']}: {val:+.4f} into {out}")
    print()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for p in sys.argv[1:]:
        summarize(p)
