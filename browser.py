import asyncio,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
side,engine=sys.argv[1:3]
port=19300 if side=='head' else 19301
base=f'http://127.0.0.1:{port}'
async def run():
 async with async_playwright() as p:
  browser_type=getattr(p,engine if engine in ['chromium','firefox'] else 'chromium')
  extra={} if engine in ['chromium','firefox'] else {'executable_path':'/task/browsers/chrome/opt/google/chrome/chrome' if engine=='chrome' else '/task/browsers/edge/opt/microsoft/msedge/msedge'}
  browser=await browser_type.launch(headless=True,args=['--no-sandbox'] if engine!='firefox' else [],**extra)
  context=await browser.new_context(viewport={'width':1440,'height':1000},locale='en-US',color_scheme='light',reduced_motion='reduce')
  page=await context.new_page()
  try:
   resp=await context.request.post(base+'/api/auth/login',data={'username':'unsloth','password':Path('/task/homes/'+side+'/test-password').read_text()})
   data=await resp.json(); assert resp.ok, data
   await page.goto(base+'/login')
   await page.evaluate('(t)=>localStorage.setItem("unsloth_auth_token",t)',data['access_token'])
   await page.goto(base+'/data-recipes')
   await page.wait_for_timeout(1500)
   await page.get_by_role('button',name='New Recipe',exact=True).click()
   await page.get_by_role('menuitem',name='Start Empty').click()
   await page.wait_for_timeout(1000)
   await page.get_by_role('button',name='Paste recipe JSON').click()
   recipe={'recipe':{'seed_config':{'source':{'seed_type':'hf','path':'datasets/lhoestq/demo1/data/train.csv','endpoint':None}},'columns':[{'column_type':'expression','name':'result','expr':'verified'}]}}
   await page.get_by_role('textbox',name='Recipe JSON',exact=True).fill(json.dumps(recipe))
   await page.get_by_role('button',name='Import recipe',exact=True).click()
   await page.get_by_role('button',name='Run',exact=True).click()
   async with page.expect_response(lambda r:r.url.endswith('/validate')) as result:
    await page.get_by_role('button',name='Check recipe',exact=True).click()
   response=await result.value
   result=await response.json()
   sent=response.request.post_data_json
   assert sent['recipe']['seed_config']['source']['endpoint'] is None
   assert result['valid'] == (side=='head'), result
   expected='Ready to run' if side=='head' else 'Fix these issues first'
   await page.get_by_text(expected,exact=True).wait_for()
   await page.screenshot(path=f'/task/artifacts/{side}-{engine}.png')
   await page.get_by_role('dialog').screenshot(path=f'/task/artifacts/{side}-{engine}-dialog.png')
   facts={'side':side,'engine':engine,'version':browser.version,'viewport':[1440,1000],'submitted_endpoint':None,'http_status':response.status,'response':result,'visible':expected}
   Path(f'/task/artifacts/{side}-{engine}.json').write_text(json.dumps(facts,indent=2))
   print(json.dumps(facts))
   if side=='head' and engine=='chromium':
    await page.locator('#run-rows').fill('2')
    await page.locator('#run-rows').press('Tab')
    async with page.expect_response(lambda r:r.request.method=='POST' and r.url.endswith('/jobs')) as job:
     await page.get_by_role('button',name='Start test run',exact=True).click()
    jr=await (await job.value).json()
    print('JOB',json.dumps(jr))
    await page.wait_for_timeout(10000)
    print('FINAL', (await page.locator('body').inner_text())[-5000:])
    await page.screenshot(path='/task/artifacts/head-job.png')
  finally: await browser.close()
asyncio.run(run())
