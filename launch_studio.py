import os
import sys
from pathlib import Path

side, port = sys.argv[1:]
repo = Path('/task') / side
os.environ['UNSLOTH_STUDIO_HOME'] = f'/task/studio-{side}-e2e'
os.environ['UNSLOTH_STUDIO_DISABLE_TORCH_WARM'] = '1'
sys.path.insert(0, str(repo / 'studio/backend'))
import main
import uvicorn

main.setup_frontend(main.app, repo / 'studio/frontend/dist')
uvicorn.run(main.app, host='127.0.0.1', port=int(port))
