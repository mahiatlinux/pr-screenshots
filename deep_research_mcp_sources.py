"""Scene: Deep Research MCP source controls for PR 13103."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

WORKSPACE = Path(os.environ.get("UNSLOTH_WORKSPACE", Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(WORKSPACE))
sys.path.insert(0, str(WORKSPACE / "scripts"))

from playwright.async_api import async_playwright  # noqa: E402

from pr_ui_scenes._common import Session  # noqa: E402
from studio_test_kit.auth import StudioAuth, seed_init_script  # noqa: E402


async def drive(
    session: Session,
    out_dir: Path,
    label: str,
    route: str = "/chat",
    **_: object,
) -> tuple[list[Path], dict]:
    auth = StudioAuth(
        access_token=session.access_token,
        refresh_token=session.refresh_token,
        base_url=session.base_url,
    )
    request_count = 0

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 1200})
        await context.add_init_script(seed_init_script(auth, providers=[]))
        await context.add_init_script(
            "window.localStorage.setItem('unsloth_chat_deep_research_enabled', 'true')"
        )
        page = await context.new_page()
        settings = {"deepResearchEnabled": True}
        if label.upper() == "AFTER":
            settings["researchMcpSources"] = []
        initialized = await context.request.put(
            f"{session.base_url}/api/chat/settings",
            headers={"Authorization": f"Bearer {session.access_token}"},
            data=settings,
        )
        assert initialized.ok, await initialized.text()

        async def fulfill_tools(route) -> None:
            nonlocal request_count
            request_count += 1
            await route.fulfill(
                status=200,
                content_type="application/json",
                body=(
                    '[{"serverId":"notes","serverName":"Project Notes",'
                    '"tool":"search_notes","description":"Search approved project notes."},'
                    '{"serverId":"papers","serverName":"Paper Index",'
                    '"tool":"search_papers","description":"Search the research paper index."}]'
                ),
            )

        await page.route("**/api/mcp/servers/research-tools", fulfill_tools)
        await page.goto(f"{session.base_url}{route}", wait_until="domcontentloaded")

        configure = page.get_by_role(
            "button", name="Configure Deep Research website access", exact=True
        )
        await configure.wait_for(state="visible", timeout=60_000)
        await configure.click()

        dialog = page.get_by_role("dialog")
        await dialog.get_by_role("heading", name="Deep research", exact=True).wait_for(
            state="visible", timeout=30_000
        )
        mcp_header = dialog.get_by_text("MCP search sources", exact=True)
        header_visible = await mcp_header.count() == 1
        tool_labels: list[str] = []
        cap_copy_visible = False
        switch_names: list[str] = []
        if header_visible:
            await dialog.get_by_text("Project Notes · search_notes", exact=True).wait_for(
                state="visible", timeout=30_000
            )
            tool_labels = [
                (await dialog.get_by_text(name, exact=True).inner_text()).strip()
                for name in ("Project Notes · search_notes", "Paper Index · search_papers")
            ]
            cap_copy_visible = (
                await dialog.get_by_text(
                    "Every research search also sends its query to the tools turned on here. Choose up to 20.",
                    exact=True,
                ).count()
                == 1
            )
            switches = dialog.get_by_role("switch", name=re.compile(r"^Search with"))
            switch_names = [
                await switches.nth(index).get_attribute("aria-label")
                for index in range(await switches.count())
            ]

        facts = {
            "mcp_header_visible": header_visible,
            "mcp_tool_labels": tool_labels,
            "cap_copy_visible": cap_copy_visible,
            "mcp_switch_names": switch_names,
            "research_tools_requests": request_count,
        }
        shot = out_dir / f"{label.lower()}_deep_research_mcp_sources.png"
        await page.screenshot(path=str(shot), clip={"x": 430, "y": 100, "width": 580, "height": 1000})
        if header_visible:
            first = dialog.get_by_role("switch", name="Search with Project Notes search_notes", exact=True)
            await first.focus()
            await page.keyboard.press("Space")
            assert await first.get_attribute("aria-checked") == "true"
            await dialog.get_by_role("button", name="Save limits", exact=True).click()
            saved = await page.evaluate("JSON.parse(localStorage.getItem('unsloth_chat_deep_research_mcp_sources'))")
            assert saved == [{"serverId": "notes", "tool": "search_notes"}]
            await configure.click()
            second = page.get_by_role("switch", name="Search with Paper Index search_papers", exact=True)
            await second.click()
            await dialog.get_by_role("button", name="Cancel", exact=True).click()
            assert await page.evaluate("JSON.parse(localStorage.getItem('unsloth_chat_deep_research_mcp_sources'))") == saved
            await configure.click()
            facts["save_and_cancel_verified"] = True
        await page.set_viewport_size({"width": 390, "height": 844})
        save = dialog.get_by_role("button", name="Save limits", exact=True)
        await save.scroll_into_view_if_needed()
        box = await save.bounding_box()
        assert box and box["y"] >= 0 and box["y"] + box["height"] <= 844
        facts["narrow_save_reachable"] = True
        narrow = out_dir / f"{label.lower()}_deep_research_mcp_narrow.png"
        await page.screenshot(path=str(narrow))

        if header_visible:
            await dialog.get_by_role("button", name="Cancel", exact=True).click()
            await page.unroute("**/api/mcp/servers/research-tools")
            async def unavailable_tools(route):
                await route.fulfill(status=200, content_type="application/json", body="[]")
            await page.route("**/api/mcp/servers/research-tools", unavailable_tools)
            await page.set_viewport_size({"width": 1440, "height": 1200})
            await page.reload(wait_until="domcontentloaded")
            await configure.click()
            try:
                await dialog.get_by_text("No enabled MCP server has a search tool that takes a single query.", exact=True).wait_for()
            except Exception:
                await page.screenshot(path=str(out_dir / "discovery_failure.png"))
                print("DISCOVERY DIALOG:", await dialog.inner_text(), flush=True)
                raise
            await dialog.get_by_role("button", name="Save limits", exact=True).click()
            assert await page.evaluate("JSON.parse(localStorage.getItem('unsloth_chat_deep_research_mcp_sources'))") == saved, "incomplete discovery deleted the saved source"
            facts["unavailable_selection_preserved"] = True
            await configure.click()
            await dialog.get_by_role("button", name="Remove unavailable source notes search_notes", exact=True).click()
            await dialog.get_by_role("button", name="Save limits", exact=True).click()
            assert await page.evaluate("JSON.parse(localStorage.getItem('unsloth_chat_deep_research_mcp_sources'))") == []
            facts["unavailable_selection_removable"] = True

        await context.close()
        await browser.close()

    return [shot, narrow], facts
