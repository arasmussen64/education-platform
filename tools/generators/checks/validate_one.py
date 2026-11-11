"""Run tools/validate_content.py's checks for a few topics only (by id), so a
new topic can be checked in seconds instead of the full run. Every topic and
track is still loaded, so prerequisites, tracks and skills are checked across
the whole content tree; only the per-topic work (running code) is limited.

Run from the repository root: python -m uv run python <this file> <topic id>...
"""

import pathlib
import sys

ROOT = pathlib.Path.cwd()
sys.path.insert(0, str(ROOT / "tools"))

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
        folder = topics[topic_id]
        place = places.get(topic_id)
        vc.check_references(folder, report)
        vc.check_packages(folder, report)
        vc.check_test_skills(folder, topics, place, report)
        if folder.topic.status == "ready":
            vc.check_ready_topic(folder, report)
            if folder.topic.kind == "checkpoint":
                vc.check_ready_checkpoint(folder, topics, place, report)
        for item_path_id, item in folder.recall.items():
            report.counts["recall items"] += 1
            item_path = folder.path / "recall" / f"{item_path_id}.yaml"
            if isinstance(item, vc.PredictOutputItem):
                vc.check_predict_output(item_path, item, report)
            elif isinstance(item, vc.ParsonsItem):
                vc.check_parsons(item_path, item, report)
            elif isinstance(item, vc.PredictShellItem):
                vc.check_predict_shell(item_path, item, report)
        for exercise_folder, exercise in folder.exercises.values():
            report.counts["exercises"] += 1
            vc.check_exercise(exercise_folder, exercise, report, True, False)

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


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
