import assert from 'node:assert/strict';
import test from 'node:test';
import {sessionEtaSeconds,sessionStepsPerSecond} from '../src/features/studio/sections/progress-section-lib.ts';
import {consumeTrainingProgressStream} from '../src/features/training/lib/training-sse-stream.ts';
import {useTrainingRuntimeStore as store} from '../src/features/training/stores/training-runtime-store.ts';
test('session arithmetic matches independently calculated windows over 10,000 cases',()=>{
 let seed=11297;
 const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/2**32;};
 for(let i=0;i<10000;i++){
  const baseline=Math.floor(rand()*10000), completed=1+Math.floor(rand()*1000), remaining=Math.floor(rand()*1000), elapsed=1+Math.floor(rand()*10000);
  assert.equal(sessionEtaSeconds(baseline+completed,baseline,baseline+completed+remaining,elapsed),Math.round(elapsed*remaining/completed));
  assert.equal(sessionStepsPerSecond(baseline+completed,baseline,elapsed),completed/elapsed);
 }
});
test('old, null, zero and resumed fields pass the real parser and store',async()=>{
 store.getState().resetRuntime();store.getState().setStartPending('review','Starting');
 async function event(step:number,extra={}){
  const p={job_id:'review',step,total_steps:1000,loss:.5,learning_rate:.001,progress_percent:step/10,epoch:1,elapsed_seconds:60,eta_seconds:null,grad_norm:null,num_tokens:null,eval_loss:null,...extra};
  const raw=`event: progress\nid: ${step}\ndata: ${JSON.stringify(p)}\n\n`;
  await consumeTrainingProgressStream({body:new Response(raw).body!,signal:new AbortController().signal,onEvent:({payload,id})=>store.getState().applyProgress(payload,id??undefined)});
 }
 await event(901,{session_start_step:900});assert.equal(store.getState().sessionStartStep,900);
 await event(902);assert.equal(store.getState().sessionStartStep,900);
 await event(903,{session_start_step:null});assert.equal(store.getState().sessionStartStep,900);
 await event(904,{session_start_step:0});assert.equal(store.getState().sessionStartStep,0);
 await event(905,{session_start_step:900});store.getState().resetRuntime();assert.equal(store.getState().sessionStartStep,0);
 store.getState().setStartPending('review','Starting');await event(1);assert.equal(store.getState().sessionStartStep,0);
});
