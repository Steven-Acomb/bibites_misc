"""Summarize a NeuronBox world save: population, mutation genes, and how far
the hidden "box" has drifted from its all-zero start.

"Box drive" for an output is the input it currently receives from the last
box layer (sum of weight * that neuron's live Value); it stays ~0 while the
box is dormant.

Usage: python tools/run_stats.py <world save .zip> [more saves...]
"""

import collections
import json
import statistics as st
import sys
import zipfile


def is_box(desc):
    return desc[0] == "L" and desc[1].isdigit()


def bibite_stats(b):
    nodes = {n["Index"]: n for n in b["brain"]["Nodes"]}
    nonzero, max_w, drive = 0, 0.0, collections.defaultdict(float)
    for s in b["brain"]["Synapses"]:
        a, c = nodes[s["NodeIn"]], nodes[s["NodeOut"]]
        if not (is_box(a["Desc"]) or is_box(c["Desc"])):
            continue
        if s["Weight"]:
            nonzero += 1
            max_w = max(max_w, abs(s["Weight"]))
        if is_box(a["Desc"]) and not is_box(c["Desc"]) and s["En"]:
            drive[c["Desc"]] += s["Weight"] * a["Value"]
    top = max(drive.items(), key=lambda kv: abs(kv[1]), default=("-", 0.0))
    return nonzero, max_w, top


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
    print(f"nonzero box synapses  {spread((s[0] for s in stats), '{}')}  (of 1224)")
    print(f"largest box |weight|  {spread(s[1] for s in stats)}")
    print(f"largest box drive     {spread(abs(s[2][1]) for s in stats)}")
    best = max(range(len(stats)), key=lambda i: abs(stats[i][2][1]))
    out, val = stats[best][2]
    print(f"strongest: bibite gen {bibites[best]['genes']['gen']} species "
          f"{bibites[best]['genes']['speciesID']}: {val:+.4f} into {out}")
    print()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for p in sys.argv[1:]:
        summarize(p)
