"""Summarize a NeuronBox world save: population, mutation genes, and how far
the added hidden layers (L1N1..L3N12 and their synapses) have drifted from
their all-zero start.

"Push on output" is, for an output, the input it currently receives
from L3 (sum of weight * that neuron's live Value); it stays ~0 until the
added layers start to matter.

It also sweeps each input over its typical range in the population to show
which inputs the added layers respond to, split into the bibite's own
state/time and its surroundings (the second group is what sensing needs).

For worlds with more than one food zone it adds a per-zone table: standing
food, residents (by position; the world size setting is a radius), their
median genes and top species. Two summary numbers follow: how tied species
are to zones, and how much residents' brains resemble their own zone.

Usage: python tools/run_stats.py <world save .zip> [more saves...]
"""

import collections
import json
import math
import random
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


# Inputs about the bibite itself or the clock, vs. inputs about its surroundings.
OWN_STATE = {"EnergyRatio", "Maturity", "LifeRatio", "Fullness", "Speed",
             "RotationSpeed", "IsGrabbing", "AttackedDamage", "EggStored",
             "Tic", "Minute", "TimeAlive"}
SWEEP_SAMPLE = 150


def sweep_effects(b, ranges):
    """For each input: biggest change at any output (from L3) when that input
    is moved from the low to the high end of its population range, all other
    values held at their saved state. Same one-tick model as input_driven."""
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
    outputs = [o for o in incoming if kind[o] == 1]

    def push(override):
        val = dict(saved)
        val.update(override)
        for n in added:
            layer = int(n["Desc"][1])
            x = n["baseActivation"]
            for src, w in incoming[n["Desc"]]:
                if kind[src] == 0 or (is_added(src) and int(src[1]) == layer - 1):
                    x += w * val[src]
                else:
                    x += w * saved[src]
            val[n["Desc"]] = math.sin(x)
        return [sum(w * val[s] for s, w in incoming[o] if is_added(s)) for o in outputs]

    effects = {}
    for inp, (lo, hi) in ranges.items():
        low, high = push({inp: lo}), push({inp: hi})
        effects[inp] = max((abs(a - c) for a, c in zip(low, high)), default=0.0)
    return effects


def input_sweep(bibites):
    """Which inputs the added layers respond to, measured fairly: each input
    swept over its 5th-95th percentile range across the population."""
    values = collections.defaultdict(list)
    for b in bibites:
        for n in b["brain"]["Nodes"]:
            if n["archetype"] == 0:
                values[n["Desc"]].append(n["Value"])
    ranges = {}
    for inp, xs in values.items():
        xs.sort()
        lo, hi = xs[int(0.05 * (len(xs) - 1))], xs[int(0.95 * (len(xs) - 1))]
        if hi > lo:
            ranges[inp] = (lo, hi)
    rng = random.Random(0)
    sample = rng.sample(bibites, min(SWEEP_SAMPLE, len(bibites)))
    per_input = collections.defaultdict(list)
    for b in sample:
        for inp, e in sweep_effects(b, ranges).items():
            per_input[inp].append(e)

    print(f"\nwhat the added layers respond to (each input swept over its typical range; "
          f"biggest output change, median / 90th pct over {len(sample)} bibites)")
    for label, group in [("own state & time", lambda i: i in OWN_STATE),
                         ("surroundings", lambda i: i not in OWN_STATE)]:
        rows = sorted(((i, st.median(v), sorted(v)[int(0.9 * (len(v) - 1))])
                       for i, v in per_input.items() if group(i)),
                      key=lambda r: -r[1])
        best = [max(e for i, e in zip(per_input, col) if group(i))
                for col in zip(*per_input.values())]
        print(f"  {label}: strongest input per bibite median {st.median(best):.4f}")
        for i, m, p90 in rows[:5]:
            lo, hi = ranges[i]
            print(f"    {i:16} {m:.4f} / {p90:.4f}   (range {lo:.3g} to {hi:.3g})")


def spread(xs, fmt="{:.4g}"):
    xs = list(xs)
    return (f"min {fmt.format(min(xs))}  med {fmt.format(st.median(xs))}  "
            f"max {fmt.format(max(xs))}")


def summarize(path):
    z = zipfile.ZipFile(path)
    saved = [json.loads(z.read(n).decode("utf-8-sig"))
             for n in z.namelist() if n.startswith("bibites/")]
    # Saves also hold bibites that have died but not yet been removed.
    bibites = [b for b in saved if not b["body"]["dead"]]
    genes = [b["genes"]["genes"] for b in bibites]
    print(f"== {path}")
    species = collections.Counter(b["genes"]["speciesID"] for b in bibites)
    print(f"bibites {len(bibites)} alive ({len(saved) - len(bibites)} dead skipped)  "
          f"species {len(species)}  "
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
    input_sweep(bibites)
    settings = json.loads(z.read("settings.bb8settings").decode("utf-8-sig"))
    if len(settings["zones"]) > 1:
        pellets = json.loads(z.read("pellets.bb8scene").decode("utf-8-sig"))["pellets"]
        zone_breakdown(settings, pellets, bibites)
    print()


# Ungrazed plant pellets hold ~20% of their nominal size, so an untouched zone
# sits at ~20% of its biomass cap (measured on the empty 7zone_hex_test_0 world
# and on test 2's starting save).
UNGRAZED_FILL = 0.2
ZONE_GENES = ["SizeRatio", "SpeedRatio", "MouthMusclesWAG", "ViewRadius", "Diet"]


def zone_breakdown(settings, pellets, bibites):
    """Per food zone: standing food, residents, species mix, genes, brains."""
    zones = settings["zones"]
    world_r = settings["independents"]["SimulationSize"]["Value"]  # a radius
    density = settings["independents"]["biomassDensity"]["Value"]

    def zone_of(x, y):
        for zn in zones:
            r = zn["radius"] * (world_r if zn["radiusIsRelative"] else 1)
            if math.hypot(x - zn["posX"] * world_r, y - zn["posY"] * world_r) <= r:
                return zn["name"]
        return "gaps"

    home = [zone_of(*b["transform"]["position"]) for b in bibites]
    names = [zn["name"] for zn in zones] + ["gaps"]
    food = {g["zone"]: sum(p["pellet"]["amount"] for p in g["pellets"]
                           if p["pellet"]["material"] == "Plant") for g in pellets}

    print("\nper zone (food % = standing plant energy vs. the zone's ungrazed level)")
    print(f"{'zone':12} {'fert':>5} {'biom':>5} {'size':>5} {'food %':>6} "
          f"{'bibites':>7}  " + "  ".join(f"{g[:9]:>9}" for g in ZONE_GENES)
          + "  top species (share of zone)")
    for name in names:
        members = [b for b, h in zip(bibites, home) if h == name]
        zn = next((zn for zn in zones if zn["name"] == name), None)
        if zn:
            r = zn["radius"] * (world_r if zn["radiusIsRelative"] else 1)
            ungrazed = UNGRAZED_FILL * density * zn["biomassDensity"] * math.pi * r * r
            cols = (f"{zn['fertility']:5.2f} {zn['biomassDensity']:5.2f} "
                    f"{zn['pelletSize']:5.2f} {100 * food.get(name, 0) / ungrazed:5.0f}%")
        else:
            cols = f"{'':5} {'':5} {'':5} {'':>6}"
        genes = "  ".join(
            f"{st.median(b['genes']['genes'][g] for b in members):9.3g}" if members else f"{'-':>9}"
            for g in ZONE_GENES)
        top = collections.Counter(b["genes"]["speciesID"] for b in members).most_common(2)
        tops = ", ".join(f"{s} ({c / len(members):.0%})" for s, c in top)
        print(f"{name:12} {cols} {len(members):7}  {genes}  {tops}")

    # Species clustering: chance two members of one species share a zone,
    # relative to two random bibites. 1 = well mixed; higher = species are
    # tied to zones.
    def same_zone_chance(groups):
        pairs = same = 0
        for g in groups:
            n = len(g)
            pairs += n * (n - 1) / 2
            same += sum(c * (c - 1) / 2 for c in collections.Counter(g).values())
        return same / pairs if pairs else 0.0

    by_species = collections.defaultdict(list)
    for b, h in zip(bibites, home):
        by_species[b["genes"]["speciesID"]].append(h)
    ratio = same_zone_chance(by_species.values()) / same_zone_chance([home])
    print(f"species tied to zones: {ratio:.2f}x  "
          "(how much likelier two same-species bibites share a zone than two random ones; 1 = mixed)")

    # Brains: distance from each bibite's weights to its own zone's average
    # (leaving itself out) vs. to other zones' averages. Below 1 = residents
    # of a zone are more alike than bibites from different zones.
    vecs = [[s["Weight"] for s in b["brain"]["Synapses"]] for b in bibites]
    groups = collections.defaultdict(list)
    for v, h in zip(vecs, home):
        groups[h].append(v)
    sums = {h: [sum(c) for c in zip(*vs)] for h, vs in groups.items() if len(vs) >= 5}
    ratios = []
    for v, h in zip(vecs, home):
        if h not in sums:
            continue
        n = len(groups[h])
        own = [(s - x) / (n - 1) for s, x in zip(sums[h], v)]
        others = [math.dist(v, [s / len(groups[o]) for s in sums[o]])
                  for o in sums if o != h]
        ratios.append(math.dist(v, own) / st.mean(others))
    print(f"brains vs. own zone: {st.median(ratios):.3f}  "
          "(median distance to own zone's average / to other zones' averages; 1 = no zone structure)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for p in sys.argv[1:]:
        summarize(p)
