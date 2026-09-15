import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

root = Path('/task/artifacts')
reports = []
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    for side, port in [('base',18755),('head',18756)]:
        token = subprocess.check_output([f'/task/{side}/.venv/bin/python',str(root/'mint_local_session.py'),side],text=True).strip()
        context = browser.new_context(viewport={'width':1280,'height':900},color_scheme='light',reduced_motion='reduce')
        context.add_init_script('localStorage.setItem("unsloth_auth_token", '+json.dumps(token)+'); window.cspViolations=[]; document.addEventListener("securitypolicyviolation", e=>window.cspViolations.push(e.effectiveDirective));')
        url = f'http://127.0.0.1:{port}'
        headers = {'Authorization':'Bearer '+token}
        endpoint = url+'/api/chat/threads/review-plot/messages/review-answer'
        original = context.request.get(endpoint,headers=headers).json()
        changed = dict(original)
        changed['content']=[{'type':'text','text':'Here is the requested plot:\n\n![Plot](/api/inference/sandbox/review-plot/line_plot.png)'}]
        assert context.request.put(endpoint,data=changed,headers=headers).ok
        csp=json.loads(Path(f'/task/{side}/studio/src-tauri/tauri.conf.json').read_text())['app']['security']['csp']
        def desktop_policy(route):
            response=route.fetch()
            route.fulfill(response=response,headers={**response.headers,'content-security-policy':csp})
        context.route('**/chat?thread=review-plot',desktop_policy)
        page=context.new_page()
        downloads=[]
        page.on('download',lambda item:downloads.append(item))
        page.goto(url+'/chat?thread=review-plot',wait_until='networkidle')
        img=page.locator('img[data-streamdown="image"][alt="Plot"]')
        expect(img).to_have_js_property('naturalWidth',600)
        img.hover()
        page.get_by_role('button',name='Download image').click()
        if side=='base':
            expect(page.get_by_text('Could not save file.',exact=True)).to_be_visible()
            assert not downloads
            assert 'connect-src' in page.evaluate('window.cspViolations')
        else:
            page.wait_for_timeout(500)
            assert len(downloads)==1
            destination=root/'desktop-download.png'
            downloads[0].save_as(destination)
            assert destination.read_bytes()==(root/'downloaded-line_plot.png').read_bytes()
            assert not page.evaluate('window.cspViolations')
        page.screenshot(path=str(root/f'{side}-desktop-download.png'))
        reports.append({'side':side,'downloads':len(downloads),'csp_violations':page.evaluate('window.cspViolations')})
        assert context.request.put(endpoint,data=original,headers=headers).ok
        context.close()
    browser.close()
(root/'download-ab.json').write_text(json.dumps(reports,indent=2))
print(json.dumps(reports))
