import json
import os
import sys
from pathlib import Path

side = sys.argv[1]
os.environ['UNSLOTH_STUDIO_HOME'] = f'/task/studio-{side}-e2e'
sys.path.insert(0, f'/task/{side}/studio/backend')
from core.inference.tools import _python_exec, get_sandbox_workdir

code = '''import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
x = np.linspace(-10, 10, 200)
fig, ax = plt.subplots(figsize=(6, 3.2), dpi=100)
ax.plot(x, -x / 3 + 2, color="red", linewidth=2)
ax.set(xlim=(-10, 10), ylim=(-5, 5), xlabel="x", ylabel="y", title="y = -x/3 + 2")
ax.grid(alpha=0.25)
fig.tight_layout()
fig.savefig("line_plot.png")
plt.close(fig)
print("Plot saved")
'''
result = _python_exec(code, session_id='review-plot', thread_id='review-plot')
assert 'Plot saved' in result, result
plot = Path(get_sandbox_workdir('review-plot')) / 'line_plot.png'
assert plot.is_file()
import hashlib
print(json.dumps({'python_tool': 'passed', 'sha256': hashlib.sha256(plot.read_bytes()).hexdigest(), 'size': plot.stat().st_size}))
