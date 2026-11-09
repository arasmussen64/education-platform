"""Turns the Cloud Solutions Architect spec into planned outlines in content/.

The spec (docs/specs/cloud-solutions-architect.md) lists every module, topic,
checkpoint and capstone in a fixed shape. This script reads it and writes:

- content/tracks/cloud-solutions-architect.yaml, the track;
- content/topics/<id>/topic.yaml for every topic, checkpoint and capstone,
  as a `planned` outline, so the track shows on the map.

It never touches a topic that someone has started writing: a topic.yaml is
replaced only if it's still a generated outline (it carries the marker below
and is `planned`). So the spec can change and the outlines follow, until a
topic becomes real content and takes over as the source of truth.

Run it from the repository root:

    python -m uv run python tools/outline_cloud_track.py
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs" / "specs" / "cloud-solutions-architect.md"
CONTENT = ROOT / "content"

TRACK_ID = "cloud-solutions-architect"
TRACK_TITLE = "Cloud Solutions Architect"
TRACK_SUMMARY = (
    "From Linux and networking to principal-level architecture on AWS, Azure "
    "and Google Cloud, proven by building in your own cloud accounts."
)
TRACK_ORDER = 2

MARKER = (
    "# An outline generated from docs/specs/cloud-solutions-architect.md by\n"
    "# tools/outline_cloud_track.py. Until this topic is written, change the\n"
    "# spec and run the script again instead of editing this file.\n"
)

# Rough sizes for outlines. They're refined when a topic is written.
TOPIC_MINUTES = 240
CHECKPOINT_MINUTES = 480

# Which modules each module builds on, mirroring the module map in the spec.
# "py" is Python Foundations; "c1".."c3" are the capstones. A topic's
# prerequisites are the checkpoints of its module's prerequisites, so a
# module opens once the modules before it are passed.
MODULE_PREREQUISITES: dict[str, list[str]] = {
    "m1": [],
    "m2": ["m1"],
    "m3": ["m1"],
    "m4": ["m3"],
    "m5": ["m3"],
    "m6": ["m1", "py"],
    "m7": ["m6"],
    "m8": ["m4"],
    "m9": ["m8", "m6"],
    "m10": ["m9"],
    "m11": ["m10"],
    "m12": ["m11", "m2"],
    "m13": ["m11", "m5"],
    "m14": ["m12", "m13", "m7"],
    "m15": ["m12"],
    "c1": ["m14", "m15"],
    "m16": ["c1"],
    "m17": ["m16"],
    "m18": ["m16"],
    "m19": ["m18"],
    "m20": ["m16"],
    "m21": ["m18", "m20"],
    "m22": ["m16"],
    "m23": ["m16"],
    "m24": ["m17", "m21"],
    "c2": ["m19", "m22", "m23", "m24"],
    "m25": ["c2"],
    "m26": ["c2"],
    "m27": ["m26"],
    "m28": ["m25"],
    "m29": ["c2"],
    "m30": ["c2"],
    "c3": ["m27", "m28", "m29", "m30"],
}

# The capstone that follows each module, where there is one.
CAPSTONE_AFTER = {"m15": "c1", "m24": "c2", "m30": "c3"}

PYTHON_CHECKPOINT = "py.m6.checkpoint"


@dataclass
class Outline:
    """One topic, checkpoint or capstone, as the spec describes it."""

    id: str
    kind: str  # topic | checkpoint
    title: str
    summary: str
    objectives: list[str]
    minutes: int
    prerequisites: list[str] = field(default_factory=list)


@dataclass
class ModuleOutline:
    key: str  # m1, m2, …
    title: str
    topics: list[Outline] = field(default_factory=list)
    checkpoint: Outline | None = None


@dataclass
class TrackOutline:
    modules: list[ModuleOutline] = field(default_factory=list)
    capstones: dict[str, Outline] = field(default_factory=dict)  # c1 → outline


MODULE_HEADING = re.compile(r"^### Module (\d+): (.+)$")
CAPSTONE_HEADING = re.compile(r"^### Capstone (\d+): (.+)$")
OTHER_HEADING = re.compile(r"^##+ ")
# | 12 | Shell scripting | `csa.linux.scripting` | write Bash scripts ... |
TOPIC_ROW = re.compile(
    r"^\| \d+ \| (?P<title>[^|]+?) \| `(?P<id>csa\.[a-z0-9.-]+)` \| (?P<text>.+?) \|$"
)
# | Networking | `csa.deep.networking` | BGP traffic engineering, ... | Redesign ... |
SPECIALTY_ROW = re.compile(
    r"^\| (?P<title>[^|`]+?) \| `(?P<id>csa\.deep\.[a-z0-9-]+)` \| "
    r"(?P<deep>[^|]+?) \| (?P<checkpoint>[^|]+?) \|$"
)
# **Checkpoint 3: the address plan and the outage** (`csa.m3.checkpoint`). Text…
CHECKPOINT_LINE = re.compile(
    r"^\*\*Checkpoint (?P<number>\d+): (?P<title>.+?)\*\* "
    r"\(`(?P<id>csa\.m\d+\.checkpoint)`\)(?P<rest>.*)$"
)
# `csa.capstone-1`, about 35 hours. Text…
CAPSTONE_LINE = re.compile(
    r"^`(?P<id>csa\.capstone-\d+)`, about (?P<hours>\d+) hours\.(?P<rest>.*)$"
)
LIST_MARKER = re.compile(r"^(?:\d+\.|-)\s+")


def sentence(text: str) -> str:
    """The first sentence of a piece of text, ending in a full stop."""
    text = text.strip().rstrip(":;,")
    match = re.match(r"(.+?[.!?])(?:\s|$)", text)
    first = match.group(1) if match else text
    return first if first.endswith((".", "!", "?")) else f"{first}."


def capitalize(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def strip_markdown(text: str) -> str:
    """Drops bold, code marks, links and list markers; keeps the words."""
    text = LIST_MARKER.sub("", text.strip())
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = text.replace("**", "").replace("`", "").replace("*", "")
    # What follows a checkpoint's name may start with ", a game day." or ".".
    return text.strip().lstrip(" ,.;:")


def description_items(lines: list[str]) -> list[str]:
    """A checkpoint's or capstone's description, one item per line of it."""
    items: list[str] = []
    for line in lines:
        text = strip_markdown(line)
        if not text:
            continue
        if text.endswith(":") and ". " in text:
            # "Build it from one repository. It has:" introduces a list; keep
            # the whole sentences and drop the lead-in.
            text = text[: text.rindex(". ") + 1]
        text = text.rstrip(";").rstrip(":")
        if not text.endswith((".", "!", "?")):
            text += "."
        items.append(capitalize(text))
    return items


def topic_outline(title: str, topic_id: str, text: str) -> Outline:
    """A topic from its table row. Its objectives are the row's clauses."""
    clauses = [capitalize(strip_markdown(part)) for part in text.split("; ")]
    objectives = [c if c.endswith(".") else f"{c}." for c in clauses if c]
    return Outline(
        id=topic_id,
        kind="topic",
        title=title.strip(),
        summary=objectives[0],
        objectives=objectives,
        minutes=TOPIC_MINUTES,
    )


def specialty_outline(title: str, topic_id: str, deep: str, checkpoint: str) -> Outline:
    deep_text = strip_markdown(deep)
    return Outline(
        id=topic_id,
        kind="topic",
        title=f"Specialty: {title.strip()}",
        summary=f"Go deep on {deep_text}.",
        objectives=[
            f"Go deep on {deep_text}.",
            f"Its checkpoint: {strip_markdown(checkpoint).rstrip('.')}.",
        ],
        minutes=TOPIC_MINUTES * 6,
    )


def parse_spec(text: str) -> TrackOutline:
    """Reads the spec's module tables, checkpoint paragraphs and capstones."""
    track = TrackOutline()
    module: ModuleOutline | None = None
    # A checkpoint or capstone being read: its outline and description lines.
    reading: tuple[Outline, list[str]] | None = None

    def finish_reading() -> None:
        nonlocal reading
        if reading is None:
            return
        outline, lines = reading
        items = description_items(lines)
        if outline.summary == "" and items:
            outline.summary = sentence(items[0])
        outline.objectives = items or [outline.summary]
        reading = None

    for raw in text.splitlines():
        line = raw.rstrip()
        if OTHER_HEADING.match(line):
            finish_reading()
            if match := MODULE_HEADING.match(line):
                module = ModuleOutline(
                    key=f"m{match.group(1)}", title=match.group(2).strip()
                )
                track.modules.append(module)
            else:
                module = None
            continue

        if match := CHECKPOINT_LINE.match(line):
            finish_reading()
            if module is None:
                raise ValueError(f"a checkpoint outside any module: {line[:60]}")
            rest = strip_markdown(match["rest"])
            outline = Outline(
                id=match["id"],
                kind="checkpoint",
                title=f"Checkpoint {match['number']}: {match['title']}",
                summary=sentence(capitalize(rest)) if rest else "",
                objectives=[],
                minutes=CHECKPOINT_MINUTES,
            )
            module.checkpoint = outline
            reading = (outline, [rest] if rest else [])
            continue

        if match := CAPSTONE_LINE.match(line):
            finish_reading()
            rest = strip_markdown(match["rest"])
            number = match["id"].rsplit("-", 1)[1]
            outline = Outline(
                id=match["id"],
                kind="checkpoint",
                title=f"Capstone {number}: {capstone_titles.get(number, '')}".rstrip(
                    ": "
                ),
                summary=sentence(capitalize(rest)) if rest else "",
                objectives=[],
                minutes=int(match["hours"]) * 60,
            )
            track.capstones[f"c{number}"] = outline
            reading = (outline, [rest] if rest else [])
            continue

        if reading is not None:
            reading[1].append(line)
            continue

        if module is not None:
            if match := TOPIC_ROW.match(line):
                module.topics.append(
                    topic_outline(match["title"], match["id"], match["text"])
                )
            elif match := SPECIALTY_ROW.match(line):
                module.topics.append(
                    specialty_outline(
                        match["title"], match["id"], match["deep"], match["checkpoint"]
                    )
                )

    finish_reading()
    return track


# Capstone titles come from their headings, read in a first pass.
capstone_titles: dict[str, str] = {}


def read_capstone_titles(text: str) -> None:
    for line in text.splitlines():
        if match := CAPSTONE_HEADING.match(line):
            capstone_titles[match.group(1)] = match.group(2).strip()


def link_prerequisites(
    track: TrackOutline, module_prerequisites: dict[str, list[str]]
) -> None:
    """Fills in prerequisites from the module map."""
    checkpoint_ids = {
        module.key: module.checkpoint.id
        for module in track.modules
        if module.checkpoint
    }
    checkpoint_ids.update({key: outline.id for key, outline in track.capstones.items()})
    checkpoint_ids["py"] = PYTHON_CHECKPOINT

    def gates(key: str) -> list[str]:
        return [checkpoint_ids[before] for before in module_prerequisites.get(key, [])]

    for module in track.modules:
        for topic in module.topics:
            topic.prerequisites = gates(module.key)
        if module.checkpoint:
            module.checkpoint.prerequisites = [topic.id for topic in module.topics]
    for key, capstone in track.capstones.items():
        capstone.prerequisites = gates(key)


def topic_yaml(outline: Outline) -> str:
    data = {
        "id": outline.id,
        "kind": outline.kind,
        "status": "planned",
        "title": outline.title,
        "summary": outline.summary,
        "prerequisites": outline.prerequisites,
        "estimated_minutes": outline.minutes,
        "rev": 1,
        "objectives": outline.objectives,
    }
    return MARKER + dump(data)


def track_yaml(track: TrackOutline, capstone_after: dict[str, str]) -> str:
    modules = []
    for module in track.modules:
        if module.checkpoint is None:
            raise ValueError(f"module {module.key} has no checkpoint")
        entry: dict[str, object] = {
            "id": f"csa.{module.key}",
            "title": module.title,
            "topics": [topic.id for topic in module.topics],
            "checkpoint": module.checkpoint.id,
        }
        if capstone := capstone_after.get(module.key):
            entry["capstone"] = track.capstones[capstone].id
        modules.append(entry)
    data = {
        "id": TRACK_ID,
        "title": TRACK_TITLE,
        "summary": TRACK_SUMMARY,
        "order": TRACK_ORDER,
        "modules": modules,
    }
    return MARKER + dump(data)


def dump(data: dict[str, object]) -> str:
    return yaml.safe_dump(
        data,
        sort_keys=False,
        allow_unicode=True,
        width=10_000,
        default_flow_style=False,
    )


def is_generated_outline(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    return text.startswith(MARKER) and "\nstatus: planned\n" in text


def write_outlines(
    track: TrackOutline, content: Path, capstone_after: dict[str, str]
) -> dict[str, int]:
    """Writes the track and every outline. Returns how many were written and
    how many were left alone because someone has started writing them."""
    counts = {"written": 0, "kept": 0}
    outlines = [
        *(topic for module in track.modules for topic in module.topics),
        *(module.checkpoint for module in track.modules if module.checkpoint),
        *track.capstones.values(),
    ]
    for outline in outlines:
        path = content / "topics" / outline.id / "topic.yaml"
        if path.exists() and not is_generated_outline(path):
            counts["kept"] += 1
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(topic_yaml(outline), encoding="utf-8", newline="\n")
        counts["written"] += 1
    track_path = content / "tracks" / f"{TRACK_ID}.yaml"
    track_path.parent.mkdir(parents=True, exist_ok=True)
    track_path.write_text(
        track_yaml(track, capstone_after), encoding="utf-8", newline="\n"
    )
    return counts


def outline(spec: Path = SPEC, content: Path = CONTENT) -> dict[str, int]:
    text = spec.read_text(encoding="utf-8")
    read_capstone_titles(text)
    track = parse_spec(text)
    link_prerequisites(track, MODULE_PREREQUISITES)
    return write_outlines(track, content, CAPSTONE_AFTER)


def main() -> int:
    counts = outline()
    print(
        f"Wrote {counts['written']} outlines; kept {counts['kept']} topics that are "
        f"being written. Now run tools/validate_content.py."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
