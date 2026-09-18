import assert from 'node:assert/strict';
const root = `/task/${process.argv[2]}/studio/frontend/`;
const {TEXT_ATTACHMENT_ACCEPT, isTextAttachmentName, readTextAttachment} = await import(root+'src/features/chat/text-attachment-accept.ts');
const {isComposerAttachmentName, classifyDropPaths} = await import(root+'src/features/native-intents/drop-paths.ts');
const text = 'private _unit = player;\n_unit sideChat "Hello 世界";\n';
const results=[];
for (const name of ['mission.sqf','MISSION.SQF','init.Player.sQf']) {
  const paths = [`/tmp/arma scripts/${name}`, `C:\\Arma scripts\\${name}`];
  for (const path of paths) {
    results.push({path,text:isTextAttachmentName(path),composer:isComposerAttachmentName(path),drop:classifyDropPaths([path]).kind});
  }
  for (const type of ['', 'application/octet-stream','text/plain']) assert.equal(await readTextAttachment(new File([text],name,{type})),text);
}
console.log(JSON.stringify({picker:TEXT_ATTACHMENT_ACCEPT.split(',').includes('.sqf'),results,decoding:'9/9'},null,2));
assert.ok(TEXT_ATTACHMENT_ACCEPT.split(',').includes('.sqf'),'SQF must be included in picker accept');
for(const row of results){assert.equal(row.text,true);assert.equal(row.composer,true);assert.equal(row.drop,'docs');}
assert.equal(classifyDropPaths(['/tmp/archive.exe']).kind,'unsupported');
assert.equal(classifyDropPaths(['/tmp/readme.txt']).kind,'docs');
