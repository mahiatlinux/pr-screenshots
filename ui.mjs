import {chromium} from '/task/playwright/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
console.log('Browser', await chromium.name());
const browser=await chromium.launch({headless:true,executablePath:'/task/playwright/browsers/chromium-1208/chrome-linux64/chrome',args:['--no-sandbox']});
for(const [side,port] of [['base',21174],['fix',21175]]){
 const context=await browser.newContext({viewport:{width:1280,height:900},colorScheme:'light'});
 await context.addInitScript(()=>{Math.random=()=>0.3;localStorage.setItem('unsloth_auth_token','ui-test');localStorage.setItem('unsloth_auth_must_change_password','false');});
 const page=await context.newPage();
 page.on('console',m=>{if(m.type()==='error')console.log(side,'CONSOLE',m.text())});
 page.on('pageerror',e=>console.log(side,'ERROR',e.message));
 await page.route('**/api/**',async route=>{
  const p=new URL(route.request().url()).pathname;
  if(!p.startsWith('/api/')) return route.continue();
  let body={models:[],providers:[],skills:[],knowledge_bases:[],downloads:[],projects:[],threads:[],active_downloads:[],hidden_models:[],entries:[],items:[],requests:[],active_requests:[],recent_requests:[]};
  if(p.startsWith('/api/providers/')) body=[];
  else if(p==='/api/health') body={device_type:'cpu',chat_only:true,version:'test'};
  else if(p.includes('/auth/status')) body={initialized:true,requires_password_change:false,full_access:true};
  else if(p.includes('/auth/me')) body={username:'review',account_id:'review',is_owner:true};
  else if(p.includes('/threads')) body={threads:[]};
  else if(p.includes('/projects')) body={projects:[]};
  else if(p.includes('/models')) body={models:[],default_models:[],loras:[]};
  else if(p.includes('/status')) body={status:'idle',model_loaded:false};
  console.log(side,p);
  await route.fulfill({json:body});
 });
 await page.goto(`http://127.0.0.1:${port}/chat`,{waitUntil:'domcontentloaded'});
 await page.waitForTimeout(7000);
 console.log(side,'TEXT', (await page.locator('body').innerText()).slice(0,5000));
 await page.locator('textarea').first().evaluate(el=>{const dt=new DataTransfer();dt.items.add(new File(['private _unit = player;\n_unit sideChat \"Hello Arma\";'], 'mission.sqf', {type:'application/octet-stream'}));el.dispatchEvent(new ClipboardEvent('paste',{clipboardData:dt,bubbles:true,cancelable:true}));});
 await page.waitForTimeout(1500);
 const chip=page.getByRole('button',{name:'Document attachment: mission.sqf',exact:true});
 const count=await chip.count();
 assert.equal(count, side==='fix'?1:0);
 if(side==='base') assert.equal(await page.getByText('Could not paste files.',{exact:true}).count(),1);
 else {await chip.hover();await page.waitForTimeout(600);}
 console.log(side, 'SQF_ATTACHMENTS',count);
 await fs.writeFile('/task/artifacts/'+side+'-facts.json',JSON.stringify({browser:browser.version(),side,sqfAttachmentCount:count,expected:side==='fix'?'mission.sqf accepted as document':'unsupported clipboard item rejected',fixture:'real frontend with mocked backend responses'},null,2));
 console.log(side,'AFTER',await page.locator('body').innerText());
 await page.screenshot({path:`/task/artifacts/${side}-initial.png`});
 if(side==='fix'){await chip.click();await page.waitForTimeout(500);assert.ok((await page.locator('body').innerText()).includes('Hello Arma'));await page.screenshot({path:'/task/artifacts/sqf-preview.png'});}
 await context.close();
}
await browser.close();
