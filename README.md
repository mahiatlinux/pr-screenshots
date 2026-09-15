# PR 10941 verification

## Before

Merge base `03af220ac0023ab846727397b3a1de9efa0aec42` exports both sibling replies in ShareGPT. With reply 1/2 selected, Training JSONL exports reply 2/2. Six regression cases fail for these branch-selection defects; the CSV control passes.

## After

Head `bd516c952a4dc74f19238effc1e0c8c7c29fb61b` exports only the selected reply in both formats. The same browser scenario passes on merge `b2782c590c89aa3815d2e86820feb6a7935a97f0`.

Real Studio requests to a local llama.cpp CUDA server used Ling-3.0-tiny-Q6_K on an NVIDIA RTX 5060 Ti. The browser sent a prompt, regenerated its reply, selected the first reply, edited the prompt, and downloaded the exports.

| ShareGPT scenario | Base turns | Head turns |
| --- | ---: | ---: |
| Regeneration request held in flight | 2 | 1 |
| Regeneration complete | 3 | 2 |
| First reply selected again | 3 | 2 |
| Prompt edited and new reply complete | 5 | 2 |

The in-flight test holds the browser request before releasing it to the real model server. Completed-generation assertions wait for saved messages. Both final edited answers were `Lion`.

## Verdict

Confirmed issue, fixed by the existing PR head. No additional defect found in the reviewed changes.

## Regression risk

99 focused tests pass on head and merge. Five additional cases pass on both: legacy flat threads, empty live branches, inactive threads, disposed views, and selection within a multi-turn branch. The extended test file also repeats the seven PR tests, for 12 total.

CSV preserves both original and edited prompts in real browser downloads. Markdown export tests pass. Both builds and the merge build pass. Head typecheck and ESLint on the changed utilities and tests pass.

## Compatibility

Linux x86_64; Python 3.14.4; Node 26.8.2; Playwright 1.62.0; NVIDIA driver 595.91.07.

The branch-picker export scenario ran against base and head in Chromium 151.0.7922.34, Firefox 153.0, Google Chrome 153.0.8010.36, and Microsoft Edge 153.0.4234.32. Each used a fresh browser context, locale en-US and a 1280x900 viewport.

Dependencies were installed under the disposable task directory. PR code ran in a credential-free Bubblewrap sandbox. Frontend dependencies came from the committed package lock; Python dependencies are recorded in requirements.lock.

## UI evidence

All five before/after composites were opened and inspected. The chat view is intentionally the same; this PR changes downloaded files. The footer is an evidence annotation generated from the downloaded files, outside the original screenshots. Original screenshots, downloaded JSONL/CSV, browser versions and semantic assertions are preserved in the per-run folders.

## Fixes

No source edits or repair commits were necessary. The reviewed head remains `bd516c952a4dc74f19238effc1e0c8c7c29fb61b`.

## Commands

Focused: `node --experimental-strip-types --test tests/ndjson-body.test.ts tests/conversation-markdown-export.test.ts tests/conversation-markdown.test.ts tests/sharegpt-export-branches.test.ts`

Extra cases: `node --experimental-strip-types --test tests/extended-export.test.ts`

Build: `npm run build`; types: `npm run typecheck`.

Base negative control mounted the head regression test and its live-view test helper onto the unchanged base. The exporter and branch-selection implementation remained from base. Browser checks used ui_review.py and gpu_review.py with the accompanying scenes and the pr-ui-evidence skill's Studio helpers.
