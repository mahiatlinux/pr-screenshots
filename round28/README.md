# Round28 transfer endpoint repair

Repaired head `318746441f80064c1275ce59b6351d5b8f421418`. Original base `9bef060ea4200fb679067c4fca406087c1c14a4b` blocks SCP and SFTP with zero connections. Previous head `30f324518e7b342a279cd771d63ad134a9a48178`, tested through local merge `f10b9da2d9014617177050a2282a9dbed096efd4` with main `1066d16aff3b4a5dbaad1c4df85a3dd94bb3bb3c`, connects twice and downloads the exact marker file before host approval when the remote path contains @approved.example.

After repair, approving only the hostname in the path makes zero connections. Approving the actual host allows both SCP and SFTP downloads; both exit successfully and the downloaded bytes equal pr10642-scp-file-ok plus a newline. The task SFTP server initially omitted SSH exit status, so SCP copied the file but returned exit code 1; that failed harness result is preserved. The final server sends a success exit status on normal subsystem completion, and base/head/fix controls were rerun with that same harness.

Eight negative regression assertions fail before repair, including local filenames with @ being mistaken for hosts; three URI/username controls pass. Exact head focused suites plus 11 external controls: 2,984 passed and one platform skip, including 365 repository SSH-policy cases. All 50 existing approved SSH connections and a separate reverse handshake pass. Ruff and diff checks pass.

Commands in credential-free private-network/PID/filesystem sandboxes:

```sh
python /evidence/round28_transfer_live.py --base
python /evidence/round28_transfer_live.py
python -m pytest /evidence/round28_regressions.py studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
python /evidence/round25_live.py
python /evidence/round21_reverse_live.py
python -m ruff check studio/backend/core/inference/ssh_policy.py studio/backend/tests/test_ssh_policy.py
```

The --base flag stops after confirming the original hard block. Paramiko 5.0.0 supplies the disposable server, with real system OpenSSH clients. No GPU, model inference or external SSH service is used. Endpoint syntax is verified against https://man.openbsd.org/scp and https://man.openbsd.org/sftp.
