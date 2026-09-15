import sys,json
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'tests/studio'))
from _playwright_robust import start_vite,stop_process,wait_for_smoke_page
from playwright.sync_api import sync_playwright
server=start_vite(5487)
try:
 wait_for_smoke_page('http://127.0.0.1:5487/smoke-prompt-queue-actions.html','/smoke-prompt-queue-actions-main.tsx',proc=server)
 with sync_playwright() as p:
  browser=p.chromium.launch()
  page=browser.new_page()
  results=[]
  for label in ['Steer with queued prompt 1','Remove queued prompt 1','Reorder queued prompt 1 of 3','More options for queued prompt 1']:
   page.goto('http://127.0.0.1:5487/smoke-prompt-queue-actions.html')
   button=page.get_by_role('button',name=label,exact=True)
   button.wait_for(timeout=60000)
   page.evaluate('''() => {
     const main=document.querySelector('main');
     const form=document.createElement('form');main.before(form);form.append(main);
     const draft=document.createElement('textarea');draft.id='draft';draft.value='Unsent draft';form.prepend(draft);
     window.submits=0;form.addEventListener('submit',e=>{e.preventDefault();window.submits++;draft.value='';});
   }''')
   button_type=button.evaluate('el=>el.type')
   button.click()
   results.append({'action':label,'type':button_type,**page.evaluate('({submits:window.submits,draft:document.querySelector("#draft").value})')})
  print(json.dumps(results,indent=2),flush=True)
  browser.close()
finally:stop_process(server)
