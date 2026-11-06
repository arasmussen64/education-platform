"""Let the tests import the tools (validate_content, content_model) by name."""

import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
