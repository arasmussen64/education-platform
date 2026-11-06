"""Let the tests import the harness modules (checks, testrunner, ...) by name,
the same way exercise tests do."""

import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS))
