import sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
sys.path.insert(0,str(Path.cwd()/'tests'))
import core.training.training
import utils.prebuilt.update_flow
import test_training_progress_callback as callbacks
for name,attrs in callbacks._STUBS.items(): callbacks._stub_if_missing(name,attrs)
import core.training.trainer
import pytest
raise SystemExit(pytest.main(sys.argv[1:]))
