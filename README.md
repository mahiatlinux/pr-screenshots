# PR 10642 review evidence

Scope: SSH target extraction, approval propagation, network exemptions, and account/session isolation.

The base hard-blocks OpenSSH. The PR should permit a reviewed literal destination while rejecting other destinations, including Python SSH clients. Risks tested: CLI option arity, redirects, shell expansion, wrapped commands, Python import aliases, nested HTTP calls, IPv6/URI endpoints, and approval cleanup across accounts.

Environment: Linux x86_64, Python 3.14.4. PR code ran in disposable bubblewrap namespaces with a cleared environment, private PID/network namespaces, synthetic device mounts, and only the selected checkout exposed. No host credentials, GPU devices, user configuration, or SSH agent were mounted. Dependencies and application homes are task-local.

The live experiment starts an actual Paramiko 5.0.0 SSH server on 127.0.0.2:22222 inside each isolated network namespace. The real terminal and Python tools run the same inputs. No model or external server is needed. Base: zero connections, both tools blocked. Original head, merge control and repaired head: no connection before approval; both tools connect after approval and return `pr10642-live-ssh-ok`.

UI evidence uses independently built base and repaired Studio frontends and separate running backend instances/application homes. Each scene restores the actual tool execution result through the authenticated chat-history API, opens the same chat in a fresh browser context, expands the tool card and asserts the result text. It does not simulate a model response or claim an interactive inference run. Chromium 153.0.8010.12 and Firefox 155.0, Linux, 1280x900, light theme. Both composites were manually inspected.

Sources:

- https://man.openbsd.org/ssh
- https://man.openbsd.org/ssh_config
- https://man.openbsd.org/scp
- https://man.openbsd.org/sftp
- https://docs.paramiko.org/en/stable/api/client.html
- https://docs.paramiko.org/en/stable/api/transport.html

The `negative-control.log`, `account-negative.log`, and `endpoints-negative.log` show failing tests on unmodified b209f4625c817c97fd72e325511585c28ae7ff4a. The final suite and live checks verify the repairs. Approval loop evidence uses the real safetensors tool loop with deterministic generated text and a recording executor; the separate live SSH test executes actual clients.

## Revisions and results

- Base/merge base: `9bef060ea4200fb679067c4fca406087c1c14a4b`
- Original head: `b209f4625c817c97fd72e325511585c28ae7ff4a`
- Original merge control: `4930857668b2e1dbefca7b14cc4e29e96c6c07a7`
- Repaired head: `8f4b97edc26b9e66c1a2ac15c87dd7194f4a9877`

The expanded suite passed 2,649 tests with one platform skip. After the final Fabric/Transport endpoint normalization, the final policy suite passed all 64 tests. The initial test setup lacked Transformers; installing the supported dependency resolved that test. The tool-loop cap test also passed unchanged on the original head with a 60-second runner timeout (33.25 seconds for both control tests), instead of the initial 30-second limit.

Commands inside each credential-free environment:

```sh
python -m pytest studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py studio/backend/tests/test_studio_tool_loop.py studio/backend/tests/test_tool_confirm_loop.py studio/backend/tests/test_tool_approvals.py studio/backend/tests/test_safetensors_tool_loop.py studio/backend/tests/test_llama_cpp_tool_loop.py -q --tb=short --timeout=60
python -m pytest studio/backend/tests/test_ssh_policy.py -q --tb=short
python live_ssh.py
python approval_loops.py
python api_probe.py
python ui_scene.py
```

Additional API checks validate the actual SSH routes with an overridden authentication dependency; UI scene login uses real disposable local authentication. `approval_loops.py` verifies that Deny adds no approval and Allow records the host before execution.

The five-command timing corpus took a median 0.080 ms per combined blocklist/policy check on original head and 0.102 ms on the repair (five repeats of 500 checks, same host). This measures parsing only.
