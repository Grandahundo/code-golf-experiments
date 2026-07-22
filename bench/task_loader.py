"""Load task JSON + gen.py, build TaskBundle."""

import json
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Example:
    input: list
    output: list


@dataclass
class TaskBundle:
    task_id: str
    train: list[Example]
    hidden: list[Example]          # test + arc-gen merged
    gen_source: str = ""           # gen.py full text, empty if missing
    has_gen: bool = False

    @property
    def hidden_count(self) -> int:
        return len(self.hidden)

    @property
    def train_count(self) -> int:
        return len(self.train)


def _parse_examples(raw: list) -> list[Example]:
    """Convert raw JSON dicts to Example objects."""
    out = []
    for ex in raw:
        inp = ex.get("input")
        outp = ex.get("output")
        if inp is not None and outp is not None:
            out.append(Example(input=inp, output=outp))
    return out


def load_task(task_path: str, gen_dir: str, gen_max_chars: int = 8000) -> TaskBundle:
    """Load a single task from its JSON file, plus optional gen.py.

    Args:
        task_path: path to taskNNN.json
        gen_dir: path to deepseek-v4-pro-baseline/ (contains taskNNN/gen.py)
        gen_max_chars: max characters of gen.py to load

    Returns:
        TaskBundle with train, hidden (test+arc-gen), and gen_source.
    """
    with open(task_path) as f:
        data = json.load(f)

    # task_id from filename: "task001.json" -> "task001"
    fname = os.path.basename(task_path)
    task_id = fname.replace(".json", "")

    train = _parse_examples(data.get("train", []))
    test = _parse_examples(data.get("test", []))
    arc_gen = _parse_examples(data.get("arc-gen", []))

    # hidden = test + arc-gen (test first)
    hidden = test + arc_gen

    # gen.py
    gen_source = ""
    has_gen = False
    gen_path = os.path.join(gen_dir, task_id, "gen.py")
    if os.path.exists(gen_path):
        has_gen = True
        with open(gen_path) as f:
            gen_source = f.read()
        if len(gen_source) > gen_max_chars:
            gen_source = gen_source[:gen_max_chars] + (
                f"\n\n# ... (truncated, full length: {len(gen_source)} chars)"
            )

    return TaskBundle(
        task_id=task_id,
        train=train,
        hidden=hidden,
        gen_source=gen_source,
        has_gen=has_gen,
    )


def grid_area(ex: Example) -> int:
    """Return rows * cols for the input grid."""
    inp = ex.input
    if isinstance(inp, list) and len(inp) > 0 and isinstance(inp[0], list):
        return len(inp) * len(inp[0])
    return 0


def grid_to_display(grid) -> str:
    """Convert a grid (list of list of ints) to compact display string.

    Since all values are 0-9, each row's digits are concatenated directly.
    """
    if not grid or not isinstance(grid, list):
        return str(grid)
    lines = []
    for row in grid:
        if isinstance(row, list):
            lines.append("".join(str(c) for c in row))
        else:
            lines.append(str(row))
    return "\n".join(lines)


def select_train_examples(
    bundle: TaskBundle, max_count: int = 3, max_chars: int = 1500
) -> list[Example]:
    """Select up to max_count train examples for display.

    Picks smallest, median, and largest by grid area.
    Skips examples whose display text exceeds max_chars.
    """
    if not bundle.train:
        return []

    # Sort by area
    indexed = [(grid_area(ex), i, ex) for i, ex in enumerate(bundle.train)]
    indexed.sort(key=lambda x: x[0])

    n = len(indexed)
    # Pick indices: smallest (0), median (n//2), largest (n-1)
    picks = {0, n // 2, n - 1}
    selected = []
    for area, i, ex in indexed:
        if i in picks:
            display = grid_to_display(ex.input)
            if len(display) <= max_chars:
                selected.append(ex)
        if len(selected) >= max_count:
            break

    return selected
