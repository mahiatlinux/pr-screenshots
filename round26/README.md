# Round26 review decisions

Reviewed head: `30f324518e7b342a279cd771d63ad134a9a48178`. Original base: `9bef060ea4200fb679067c4fca406087c1c14a4b`. Head execution uses prospective merge `e2726a62faadcf60181789eae4e7a32205ae09eb` (base `c5faa7fb31a92af7eb996a4de5536025eedb7a63`). Identical disposable server, commands and installed Paramiko 5.0.0 are used in isolated filesystem/network/PID environments.

Both review findings reproduce identically before the PR and on the current head: a script written with printf then launched by bash executes the remote marker with one connection, and operator.methodcaller dispatches a Paramiko connect and executes the marker with one connection. Each harness deliberately asserts zero connections to expose the missing restriction, so both base and head controls fail that assertion for the same reason.

These are pre-existing confinement gaps, not regressions introduced by the SSH approval PR. No new source change was pushed. An uncommitted operator proposal was discarded after the original-base control disproved the initial regression classification. The PR's new supported inline-command and recognized Python-call approval paths remain covered by round25 checks; those checks do not establish runtime confinement of arbitrary scripts or reflective dispatch.

Commands in each isolated checkout:

```sh
python /evidence/round26_script_live.py
python /evidence/round26_methodcaller_base.py
```

The head methodcaller negative uses the identical invocation and stops on the same preapproval assertion. No model inference, GPU, host credentials or external SSH service is used.
