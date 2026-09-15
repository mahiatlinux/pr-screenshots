import json
from pathlib import Path
import sys

import utils.paths
import pytest

artifacts = Path(__file__).resolve().parent
side = Path.cwd().name
paths = json.loads((artifacts / "expanded-test-files.json").read_text())
raise SystemExit(pytest.main([
    "-q", "-rs", "-p", "no:cacheprovider", "--timeout=60",
    f"--junitxml={artifacts}/{side}-expanded.xml", *paths,
]))
