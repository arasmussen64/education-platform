"""Run tools/validate_content.py's checks for a few topics only (by id), so a
new topic can be checked in seconds instead of the full run. Every topic and
track is still loaded, so prerequisites, tracks and skills are checked across
the whole content tree; only the per-topic work (running code) is limited.

The per-topic checks are the full validator's own (validate_content.check_topic),
so the two can't drift apart. Two things stay with the full run only: the
placement test's questions, and the answer-length list's entries for other
topics. Labs are checked but not run in Docker (tools/labcheck.py test does
that, and CI runs every lab).

Run from the repository root: python -m uv run python <this file> <topic id>...
"""

import pathlib
import sys

ROOT = pathlib.Path.cwd()
sys.path.insert(0, str(ROOT / "tools"))

import mcq_lengths  # noqa: E402
import validate_content as vc  # noqa: E402


def main(ids: list[str]) -> int:
    report = vc.Report(vc.ROOT)
    content = vc.ROOT / "content"

    tracks = {}
    for path in sorted((content / "tracks").glob("*.yaml")):
        track = vc.load(path, vc.Track, report)
        if track is not None:
            tracks[path] = track

    topics = {}
    for folder in sorted(p for p in (content / "topics").glob("*") if p.is_dir()):
        loaded = vc.load_topic_folder(folder, report)
        if loaded is None:
            continue
        topics[loaded.topic.id] = loaded

    vc.check_tracks(tracks, topics, report)
    vc.check_prerequisites(topics, report)
    places = vc.checkpoint_places(tracks)

    for topic_id in ids:
        if topic_id not in topics:
            report.problems.append(f"{topic_id}: no such topic (or it failed to load)")
            continue
        vc.check_topic(
            topics[topic_id],
            topics,
            places.get(topic_id),
            report,
            run=True,
            labs=False,
        )
    report_long_answers(report)

    c = report.counts
    print(
        f"Checked {', '.join(ids)}: {c['exercises']} exercises, "
        f"{c['recall items']} recall items; ran {c['runs']} programs."
    )
    if report.problems:
        print(f"\n{len(report.problems)} problem(s):")
        for problem in report.problems:
            print(f"  - {problem}")
        return 1
    print("No problems found.")
    return 0


def report_long_answers(report: vc.Report) -> None:
    """The named topics' answer-length problems. The full validator also
    reports list entries that are fixed or misplaced; those are about other
    topics here, so they're left to it."""
    baseline_file = report.root / mcq_lengths.BASELINE
    try:
        baseline = mcq_lengths.read_baseline(baseline_file)
    except mcq_lengths.BadBaseline as exc:
        report.add(baseline_file, str(exc))
        return
    found = report.long_answers
    for path, message in mcq_lengths.problems(found, baseline, baseline_file):
        if path != baseline_file:
            report.add(path, message)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
