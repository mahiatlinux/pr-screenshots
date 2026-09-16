# Git SSH transport repair

Head ef983da5095ba3d5d0672def1eb49738d77a9ca2. Prior head d76ee3ea2e28cfe8d04c9e3c520838ca71246c6b; negative control used prospective merge 2fa44449e8cd51d4ce2832721f60de59d43a86bd.

Actual git ls-remote completed its SSH exchange with an unapproved disposable server before repair. After repair it makes zero connections. A valid empty Git ref advertisement is served over real OpenSSH/Paramiko; this is not model inference. The first harness attempt encountered the inaccessible worktree Git metadata, so the final control uses git -C /tmp and an absolute disposable key path.

Fifteen regression assertions fail before repair; nine non-SSH Git controls pass. Final focused suites plus 24 external controls: 2927 passed, 1 platform skip, including 295 repository SSH-policy cases. The existing 42 approved SSH connection controls also pass. Ruff 0.6.9 and diff whitespace checks pass.

Git SSH transports remain blocked even after approving a literal URL, because Git configuration, URL rewriting and environment overrides can change the destination. Named/default remotes and opaque transport settings fail closed. Local Git operations and the tested explicit non-SSH remotes remain available. Direct approved SSH is the supported connection path.

Primary sources: https://git-scm.com/docs/git-fetch#_git_urls, https://git-scm.com/docs/git-config and https://git-scm.com/docs/git. Installed git clone/fetch/push/ls-remote help verified option arity.

Commands:

    ./sandbox.sh latest-merge python -m pytest /evidence/round20_regressions.py -q --tb=short -p no:cacheprovider
    ./sandbox.sh latest-merge python /evidence/round20_git_live.py
    ./sandbox.sh fix python -m pytest /evidence/round20_regressions.py studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
    ./sandbox.sh fix env PATH=/work/.probe-venv/bin:/node/bin:/opt:/usr/bin:/bin python /evidence/round20_git_live.py
    ./sandbox.sh fix env PATH=/work/.probe-venv/bin:/node/bin:/opt:/usr/bin:/bin python /evidence/round19_live.py
