"""Labs' Dockerfiles never COPY two different files of the same size onto
one path.

A lab that copies a working file into its image and later a broken one over
it can lose the broken one: on a fresh checkout both files have the same
time, and when they are also the same size, Docker's layer differ can take
the second copy for no change. csa.linux.net-tools' debug-not-from-the-office
then started on GitHub's runner with its fault already mended, so two of its
known-wrong fixes passed (#263). Copy only the file the lab needs, or make the
two differ in size.
"""

from pathlib import Path

TOPICS = Path(__file__).resolve().parents[2] / "content" / "topics"


def copies_onto(dockerfile: Path) -> dict[str, list[Path]]:
    """For each path the Dockerfile's COPY lines write, the files copied there."""
    written: dict[str, list[Path]] = {}
    for line in dockerfile.read_text(encoding="utf-8").splitlines():
        words = line.split()
        if not words or words[0] != "COPY":
            continue
        if any(word.startswith("--from") for word in words):
            continue
        parts = [word for word in words[1:] if not word.startswith("--")]
        if len(parts) < 2:
            continue
        *sources, dest = parts
        for source in sources:
            target = dest + Path(source).name if dest.endswith("/") else dest
            written.setdefault(target, []).append(dockerfile.parent / source)
    return written


def same_size_overwrites(dockerfile: Path) -> list[str]:
    found = []
    for target, sources in copies_onto(dockerfile).items():
        files = [source for source in sources if source.is_file()]
        contents = {file.read_bytes() for file in files}
        sizes = [file.stat().st_size for file in files]
        if len(contents) > 1 and len(set(sizes)) < len(sizes):
            found.append(f"{target} <- {', '.join(file.name for file in files)}")
    return found


def test_no_lab_copies_two_same_size_files_onto_one_path() -> None:
    problems = []
    for dockerfile in sorted(TOPICS.glob("*/exercises/*/Dockerfile")):
        for problem in same_size_overwrites(dockerfile):
            problems.append(f"{dockerfile.parent.relative_to(TOPICS)}: {problem}")
    assert not problems, "\n".join(problems)


def test_it_finds_a_same_size_overwrite(tmp_path) -> None:
    (tmp_path / "good.conf").write_text("address=10.0.9.1\n", encoding="utf-8")
    (tmp_path / "stale.conf").write_text("address=10.0.9.5\n", encoding="utf-8")
    (tmp_path / "longer.conf").write_text("address=10.0.9.50\n", encoding="utf-8")
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text(
        "FROM ubuntu:24.04\n"
        "COPY good.conf /etc/app.conf\n"
        "COPY stale.conf /etc/app.conf\n"
        "COPY good.conf /etc/other/\n"
        "COPY longer.conf /etc/other/good.conf\n",
        encoding="utf-8",
    )
    assert same_size_overwrites(dockerfile) == [
        "/etc/app.conf <- good.conf, stale.conf"
    ]
