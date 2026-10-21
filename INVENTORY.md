# Bibites inventory — what's on this machine (as of 2026-10-21)

Found by scanning every drive (A, B, C, D, E, G) for anything named `*bibit*`,
then searching scripts/text files for bibite brain content. B, D and E had nothing.
The content search found no other brain-editing scripts besides the two in §4.
The `C:\Recovered\alpha` file lists mention a `D:\...\The Bibites\Bibitinator`.
That's the same old-PC tree from when it was mounted as D, not a separate copy.

**TL;DR**

- **The most complete copy of everything is on the A drive (old PC).** The
  current PC's save folder is only a partial Steam Cloud sync. It is missing the
  last two weeks of the Neuron Box run.
- **The 2025 "real-ish neural network" bibite is `NeuronBox_Complete`** (plus a
  `_Carnivore` variant). The final save is `Neuron_Box_Test_1_09_07_25.zip`
  (Sep 7 2025): 1,337 bibites at generation ~875, all still carrying the
  NeuronBox hidden layers, with 655 species recorded over the run.
- **"Bibitinator" is real and spelled exactly like that.** It's a 2022 .NET build
  that predates game v0.6. It probably won't open the 2025 files (not tested).
- **The ChatGPT brain script is `generate_bibite_brain.py`** (Jul 8 2025). The
  ChatGPT conversation that produced it is in your ChatGPT export.

---

## 1. Where things live

| Location | What | Notes |
|---|---|---|
| `A:\Users\acomb\AppData\LocalLow\The Bibites\The Bibites\` | **Game data folder, old PC (Steam v0.6.x)**: Bibites, Templates, Savefiles, Autosaves, Scenarios | **Most complete copy.** 202 files / 585 MB, 2022-09 → 2025-09-07 |
| `C:\Users\Stephen\AppData\LocalLow\The Bibites\The Bibites\` | Game data folder, this PC | Steam Cloud copy of the above, missing the 09_07_25 save and 23 of the 26 autosaves. The game was launched here today, so default templates and `Player.log` are from today |
| `A:\Users\acomb\Desktop\Media\Applications\The Bibites\` | Old manual-install era (2022–2023): Bibitinator, game builds 0.4.2 and 0.5.1, "My Saves", papers | 21k files / 583 MB, most of it one 20k-bibite dump |
| `A:\Users\acomb\Desktop\generate_bibite_brain.py` | The 2025 brain-generator script | Identical copy (same MD5) at `C:\Recovered\alpha\files\Desktop_misc\` |
| `A:\Users\acomb\Desktop\bibite_13.bb8` | A loose bibite from 2024-10-10 | Also copied into `C:\Recovered\alpha\files\Desktop_misc\` |
| `A:\Users\acomb\Desktop\Media\Projects\Programming\Python\BibiteFixer\` | 2022 `bibite_fixer.py` | Also copied into `C:\Recovered\alpha\...` and `C:\Recovered\gamma\...` |
| `C:\Recovered\alpha\files\Media\Games\The Bibites\` | 2023 "free for all" tournament bibites (223 `.bb8`) plus two screenshots of a baby Infirmus Agricola | Recovered-files copy. I didn't find these in A's game folder |
| `C:\Recovered\alpha\files\Desktop_misc\` | `Iratus Artificium v2.bb8`, `LabRat.bb8`, `bibite_13.bb8`, `generate_bibite_brain.py` | Copies of A Desktop files |
| `C:\Users\Stephen\Downloads\project_sweep_state\exports_chatgpt_full\generate-bibite-brain--686d424d.md` | The ChatGPT conversation that wrote the brain script (2025-07-08) | See §4 |
| `A:\Users\acomb\AppData\LocalLow\Sebastian Lague _ Lime inc_\Digital Logic Sim\SaveData\Bibite Brains\` | 2023-08-09 Digital Logic Sim chips: 2AD, 4BA, 4BM, D-LT, FAD, OR, TICK, XNOR (+ WireLayout) | You apparently prototyped bibite brain logic circuits in DLS |
| `G:\My Drive\__Media\0  Projects\Personal\Other\Gaming\The Bibites\Bibites Gaussian.gsheet` | Google Sheet (2023-08-09) | `.gsheet` is just a link, so open it in Drive |
| `A:\` and `C:\Program Files (x86)\Steam\steamapps\common\The Bibites\` | Steam installs (app 2736860, "The Bibites: Digital Life") | A: build 19588323, last updated 2025-08-23. C: build 22383127, updated 2026-10-21 (newer than all your saves) |
| `A:\ProgramData\Microsoft\Windows\WER\...`, `A:\Users\acomb\AppData\Local\CrashDumps\The Bibites.exe.2312.dmp` | Crash and hang reports | Junk |

---

## 2. The 2025 Neuron Box experiment (the thing you remembered)

Game version in the files: **0.6.2 / 0.6.2.1** (new JSON layout: top-level `nodes` / `synapses` / `nodeAnchors`).

### Templates — `...\The Bibites\Bibites\Templates\`

| File | Date | Notes |
|---|---|---|
| `NeuronBox_Complete.bb8template` | 2025-07-08 | Description: *"Starter Bibite for brain evolution experiment. Created from easy herbivore and modified to have a large number of tiny modifications to the brain. Nodes sorted! Hidden L1 = sine, Hidden L2 = sine"*. 62 nodes (33 inputs, 15 outputs, 12 hidden `L1N1–L1N6` / `L2N1–L2N6` + `Hidden0/1`), 342 synapses |
| `NeuronBox_Complete_Carnivore.bb8template` | 2025-07-26 | Carnivore variant |
| `archive\NeuronBox_archive\07-08-25\NeuronBox.bb8template`, `NeuronBox_Complete.bb8template` | 2025-07-08 | Earlier versions |
| 13 stock templates (Basic Bibite, Camel, Whale, …) | — | Game defaults. On C they were refreshed today and `Darth bibitus` was added |

### Scenarios built for it — `...\Scenarios\`

`Neural Net Training.zip` and v2–v5 (Jul 8 2025), `NeuronBox_update_07-18-25`,
`Neuron_Box_07-18-25_1900`, `NeuronBox_07-18-25_2345`,
`Neuronbox Carnivore Update 07-26-25`, `Neuronbox 07-26-25 2130`.

### The long evolution run — `...\Savefiles\Neuron_Box_Test_1_*.zip` (19 saves)

| Save | Bibites | Max generation | Notes |
|---|---|---|---|
| `_07-8-25_1200` | — | — | Start, 0.6 MB |
| `_07-18-25_1600` … `_07-23-25_1830` | | | |
| `_07-26-25_1700/1705/2100` | | | ~28 MB each (population boom) |
| `_07-26-25_2300` | 863 | 359 | |
| `_07-27-25_1000`, `_07-31-25_*`, `_08-08-25_1430`, `_08_11_25` | | | |
| `_08_24_25` | 1,071 | 698 | ← roughly where you remembered stopping |
| **`_09_07_25`** | **1,337** | **875** | **Final manual save. On A only** |
| `Autosaves\autosave_20250831…` → `autosave_20250907111241` (26 files, 270 MB) | 1,243 (last one) | 873 | 23 of 26 on A only |

Every bibite in the later saves still has the L1/L2 hidden nodes, with a median of
about 250 hidden-layer synapses at |weight| > 0.05, so the hidden layers did evolve
non-zero weights. The final save's `speciesData.json` records 655 species, e.g.
*Noyoudontus rinus*, *Coderus alternatus*,
*Neuronbox_complete_carnivore burgessdanielus*.

---

## 3. Your own bibites (`.bb8`)

**In `...\The Bibites\Bibites\` (same on A and C):**
Aenus Tyrannus, Rosa Tyrannus (2023-07 "Duel of Tyrants"); Blue/Green/Red Stinkbag,
Brainlet (2023-08 test subjects); Infirmus Agricola (2022-09); Iratus Artificium
v0/v1/v2 (2023-08, engineered); Iratus Populator (2023-08); LabRat, Lab_Rat
(2024-10); bibite_2 (2023-08).

**Old "My Saves" archive, `A:\...\Media\Applications\The Bibites\My Saves\Bibites\` (2022–2023, pre-0.6 format):**

| Folder | Contents |
|---|---|
| `000_Test` | Pascuis Initium.json |
| `001_Trinity` | Cyanoculi Familiaria, Flavumoculi Devortador, Rosoculi Urbanum, a `Stable\t0` set (30), and `102_51_59\` = **19,945 dumped bibites (202 MB)** |
| `002_Neurogenesis` | 244 bibites incl. `t0\l1`, `t0\w1` |
| `003_Neurostabilization 1` | 297 + `Fixed\` (17) + `Tournament\` (17) |
| `004_Quinque Integrare 1` | Infirmus Agricola |
| `005_Duel of Tyrants` | Aenus / Rosa Tyrannus |
| `006_Shakeout` | Iratus Populator |
| `_Engineered` | Iratus Artificium v0–v2; Test Subjects (Stinkbags, Brainlet) |

That folder also has `Simulation Settings\` (7 presets: Lab, Neo Galapagos,
Neurogenesis, Neurostabalization 1/2, The Meat Grinder, Trinity) and `Worlds\`
(228 world zips, 105 MB, Sep 2022).

**Other saves in `...\Savefiles\` (2023–2024):** Duel of Tyrants (25 snapshots, ends "Aennus Wins!"),
Quinque Integrare 1 + qualifier groups, QI1 QG (12), Amica Tyrannus Brain Sorting,
Iratus Populator Shakeout, Red Ocean (4), Test Tube 1 (2), Lab_Rat_Cage (2).
Plus 26 old 2022 world autosaves in `...\autosaves\`.

---

## 4. Tools and scripts

### Bibitinator — `A:\Users\acomb\Desktop\Media\Applications\The Bibites\Bibitinator\`
Fan-made bibite editor, a .NET app (`Bibitinator.exe/.dll`, `Newtonsoft.Json.dll`,
bundled `7z.exe`, `SettingsData.json`). Built 2022-06-05. It predates the v0.6 file
format, so it probably can't edit the 2025 NeuronBox files. I haven't tested it.
I found no newer copy anywhere on the machine, so if you used a newer Bibitinator
in 2025, it isn't saved locally.

### `generate_bibite_brain.py` (2025-07-08) — the ChatGPT script
Writes JSON text snippets that you pasted into the bibite file by hand:
- `make_layer_snippet(x)` → two hidden nodes `L1N{x}`/`L2N{x}` (Type 4, Index `48+2x`/`49+2x`) → `nodes.txt`
- `make_connection_snippet(x, y)` → 33 synapses from every input node into a hidden node, weight 0 → `connections.txt`
- `make_inverse_connection_snippet(node_in, y)` → 15 synapses from a hidden node to every output, weight 0 → `connections_out.txt`
- Run for x = 2…6. The output `.txt` files weren't found anywhere.

**ChatGPT conversation** (`generate-bibite-brain--686d424d.md`, 2025-07-08): you asked
which activation function to use for the zero-weight hidden layers. Its answer was
**Sine**, and it still recommended Sine after you mentioned feedback loops from the
outputs into layer 1. The rest of the conversation is iterating on the three
functions above.

### `bibite_fixer.py` (2022-09-29) — `...\Projects\Programming\Python\BibiteFixer\`
Batch-converts files in `Input\` → `Output\`: strips a 3-char BOM, sets
`version = "0.4.2"`, and sets `genes.tag` to the filename. For migrating old
bibites to 0.4.2. `Input` and `Output` are empty.

### Reference material — `A:\...\The Bibites\Literature and Background\`
- *Help on The Bibites interface.pdf*
- Stanley & Miikkulainen 2002, *NEAT*
- Stanley et al. 2005, *NERO*
- `bibite eye color.txt`

---

## 5. Copied into this repo

The small, irreplaceable files are now in [`legacy/`](legacy/README.md).

## 6. Suggested next steps

1. **Copy the A-drive-only files to C** before anything else:
   `Neuron_Box_Test_1_09_07_25.zip` and the 23 autosaves. Otherwise the last two
   weeks of the run exist only on the old drive.
2. The Steam build on C was updated today. Your saves are v0.6.2.1. Back up the
   save folder before loading anything in the new version, in case it migrates
   the files.
3. Still not copied into `legacy/` (on hold): NeuronBox champions extracted
   from the final save.
