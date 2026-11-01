"""Read the statistics the game logs on its own clock, from a world save's
data.bin, so a single save gives a regular time series of the whole run.

What the game logs (decompiled v0.6.3.1: DataLogger, BibiteTracker):
- every 60 sim-seconds: energy in Bibites / Plants / Meats / Free, entity
  counts, age quartiles, age-at-death quartiles, brain size, eggs laid,
  births and deaths since the last point;
- every sim-hour: a 20-bin histogram of every gene across the population.
  It is kept hourly for 6 h, then 3-hourly, 12-hourly, daily, weekly and
  4-weekly. Older points are averages of the finer ones.

Two "adapted enough?" readouts, both measured from a given sim time
(--since: when the world's settings last changed, which the log doesn't
record):
- Bibite share of total energy, averaged per doubling of time since then.
  Gains that shrink from one doubling to the next mean it's levelling off.
- Per gene, net change of the population median vs. the total distance it
  moved ("directionality": ~1 = trending, ~0 = wandering), on an even
  8-step grid.

Format notes:
- data.bin is nested blocks, each prefixed by its byte length (int32).
  The DataLogger block holds progress (float32) and nMinutes (int32), then
  one block per stream group.
- A "parallel" stream group keeps the same series at several resolutions at
  once. The 1-minute points cover the last hour, 10-minute points the last
  ~10 h, 30-minute points ~48 h, 3-hour points ~14 days, daily ~16 weeks,
  weekly ~2 years. Each coarser point is a sample of the finer one (the
  oldest of its group), except births/deaths, which are summed.
- Block layout: nData (int32), width (byte), nScales (byte), then
  width x nData float32 stored stream by stream, then pushCounters
  (nScales-1 bytes) and points per scale (nScales bytes). Within a scale,
  point 0 is the newest.

Point times follow the in-game graphs and Gene Analysis panel (values and
times checked against both, 2026-11-01).

Usage:
  python tools/game_log.py <world save .zip> [--since SIM_HOURS] [--genes] [--csv OUT_DIR]
"""

import argparse
import csv
import json
import math
import statistics as st
import struct
import sys
import zipfile
from pathlib import Path

# Minutes per point at each scale of the game's ParallelDetailedConfig:
# feed ratios 10, 3, 6, 8, 7 between successive scales.
PARALLEL_STEPS_MIN = [1, 10, 30, 180, 1440, 10080]

# Order of DataLogger's saveable stack; the genes histogram group is 3rd.
STREAMS = [
    ("biomass", ["bibites_E", "plants_E", "meats_E", "free_E"]),
    ("counts", ["bibites_and_eggs", "plant_pellets", "meat_pellets"]),
    ("genes", None),
    ("brain_size", ["min_nodes", "mean_nodes", "max_nodes",
                    "min_synapses", "mean_synapses", "max_synapses"]),
    ("age_h", ["q25", "median", "q75", "max"]),
    ("death_age_h", ["q25", "median", "q75", "max"]),
    ("eggs_laid", ["median", "c1", "c2", "c3", "max", "mean"]),
    ("births_deaths", ["births", "deaths"]),
]


# Gene histograms: SerialHeavyConfig in hours, as (points kept, feed ratio).
SERIAL_FORMATS = [(6, 3), (6, 4), (8, 2), (9, 7), (6, 4), (8, 2), (8, 0)]

# Genes in the game's enum order, with each gene's (min, max) setting.
GENES = [
    ("LayTime", 1, 51), ("BroodTime", 1, 101), ("HatchTime", 1, 101),
    ("SizeRatio", 0.05, 2.55), ("SpeedRatio", 0, 2.5), ("ColorR", 0, 1),
    ("ColorG", 0, 1), ("ColorB", 0, 1), ("MutationAmountSigma", 0, 0.25),
    ("AverageMutationNumber", 0, 30), ("BrainMutationSigma", 0, 0.25),
    ("BrainAverageMutation", 0, 10), ("ViewAngle", 0, 360), ("ViewRadius", 0, 200),
    ("ClockSpeed", 0.1, 10.1), ("PheroSense", 0, 500), ("Diet", 0, 1),
    ("HerdSeparationWeight", 0, 4), ("HerdAlignmentWeight", 0, 4),
    ("HerdCohesionWeight", 0, 4), ("HerdVelocityWeight", 0, 1),
    ("HerdSeparationDistance", 0, 100), ("GrowthScale", 0, 2),
    ("GrowthMaturityFactor", 0, 10), ("GrowthMaturityExponent", 0, 10),
    ("EyeOffset", 0, 1), ("StomachWAG", -1, 9), ("WombWAG", -1, 9),
    ("FatWAG", -1, 9), ("ArmorWAG", -1, 9), ("ThroatWAG", -1, 9),
    ("MouthMusclesWAG", -1, 9), ("MoveMusclesWAG", -1, 9),
    ("FatStorageThreshold", 0, 1), ("FatStorageDeadband", 0, 0.5),
]


def blocks(buf, start, end):
    """Split a run of length-prefixed blocks into (offset, length) pairs."""
    out = []
    while start + 4 <= end:
        (n,) = struct.unpack_from("<i", buf, start)
        out.append((start + 4, n))
        start += 4 + n
    return out


def parallel_group(buf, off, n):
    """Decode one parallel stream group into per-scale lists, newest first."""
    n_data, width, n_scales = struct.unpack_from("<iBB", buf, off)
    floats = struct.unpack_from(f"<{width * n_data}f", buf, off + 6)
    tail = off + 6 + width * n_data * 4
    push_counters = list(buf[tail:tail + n_scales - 1])
    per_scale = list(buf[tail + n_scales - 1:tail + 2 * n_scales - 1])
    points = [[floats[j * n_data + i] for j in range(width)] for i in range(n_data)]
    scales, i = [], 0
    for count in per_scale:
        scales.append(points[i:i + count])
        i += count
    return scales, push_counters


def series(scales, push_counters, end_min):
    """Merge scales into one time series (oldest first), using the finest
    resolution available for each period. Returns [(minute, values)].
    Point i of a scale is placed (i + 1) steps before the save, the same as
    the in-game graphs draw it (checked against them 2026-11-01)."""
    out, covered_from = [], end_min
    for k, pts in enumerate(scales):
        if not pts:
            break
        step = PARALLEL_STEPS_MIN[k]
        for i, vals in enumerate(pts):
            t = end_min - (i + 1) * step
            if t < covered_from:
                out.append((t, vals))
        covered_from = min(t for t, _ in out) if out else end_min
    return sorted(out, key=lambda p: p[0])


def hist_median(lo, hi, counts, span):
    """Median of a gene histogram. Bins start at lo; their width follows the
    game's rule (range rounded up to fifths of the gene's span, / 20)."""
    total = sum(counts)
    if total == 0:
        return float("nan")
    width = max(1, math.ceil(round(5 * (hi - lo) / span, 6))) / 5 * span / len(counts)
    half, acc = total / 2, 0
    for i, c in enumerate(counts):
        if c and acc + c >= half:
            return lo + width * (i + (half - acc) / c)
        acc += c
    return hi


def gene_group(buf, off, end_min):
    """Decode the hourly gene histograms into [(minute, {gene: median})],
    oldest first. Only the points the game displays are kept, timed the way
    its Gene Analysis slider labels them (TimeOfPointInSerialConfig: the
    n-th point sits n+1 steps back, steps growing per scale). Verified
    against the panel 2026-11-01."""
    n_points, _n_data, n_bins, n_gene = struct.unpack_from("<iiii", buf, off)
    p = off + 16
    points = []
    for _ in range(n_points):
        genes = []
        for _g in range(n_gene):
            lo, hi = struct.unpack_from("<ff", buf, p)
            counts = struct.unpack_from(f"<{n_bins}H", buf, p + 8)
            genes.append((lo, hi, counts))
            p += 8 + 2 * n_bins
        points.append(genes)
    n_scales = len(SERIAL_FORMATS)
    per_scale = list(buf[p + n_scales - 1:p + 2 * n_scales - 1])
    # Each scale stores its kept points, then "accumulator" slots waiting to
    # be averaged into the next scale; the game displays only the former.
    out, i, age_h, step = [], 0, 0, 1
    for k, (size, feed) in enumerate(SERIAL_FORMATS):
        for j in range(per_scale[k]):
            genes = points[i + j]
            med = {name: hist_median(*genes[g], mx - mn)
                   for g, (name, mn, mx) in enumerate(GENES)}
            out.append((end_min - 60 * (age_h + (j + 1) * step), med))
        i += min(size + feed, n_points - i)
        age_h += size * step
        step *= max(feed, 1)
    return sorted(out, key=lambda q: q[0])


def read(path):
    z = zipfile.ZipFile(path)
    buf = z.read("data.bin")
    scene = json.loads(z.read("scene.bb8scene").decode("utf-8-sig"))
    end_min = scene["simulatedTime"] / 60.0
    logger_off, logger_len = blocks(buf, 0, len(buf))[0]
    groups = blocks(buf, logger_off + 8, logger_off + logger_len)
    result = {}
    for (name, cols), (off, n) in zip(STREAMS, groups):
        if cols is None:
            result["genes"] = gene_group(buf, off, end_min)
            continue
        scales, pc = parallel_group(buf, off, n)
        result[name] = (cols, series(scales, pc, end_min))
    return result, end_min


def bibite_share(data):
    """[(sim hours, % of total energy held by bibites and eggs)]."""
    return [(t / 60, 100 * v[0] / sum(v)) for t, v in data["biomass"][1] if sum(v) > 0]


def doubling_windows(since_h, end_h, n=4):
    """[since+T/2, end], [since+T/4, since+T/2], ... newest first."""
    span = end_h - since_h
    return [(since_h + span / 2 ** (k + 1), since_h + span / 2 ** k) for k in range(n)]


def doubling_report(share, since_h, end_h):
    print(f"\nbibite share of total energy per doubling of time since {since_h:g} h "
          "(shrinking gains = levelling off)")
    rows = []
    for a, b in reversed(doubling_windows(since_h, end_h)):
        xs = [s for h, s in share if a <= h < b]
        if len(xs) >= 2:
            rows.append((a, b, st.mean(xs), st.pstdev(xs), len(xs)))
    prev = None
    for a, b, m, sd, n in rows:
        gain = f"{m - prev:+5.1f} pts" if prev is not None else ""
        print(f"  {a:7.1f} - {b:7.1f} h   mean {m:5.1f}%  (sd {sd:.1f}, {n} points)  {gain}")
        prev = m


def gene_trends(genes, since_h, end_h, steps=8):
    """Per gene over [since, end]: median then and now, net change as % of the
    gene's range, and directionality = |net| / distance travelled on an even
    grid (nearest logged point at each step)."""
    pts = [(t / 60, m) for t, m in genes if since_h <= t / 60 <= end_h]
    if len(pts) < 3:
        return None, pts
    grid = [since_h + (end_h - since_h) * k / steps for k in range(steps + 1)]
    sampled = [min(pts, key=lambda p: abs(p[0] - g))[1] for g in grid]
    rows = []
    for name, mn, mx in GENES:
        ys = [s[name] for s in sampled]
        path = sum(abs(b - a) for a, b in zip(ys, ys[1:]))
        net = ys[-1] - ys[0]
        rows.append((name, ys[0], ys[-1], 100 * net / (mx - mn),
                     abs(net) / path if path else 0.0))
    return rows, pts


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("save")
    p.add_argument("--since", type=float, default=0.0,
                   help="sim hours when the world's settings last changed")
    p.add_argument("--genes", action="store_true", help="print per-gene trends")
    p.add_argument("--csv", help="write one CSV per stream into this folder")
    a = p.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    data, end_min = read(a.save)
    end_h = end_min / 60
    print(f"{a.save}: sim time {end_h:.1f} h")
    for name, val in data.items():
        if name == "genes":
            print(f"  {'genes':14} {len(val):4} points from {val[0][0] / 60:7.1f} h to "
                  f"{val[-1][0] / 60:6.1f} h  (per-gene histograms)")
            continue
        cols, pts = val
        print(f"  {name:14} {len(pts):4} points from {pts[0][0] / 60:7.1f} h to {pts[-1][0] / 60:6.1f} h  ({', '.join(cols)})")
    doubling_report(bibite_share(data), a.since, end_h)
    if a.genes:
        rows, pts = gene_trends(data["genes"], a.since, end_h)
        if rows is None:
            print(f"\ngene trends: only {len(pts)} gene snapshots after {a.since:g} h")
        else:
            print(f"\ngene medians from {a.since:g} h to {end_h:.1f} h "
                  f"({len(pts)} snapshots, 8-step grid); sorted by |net change|")
            print(f"  {'gene':24} {'then':>9} {'now':>9} {'net, % of range':>16} {'directionality':>15}")
            for name, y0, y1, net, d in sorted(rows, key=lambda r: -abs(r[3])):
                print(f"  {name:24} {y0:9.4g} {y1:9.4g} {net:+15.1f}% {d:15.2f}")
    if a.csv:
        out = Path(a.csv)
        out.mkdir(parents=True, exist_ok=True)
        with open(out / "genes_median.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["sim_hours"] + [g[0] for g in GENES])
            for t, med in data["genes"]:
                w.writerow([round(t / 60, 3)] + [round(med[g[0]], 5) for g in GENES])
        for name, val in data.items():
            if name == "genes":
                continue
            cols, pts = val
            with open(out / f"{name}.csv", "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["sim_hours"] + cols)
                for t, vals in pts:
                    w.writerow([round(t / 60, 3)] + [round(v, 4) for v in vals])
        print(f"wrote CSVs to {out}")


if __name__ == "__main__":
    main()
