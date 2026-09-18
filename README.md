PR 11272 evidence

Base: bf61e642b458afe22f6f62915ea560f8fde5a60f
Head: 2ab2e8f5a9c0f214428ca9a15358d44bfefd8c0e
Prospective merge: d7771a5e3d182104e9333abd90bbc630e698883e
Review mirror: 4d66858321e5f289be670a020bb01008c30b71a9

Linux x86_64, Python 3.12.13, pytest 8.4.2. Separate no-torch Studio installs used Python 3.13 and Hugging Face Hub 1.23.0. Playwright 1.62.0, Chromium 151.0.7922.34 and Firefox 153.0, viewport 1280x900.

Both caches contained identical synthetic model files and a dataset README symlink whose target parent had mode 000. This produces a real PermissionError without patching the scanner. The cached-models API returned zero models before and one afterward. The model is an inventory fixture, not a usable checkpoint.

Test command: python -m pytest studio/backend/tests/test_hf_cache_dangling_refs.py --noconftest -q
Base negative control: run the head test file with base backend PYTHONPATH and -k oserror. Both cases fail because Org/Model is absent.

Cross-platform A/B logs: https://github.com/mahiatlinux/unsloth/actions/runs/35405111692
