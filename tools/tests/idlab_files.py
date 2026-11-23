"""Loads the identity-lab base's helpers (content/lab-bases/id/) for their
tests. Most have no .py ending, because a learner types them as commands, so
they are loaded by path."""

import importlib.machinery
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "content" / "lab-bases" / "id"


def load(name: str, path: Path) -> ModuleType:
    """The file at `path` as a module called `name`. Nothing in these files
    runs at import: each keeps its command line under `__main__`."""
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, module)
    # No __pycache__ beside the file: the base's bin/ and lib/ are copied
    # whole into the image, and a stray folder there would change it.
    before = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = before
    return module


jwtlib = load("jwtlib", BASE / "lib" / "jwtlib.py")
kcapi = load("kcapi", BASE / "lib" / "kcapi.py")
signin = load("idlab_signin", BASE / "bin" / "signin")
timesync = load("idlab_timesync", BASE / "lib" / "timesync")
