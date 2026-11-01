"""Read the statistics the game logs on its own clock, from a world save's
data.bin, so a single save gives a regular time series of the whole run.

What the game logs (decompiled v0.6.3.1: DataLogger, BibiteTracker):
- every 60 sim-seconds: energy in Bibites / Plants / Meats / Free, entity
  counts, age quartiles, age-at-death quartiles, brain size, eggs laid,
  births and deaths since the last point;
- every sim-hour: a 20-bin histogram of every gene (not decoded here yet).

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

Point times are approximate (within one step of their scale).

Usage:
  python tools/game_log.py <world save .zip> [--csv OUT_DIR]
"""

import argparse
import csv
import io
import json
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
    resolution available for each period. Returns [(minute, values)]."""
    out, covered_from = [], end_min
    for k, pts in enumerate(scales):
        if not pts:
            break
        step = PARALLEL_STEPS_MIN[k]
        lag = sum(push_counters[j] * PARALLEL_STEPS_MIN[j] for j in range(min(k, len(push_counters))))
        for i, vals in enumerate(pts):
            t = end_min - lag - i * step
            if t < covered_from:
                out.append((t, vals))
        covered_from = min(t for t, _ in out) if out else end_min
    return sorted(out, key=lambda p: p[0])


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
            continue
        scales, pc = parallel_group(buf, off, n)
        result[name] = (cols, series(scales, pc, end_min))
    return result, end_min


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("save")
    p.add_argument("--csv", help="write one CSV per stream into this folder")
    a = p.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    data, end_min = read(a.save)
    print(f"{a.save}: sim time {end_min / 60:.1f} h")
    for name, (cols, pts) in data.items():
        print(f"  {name:14} {len(pts):4} points from {pts[0][0] / 60:7.1f} h to {pts[-1][0] / 60:6.1f} h  ({', '.join(cols)})")
    if a.csv:
        out = Path(a.csv)
        out.mkdir(parents=True, exist_ok=True)
        for name, (cols, pts) in data.items():
            with open(out / f"{name}.csv", "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["sim_hours"] + cols)
                for t, vals in pts:
                    w.writerow([round(t / 60, 3)] + [round(v, 4) for v in vals])
        print(f"wrote CSVs to {out}")


if __name__ == "__main__":
    main()
