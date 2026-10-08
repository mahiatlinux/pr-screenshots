"""Scene: hold assistant-ui message hover still during a wheel gesture."""

from __future__ import annotations

import asyncio
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

from pr_ui_scenes._common import Session
from studio_test_kit.auth import StudioAuth, seed_init_script
from studio_test_kit.ui import open_chat


THREAD_ID = "uidiff-thread-wheel-hover"


def _request(session: Session, method: str, path: str, payload: dict) -> dict:
    request = urllib.request.Request(
        f"{session.base_url}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {session.access_token}",
            "Content-Type": "application/json",
        },
        method=method,
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read())


def _seed_thread(session: Session) -> None:
    now = int(time.time() * 1000)
    _request(
        session,
        "POST",
        "/api/chat/threads",
        {
            "id": THREAD_ID,
            "title": "Wheel hover evidence",
            "modelType": "base",
            "modelId": "",
            "createdAt": now,
            "updatedAt": now,
        },
    )
    messages = []
    parent_id = None
    for turn in range(40):
        user_id = f"u-{turn:03d}"
        messages.append(
            {
                "id": user_id,
                "threadId": THREAD_ID,
                "parentId": parent_id,
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Question {turn + 1}: explain wheel hover behavior briefly.",
                    }
                ],
                "createdAt": now + turn * 2,
            }
        )
        assistant_id = f"a-{turn:03d}"
        messages.append(
            {
                "id": assistant_id,
                "threadId": THREAD_ID,
                "parentId": user_id,
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Reply {turn + 1}. A stationary pointer should not make every "
                            "message boundary update the action bar while the thread is moving. "
                            "This repeated sentence gives each reply stable height for the test."
                        ),
                    }
                ],
                "createdAt": now + turn * 2 + 1,
            }
        )
        parent_id = assistant_id
    _request(
        session,
        "PUT",
        f"/api/chat/threads/{THREAD_ID}/messages",
        {"messages": messages, "pruneMissing": True, "deletedMessageIds": []},
    )


async def _visible_state(page, point: dict) -> dict:
    return await page.evaluate(
        """({x, y}) => {
          const viewport = document.querySelector('.aui-thread-viewport');
          const current = document.elementFromPoint(x, y)?.closest?.('[data-message-id]');
          const vr = viewport.getBoundingClientRect();
          const selectors = '.aui-assistant-action-bar-root, .aui-user-action-controls';
          const owners = [...document.querySelectorAll(selectors)]
            .filter((bar) => {
              const r = bar.getBoundingClientRect();
              const style = getComputedStyle(bar);
              return style.display !== 'none' && style.visibility !== 'hidden' &&
                r.width > 0 && r.height > 0 && r.bottom > vr.top && r.top < vr.bottom;
            })
            .map((bar) => bar.closest('[data-message-id]')?.dataset.messageId)
            .filter(Boolean);
          return {
            css_owner: current?.dataset.messageId ?? null,
            visible_bar_owners: owners,
            scroll_top: Math.round(viewport.scrollTop),
            captured_count: window.__wheelHoverCaptured.length,
            target_count: window.__wheelHoverTarget.length,
            trusted_target_count: window.__wheelHoverTarget.filter((e) => e.trusted).length,
          };
        }""",
        point,
    )


async def drive(
    session: Session, out_dir: Path, label: str, **_: object
) -> tuple[list[Path], dict]:
    _seed_thread(session)
    auth = StudioAuth(
        access_token=session.access_token,
        refresh_token=session.refresh_token,
        base_url=session.base_url,
    )
    init = seed_init_script(auth, providers=[])
    async with open_chat(
        session.base_url,
        init_scripts=[init],
        viewport=(1280, 900),
        headless=True,
    ) as studio_page:
        page = studio_page.page
        await page.goto(
            f"{session.base_url}/chat?thread={urllib.parse.quote(THREAD_ID, safe='')}",
            wait_until="domcontentloaded",
        )
        viewport = page.locator(".aui-thread-viewport").first
        await viewport.wait_for(state="visible", timeout=60_000)
        messages = page.locator("[data-message-id]")
        for _ in range(120):
            if await messages.count() >= 80:
                break
            await page.wait_for_timeout(250)
        count = await messages.count()
        if count != 80:
            raise RuntimeError(f"{label} rendered {count} messages, expected 80")

        point = await page.evaluate(
            """() => {
              const viewport = document.querySelector('.aui-thread-viewport');
              viewport.style.scrollBehavior = 'auto';
              viewport.scrollTop = Math.round((viewport.scrollHeight - viewport.clientHeight) * 0.45);
              const vr = viewport.getBoundingClientRect();
              const choices = [...viewport.querySelectorAll('[data-message-id][data-role="assistant"]')];
              const chosen = choices.find((node) => {
                const r = node.getBoundingClientRect();
                return r.top > vr.top + 100 && r.bottom < vr.bottom - 100;
              });
              if (!chosen) throw new Error('no interior assistant message');
              const r = chosen.getBoundingClientRect();
              return {x: Math.round(r.left + Math.min(180, r.width / 2)),
                      y: Math.round((r.top + r.bottom) / 2),
                      id: chosen.dataset.messageId};
            }"""
        )
        await page.mouse.move(1240, 860)
        await page.mouse.move(point["x"], point["y"])
        await page.wait_for_timeout(250)

        initial = await page.evaluate(
            """({x, y, id}) => {
              const owner = document.elementFromPoint(x, y)?.closest?.('[data-message-id]');
              if (owner?.dataset.messageId !== id) {
                throw new Error(`pointer owner ${owner?.dataset.messageId} != ${id}`);
              }
              window.__wheelHoverCaptured = [];
              window.__wheelHoverTarget = [];
              for (const root of document.querySelectorAll('[data-message-id]')) {
                for (const type of ['mouseenter', 'mouseleave']) {
                  root.addEventListener(type, (event) => {
                    window.__wheelHoverTarget.push({
                      type, id: root.dataset.messageId, trusted: event.isTrusted,
                      buttons: event.buttons,
                    });
                  });
                }
              }
              const viewport = document.querySelector('.aui-thread-viewport');
              for (const type of ['mouseenter', 'mouseleave']) {
                document.addEventListener(type, (event) => {
                  if (viewport.contains(event.target) && event.target.matches?.('[data-message-id]')) {
                    window.__wheelHoverCaptured.push({
                      type, id: event.target.dataset.messageId, trusted: event.isTrusted,
                      buttons: event.buttons,
                    });
                  }
                }, true);
              }
              const marker = document.createElement('div');
              marker.id = 'wheel-hover-evidence-pointer';
              marker.style.cssText = `position:fixed;left:${x - 8}px;top:${y - 8}px;` +
                'width:16px;height:16px;border:3px solid #ef4444;border-radius:999px;' +
                'box-sizing:border-box;z-index:2147483647;pointer-events:none;' +
                'box-shadow:0 0 0 2px white;';
              document.body.append(marker);
              return {id: owner.dataset.messageId};
            }""",
            point,
        )

        async def wheel_gesture() -> None:
            for _ in range(28):
                await page.mouse.wheel(0, 34)
                await page.wait_for_timeout(24)

        gesture = asyncio.create_task(wheel_gesture())
        await page.wait_for_timeout(260)
        during = await _visible_state(page, point)
        shot = out_dir / f"{label.lower()}_thread_wheel_hover.png"
        await viewport.screenshot(path=str(shot))
        await gesture
        await page.wait_for_timeout(700)
        settled = await _visible_state(page, point)

        if settled["css_owner"] not in settled["visible_bar_owners"]:
            raise RuntimeError(
                f"{label} did not settle its visible action bar on the pointer: {settled!r}"
            )
        if during["captured_count"] == 0:
            raise RuntimeError(f"{label} wheel gesture crossed no message boundary")

        facts = {
            "message_count": count,
            "initial_owner": initial["id"],
            "during_css_owner": during["css_owner"],
            "during_visible_bar_owners": during["visible_bar_owners"],
            "during_scroll_top": during["scroll_top"],
            "captured_boundary_events": during["captured_count"],
            "target_boundary_events": during["target_count"],
            "trusted_target_boundary_events": during["trusted_target_count"],
            "settled_css_owner": settled["css_owner"],
            "settled_visible_bar_owners": settled["visible_bar_owners"],
            "settled_target_boundary_events": settled["target_count"],
        }
        return [shot], facts
