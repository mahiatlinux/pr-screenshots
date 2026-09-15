import asyncio, json, os, socket, subprocess, sys, time, urllib.request
from contextlib import asynccontextmanager
from pathlib import Path
from playwright.async_api import async_playwright
from studio_test_kit.ui import StudioPage
from pr_ui_scenes._common import studio_session
import gpu_scene as scene
root=Path(__file__).resolve().parent.parent
side=sys.argv[1]
engine=sys.argv[2] if len(sys.argv)>2 else 'chromium'
out=root/'artifacts'/f'gpu-{side}-{engine}'
out.mkdir(exist_ok=True)
os.environ['UNSLOTH_STUDIO_HOME']=str(root/f'home-{side}-gpu-{time.time_ns()}')
@asynccontextmanager
async def open_chat(base_url, init_scripts, viewport, **kwargs):
    async with async_playwright() as p:
        browser=await getattr(p,engine).launch(headless=True, args=['--no-sandbox'] if engine=='chromium' else [])
        context=await browser.new_context(viewport={'width':viewport[0],'height':viewport[1]},locale='en-US',color_scheme='light',reduced_motion='reduce')
        for script in init_scripts:await context.add_init_script(script)
        page=await context.new_page()
        await page.goto(base_url+'/chat',wait_until='domcontentloaded')
        try:yield StudioPage(page=page,context=context,base_url=base_url)
        finally:
            await page.screenshot(path=str(out/'unannotated.png'))
            (out/'page.txt').write_text(await page.locator('body').inner_text())
            (out/'browser.json').write_text(json.dumps({'version':browser.version,'engine':engine,'viewport':viewport}))
            await context.close()
            await browser.close()
scene.open_chat=open_chat
# expected: the selected first reply is the only exported assistant turn on head.
async def capture_plain(page,label,picker,sharegpt,training):
    await page.screenshot(path=str(out/'chat.png'))
    (out/'download-summary.json').write_text(json.dumps({'sharegpt':sharegpt,'training':training},indent=2))
scene._pin_panel=capture_plain
with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
with (out/'studio.log').open('w') as log:
    process=subprocess.Popen([sys.executable,str(root/'artifacts/launch-studio.py'),str(port)],stdout=log,stderr=subprocess.STDOUT)
try:
    for i in range(90):
        try:
            urllib.request.urlopen(f'http://127.0.0.1:{port}/healthz',timeout=1);break
        except Exception:time.sleep(1)
    else:raise RuntimeError('startup timeout')
    session=studio_session(f'http://127.0.0.1:{port}',Path(os.environ['UNSLOTH_STUDIO_HOME']),'<generated local test password>')
    shots,facts=asyncio.run(scene.drive(session,out,'BEFORE' if side=='base' else 'AFTER'))
    (out/'facts.json').write_text(json.dumps(facts,indent=2))
    print(json.dumps(facts,indent=2))
finally:
    process.terminate()
    try:process.wait(timeout=15)
    except subprocess.TimeoutExpired:process.kill();process.wait()
