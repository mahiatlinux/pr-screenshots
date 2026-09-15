import json
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'fix/tests/studio'))
import playwright_data_settings as suite
import _playwright_robust as robust
robust.FRONTEND = Path.cwd() / 'studio/frontend'
port = int(sys.argv[1])
server = robust.start_vite(port)
try:
    url = f'http://127.0.0.1:{port}/smoke-settings.html'
    robust.wait_for_smoke_page(url, 'smoke-settings-main.tsx', proc=server, timeout_s=60)
    with sync_playwright() as p:
        browser = getattr(p, os.environ.get("PW_ENGINE", "chromium")).launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 1000})
        page.add_init_script(suite.FIXTURE)
        page.goto(url)
        page.wait_for_function('!!window.__settingsSmoke', timeout=120000)
        print(json.dumps({'version': browser.version, 'checks': suite.run_thumbnail_retention(page)}))
        browser.close()
finally:
    robust.stop_process(server)
