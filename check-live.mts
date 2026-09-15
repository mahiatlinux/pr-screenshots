import {readFileSync} from 'node:fs';
import {pathToFileURL} from 'node:url';
const root=process.cwd();
const {registerBundlerResolver,installLocalStorageFake}=await import(pathToFileURL(root+'/studio/frontend/tests/helpers/kit.ts').href);
registerBundlerResolver();installLocalStorageFake();
const caps=await import(pathToFileURL(root+'/studio/frontend/src/features/chat/provider-capabilities.ts').href);
const vision=await import(pathToFileURL(root+'/studio/frontend/src/features/chat/external-providers.ts').href);
let catalog;
try {catalog=await import(pathToFileURL(root+'/studio/frontend/src/features/chat/model-catalog.ts').href);}catch{}
const data=JSON.parse(readFileSync('../artifacts/openrouter-models.json','utf8')).data;
catalog?.setProviderModelCatalog('openrouter',data.map(m=>({id:m.id,reasoning:m.reasoning,input_modalities:m.architecture?.input_modalities,max_output_tokens:m.top_provider?.max_completion_tokens})));
let mismatches=[];
for (const m of data){
 const c=caps.getExternalReasoningCapabilities('openrouter',m.id);
 if(m.reasoning?.supported_efforts?.length && c.reasoningStyle!=='reasoning_effort')mismatches.push({id:m.id,expected:m.reasoning.supported_efforts,actual:c});
}
for(const id of ['deepseek/deepseek-v4-pro','~google/gemini-pro-latest','openai/gpt-5.1','openrouter/free'])console.log(JSON.stringify({id,caps:caps.getExternalReasoningCapabilities('openrouter',id),vision:vision.providerModelSupportsVision('openrouter',id)}));
console.log(JSON.stringify({models:data.length,missingLadders:mismatches},null,2));
process.exitCode=mismatches.length?1:0;
