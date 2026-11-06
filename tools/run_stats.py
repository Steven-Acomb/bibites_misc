"""Summarize a NeuronBox world save: population, mutation genes, and how far
the added hidden layers (L1N1..L3N12 and their synapses) have drifted from
their all-zero start.

"Push on output" is, for an output, the input it currently receives
from L3 (sum of weight * that neuron's live Value); it stays ~0 until the
added layers start to matter.

It also sweeps each input over its typical range in the population to show
which inputs the added layers respond to, split into the bibite's own
state/time and its surroundings (the second group is what sensing needs),
and which outputs those inputs reach. A behavior report then measures the
real change in each output's actual value (through base wiring, biases and the
output's activation) and how consistent its direction is across bibites,
which separates shared habits from per-bibite noise. A wiring report then compares how far
each kind of added connection has drifted (feedback paths that rise above the
rest are in use) and counts sine self-loops in the latch (1-bit memory) and
chaotic regimes.

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
    """For each input, when it is moved from the low to the high end of its
    population range (all other values held at their saved state):
    (biggest change at any output from L3, biggest change in any L3 neuron).
    The second is internal structure that may not reach behavior yet.
    Same one-tick model as input_driven."""
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
    last = max(int(n["Desc"][1]) for n in added)
    top = [n["Desc"] for n in added if int(n["Desc"][1]) == last]

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
        return ([sum(w * val[s] for s, w in incoming[o] if is_added(s)) for o in outputs],
                [val[d] for d in top])

    effects = {}
    for inp, (lo, hi) in ranges.items():
        (out_lo, hid_lo), (out_hi, hid_hi) = push({inp: lo}), push({inp: hi})
        per_output = {o: abs(a - c) for o, a, c in zip(outputs, out_lo, out_hi)}
        effects[inp] = (max(per_output.values(), default=0.0),
                        max((abs(a - c) for a, c in zip(hid_lo, hid_hi)), default=0.0),
                        per_output)
    return effects


def input_ranges(bibites):
    """Each input's 5th-95th percentile across the population."""
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
    return ranges


# Output activation functions by node Type (bibite.py: SIGMOID 1, LINEAR 2,
# TANH 3, SINE 4, RELU 5).
ACTIVATIONS = {1: lambda x: 1 / (1 + math.exp(-max(-60.0, min(60.0, x)))),
               2: lambda x: x, 3: math.tanh, 4: math.sin, 5: lambda x: max(0.0, x)}


def behavior_effects(b, ranges):
    """{(input, output): change in the output's actual value} when the input
    goes from the low to the high end of its range. Unlike sweep_effects this
    includes the base wiring, biases and the output activation, so it is the
    behavior change, not just the push into the output."""
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
    outputs = [n for n in nodes.values() if n["archetype"] == 1]

    def run(override, frozen=False):
        # frozen: the added layers keep their saved outputs, so their constant
        # offset still shifts each output's operating point but they don't
        # respond to the swept input.
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
            val[n["Desc"]] = saved[n["Desc"]] if frozen else math.sin(x)
        out = {}
        for o in outputs:
            x = o["baseActivation"] + sum(w * val[s] for s, w in incoming[o["Desc"]])
            out[o["Desc"]] = ACTIVATIONS.get(o["Type"], lambda v: v)(x)
        return out

    effects = {}
    for inp, (lo, hi) in ranges.items():
        low, high = run({inp: lo}), run({inp: hi})
        fz_low, fz_high = run({inp: lo}, True), run({inp: hi}, True)
        for o in low:
            total = high[o] - low[o]
            # owed to the added layers *responding* to the input: total minus
            # the same sweep with them frozen (a constant offset that only
            # shifts the base reflex's operating point is not counted)
            effects[(inp, o)] = (total, total - (fz_high[o] - fz_low[o]))
    return effects


def behavior_report(bibites, top=8):
    """Real behavior changes owed to the added layers responding to inputs:
    biggest input -> output effects on the outputs' actual values, minus the
    same sweep with the added layers frozen (so a constant offset that merely
    strengthens a base reflex isn't counted), and how consistent their
    direction is across bibites (~50% = each bibite random, ~100% = shared)."""
    ranges = input_ranges(bibites)
    sample = random.Random(0).sample(bibites, min(SWEEP_SAMPLE, len(bibites)))
    eff = collections.defaultdict(list)
    for b in sample:
        for key, (_total, from_added) in behavior_effects(b, ranges).items():
            eff[key].append(from_added)
    rows = []
    for (inp, o), ds in eff.items():
        pos = sum(d > 0 for d in ds)
        same = max(pos, sum(d < 0 for d in ds)) / len(ds)
        rows.append((inp, o, st.median(ds), st.median(abs(d) for d in ds), same))
    print(f"\nactual behavior change from the added layers responding to inputs (output's "
          f"real value, input swept over its typical range, minus the same sweep with the "
          f"added layers frozen; median over {len(sample)} bibites; 'same sign' ~50% = "
          f"random per bibite, ~100% = shared habit)")
    for label, group in [("own state & time", lambda i: i in OWN_STATE),
                         ("surroundings", lambda i: i not in OWN_STATE)]:
        print(f"  {label}:")
        for inp, o, med, size, same in sorted((r for r in rows if group(r[0])),
                                              key=lambda r: -r[3])[:top]:
            print(f"    {inp:16} -> {o:14} size {size:.4f}  median {med:+.4f}  same sign {same:4.0%}")
    shared = [r for r in rows if r[4] >= 0.8 and r[3] >= 0.005]
    print(f"  shared habits (same sign >= 80% and size >= 0.005): "
          + (", ".join(f"{i}->{o} {m:+.3f} ({s:.0%})" for i, o, m, _, s in
                       sorted(shared, key=lambda r: -r[3])) or "none"))


def input_sweep(bibites):
    """Which inputs the added layers respond to, measured fairly: each input
    swept over its 5th-95th percentile range across the population."""
    ranges = input_ranges(bibites)
    rng = random.Random(0)
    sample = rng.sample(bibites, min(SWEEP_SAMPLE, len(bibites)))
    per_input = collections.defaultdict(list)
    per_input_hidden = collections.defaultdict(list)
    # per output: strongest own-state and strongest surroundings input, per bibite
    per_output = collections.defaultdict(lambda: ([], []))
    for b in sample:
        best_by_output = collections.defaultdict(lambda: [0.0, 0.0])
        for inp, (out_e, hid_e, outs) in sweep_effects(b, ranges).items():
            per_input[inp].append(out_e)
            per_input_hidden[inp].append(hid_e)
            slot = 0 if inp in OWN_STATE else 1
            for o, e in outs.items():
                best_by_output[o][slot] = max(best_by_output[o][slot], e)
        for o, (own, sur) in best_by_output.items():
            per_output[o][0].append(own)
            per_output[o][1].append(sur)

    print(f"\nwhat the added layers respond to (each input swept over its typical range; "
          f"biggest output change, median / 90th pct over {len(sample)} bibites; "
          f"L3 = biggest change inside the last added layer)")
    for label, group in [("own state & time", lambda i: i in OWN_STATE),
                         ("surroundings", lambda i: i not in OWN_STATE)]:
        rows = sorted(((i, st.median(v), sorted(v)[int(0.9 * (len(v) - 1))])
                       for i, v in per_input.items() if group(i)),
                      key=lambda r: -r[1])
        best = [max(e for i, e in zip(per_input, col) if group(i))
                for col in zip(*per_input.values())]
        best_hidden = [max(e for i, e in zip(per_input_hidden, col) if group(i))
                       for col in zip(*per_input_hidden.values())]
        print(f"  {label}: strongest input per bibite median {st.median(best):.4f} at outputs, "
              f"{st.median(best_hidden):.4f} inside L3 (internal, may not be used yet)")
        for i, m, p90 in rows[:5]:
            lo, hi = ranges[i]
            print(f"    {i:16} {m:.4f} / {p90:.4f}   L3 {st.median(per_input_hidden[i]):.4f}"
                  f"   (range {lo:.3g} to {hi:.3g})")
    print("  which outputs the inputs reach (median over bibites of the strongest input's effect):")
    print(f"    {'output':14} {'own state':>10} {'surroundings':>13}")
    for o, (own, sur) in sorted(per_output.items(), key=lambda kv: -st.median(kv[1][1])):
        print(f"    {o:14} {st.median(own):10.4f} {st.median(sur):13.4f}")


# Regimes of a sine self-loop x -> sin(w*x + input), from docs/brain_mechanics.md
LATCH_LO, LATCH_HI = 1.0, 2.26


def wiring_report(bibites):
    """How each kind of added connection has drifted, and whether any sine
    self-loop has reached the latch (1-bit memory) or chaotic regime."""
    kinds = collections.defaultdict(list)
    loops = []
    for b in bibites:
        nodes = {n["Index"]: n for n in b["brain"]["Nodes"]}
        for s in b["brain"]["Synapses"]:
            a, c = nodes[s["NodeIn"]], nodes[s["NodeOut"]]
            sa, sc = a["Desc"], c["Desc"]
            if not (is_added(sa) or is_added(sc)):
                continue
            if sa == sc:
                kind = "self-loops"
                loops.append(s["Weight"])
            elif a["archetype"] == 0:
                kind = "inputs -> L1"
            elif c["archetype"] == 1:
                kind = "L3 -> outputs"
            elif a["archetype"] == 1:
                kind = "outputs -> L1 (feedback)"
            elif int(sc[1]) == int(sa[1]) + 1:
                kind = f"L{sa[1]} -> L{sc[1]}"
            else:
                kind = f"L{sa[1]} -> L{sc[1]} (feedback)"
            kinds[kind].append(abs(s["Weight"]))
    n = len(bibites)
    print("\nadded wiring by kind (feedback weights well above the background drift = in use)")
    print(f"  {'kind':26} {'per bibite':>10} {'mean |w|':>9} {'non-zero':>9} {'max |w|':>8}")
    for kind, ws in sorted(kinds.items()):
        print(f"  {kind:26} {len(ws) // n:10} {st.mean(ws):9.4f} "
              f"{sum(w > 0 for w in ws) / len(ws):8.0%} {max(ws):8.3f}")
    latch = sum(LATCH_LO < w < LATCH_HI for w in loops)
    print(f"  self-loop regimes: leaky |w|<1 {sum(abs(w) < 1 for w in loops)}, "
          f"latch {LATCH_LO}<w<{LATCH_HI} {latch}, chaotic w>{LATCH_HI} "
          f"{sum(w >= LATCH_HI for w in loops)}, flip-flopping w<-1 {sum(w <= -1 for w in loops)}"
          f"  (of {len(loops)}; largest {max(loops):+.3f}, smallest {min(loops):+.3f})")


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
    behavior_report(bibites)
    wiring_report(bibites)
    settings = json.loads(z.read("settings.bb8settings").decode("utf-8-sig"))
    if len(settings["zones"]) > 1:
        pellets = json.loads(z.read("pellets.bb8scene").decode("utf-8-sig"))["pellets"]
        zone_breakdown(settings, pellets, bibites)
    print()


ZONE_GENES = ["SizeRatio", "SpeedRatio", "MouthMusclesWAG", "ViewRadius", "Diet"]


def zone_breakdown(settings, pellets, bibites):
    """Per food zone: standing food, residents, species mix, genes, brains."""
    zones = settings["zones"]
    world_r = settings["independents"]["SimulationSize"]["Value"]  # a radius
    density = settings["independents"]["biomassDensity"]["Value"]
    # A pellet's "amount" is material; its energy is amount x energy density.
    plant_energy = settings["materials"]["PlantSettings"]["energyDensity"]

    def zone_of(x, y):
        for zn in zones:
            r = zn["radius"] * (world_r if zn["radiusIsRelative"] else 1)
            if math.hypot(x - zn["posX"] * world_r, y - zn["posY"] * world_r) <= r:
                return zn["name"]
        return "gaps"

    home = [zone_of(*b["transform"]["position"]) for b in bibites]
    names = [zn["name"] for zn in zones] + ["gaps"]
    food = {g["zone"]: plant_energy * sum(p["pellet"]["amount"] for p in g["pellets"]
                                          if p["pellet"]["material"] == "Plant") for g in pellets}

    print("\nper zone (food % = standing plant energy vs. the zone's biomass cap)")
    print(f"{'zone':12} {'fert':>5} {'biom':>5} {'size':>5} {'food %':>6} "
          f"{'bibites':>7}  " + "  ".join(f"{g[:9]:>9}" for g in ZONE_GENES)
          + "  top species (share of zone)")
    for name in names:
        members = [b for b, h in zip(bibites, home) if h == name]
        zn = next((zn for zn in zones if zn["name"] == name), None)
        if zn:
            r = zn["radius"] * (world_r if zn["radiusIsRelative"] else 1)
            cap = density * zn["biomassDensity"] * math.pi * r * r
            cols = (f"{zn['fertility']:5.2f} {zn['biomassDensity']:5.2f} "
                    f"{zn['pelletSize']:5.2f} {100 * food.get(name, 0) / cap:5.0f}%")
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
