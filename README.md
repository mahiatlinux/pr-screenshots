# PR 11018 review evidence

Base: bda17fd83c4b7fdbe24f83bda2c0477f402668c5.
Original head: 66228651813568c4e46565c4792053170c5ee5f2.
Tested repair: 9e73b4a14, mirrored as 57948b74ebbf6d53f7b41434fd19f26be6ee2aba.
Linux x86_64, Python 3.14.4. Dependencies are pinned in requirements.lock.

The 16 companion lifecycle cases fail on base and pass on head. The sibling-snapshot readiness check passes on base, fails on the original head, and passes after the repair. The repaired model-services suite plus independent matrix passes 311 tests. The repaired mirror passes 312. The GGUF variant-row and MTP companion suites pass 325 tests.

Commands: `python -m pytest studio/backend/hub/tests/test_model_services.py test_companion_matrix.py -q` and `python -m pytest studio/backend/tests/test_gguf_variant_rows.py studio/backend/tests/test_mtp_drafter_companion.py -q`. Tests ran in separate credential-free Bubblewrap sandboxes with isolated homes and caches.

Screenshots show the production GgufDownloadCard from separate base/head frontend builds, with the actual GGUF backend service and identical seeded local caches. Unrelated endpoints use fixture responses. This is component/service evidence, not a full Studio launch or a model inference test. Both composites were inspected. Browser versions, viewport and observed labels are recorded in ui-facts.json.
