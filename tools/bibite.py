"""Read, edit, and write Bibites (v0.6) bibite templates.

A template (.bb8template) is JSON with top-level "nodes", "synapses", "genes",
and optional "nodeAnchors" (brain-viewer layout). Saved bibites (.bb8) wrap the
same brain under "brain": {"Nodes", "Synapses"}; only templates are handled here.

Format notes (verified against game files):
- Node "Index" is its position in the list (contiguous from 0); synapses refer
  to nodes by Index. Input/output Indexes are NOT fixed across bibites
  (Easy Herbivore lacks RotationSpeed, so everything after it shifts), so look
  nodes up by "Desc".
- Node and synapse "Inov" numbers are separate sequences.
- "baseActivation" is the node's resting value / bias.
- "nodeAnchors" is keyed by node Inov (as a string). Inputs sit at x=0 and
  outputs at x=1 with y as a column slot; hidden nodes use x, y in 0..1.
"""

import json
from pathlib import Path

# Activation function "Type" codes, in the game's menu order.
INPUT, SIGMOID, LINEAR, TANH, SINE, RELU, GAUSSIAN, LATCH, DIFFERENTIAL, \
    ABS, MULT, INTEGRATOR, INHIBITORY, SOFTLATCH = range(14)

# Every input and output node a v0.6 bibite can have, in the game's order.
INPUTS = [
    "EnergyRatio", "Maturity", "LifeRatio", "Fullness", "Speed", "RotationSpeed",
    "IsGrabbing", "AttackedDamage", "EggStored", "BibiteCloseness", "BibiteAngle",
    "NBibites", "PlantCloseness", "PlantAngle", "NPlants", "MeatCloseness",
    "MeatAngle", "NMeats", "RedBibite", "GreenBibite", "BlueBibite", "Tic",
    "Minute", "TimeAlive", "PheroSense1", "PheroSense2", "PheroSense3",
    "Phero1Angle", "Phero2Angle", "Phero3Angle", "Phero1Heading",
    "Phero2Heading", "Phero3Heading",
]
OUTPUTS = [
    "Accelerate", "Rotate", "Herding", "EggProduction", "Want2Lay", "Want2Eat",
    "Digestion", "Grab", "ClkReset", "PhereOut1", "PhereOut2", "PhereOut3",
    "Want2Grow", "Want2Heal", "Want2Attack",
]


class Template:
    def __init__(self, data):
        self.data = data

    @classmethod
    def load(cls, path):
        return cls(json.loads(Path(path).read_text(encoding="utf-8-sig")))

    def save(self, path):
        # The game writes 2-space indented JSON with CRLF line endings.
        text = json.dumps(self.data, indent=2, ensure_ascii=False)
        Path(path).write_bytes(text.replace("\n", "\r\n").encode("utf-8"))

    @property
    def nodes(self):
        return self.data["nodes"]

    @property
    def synapses(self):
        return self.data["synapses"]

    def node(self, desc):
        matches = [n for n in self.nodes if n["Desc"] == desc]
        if len(matches) != 1:
            raise KeyError(f"expected one node named {desc!r}, found {len(matches)}")
        return matches[0]

    def add_node(self, desc, type_, bias=0.0, anchor=None):
        node = {
            "Type": type_,
            "Index": len(self.nodes),
            "Inov": max(n["Inov"] for n in self.nodes) + 1,
            "Desc": desc,
            "baseActivation": bias,
        }
        self.nodes.append(node)
        if anchor is not None:
            x, y = anchor
            self.data.setdefault("nodeAnchors", {})[str(node["Inov"])] = {"x": x, "y": y}
        return node

    def connect(self, src, dst, weight, enabled=True):
        """Add a synapse; src/dst are node dicts or Desc names."""
        src = self.node(src) if isinstance(src, str) else src
        dst = self.node(dst) if isinstance(dst, str) else dst
        syn = {
            "Inov": max((s["Inov"] for s in self.synapses), default=0) + 1,
            "NodeIn": src["Index"],
            "NodeOut": dst["Index"],
            "Weight": weight,
            "En": enabled,
        }
        self.synapses.append(syn)
        return syn

    def add_missing_inputs(self):
        """Insert any absent input nodes at their standard positions.

        Rebuilds the node list as inputs, outputs, then hidden nodes, and
        renumbers Index/Inov (remapping synapses and anchors) to match.

        Files labelled version "0.6" predate RotationSpeed, and the game
        inserts it at Index 5 on load, shifting every later node. So once it's
        present we must relabel the file 0.6.2 or the game inserts it twice.
        """
        by_desc = {n["Desc"]: n for n in self.nodes}
        if "RotationSpeed" not in by_desc:
            self.data["version"] = "0.6.2"
        missing_outputs = [d for d in OUTPUTS if d not in by_desc]
        if missing_outputs:
            raise ValueError(f"template lacks outputs {missing_outputs}")
        inputs = [by_desc.get(d) or {"Type": INPUT, "Index": None, "Inov": None,
                                     "Desc": d, "baseActivation": 0.0}
                  for d in INPUTS]
        hidden = [n for n in self.nodes if n["Desc"] not in INPUTS + OUTPUTS]
        ordered = inputs + [by_desc[d] for d in OUTPUTS] + hidden

        old_index = {n["Index"]: i for i, n in enumerate(ordered) if n["Index"] is not None}
        old_anchors = self.data.get("nodeAnchors", {})
        anchors = {}
        for i, n in enumerate(ordered):
            if str(n["Inov"]) in old_anchors:
                anchors[str(i + 1)] = old_anchors[str(n["Inov"])]
            n["Index"], n["Inov"] = i, i + 1
        for s in self.synapses:
            s["NodeIn"], s["NodeOut"] = old_index[s["NodeIn"]], old_index[s["NodeOut"]]
        self.data["nodes"] = ordered
        if anchors:
            self.data["nodeAnchors"] = anchors

    def copy_anchors_from(self, other):
        """Give every node that shares a Desc with `other` the same layout spot."""
        theirs = {n["Desc"]: other.data["nodeAnchors"][str(n["Inov"])]
                  for n in other.nodes if str(n["Inov"]) in other.data.get("nodeAnchors", {})}
        anchors = self.data.setdefault("nodeAnchors", {})
        for n in self.nodes:
            if n["Desc"] in theirs:
                anchors[str(n["Inov"])] = dict(theirs[n["Desc"]])

    def rename(self, name, description):
        self.data["name"] = name
        self.data["speciesName"] = name
        self.data["description"] = description
        self.data.pop("isOfficial", None)
