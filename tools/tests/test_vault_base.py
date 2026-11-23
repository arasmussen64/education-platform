"""The vault lab base (content/lab-bases/vault): image-search, the helper
behind the checks' image_has, against saved images built here by hand, and
two facts about the base's Dockerfile.

image-search decides whether a secret is still inside a container image, so
a place it doesn't look is a leak a check would pass. The archives below
have the two layouts `podman save` can write (docker-archive, its default,
and oci-archive), with a value planted in each place a build can leave one:
a file in a layer, a file a later layer deleted, a file's name, a build
step's command in the history, and the image's settings.
"""

import hashlib
import importlib.machinery
import importlib.util
import io
import json
import re
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BASES = ROOT / "content" / "lab-bases"
VAULT = BASES / "vault"


def load():
    path = str(VAULT / "image-search")
    loader = importlib.machinery.SourceFileLoader("image_search", path)
    spec = importlib.util.spec_from_loader("image_search", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


image_search = load()


def tar_of(files: dict[str, bytes], compress: bool = False) -> bytes:
    """A tar archive of the files, in the order given."""
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz" if compress else "w") as archive:
        for name, content in files.items():
            info = tarfile.TarInfo(name)
            info.size = len(content)
            archive.addfile(info, io.BytesIO(content))
    return buffer.getvalue()


# Three layers, oldest first: the base image, a step that copies a token
# in, and a step that deletes it (a deletion is an empty ".wh." file).
LAYERS = [
    {"bin/sh": b"#!/bin/true\n"},
    {"tmp/deploy.token": b"tok_deploy_12345\n", "opt/lib.txt": b"shop-lib 2.4.1\n"},
    {"tmp/.wh.deploy.token": b""},
]
CONFIG = {
    "architecture": "amd64",
    "config": {"Env": ["PATH=/bin", "REGION=eu-west-9"], "Cmd": ["/bin/sh"]},
    "history": [
        {"created_by": "/bin/sh -c #(nop) ADD file:abc in /"},
        {"created_by": "/bin/sh -c #(nop) COPY file:def in /tmp/deploy.token"},
        {"created_by": "|1 API_KEY=key_example_1234 /bin/sh -c rm /tmp/deploy.token"},
    ],
}


def docker_archive() -> bytes:
    """What `podman save` writes by default: the layers under their own
    names, the settings, and manifest.json, which gives the layers' order."""
    config = json.dumps(CONFIG).encode()
    # Named so that name order is the wrong order: only manifest.json says
    # which layer is the oldest.
    names = ["c.tar", "a.tar", "b.tar"]
    files = {name: tar_of(layer) for name, layer in zip(names, LAYERS, strict=True)}
    files["config.json"] = config
    files["manifest.json"] = json.dumps(
        [{"Config": "config.json", "RepoTags": ["localhost/shop:1"], "Layers": names}]
    ).encode()
    return tar_of(files)


def oci_archive() -> bytes:
    """What `podman save --format oci-archive` writes: every piece is a
    blob named by its checksum, layers compressed, found through index.json."""

    def blob(data: bytes) -> tuple[str, str]:
        digest = hashlib.sha256(data).hexdigest()
        return f"blobs/sha256/{digest}", f"sha256:{digest}"

    files: dict[str, bytes] = {}
    layers = []
    for layer in LAYERS:
        data = tar_of(layer, compress=True)
        name, digest = blob(data)
        files[name] = data
        layers.append({"digest": digest})
    config = json.dumps(CONFIG).encode()
    config_name, config_digest = blob(config)
    files[config_name] = config
    manifest = json.dumps({"config": {"digest": config_digest}, "layers": layers})
    manifest_name, manifest_digest = blob(manifest.encode())
    files[manifest_name] = manifest.encode()
    files["index.json"] = json.dumps(
        {"manifests": [{"digest": manifest_digest}]}
    ).encode()
    return tar_of(files)


ARCHIVES = {"docker-archive": docker_archive, "oci-archive": oci_archive}

CASES = [
    # A file deleted by a later step is still in the layer that added it.
    ("tok_deploy_12345", ["layer 2: tmp/deploy.token"]),
    ("shop-lib 2.4.1", ["layer 2: opt/lib.txt"]),
    # A build argument is in the command of every step after its ARG line.
    ("key_example_1234", ["history: step 3"]),
    ("REGION=eu-west-9", ["config"]),
    # A value in a file's name, and so also in the name of its deletion,
    # and in the history line that names the file.
    (
        "deploy.token",
        [
            "layer 2: name of tmp/deploy.token",
            "layer 3: name of tmp/.wh.deploy.token",
            "history: step 2",
            "history: step 3",
        ],
    ),
    ("nowhere-in-this-image", []),
]


@pytest.mark.parametrize("layout", ARCHIVES)
@pytest.mark.parametrize(("value", "expected"), CASES)
def test_it_finds_a_value_wherever_a_build_can_leave_it(layout, value, expected):
    assert image_search.search(ARCHIVES[layout](), value) == expected


def test_a_value_with_a_quote_is_found_in_the_history():
    # In the settings file the quote is written \", so the value has to be
    # looked for in the text the JSON stands for, not in the file's bytes.
    config = dict(CONFIG)
    config["history"] = [{"created_by": '/bin/sh -c echo pass=a"b'}]
    archive = tar_of(
        {
            "config.json": json.dumps(config).encode(),
            "manifest.json": json.dumps([{"Layers": []}]).encode(),
        }
    )
    assert image_search.search(archive, 'pass=a"b') == ["history: step 1"]


def test_a_layer_no_manifest_names_is_still_searched():
    archive = tar_of({"stray.tar": tar_of({"etc/key": b"tok_deploy_12345"})})
    assert image_search.search(archive, "tok_deploy_12345") == ["layer 1: etc/key"]


def test_a_file_that_is_no_image_is_refused(tmp_path, capsys):
    not_an_image = tmp_path / "notes.txt"
    not_an_image.write_bytes(b"tok_deploy_12345, written down\n")
    assert image_search.main(["image-search", str(not_an_image), "tok"]) == 2
    assert "can't read" in capsys.readouterr().err


def test_the_command_exits_0_when_found_and_1_when_not(tmp_path, capsys):
    saved = tmp_path / "image.tar"
    saved.write_bytes(docker_archive())
    assert image_search.main(["image-search", str(saved), "tok_deploy_12345"]) == 0
    assert capsys.readouterr().out == "layer 2: tmp/deploy.token\n"
    assert image_search.main(["image-search", str(saved), "not-there"]) == 1
    assert capsys.readouterr().out == ""


# --- The base's Dockerfile --------------------------------------------------------


def first_run(dockerfile: Path) -> str:
    """The Dockerfile's first RUN instruction, with its continuation lines."""
    lines = dockerfile.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("RUN "))
    end = start
    while lines[end].endswith("\\"):
        end += 1
    return "\n".join(lines[start : end + 1])


def test_its_first_layer_is_the_one_every_systemd_lab_shares():
    # Docker reuses a layer only when its instruction is the same text, so
    # a stray edit here would cost every machine a second copy of 150 MB.
    assert first_run(VAULT / "Dockerfile") == first_run(BASES / "net" / "Dockerfile")


def test_its_one_download_is_pinned_by_checksum():
    # README.md's "Pins" table is where the version and checksum are
    # recorded; the Dockerfile must check the same file it downloads.
    text = (VAULT / "Dockerfile").read_text(encoding="utf-8")
    downloads = re.findall(r"curl \S+ -o (\S+) (https://\S+)", text)
    assert len(downloads) == 1
    saved_as, url = downloads[0]
    checked = re.search(r'echo "([0-9a-f]{64})  (\S+)" \| sha256sum -c -', text)
    assert checked and checked.group(2) == saved_as
    version = re.search(r"/v(\d+\.\d+\.\d+)/", url).group(1)
    readme = (VAULT / "README.md").read_text(encoding="utf-8")
    assert version in readme and checked.group(1) in readme
