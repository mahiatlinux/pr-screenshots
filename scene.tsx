import React from 'react';
import {createRoot} from 'react-dom/client';
import {createRootRoute, createRouter, RouterProvider} from '@tanstack/react-router';
import {LiveTrainingView} from './src/features/studio/live-training-view';
import {useTrainingRuntimeStore} from './src/features/training/stores/training-runtime-store';
import {consumeTrainingProgressStream} from './src/features/training/lib/training-sse-stream';
import './src/index.css';
const store=useTrainingRuntimeStore;
window.review = {
  async ingest(raw: string) {
    store.getState().resetRuntime();
    store.getState().setStartPending('job-1','Starting');
    store.setState({message:'Training in progress...',phase:'training',isStarting:false,isTrainingRunning:true,firstStepReceived:true,startModelName:'Resume verification',startProjectName:'Checkpoint 900'});
    const body=new Response(raw).body!;
    await consumeTrainingProgressStream({body,signal:new AbortController().signal,onEvent:({payload,id})=>store.getState().applyProgress(payload,id??undefined)});
    return {step:store.getState().currentStep,baseline:store.getState().sessionStartStep,eta:store.getState().etaSeconds};
  },
  reset(){store.getState().resetRuntime();return store.getState().sessionStartStep;}
};
const root=createRootRoute({component:()=> <main style={{padding:24,maxWidth:1200,margin:'auto'}}><LiveTrainingView/></main>});
const router=createRouter({routeTree:root});
createRoot(document.getElementById('root')!).render(<RouterProvider router={router}/>);
