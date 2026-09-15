import hashlib
import json
import os
import secrets
import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright, expect
from ui_common import studio_session

ROOT = Path('/task/artifacts')
EXPECT = 'The base shows [Image blocked: Plot]; the head displays the red line plot from the same relative filename.'
reports = []
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    for side, port in [('base', 18755), ('head', 18756)]:
        session = studio_session(f'http://127.0.0.1:{port}', Path(f'/task/studio-{side}-e2e'), secrets.token_urlsafe(24))
        context = browser.new_context(viewport={'width': 1280, 'height': 900}, device_scale_factor=1, color_scheme='light', reduced_motion='reduce')
        context.add_init_script('localStorage.setItem("unsloth_auth_token", '+json.dumps(session.access_token)+'); localStorage.setItem("unsloth_auth_refresh_token", '+json.dumps(session.refresh_token)+'); localStorage.setItem("unsloth_auth_must_change_password", "false");')
        headers = {'Authorization': 'Bearer '+session.access_token}
        api = context.request
        thread = {'id':'review-plot', 'title':'Python line plot', 'modelType':'base', 'createdAt':1789440000000, 'updatedAt':1789440000000}
        response = api.post(session.base_url+'/api/chat/threads', data=thread, headers=headers)
        assert response.ok, response.text()
        messages = [
            {'id':'review-user', 'role':'user', 'parentId':None, 'content':[{'type':'text', 'text':'Plot y = -x/3 + 2 in red, with x from -10 to 10 and y from -5 to 5.'}]},
            {'id':'review-answer', 'role':'assistant', 'parentId':'review-user', 'content':[{'type':'text', 'text':'Here is the requested plot:\n\n![Plot](line_plot.png)'}]},
        ]
        for index, message in enumerate(messages):
            message.update(threadId='review-plot', createdAt=1789440000000+index)
            response = api.put(session.base_url+'/api/chat/threads/review-plot/messages/'+message['id'], data=message, headers=headers)
            assert response.ok, response.text()
        seed = subprocess.run([f'/task/{side}/.venv/bin/python', str(ROOT/'seed_plot.py'), side], text=True, capture_output=True)
        (ROOT/f'{side}-python-tool.log').write_text(seed.stdout+seed.stderr)
        assert seed.returncode == 0, seed.stdout+seed.stderr
        route = session.base_url+'/api/inference/sandbox/review-plot/line_plot.png'
        response = api.get(route, headers=headers)
        assert response.status == 200, response.text()
        source_bytes = response.body()
        assert api.get(route).status == 401
        page = context.new_page()
        errors, requests = [], []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('response', lambda res: requests.append({'path':res.url.split(str(port))[-1], 'status':res.status}) if '/api/inference/sandbox/' in res.url else None)
        page.goto(session.base_url+'/chat?thread=review-plot', wait_until='networkidle')
        page.screenshot(path=str(ROOT/f'{side}-initial.png'))
        (ROOT/f'{side}-body.txt').write_text(page.locator('body').inner_text())
        if side == 'base':
            expect(page.get_by_text('[Image blocked: Plot]', exact=False)).to_be_visible(timeout=30000)
            dimensions = None
        else:
            img = page.locator('img[data-streamdown="image"][alt="Plot"]')
            expect(img).to_be_visible(timeout=30000)
            expect(img).to_have_js_property('naturalWidth', 600)
            dimensions = [600,320]
            img.hover()
            with page.expect_download() as event:
                page.get_by_role('button', name='Download image').click()
            download = event.value
            assert download.suggested_filename == 'line_plot.png'
            destination = ROOT/'downloaded-line_plot.png'
            download.save_as(destination)
            assert destination.read_bytes() == source_bytes
            assert len(requests) == 1, requests
        page.screenshot(path=str(ROOT/f'{side}-chat.png'))
        reports.append({'side':side,'expected':EXPECT,'browser':browser.version,'dimensions':dimensions,'sandbox_responses':requests,'download_identical':side=='head','page_errors':errors,'plot_sha256':hashlib.sha256(source_bytes).hexdigest()})
        assert not errors, errors
        context.close()
    browser.close()
(ROOT/'ui-evidence.json').write_text(json.dumps(reports,indent=2))
assert reports[0]['plot_sha256']==reports[1]['plot_sha256']
print(json.dumps(reports))
