# Prospective merge verification

Merge and parents: `b054eec844efaededd76562a3089276de04c9897 af4e98e2f63f1907eb4b5d5f8b9375311d9b667a 308b23607a5febaaa4972a86f904fb3d0ad6309c`.

Policy, sandbox and permission suites: 2,744 passed, one platform skip. Real tools: ten successful SSH connections after approval and no connection for the blocked controls. Frontend assets reuse the passing round-four build on unchanged base af4e98e2; rebuilt authenticated Studio UI captures pass in Chromium 153 and Firefox 155 and were manually inspected. UI uses restored real tool outputs, not model inference.

A previous merge control at f58743741e7fbce4816f6a0ae112322cef0998a8 passed 632 tool-loop tests; its log is preserved separately and is not a latest-head claim.
