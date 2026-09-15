import json
import base64
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'fix/tests/studio'))
import playwright_data_settings as suite
import _playwright_robust as robust
robust.FRONTEND = Path.cwd() / 'studio/frontend'
label, port = sys.argv[1], int(sys.argv[2])
output = root / 'artifacts' / label
output.mkdir(exist_ok=True)
expected = 'Data controls become grouped sections and archive cards. Managed and archived chats gain search and project groups; media archives gain search and compact dated rows.'
(root / 'artifacts/ui-expect.txt').write_text(expected)
server = robust.start_vite(port)
results = {}
try:
    url = f'http://127.0.0.1:{port}/smoke-settings.html'
    robust.wait_for_smoke_page(url, 'smoke-settings-main.tsx', proc=server, timeout_s=60)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=str(root / 'playwright/chrome/opt/google/chrome/chrome'))
        for shelf in os.environ.get('UI_SHELVES', 'data,manage,chats,images,videos,audio').split(','):
            context = browser.new_context(viewport={'width':1280, 'height':1000}, locale='en-US', timezone_id='UTC', reduced_motion='reduce')
            page = context.new_page()
            page.add_init_script(suite.FIXTURE.replace("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aZwoAAAAASUVORK5CYII=", base64.b64encode((root / "artifacts/thumbnail.png").read_bytes()).decode()))
            page.add_init_script('''(() => { const previous = window.fetch; const data = ''' + json.dumps(base64.b64encode((root/'artifacts/thumbnail.png').read_bytes()).decode()) + '''; window.fetch = async (input, init) => { const url = new URL(typeof input === 'string' ? input : input.url, location.origin); if(url.pathname.startsWith('/v1/videos/')) return new Response(Uint8Array.from(atob(data), c => c.charCodeAt(0)), {headers:{'Content-Type':'image/png'}}); return previous(input, init); }; })();''')
            page.goto(url)
            page.wait_for_function('!!window.__settingsSmoke', timeout=120000)
            page.evaluate('''shelf => {
                const f = window.__dataFixture;
                f.rows = ['Research summary', 'Project notes', 'Weekend ideas'].map((title, i) => ({
                    id:`evidence-${i}`, title, modelType:'base', modelId:'test', createdAt:1700000000000,
                    updatedAt:1700000000000, projectId:i<2?'research':null, archived:shelf==='chats'}));
                for (const kind of ['images','videos','audio']) f.media[kind] = ['Forest at sunrise','Ocean waves','City lights'].map((prompt,i)=>({
                    id:`media-${i}`, prompt, url:`/api/inference/${kind==='videos'?'video':kind}/gallery/media-${i}/content`, archived:true,
                    created_at:kind==='images'?1700000000:'2023-11-14T22:13:20Z'}));
                document.documentElement.classList.remove('dark');
                if (shelf==='data'||shelf==='manage') window.__settingsSmoke.open('data');
                else window.__settingsSmoke.openArchived(shelf);
            }''', shelf)
            dialog=page.get_by_role('dialog')
            expect(dialog).to_be_visible()
            if shelf in ['data','manage']:
                row=page.locator('[data-settings-label="Manage chats"]')
                expect(row).to_be_visible()
                if shelf=='manage': row.get_by_role('button',name='Manage',exact=True).click()
            if shelf in ['manage','chats']: expect(page.get_by_role('button',name='Research summary',exact=True)).to_be_visible()
            if shelf in ['images','videos','audio']: expect(page.get_by_text('Forest at sunrise',exact=True)).to_be_visible()
            page.evaluate('document.fonts.ready')
            page.wait_for_timeout(300)
            dialog.screenshot(path=str(output/f'{shelf}.png'), animations='disabled')
            results[shelf]={'searchboxes':dialog.get_by_role('searchbox').count(),'text':dialog.inner_text()}
            context.close()
        results['browser']=browser.version
        browser.close()
finally:
    robust.stop_process(server)
(output/('video-facts.json' if os.environ.get('UI_SHELVES') else 'facts.json')).write_text(json.dumps(results,indent=2))
print(json.dumps({'label':label,'browser':results['browser'],'surfaces':6}))
