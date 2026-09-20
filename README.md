PR #11292 verification artifacts

Base: ef00d4946731d2cb9bed2982f1a24346843e7e19
Head: ab33964d7e952515ad1849d1f930d797a125eac1
Current-upstream mirror: d9a79bfc2a76fd240a99c8aed9d787374ea983cc

Linux x86_64. Separate worktrees, Python environments, Studio homes, frontend builds, and browser contexts. Browser viewport 1440 x 1000, English, reduced motion. Browser fixture changes only the chat-only capability gate to expose the dataset form; file upload, format detection, preview data, role selection, and persistence use the real application. No model or training execution.

The base negative control has eight expected assertion failures. Both head and the mirror pass the 127-test focused suite. Python 3.11 passes the 40 PR tests; the main suite uses Python 3.13. Source lint passes and the repository formatter leaves a clean diff.

probe.py checks 5,808 QA cases and 6,413 compatibility cases against both implementations. live_api.py checks JSONL and Parquet uploads and concurrent reads on two live authenticated Studio instances. ui.py drives the real mapping dialog. Chrome additionally checks explicit manual roles survive reload.

Commands: python probe.py; python live_api.py; python ui.py chrome; python ui.py firefox; python ui.py edge. The scripts expect base/head/merge worktrees as siblings, task-specific authenticated local Studio instances on ports 19391/19392, and isolated browser binaries. Session credentials are excluded.
