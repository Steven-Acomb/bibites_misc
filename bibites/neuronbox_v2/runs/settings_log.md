# Settings log: NeuronBox v2 test 2

Every change to the world's rules, with the sim time it took effect. The
game's statistics log doesn't record settings changes. This table supplies
the `--since` value for `tools/game_log.py`, which measures adaptation from
the last change.

**Adding a row:** note the in-game **Time** (top right) when you change
something, or save just before and after. Sim hours = days × 24 + hours.

| Date | Sim time | What changed | Source |
|---|---|---|---|
| 2026-10-21 | 0 h | World started from the 2025 run's settings (saved as a scenario), seeded with a few NeuronBox_v2. | Steve |
| 2026-10-22 ~06:40 | 14.9 h | Background Mutation Variance 5% → 10%; Mutation Value Relativity 50% → 25%. | Save diff: `10-22` (14.91 h) vs `10-22 p1` (14.93 h) |
| 2026-10-25 ~12:00 | 28.8 h | Food zones hot-swapped from World + Zone 1 (both Center-to-edge) to the 7-zone hexagon. Each outer zone varies one of fertility, biomass or pellet size along a line through Center. Totals matched (1.339 ME, 2.13 kE/s, ~6.7k pellets). | Save diff: `10-25 p1` vs `p2 (hex)` (both 28.80 h) |
| 2026-10-25 ~12:00–13:14 | 28.8 → 29.0 h | Temporary food boost: global spawn rates and limits raised, pellets hand-spawned, then repeated "delete 50% of pellets" and settings restored. The boost settings were never captured in a save. | Steve; `p4` (29.01 h) has the hex settings again |

**For `--since`:** use **29.0** for the hex phase. That's the clean start
after the boost was undone. 28.8 includes the boost transient.
