import asyncio,json,pathlib,httpx,secrets
from playwright.async_api import async_playwright
root=pathlib.Path(__file__).resolve().parent
row={'context': 'The River Archive records that Mira founded the observatory in 1842. It stands on the eastern hill above the town. '*6,'question':'Who founded the observatory?','answer':'Mira founded the observatory.'}
async def main():
 results={'expected_visible_difference':'context User to System; question System to User; answer remains Assistant','ui_fixture':'chat_only capability overridden to expose the dataset UI; upload and format responses are live','browsers':{}}
 async with async_playwright() as p:
  browser_name=__import__('sys').argv[1] if len(__import__('sys').argv)>1 else 'chromium'
  paths={'chrome':root/'branded/chrome/opt/google/chrome/chrome','edge':root/'branded/edge/opt/microsoft/msedge/msedge'}
  launch={} if browser_name=='firefox' else {'args':['--no-sandbox']}
  if browser_name in paths: launch['executable_path']=str(paths[browser_name])
  browser=await (p.firefox if browser_name=='firefox' else p.chromium).launch(**launch)
  results['browsers'][browser_name]=browser.version
  for side,port in [('base',19391),('fix',19392)]:
   url=f'http://127.0.0.1:{port}'
   client=httpx.Client(base_url=url,timeout=60)
   secret=root/side/'.ui-session.json'
   if secret.exists(): auth=json.loads(secret.read_text())
   else:
    pw=(root/side/'.studio-home/auth/.bootstrap_password').read_text().strip()
    response=client.post('/api/auth/login',json={'username':'unsloth','password':pw}); response.raise_for_status(); auth=response.json()
    response=client.post('/api/auth/change-password',headers={'Authorization':'Bearer '+auth['access_token']},json={'current_password':pw,'new_password':secrets.token_urlsafe(24)}); response.raise_for_status(); auth=response.json(); secret.write_text(json.dumps(auth)); secret.chmod(0o600)
   client.headers['Authorization']='Bearer '+auth['access_token']
   response=client.post('/api/hub/datasets/upload',files={'file':('observatory-qa.jsonl',json.dumps(row)+'\n','application/json')}); response.raise_for_status(); upload=response.json()
   data=client.post('/api/hub/datasets/check-format',json={'dataset_name':upload['stored_path']}); data.raise_for_status(); data=data.json()
   expected={'answer':'assistant','context':'user','question':'system'} if side=='base' else {'answer':'assistant','question':'user','context':'system'}
   assert data['suggested_mapping']==expected,data
   assert data['preview_samples']==[row]
   results[side]={'mapping':data['suggested_mapping'],'format':data['detected_format'],'total_rows':data['total_rows']}
   state={'datasetSource':'upload','uploadedFile':upload['stored_path'],'datasetFormat':'chatml','manualMapping':{},'datasetStreaming':False}
   context=await browser.new_context(viewport={'width':1440,'height':1000},locale='en-US',reduced_motion='reduce')
   await context.add_init_script('''const s = %s; if(!localStorage.getItem('unsloth_auth_token')) { localStorage.setItem('unsloth_auth_token',s.auth.access_token);localStorage.setItem('unsloth_auth_refresh_token',s.auth.refresh_token);localStorage.setItem('unsloth_training_config_v1',JSON.stringify({state:s.state,version:22})); }''' % json.dumps({'auth':auth,'state':state}))
   async def enable_dataset_ui(route):
    response=await route.fetch(); data=await response.json(); data['chat_only']=False; data['capabilities_pending']=False; await route.fulfill(response=response,json=data)
   await context.route('**/api/health',enable_dataset_ui)
   page=await context.new_page()
   await page.goto(url+'/studio',wait_until='networkidle',timeout=60000)


   try:
    await page.get_by_role('button',name='View dataset',exact=False).click(timeout=15000)
    dialog=page.get_by_role('dialog'); await dialog.wait_for(); await page.wait_for_timeout(1500)
    headers=dialog.locator('th')
    for name in ['context','question','answer']:
     header=headers.filter(has_text=name).first
     text=await header.get_by_role('combobox').inner_text()
     assert text.lower()==expected[name],(name,text,expected)
    card=dialog.get_by_text('Heuristic-detected mapping',exact=True).locator('xpath=../../..')
    box=await card.bounding_box(); table=await dialog.locator('table').bounding_box()
    await page.screenshot(path=str(root/'artifacts'/f'final-{browser_name}-{side}-mapping.png'),clip={'x':box['x'],'y':box['y'],'width':box['width'],'height':table['y']+table['height']-box['y']})
    await page.reload(wait_until='networkidle'); await page.get_by_role('button',name='View dataset',exact=False).click()
    await page.get_by_role('dialog').wait_for()
    for name in ['context','question','answer']:
     actual=await page.get_by_role('dialog').locator('th').filter(has_text=name).first.get_by_role('combobox').inner_text(); assert actual.lower()==expected[name]
    results[side]['refresh_preserves_mapping']=True
    custom={'context':'user' if expected['context']=='system' else 'system','question':'system' if expected['question']=='user' else 'user'}
    for name,role in custom.items():
     await page.get_by_role('dialog').locator('th').filter(has_text=name).first.get_by_role('combobox').click()
     await page.get_by_role('option',name=role.title(),exact=True).click()
    await page.reload(wait_until='networkidle'); await page.get_by_role('button',name='View dataset',exact=False).click()
    for name,role in custom.items():
     actual=await page.get_by_role('dialog').locator('th').filter(has_text=name).first.get_by_role('combobox').inner_text(); assert actual.lower()==role
    results[side]['explicit_manual_mapping_survives_reload']=True
    print(side,expected,'refresh passed',flush=True)
   finally: await context.close()
  (root/f'artifacts/ui-facts-final-{browser_name}.json').write_text(json.dumps(results,indent=2)); await browser.close()
asyncio.run(main())
