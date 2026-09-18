import { chromium, firefox, webkit } from 'playwright';
import { createServer } from 'node:http';
import { readFile, writeFile } from 'node:fs/promises';
import { join, extname } from 'node:path';
import assert from 'node:assert/strict';
const artifacts = '/task/artifacts';
const servers = [];
const urls = {};
for (const side of ['base','head','merge']) {
  const root = `/task/${side}/studio/frontend/review-dist`;
  const server = createServer(async (req,res) => {
    try {
      const pathname = new URL(req.url,'http://localhost').pathname;
      if (pathname.includes('..')) throw new Error();
      const bytes = await readFile(join(root,pathname));
      res.setHeader('Content-Type', {'.html':'text/html','.js':'text/javascript','.css':'text/css','.woff2':'font/woff2','.svg':'image/svg+xml'}[extname(pathname)] ?? 'application/octet-stream');
      res.end(bytes);
    } catch {res.writeHead(404);res.end();}
  });
  await new Promise(resolve => server.listen(0,'127.0.0.1',resolve));
  servers.push(server);
  urls[side] = `http://127.0.0.1:${server.address().port}/review-ui.html`;
}
const results=[];
try {
 for (const [engine,type] of Object.entries(process.env.REVIEW_ENGINE === "chromium" ? {chromium} : {firefox,webkit})) {
  let browser;
  try { browser=await type.launch({headless:true, ...(engine === "chromium" ? {channel:"chromium"} : {})}); } catch(error) {results.push({engine,launchFailure:String(error)});continue;}
  try {
   for (const side of ['base','head','merge']) {
    for (const width of [760,360]) {
     for (const locale of ['en','de','ar','es','fr','hi','it','ja','ko','pt-BR','ru','zh-CN']) {
      const context = await browser.newContext({viewport:{width,height:900},locale:'en-US',colorScheme:'light',reducedMotion:'reduce'});
      const page=await context.newPage();
      const errors=[];page.on('pageerror',e=>errors.push(String(e)));
      await page.goto(`${urls[side]}?locale=${locale}`);
      const banner=page.getByTestId('tauri-update-banner');
      await banner.waitFor();
      await page.waitForFunction(()=>window.expected);
      const expected=await page.evaluate(()=>window.expected);
      const settings=await page.getByTestId('settings-control').innerText();
      const bannerText=await banner.innerText();
      assert(settings.includes(expected),`${side} settings ${locale}`);
      assert.equal(bannerText.includes(expected),side!=='base',`${side} banner ${locale}`);
      assert(await page.getByTestId('tauri-update-install').isDisabled());
      assert.equal(await page.getByTestId('settings-control').getByRole('button').count(),0);
      assert.equal(await page.evaluate(()=>window.installs),0);
      const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
      assert(!overflow,`${side} ${locale} ${width} overflow`);
      const bounds=await banner.boundingBox();
      const buttonBounds=await page.getByTestId('tauri-update-install').boundingBox();
      assert(buttonBounds.y+buttonBounds.height <= bounds.y+bounds.height+1,`${side} clipped update button`);
      assert.deepEqual(errors,[]);
      if(engine==='chromium'&&['en','de','ar'].includes(locale)) {
       await page.waitForTimeout(400);
       await page.screenshot({path:`${artifacts}/${side}-${locale}-${width}.png`,fullPage:true});
      }
      results.push({engine,version:browser.version(),side,width,locale,expected,bannerText,settings,overflow,pass:true});
      await context.close();
     }
    }
    for(const manual of [false,true]) {
     const context=await browser.newContext({viewport:{width:760,height:900}});
     const page=await context.newPage();
     await page.goto(`${urls[side]}?external=false&manual=${manual}`);
     const button=page.getByTestId('tauri-update-install');
     await button.waitFor();
     assert(await button.isEnabled());await button.click();
     await page.getByTestId('settings-control').getByRole('button').click();
     assert.equal(await page.evaluate(()=>window.installs),2);
     if(manual) assert((await button.innerText()).includes('Open release page'));
     results.push({engine,side,owned:true,manual,callbacks:2,pass:true});
     await context.close();
    }
   }
  } finally {await browser.close();}
 }
 await writeFile(`${artifacts}/browser-results-${process.env.REVIEW_ENGINE ?? "other"}.json`,JSON.stringify(results,null,2));
 console.log(JSON.stringify({passed:results.filter(r=>r.pass).length,launchFailures:results.filter(r=>r.launchFailure)}));
} finally {for(const server of servers)server.close();}
