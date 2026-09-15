import asyncio, json
from pathlib import Path
from pr_ui_scenes._common import api_get,api_post
from studio_test_kit.auth import seed_init_script
from studio_test_kit.ui import open_chat,send_prompt
async def _export(page, item_label: str, dest: Path) -> str:
    await page.get_by_role("button", name="Tools and attachments").first.click()
    sub = page.get_by_role("menuitem", name="Export chat").first
    try:
        await sub.wait_for(state="visible", timeout=4_000)
    except Exception:
        more = page.get_by_role("menuitem", name="More").first
        await more.hover()
        try:
            await sub.wait_for(state="visible", timeout=4_000)
        except Exception:
            await more.click()
            await sub.wait_for(state="visible", timeout=10_000)
    await sub.hover()
    await sub.click()
    item = page.get_by_role("menuitem", name=item_label, exact=True).first
    await item.wait_for(state="visible", timeout=15_000)
    async with page.expect_download(timeout=30_000) as caught:
        await item.click()
    download = await caught.value
    await download.save_as(str(dest))
    return dest.read_text()




async def drive(session,out_dir,label,**kwargs):
    out=Path(out_dir)
    api_post(session,'/api/providers/',{'provider_type':'custom','display_name':'Review GPU','base_url':'http://127.0.0.1:18941/v1','models':['review-tiny'],'available_models':['review-tiny']})
    facts={'label':label,'model':'Ling-3.0-tiny-Q6_K','provider':'local llama.cpp CUDA'}
    async with open_chat(session.base_url,init_scripts=[seed_init_script(session,[])],viewport=(1280,900)) as sp:
        page=sp.page
        await page.get_by_role('button',name='Select model').first.click(timeout=60000)
        await page.get_by_role('tab',name='Connected').click()
        await page.get_by_text('review-tiny',exact=True).first.click()
        await send_prompt(sp,'Name one fruit. Answer with one word only.')
        async def finished(expected):
            await page.get_by_role('button',name='Refresh',exact=True).last.wait_for(state='visible',timeout=120000)
            for _ in range(120):
                threads=api_get(session,'/api/chat/threads')['threads']
                if threads:
                    rows=api_get(session,f"/api/chat/threads/{threads[0]['id']}/messages")['messages']
                    if len(rows)==expected and rows[-1]['content']:
                        await page.wait_for_timeout(500)
                        return
                await page.wait_for_timeout(500)
            raise AssertionError(f'expected {expected} saved messages')
        await finished(2)
        facts['first_reply']=await page.locator('[data-role="assistant"]').last.inner_text()
        raw=await _export(page,'ShareGPT JSONL',out/'first.jsonl')
        assert len(json.loads(raw)['conversations'])==2,raw
        await page.locator('[data-role="assistant"]').last.hover()
        entered=asyncio.Event()
        release=asyncio.Event()
        async def pause_generation(route):
            entered.set()
            await release.wait()
            await route.continue_()
        await page.route('**/v1/chat/completions',pause_generation)
        await page.get_by_role('button',name='Refresh',exact=True).last.click()
        await asyncio.wait_for(entered.wait(),15)
        try:
            raw=await _export(page,'ShareGPT JSONL',out/'during-regeneration.jsonl')
            facts['during_regeneration_export_turns']=len(json.loads(raw)['conversations'])
            assert facts['during_regeneration_export_turns']==(2 if label=='BEFORE' else 1),raw
        finally:
            release.set()
        await finished(3)
        await page.unroute('**/v1/chat/completions',pause_generation)
        raw=await _export(page,'ShareGPT JSONL',out/'regenerated.jsonl')
        conv=json.loads(raw)['conversations']
        facts['regenerated_export_turns']=len(conv)
        assert len(conv)==(3 if label=='BEFORE' else 2),raw
        await page.locator('[data-role="assistant"]').last.hover()
        await page.locator('.aui-branch-picker-root').last.get_by_role('button',name='Previous').click()
        raw=await _export(page,'ShareGPT JSONL',out/'selected-first.jsonl')
        conv=json.loads(raw)['conversations']
        facts['picked_export_turns']=len(conv)
        assert len(conv)==(3 if label=='BEFORE' else 2),raw
        await page.locator('[data-role="user"]').first.hover()
        await page.locator('[data-role="user"]').first.get_by_role('button',name='Edit',exact=True).click()
        await page.locator('.aui-edit-composer-input').fill('Name one animal. Answer with one word only.')
        await page.get_by_role('button',name='Update',exact=True).click()
        await finished(5)
        raw=await _export(page,'ShareGPT JSONL',out/'edited.jsonl')
        conv=json.loads(raw)['conversations']
        facts['edited_export_turns']=len(conv)
        facts['edited_reply']=await page.locator('[data-role="assistant"]').last.inner_text()
        assert len(conv)==(5 if label=='BEFORE' else 2),raw
        if label!='BEFORE':assert conv[0]['value']=='Name one animal. Answer with one word only.',raw
        csv=await _export(page,'CSV',out/'all-branches.csv')
        assert 'Name one fruit.' in csv and 'Name one animal.' in csv
        facts['csv_preserves_both_prompts']=True
        await page.screenshot(path=str(out/'gpu-edited.png'))
    return [out/'gpu-edited.png'],facts
