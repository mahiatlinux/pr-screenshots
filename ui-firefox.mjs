import {chromium,firefox} from './tools/playwright/node_modules/playwright/index.mjs';
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
const root=process.cwd();
const browser=await firefox.launch({executablePath:path.join(root,'tools/firefox/firefox/firefox'),headless:true});
const facts={browser:browser.version(),viewport:{width:1400,height:1000},cases:fs.existsSync('artifacts/ui-firefox-facts.json')?JSON.parse(fs.readFileSync('artifacts/ui-firefox-facts.json','utf8')).cases.filter(c=>!process.argv.slice(2).includes(c.side)):[]};
const sides=process.argv.slice(2).length?process.argv.slice(2):['base','head','fix'];
for(const side of sides){
 const auth=JSON.parse(fs.readFileSync(`home-${side}/ui_auth.json`,'utf8'));
 for(const [slug,model,levels]of [
  ['deepseek','deepseek/deepseek-v4-pro',['None','High','Extra High']],
  ['gemini','~google/gemini-pro-latest',['Low','Medium','High']],
  ['gpt51','openai/gpt-5.1',['None','Low','Medium','High']],
  ['router','openrouter/free',[]],
  ['flash','google/gemini-3.5-flash',['Minimal','Low','Medium','High']],
 ]){
  if(process.env.SCENE_IMAGES_ONLY && !['deepseek','gpt51'].includes(slug))continue;
  const context=await browser.newContext({viewport:facts.viewport,locale:'en-US',colorScheme:'light',reducedMotion:'reduce'});
  await context.addInitScript(seed=>{for(const[k,v]of Object.entries(seed))localStorage.setItem(k,v);},{unsloth_auth_token:auth.access_token,unsloth_refresh_token:auth.refresh_token,unsloth_chat_connections_enabled:'true',unsloth_chat_last_external_checkpoint:`external::${auth.provider}::${encodeURIComponent(model)}`});
  const page=await context.newPage();
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(`${auth.url}/chat`,{waitUntil:'domcontentloaded'});
  await page.locator('textarea').first().waitFor({timeout:60000});
  await page.waitForFunction(m=>document.querySelector('.unsloth-model-selector-trigger')?.textContent.includes(m),model);
  if(side!=='base')await page.waitForFunction(()=>!!localStorage.getItem('unsloth_chat_provider_model_catalog'));
  await page.waitForTimeout(700);
  const record={side,model,errors};
  const think=page.locator('button.unsloth-thinking-pill').first();
  record.thinking=await think.innerText();record.aria=await think.getAttribute('aria-label');record.disabled=await think.isDisabled();
  const expectLadder=side!=='base'&&slug!=='router'&&(slug!=='gemini'||side==='fix');
  if(expectLadder){
   await think.click();
   await page.getByRole('menuitem').first().waitFor();
   record.menu=await page.getByRole('menuitem').allTextContents();
   for(const level of levels)assert(record.menu.some(text=>text.trim()===level),`${side} ${model}: missing ${level} in ${record.menu}`);
   if(['gemini','flash'].includes(slug))assert(!record.menu.some(text=>['Off','None'].includes(text.trim())));
  }else assert(!record.aria.startsWith('Reasoning effort:'),`${side} ${model} unexpectedly has ladder`);
  if(['deepseek','gemini','flash'].includes(slug))await page.screenshot({path:`artifacts/firefox-${side}-${slug}-reasoning.png`});
  if(expectLadder){
   const target=levels.at(-1);
   await page.getByRole('menuitem',{name:target,exact:true}).click();
   record.selected=await think.getAttribute('aria-label');
   assert(record.selected.includes(target==='Extra High'?'xhigh':target.toLowerCase()));
  }
  if(slug==='deepseek'||slug==='gpt51'){
   const picker=page.waitForEvent('filechooser');
   await page.getByRole('button',{name:'Tools and attachments',exact:true}).click();
   await page.getByRole('menuitem',{name:'Add photos & files',exact:true}).click();
   await (await picker).setFiles({name:'capability-check.png',mimeType:'image/png',buffer:fs.readFileSync('artifacts/test-image.png')});
   await page.waitForTimeout(600);
   const body=await page.locator('body').innerText();
   record.attachments=await page.locator('img').evaluateAll(es=>es.filter(e=>e.alt==='capability-check.png').map(e=>({width:e.naturalWidth,height:e.naturalHeight})));
   record.imageRejected=/does not support image|doesn't support image|does not accept image|cannot accept image|text-only/i.test(body);
   record.toasts=await page.locator('[data-sonner-toast]').allTextContents();
   if(slug==='deepseek')assert.equal(record.imageRejected,side!=='base',`${side}: ${record.toasts}`);
   else assert.equal(record.imageRejected,false);
   if(!record.imageRejected)assert(record.attachments.some(a=>a.width===64&&a.height===64),JSON.stringify(record.attachments));
   if(slug==='deepseek')await page.screenshot({path:`artifacts/firefox-${side}-image.png`});
  }
  if(slug==='deepseek'){
   const trigger=page.getByRole('button',{name:'Open run settings',exact:true});
   if(await trigger.count())await trigger.click();
   const field=page.getByLabel('Max Tokens',{exact:true}).first();
   await field.scrollIntoViewIfNeeded();await field.fill('999999');await field.press('Enter');await page.waitForTimeout(500);
   record.maxTokens=await field.inputValue();
   await page.screenshot({path:`artifacts/firefox-${side}-tokens.png`});
  }
  facts.cases.push(record);console.log(JSON.stringify(record));
  fs.writeFileSync('artifacts/ui-firefox-facts.json',JSON.stringify(facts,null,2));
  await context.close();
 }
}
await browser.close();
