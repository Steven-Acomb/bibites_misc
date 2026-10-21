# GoodNotes notes (iPad), Aug 2023

Four handwritten notebooks, exported from GoodNotes on 2026-10-21. Each one has
an archival note at the end giving its original GoodNotes date. The PDFs have no
usable text layer (OCR reads "Iratus" as "Fratus", among other errors), so the
transcription below is the searchable version. Values are read off the
handwriting. Where I'm unsure of a reading, I say so.

| PDF | Pages | Dated | What it is |
|---|---|---|---|
| `Lineages.pdf` | 12 | 2023-08-08 | Family tree from 2022 to 2023, the Quinque Integrare 1 tournament, the Duel of Tyrants, scenario settings |
| `Bibite Brains.pdf` | 3 | 2023-08-08 | How neurons work + testing "Brainlet" |
| `Bibite Editing.pdf` | 14 | 2023-08-09 | Reverse-engineering Iratus Populator's brain into equations, used to build **Iratus Artificium v1/v2** |
| `Brainy Bibite.pdf` | 1 | 2023-08-25 | Start of the "large-brained bibite template" idea, the seed of the 2025 NeuronBox |

---

## Lineages

**Family tree** (each one evolved from the one above):

```
Pascuis Initium (gen 1)                     "Test" generation
 ├─ Cyanoculi Familiaria (gen 40)           "Trinity" generation
 ├─ Flavumoculi Devortador (gen 69)
 │   └─ Bibite_24 (gen 223)                  "Neurogenesis" generation
 │       └─ [Neurostabilization tournament: never completed, skipped;
 │           only did the first 10-bibite section of 1 tier; totally neglected NS2]
 │       └─ Infirmus Agricola (gen 420)      (game v0.4.2 → v0.5.1;
 │           +0.03 digestion, −0.05 growth, −0.03 pheromones, −0.04 brain)
 │           ├─ Aenus Tyrannus (gen 452)  ┐  "Quinque Integrare 1"
 │           │   └─ Iratus Populator (gen 678)   via "Duel of Tyrants"
 │           └─ Rosa Tyrannus (gen 451)   ┘
 └─ Rosoculi Urbanum (gen 80)
```

**"Quinque Integrare 1"**: seeded with Infirmus Agricola (gen 420). Settings:
¼ brain costs, ½ pheromone costs, everything else default. Sim area smallest,
biomass density sparse, fertility low, radioactivity severe.
Named descendants: *Congregor Remissa* (gen 444), *Ratis Mitis* (446),
*Monstri Instabilitate* (446), *Parum Cursor* (447), *Pater Subidens* (442),
*Hostiliter Agricola* (439), *Juxta Hostilis* (431).

**Candidate table** (2 pages; columns are #, eye color, body color, gen, diet,
hidden nodes, synapses). All are gen 449–456, mostly diet 0 with a few small
omnivores (0.02–0.27), and 0–3 hidden nodes with 18–26 synapses. Examples:
#10 red/pale cyan, 2 hidden, 22 syn. #14 green/violet, diet 0.183, 3 hidden.
#41 rust/black-grey, diet 0.158, 3 hidden, 26 syn. #8 brown/cyan, 0 hidden, 18 syn.
They're grouped into look-alike clusters, which became the qualifier groups.

**Qualifiers** (⚠ "PREVENT MUTATIONS?"), with winners highlighted:
| Group | Members | Winners |
|---|---|---|
| 1 | 10, 36-001, 36, 42-001, 42, 44 | **36-001, 42-001** |
| 2 | 8, 70, 77, 29-001, 29 | **77, 29-001** |
| 3 | 41-002, 41, 61-001, 61 | **41-002, 41** |
| 4 | 14, 60 / 11-001, 11 | **60** |
| 5 | 82-001, 56, 82 | **82** |

**"QI1 QG" sub-groups**: "9" (9-002, 9-003), "33", "52" (52-001), "64" (64-001,
64-002), "h" (h-004/006/008), "m" (m-003), 22/28/58 (58-001, 22-002),
67/76/83/90 (90-001, 76, 83-002), 50/84/87 (84, 87-003, 50-002), 69/101
(101-004, 69-004), 20/55 (55, 55-002), 75 (75-002, 75-007).

**Limbo** (⅓ brain, ⅔ pheromone costs). 101-004, 22-002, 29-001 and 33 are
crossed out. 36-001, 41-002, 41, 42-001, 50-002, 52-001, 55-002, 55, 58-001 and
60 are checked.
- **Limbo FFA 1**: 36-001 (copper + cyan) ✓, 41-002, 41, 42-001 (rose + sea green) ✓, 50-002
- **Limbo FFA 2**: 52-001 (copper + slate) ✓, 55-002, 55 ("cool!"), 58-001 (rose + sea green) ✓, 60 ("greedy/envious?")
- **T2-A**: 36-001 ✓ vs 52-001 → **"Aenus Tyrannus", "the bronze tyrant"** (36-001 noted as "territorial!", 52-001 "tyrant?")
- **T2-B**: 42-001 ✓ vs 58-001 → **"Rosa Tyrannus", "Rose Tyrant"**

**"Duel of Tyrants"** (⅓ brain, ⅔ pheromone costs): Aenus (−0.333 x, rad 0.667,
crowned winner) vs Rosa (0.334 x, 0.666 rad). Two pellet sources: hue 0.10 and
hue 0.9, tolerance 10%, radius 664, period 30 s.

**"Red Ocean"** settings: tried default, then ½ brain, then 2/5 brain (all
crossed out). Settled on **2/5 brain, ¾ pheromone** ✓.

## Bibite Brains

- All output neurons default to 0.5 unless set otherwise in their brain.
- A neuron's value is the sum of the synapse strengths coming into it. Neurons
  apply their activation function to that sum. (Sketch of the sigmoid crossing 0.5.)
- **Testing "Brainlet"** (a lobotomized Iratus Populator) shows what a bibite does
  with no brain at all:
  - It doesn't move, and growth is −0.08 E/s.
  - Everything else reads 0.00, yet energy flow is −0.09 E/s. That's almost
    certainly rounding.
  - It eats when a pellet is placed directly in its mouth.
  - It lays eggs, heals and attacks whenever it can, and digestion is always ½.
  - It emits no pheromones.

## Bibite Editing (reverse-engineering Iratus Populator)

Each output was worked out as a closed-form function of its inputs, then
simplified:

| Output | Evolved brain | Simplified ("Artificial") |
|---|---|---|
| Accelerate | `1 → 0.26 → sigmoid → ×1.41 → tanh` ≈ 0.66 (a direct 0.15 link seems ignored) | **A ≈ 0.6̄**, i.e. `tanh(arctanh(0.66))` |
| Eat | `EAT ≈ sig(−1.01·E% − 0.84)` (meat input has no effect); 0.5 at E%=0 → 0.26̄ at E%=1 | **EAT ≈ sig(−1·E% − 0.85)** |
| Digestion | `DGN = sig(9.11·Full − 4.45)`; DGN(0)≈0.0115, DGN(1)≈0.9906, slope 2.27 at Full=½ | **DGN ≈ sig(10·Full − 5)** |
| Rotate | `ROT ≈ tanh(1.88·PlantAngle)` | same |
| Herding | Red pheromone angle ×2.78 and gauss(plant closeness) ×−0.5 → tanh. Then: "the red pheromone interaction is directional. WAIT: it actually doesn't even matter. Functionally zero impact?" | **HRD ≈ tanh(0.3̄·PlantΔ − ½)** |
| Grab | `GRB = tanh(1.42·gauss(−1.37·PlantCloseness))`. The 24 measured points (0.00→0.91 … 0.90→0.54) match. "data matches model!" ✓ | **GRB ≈ tanh(−1·PlantΔ + 3/2)** (added in v2) |
| Attack | — | **ATK ≈ 2.25·BibiteCloseness** |
| Red pheromone | `(−0.44)·TimeAlive + 1.61·NPlants − 0.85·Fullness` (the Minute input is used as time alive) | Emits red pheromone while younger than **3.66 s per nearby plant** when hungry, **1.72 s** when full |

The first six simplified rows are **"Iratus Artificium v1"**. Adding GRB makes **v2**.
These match `legacy/bibites/my_saves_2022-2023/_Engineered/Iratus Artificium/`.

Other observations: rotation is clockwise (confirmed experimentally). The empty
world baseline outputs were Accel 0.66, Rot 0, HRD −0.47, EAT 0.27, DGN 0.01,
GRB 0.89, pheromones 0, Heal 0.5, Attack 0.5, Grow −0.85.

**Later pages (logic sketches):**
- **Omnivory**: separate herbivory (plant angle ×1.88 → rotate; 1.5 bias − plant
  closeness → grab) and carnivory (the same with meat). A "Plants or meat closer?"
  selector: plants closer = −1, meat closer = +1, equidistant = 0. Unfinished:
  `X = 0.5 + ReLU(∞ × Diff(…`.
- **Logic gates out of latch neurons**: AND = two inputs at 0.5 each, OR/XOR =
  inputs at ∞.
- **Differential neuron**: diff at 0⁻ = 100, at 0⁺ = 0. Chain:
  Full →1→ d/dt →1→ ReLU →∞→ latch, to detect "is eating?".
- Truth tables for a half adder (A, B, Σ, C) and binary 5 / 7. These tie in with
  the Digital Logic Sim "Bibite Brains" chips (2023-08-09) in
  `../digital_logic_sim_bibite_brains/`.

## Brainy Bibite (2023-08-25)

"Starts with Iratus Artificium v2." The default wiring diagram is: bias/energy/
fullness/plant-closeness/plant-angle inputs → Accel, Rot, HRD, EAT, DGN, GRB, ATK.
**"Want: a good template for a large-brained bibite which…"** It stops there.
This is the idea that was picked back up two years later as NeuronBox (2025).
`legacy/bibites/named/bibite_2.bb8` has the same date (2023-08-25) and may be this one.

---

## Connections to the saved files

- The **2023 "free for all" tournament bibites** (on hold, at
  `C:\Recovered\alpha\files\Media\Games\The Bibites\free for all\`) are exactly
  this tournament. The 32 top-level files (`36 001.bb8`, `41 002.bb8`, `60.bb8`, …)
  are the QI1 qualifier and Limbo entrants named above. Its `qualifiers\` folders
  (9, 33, 52, 64, h, m, group 1–5, …) match the QI1 QG groups.
- The save zips `Quinque Integrare 1 *`, `QI1 QG - *`, `Duel of Tyrants *` and
  `Red Ocean *` (still on the A drive) are the runs these pages describe.
