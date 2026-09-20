PR #11292 verification artifacts

Base: ef00d4946731d2cb9bed2982f1a24346843e7e19
Original head: ab33964d7e952515ad1849d1f930d797a125eac1
Repaired head: 576685ae138cfd55cbb1cd06318f28017f031b20
Current-upstream mirror: 9c1260938a766c4cd0b13a148246212ce05770c7

Linux x86_64. Separate worktrees, Python environments, Studio homes, frontend builds, and browser contexts. Browser viewport 1440 x 1000, English, reduced motion. Browser fixture changes only the chat-only capability gate to expose the dataset form; upload, detection, preview, role selection, and persistence use the real application. No model or training execution.

The initial base negative control has eight expected assertion failures. The repair negative control fails in both implementations on the original PR head. Repaired head and mirror each pass the 131-test focused suite on Python 3.13.14; Python 3.11.15 passes all 44 role tests. Source lint passes and the repository formatter leaves no extra changes.

The repair preserves short prompt/question columns for the existing fallback, instead of assigning context as user. repair_probe.py tests 1,944 short-value and column-order cases in both implementations: 3,888 original-head regressions, zero repaired regressions against base. probe.py also checks 5,808 QA cases and 6,413 compatibility cases.

live_api.py checks 18 JSONL/Parquet upload and preview cases plus 16 concurrent reads per revision, including the repaired short-input case. ui.py drives the real mapping dialog on Chrome, Firefox, and Edge and checks default and explicit manual mappings survive reload.

Commands: python probe.py; python repair_probe.py; python live_api.py; python ui.py chrome; python ui.py firefox; python ui.py edge. Scripts expect base/head/fix/mirror worktrees as siblings, task-specific authenticated local Studio instances on ports 19391/19392, and isolated browser binaries. Session credentials are excluded.
