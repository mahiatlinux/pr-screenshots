from __future__ import annotations

import json
import time
from pathlib import Path

from pr_ui_scenes._common import Session
from studio_test_kit.auth import seed_init_script
from studio_test_kit.ui import open_chat


async def drive(session: Session, out_dir: Path, label: str, **_: object):
    progress = label == "AFTER"
    entry = {
        "id": "apireq_prefill_evidence",
        "endpoint": "/v1/chat/completions",
        "model": "demo-model",
        "prompt_preview": "Explain a long request",
        "reply_preview": "",
        "status": "running",
        "started_at": time.time(),
        "updated_at": time.time(),
        "running_phase": "prompt_processing",
        "prompt_progress": (
            {
                "total": 2000,
                "processed": 1200,
                "cached": 0,
                "time_ms": 15000.0,
                "percent": 60.0,
            }
        ),
    }
    response = {
        "status": "generating",
        "server_time": time.time(),
        "active_model": "demo-model",
        "context_length": 8192,
        "active_requests": 1,
        "queue": None,
        "logging_enabled": True,
        "entries": [entry],
    }

    async def mock_monitor(route):
        path = route.request.url.split("?", 1)[0]
        body = entry if path.endswith(entry["id"]) else response
        await route.fulfill(status=200, content_type="application/json", body=json.dumps(body))

    init = seed_init_script(
        type(
            "Auth",
            (),
            {"access_token": session.access_token, "refresh_token": session.refresh_token},
        )(),
        [],
    )
    async with open_chat(
        session.base_url,
        init_scripts=[init],
        viewport=(1500, 920),
        headless=True,
    ) as studio_page:
        page = studio_page.page
        await page.route("**/api/inference/monitor**", mock_monitor)
        await page.goto(f"{session.base_url}/api-monitor", wait_until="domcontentloaded")
        await page.get_by_role("heading", name="API", exact=True).wait_for(
            state="visible", timeout=60_000
        )
        row = page.get_by_role("button").filter(has_text="/chat/completions").first
        await row.wait_for(state="visible", timeout=30_000)
        await row.click()
        status = "Prompt processing · 60%" if progress else "running"
        status_element = page.locator("span.uppercase").filter(has_text=status)
        await status_element.wait_for(state="visible", timeout=30_000)
        rendered_status = await status_element.inner_text()
        out_dir.mkdir(parents=True, exist_ok=True)
        shot = out_dir / f"{label.lower()}_prefill_progress.png"
        await page.screenshot(path=str(shot), full_page=True)
    facts = {
        "running_phase": "prompt_processing",
        "percent": 60.0,
        "rendered_status": rendered_status,
    }
    return [shot], facts
