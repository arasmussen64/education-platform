"""The outline generator reads the spec's shape and writes content the
validator accepts, without touching topics that are being written."""

from pathlib import Path

from content_fixture import write
from outline_cloud_track import (
    MARKER,
    link_prerequisites,
    parse_spec,
    read_capstone_titles,
    write_outlines,
)
from validate_content import validate

# A spec in miniature, in the same shape as the real one.
SPEC = """# A track

## Stage 1

### Module 1: Linux

Some words about the module.

| # | Topic | ID | You'll be able to… |
|---|---|---|---|
| 1 | Shell essentials | `csa.linux.shell` | find files with `grep`; read logs |
| 2 | Services and logs | `csa.linux.services` | run services with systemd |

**Checkpoint 1: the server** (`csa.m1.checkpoint`). A container with two faults:
- a full disk;
- a blocked port.

Restore service within 45 minutes.

### Module 2: Specialist depth

| Specialty | ID | Goes deep on | Checkpoint |
|---|---|---|---|
| Networking | `csa.deep.networking` | BGP, cloud WANs | Redesign a global network |

**Checkpoint 2: your specialty** (`csa.m2.checkpoint`). Whichever you chose.

### Capstone 1: one product

`csa.capstone-1`, about 35 hours. Build a product on all three clouds. It has:
- an API;
- a database.

## Afterwards

Nothing here is part of a module.
"""

PREREQUISITES = {"m1": [], "m2": ["m1"], "c1": ["m2"]}
CAPSTONE_AFTER = {"m2": "c1"}


def parsed():
    read_capstone_titles(SPEC)
    track = parse_spec(SPEC)
    link_prerequisites(track, PREREQUISITES)
    return track


def test_reads_modules_topics_checkpoints_and_capstones() -> None:
    track = parsed()
    assert [module.title for module in track.modules] == ["Linux", "Specialist depth"]

    shell = track.modules[0].topics[0]
    assert shell.id == "csa.linux.shell"
    assert shell.title == "Shell essentials"
    assert shell.objectives == ["Find files with grep.", "Read logs."]
    assert shell.summary == "Find files with grep."

    checkpoint = track.modules[0].checkpoint
    assert checkpoint is not None
    assert checkpoint.title == "Checkpoint 1: the server"
    assert checkpoint.summary == "A container with two faults."
    assert checkpoint.objectives == [
        "A container with two faults.",
        "A full disk.",
        "A blocked port.",
        "Restore service within 45 minutes.",
    ]

    specialty = track.modules[1].topics[0]
    assert specialty.title == "Specialty: Networking"
    assert specialty.summary == "Go deep on BGP, cloud WANs."

    capstone = track.capstones["c1"]
    assert capstone.title == "Capstone 1: one product"
    assert capstone.minutes == 35 * 60
    assert capstone.summary == "Build a product on all three clouds."
    assert capstone.objectives == [
        "Build a product on all three clouds.",
        "An API.",
        "A database.",
    ]


def test_prerequisites_follow_the_module_map() -> None:
    track = parsed()
    checkpoint = track.modules[0].checkpoint
    assert checkpoint is not None
    assert track.modules[0].topics[0].prerequisites == []
    assert checkpoint.prerequisites == ["csa.linux.shell", "csa.linux.services"]
    assert track.modules[1].topics[0].prerequisites == ["csa.m1.checkpoint"]
    assert track.capstones["c1"].prerequisites == ["csa.m2.checkpoint"]


def test_writes_content_the_validator_accepts(tmp_path: Path) -> None:
    content = tmp_path / "content"
    counts = write_outlines(parsed(), content, CAPSTONE_AFTER)
    assert counts == {"written": 6, "kept": 0}

    track_text = (content / "tracks" / "cloud-solutions-architect.yaml").read_text()
    assert track_text.startswith(MARKER)
    assert "capstone: csa.capstone-1" in track_text

    report = validate(tmp_path, run=False)
    assert report.problems == []
    assert report.counts["planned"] == 6


def test_leaves_topics_that_are_being_written_alone(tmp_path: Path) -> None:
    content = tmp_path / "content"
    write_outlines(parsed(), content, CAPSTONE_AFTER)
    shell = content / "topics" / "csa.linux.shell" / "topic.yaml"
    started = shell.read_text().replace("status: planned", "status: draft")
    write(tmp_path, "content/topics/csa.linux.shell/topic.yaml", started)

    counts = write_outlines(parsed(), content, CAPSTONE_AFTER)
    assert counts == {"written": 5, "kept": 1}
    assert shell.read_text() == started
