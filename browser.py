import re
import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright
root=Path(__file__).resolve().parent
async def main():
    facts=[]
    async with async_playwright() as p:
        for engine in ['chrome','edge','firefox']:
            browser=await p.chromium.launch(executable_path=str(root/'playwright/brands/opt'/('google/chrome/chrome' if engine=='chrome' else 'microsoft/msedge/msedge')),headless=True,args=['--no-sandbox']) if engine in ('chrome','edge') else await p.firefox.launch(headless=True)
            for side,port in [('base',19197),('head',19297)]:
                ctx=await browser.new_context(viewport={'width':1366,'height':900},locale='en-US',reduced_motion='reduce',color_scheme='light')
                page=await ctx.new_page(); errors=[]
                page.on('pageerror',lambda e: errors.append(str(e)))
                async def api(route):
                    url=route.request.url
                    body={'config':{},'status':'running'} if '/train/runs/' in url else {'gpus':[]}
                    await route.fulfill(json=body)
                await page.route(re.compile(r'^http://127\.0\.0\.1:[0-9]+/api/'),api)
                await page.goto(f'http://127.0.0.1:{port}/review-scene.html',wait_until='networkidle')
                await page.wait_for_function('window.review !== undefined')
                for scenario in ['resumed','fresh','legacy','initial','complete']:
                    rawpath=root/'artifacts'/f'{side}-{scenario}.sse'
                    raw=rawpath.read_text() if rawpath.exists() else ''
                    if not raw: continue
                    state=await page.evaluate('(raw)=>window.review.ingest(raw)',raw)
                    card=page.locator('[data-tour="studio-training-progress"]')
                    await card.wait_for()
                    await page.wait_for_timeout(200)
                    text=await card.inner_text()
                    if scenario=='resumed':
                        assert ('0.17' if side=='head' else '15.17') in text,text
                        assert ('9m 0s' if side=='head' else '5s') in text,text
                    if scenario=='fresh': assert '1.67' in text and '9m 0s' in text,text
                    await card.screenshot(path=str(root/'artifacts'/f'{engine}-{side}-{scenario}.png'))
                    facts.append({'engine':engine,'version':browser.version,'side':side,'scenario':scenario,'state':state,'text':text,'errors':list(errors)})
                    assert not errors,errors
                await page.set_viewport_size({'width':390,'height':844})
                raw=(root/'artifacts'/f'{side}-resumed.sse').read_text()
                await page.evaluate('(raw)=>window.review.ingest(raw)',raw)
                await page.wait_for_timeout(200)
                assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'horizontal overflow'
                await page.screenshot(path=str(root/'artifacts'/f'{engine}-{side}-mobile.png'),full_page=True)
                await ctx.close()
            await browser.close()
    (root/'artifacts/browser-facts.json').write_text(json.dumps(facts,indent=2))
    print(f'PASS {len(facts)} desktop scenarios plus six mobile views')
asyncio.run(main())
