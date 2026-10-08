import assert from "node:assert/strict";
import fs from "node:fs";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium, firefox, webkit } = require("../playwright/runtime/node_modules/playwright");
const ts = require("../fix/studio/frontend/node_modules/typescript");

const source = fs.readFileSync(
  new URL("../fix/studio/frontend/src/components/assistant-ui/thread-wheel-hover.ts", import.meta.url),
  "utf8",
);
const compiled = ts.transpileModule(source, {
  compilerOptions: {
    module: ts.ModuleKind.CommonJS,
    target: ts.ScriptTarget.ES2022,
  },
}).outputText;
const installSuppression = `(() => {
  const exports = {};
  ${compiled}
  window.attachWheelHoverSuppression = exports.attachWheelHoverSuppression;
})();`;

const html = String.raw`<!doctype html>
<meta charset="utf-8">
<style>
  body { margin: 0; padding: 30px; font: 16px sans-serif; }
  #viewport { width: 480px; height: 280px; overflow-y: auto; border: 2px solid #222; }
  [data-message-id] { box-sizing: border-box; height: 116px; padding: 22px; border-bottom: 1px solid #888; user-select: text; }
  [data-message-id]:nth-child(odd) { background: #eef4ff; }
  [data-message-id]:nth-child(even) { background: #fff4e8; }
  .bar { display: none; float: right; border: 1px solid #333; padding: 4px; }
  [data-message-id].store-hover .bar { display: block; }
</style>
<div id="viewport"></div>
<script>
  window.delivered = [];
  window.captured = [];
  const viewport = document.querySelector('#viewport');
  for (let i = 0; i < 24; i += 1) {
    const message = document.createElement('div');
    message.dataset.messageId = 'm' + i;
    message.innerHTML = '<span>Message ' + i + ' selectable text</span><span class="bar">actions</span>';
    for (const type of ['mouseenter', 'mouseleave']) {
      message.addEventListener(type, (event) => {
        window.delivered.push({ type, id: message.dataset.messageId, buttons: event.buttons, trusted: event.isTrusted });
        message.classList.toggle('store-hover', type === 'mouseenter');
      });
    }
    viewport.append(message);
  }
  document.addEventListener('mouseenter', (event) => {
    if (event.target.matches?.('[data-message-id]')) {
      window.captured.push({ type: event.type, id: event.target.dataset.messageId, buttons: event.buttons, trusted: event.isTrusted });
    }
  }, true);
  document.addEventListener('mouseleave', (event) => {
    if (event.target.matches?.('[data-message-id]')) {
      window.captured.push({ type: event.type, id: event.target.dataset.messageId, buttons: event.buttons, trusted: event.isTrusted });
    }
  }, true);
</script>`;

async function reset(page, enabled) {
  await page.setContent(html, { waitUntil: "load" });
  await page.evaluate(() => {
    if (document.querySelector("#viewport").childElementCount !== 0) return;
    window.delivered = [];
    window.captured = [];
    const viewport = document.querySelector("#viewport");
    for (let i = 0; i < 24; i += 1) {
      const message = document.createElement("div");
      message.dataset.messageId = `m${i}`;
      message.innerHTML = `<span>Message ${i} selectable text</span><span class="bar">actions</span>`;
      for (const type of ["mouseenter", "mouseleave"]) {
        message.addEventListener(type, (event) => {
          window.delivered.push({
            type,
            id: message.dataset.messageId,
            buttons: event.buttons,
            trusted: event.isTrusted,
          });
          message.classList.toggle("store-hover", type === "mouseenter");
        });
      }
      viewport.append(message);
    }
    for (const type of ["mouseenter", "mouseleave"]) {
      document.addEventListener(
        type,
        (event) => {
          if (event.target.matches?.("[data-message-id]")) {
            window.captured.push({
              type: event.type,
              id: event.target.dataset.messageId,
              buttons: event.buttons,
              trusted: event.isTrusted,
            });
          }
        },
        true,
      );
    }
  });
  if (enabled) {
    await page.addScriptTag({ content: installSuppression });
    await page.evaluate(() => {
      window.detachSuppression = window.attachWheelHoverSuppression(
        document.querySelector("#viewport"),
      );
    });
  }
  await page.mouse.move(650, 390);
  await page.locator("#viewport").hover({ position: { x: 240, y: 58 } });
  await page.waitForTimeout(100);
  await page.evaluate(() => {
    window.delivered = [];
    window.captured = [];
  });
}

async function wheelTrial(page, enabled) {
  await reset(page, enabled);
  for (let i = 0; i < 12; i += 1) {
    await page.mouse.wheel(0, 60);
    await page.waitForTimeout(8);
  }
  await page.waitForTimeout(700);
  return page.evaluate(() => {
    const css = document.querySelector("[data-message-id]:hover")?.dataset.messageId ?? null;
    const stored = [...document.querySelectorAll("[data-message-id].store-hover")].map(
      (node) => node.dataset.messageId,
    );
    return {
      captured: window.captured,
      delivered: window.delivered,
      css,
      stored,
      childCount: document.querySelector("#viewport").childElementCount,
      bounds: document.querySelector("#viewport").getBoundingClientRect().toJSON(),
      scrollTop: document.querySelector("#viewport").scrollTop,
    };
  });
}

async function dragDuringTail(page) {
  await reset(page, true);
  await page.mouse.wheel(0, 240);
  await page.waitForTimeout(20);
  await page.mouse.down();
  await page.evaluate(() => {
    window.delivered = [];
    window.captured = [];
  });
  await page.mouse.move(270, 250, { steps: 12 });
  await page.mouse.up();
  await page.waitForTimeout(700);
  return page.evaluate(() => ({
    captured: window.captured,
    delivered: window.delivered,
    css: document.querySelector("[data-message-id]:hover")?.dataset.messageId ?? null,
    stored: [...document.querySelectorAll("[data-message-id].store-hover")].map(
      (node) => node.dataset.messageId,
    ),
  }));
}

const engines = { chromium, firefox, webkit };
const results = {};
for (const [name, browserType] of Object.entries(engines)) {
  let browser;
  try {
    browser = await browserType.launch({ headless: true, env: process.env });
    const context = await browser.newContext({ viewport: { width: 700, height: 420 } });
    const page = await context.newPage();
    const before = await wheelTrial(page, false);
    const after = await wheelTrial(page, true);
    const drag = await dragDuringTail(page);
    assert.equal(
      after.stored.length,
      1,
      `${name}: repaired wheel trial has one stored hover: ${JSON.stringify(after)}`,
    );
    assert.equal(after.stored[0], after.css, `${name}: stored hover matches CSS hover`);
    assert.ok(
      after.delivered.filter((event) => event.trusted).length <=
        before.delivered.filter((event) => event.trusted).length,
      `${name}: suppression does not add trusted target events`,
    );
    const held = drag.delivered.filter((event) => event.trusted && event.buttons !== 0);
    assert.ok(held.length >= 1, `${name}: button-held boundary event reaches the target`);
    assert.equal(drag.stored.length, 1, `${name}: drag trial ends with one stored hover`);
    assert.equal(
      drag.stored[0],
      drag.css,
      `${name}: drag stored hover matches CSS hover: ${JSON.stringify(drag)}`,
    );
    results[name] = {
      version: browser.version(),
      before: {
        captured: before.captured.length,
        target: before.delivered.length,
        trustedTarget: before.delivered.filter((event) => event.trusted).length,
        css: before.css,
        stored: before.stored,
        scrollTop: before.scrollTop,
      },
      after: {
        captured: after.captured.length,
        target: after.delivered.length,
        trustedTarget: after.delivered.filter((event) => event.trusted).length,
        css: after.css,
        stored: after.stored,
        scrollTop: after.scrollTop,
      },
      drag: {
        captured: drag.captured,
        delivered: drag.delivered,
        heldDelivered: held.length,
        css: drag.css,
        stored: drag.stored,
      },
    };
    await context.close();
  } catch (error) {
    results[name] = { error: String(error?.stack ?? error) };
  } finally {
    await browser?.close();
  }
}

console.log(JSON.stringify(results, null, 2));
if (Object.values(results).some((result) => "error" in result)) process.exitCode = 1;
