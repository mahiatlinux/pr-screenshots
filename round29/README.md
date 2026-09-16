# Round29 native cmd approval repair

Repaired head `f7f620ff5c0eec60b2b65262cbcf24280cbfa487`. Previous head `318746441f80064c1275ce59b6351d5b8f421418`; original base `9bef060ea4200fb679067c4fca406087c1c14a4b`.

Native Windows 2022 base/head control: https://github.com/mahiatlinux/unsloth/actions/runs/35088888371. With the cmd fallback selected, original base blocks the real OpenSSH command with zero connections; reviewed head authenticates and executes the remote marker without approval. The probe disables only trusted Bash discovery to select the supported cmd fallback. The server listens on private loopback with generated keys. No production safety checks are bypassed.

The safe child PATH excludes System32/OpenSSH, so the probe uses the actual extensionless absolute executable path. Its .exe spelling encountered an existing unrelated generic blocklist match. The safe environment omits ProgramData, which Windows OpenSSH 9.5p2 needs at startup; direct version probes demonstrate this. The executed command supplies PROGRAMDATA with cmd set before the adjacent SSH command. Quoting that set assignment through Python list argv did not initialize it correctly; the final command uses the valid unquoted assignment. Initial startup, listener-shutdown and Windows patch line-ending failures are preserved. These are test setup observations, not product repairs.

The repair tokenizes unquoted cmd operators and tracks quoted/caret-escaped data. Seven bypass assertions and a literal-semicolon false-positive assertion fail on the preceding head; three quoted/escaped controls pass. Focused suites plus 11 external checks: 2,995 passed, one platform skip, including 376 repository SSH-policy cases. Existing real Linux controls pass: 50 ordinary SSH connections, two exact-byte SCP/SFTP downloads, one reverse SSH handshake. Ruff and whitespace checks pass.

Commands in credential-free task sandboxes:

```sh
python -m pytest /evidence/round29_regressions.py studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
python /evidence/round25_live.py
python /evidence/round28_transfer_live.py
python /evidence/round21_reverse_live.py
python -m ruff check studio/backend/core/inference/tools.py studio/backend/tests/test_ssh_policy.py
```

Native VM commands: `python round29_windows_live.py --base`, `--negative`, or `--fixed`. The first stops after the original hard block, the second requires the unauthorized remote marker, and the fixed control requires zero connections before approval then successful remote execution after approval. No GPU or model inference. Operator and quoting semantics: https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cmd.

Native base/head/fix verification passed: https://github.com/mahiatlinux/unsloth/actions/runs/35089227773. Both modified source blobs match the committed repair exactly. Fixed command makes zero connections before approval and one authenticated remote-marker connection afterward.
