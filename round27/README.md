# Round27 original-base control

Reviewed head `30f324518e7b342a279cd771d63ad134a9a48178`; original base `9bef060ea4200fb679067c4fca406087c1c14a4b`. The head control ran in its already-tested merge `e2726a62faadcf60181789eae4e7a32205ae09eb`.

Run `python /evidence/round27_mapping_live.py` independently in each credential-free sandbox using identical Paramiko 5.0.0 and disposable SSH server. Both execute the remote marker through `clients.get('prod').connect(hostname=...)` with one connection. Both fail the deliberate zero-connection assertion for that same reason.

This is a pre-existing confinement gap, not a regression introduced by the PR. No source change was made for the finding. The current inline-call approval controls do not establish confinement of arbitrary reflective/container dispatch.
