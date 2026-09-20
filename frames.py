import asyncio, json, sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
root=Path(__file__).resolve().parent
side=sys.argv[1]
sys.path.insert(0,str(root/side/'studio/backend'))
sys.path.insert(0,str(root/side/'studio/backend/tests'))
import test_training_progress_callback as cb
import test_training_progress_stream_nan as stream
facts=[]
for scenario,baseline,step,start in [('resumed',900,910,700),('resumed_setup',900,910,100),('fresh',0,100,700),('initial',900,900,100),('complete',900,1000,100)]:
    owner=cb._make_owner();owner._update_progress(total_steps=1000);owner.training_start_time=start
    q=cb._FakeQueue();owner.add_progress_callback(cb._create_trainer_progress_callback(q))
    callback=owner._create_progress_callback()
    state=SimpleNamespace(global_step=baseline,epoch=.9,num_input_tokens_seen=100)
    control=SimpleNamespace(should_training_stop=False)
    with patch('time.time',return_value=700): callback.on_train_begin(None,state,control)
    state.global_step=step
    with patch('time.time',return_value=760): callback.on_log(None,state,control,logs={'loss':.5,'learning_rate':1e-4})
    backend=cb.TrainingBackend()
    for e in q.events: backend._handle_event(e)
    fake=stream._FakeBackend(active_polls=2);fake.trainer.training_progress=backend._progress
    fake.step_history=[step];fake.loss_history=[.5];fake.lr_history=[1e-4]
    with patch.object(stream.rt,'get_training_backend',return_value=fake):
        response=asyncio.run(stream.rt.stream_training_progress(stream._FakeRequest(),current_subject='tester'))
        raw=stream._collect_events(response)
    (root/'artifacts'/f'{side}-{scenario}.sse').write_text(raw)
    payloads=stream._progress_payloads(raw)
    facts.append({'scenario':scenario,'payloads':payloads})
    if scenario=='resumed':
        legacy='\n\n'.join('\n'.join('data: '+json.dumps({k:v for k,v in json.loads(l[6:]).items() if k!='session_start_step'}) if l.startswith('data: ') else l for l in block.splitlines()) for block in raw.split('\n\n'))
        (root/'artifacts'/f'{side}-legacy.sse').write_text(legacy)
(root/'artifacts'/f'frames-{side}.json').write_text(json.dumps(facts,indent=2))
print(side,[(f['scenario'],f['payloads'][0].get('eta_seconds'),f['payloads'][0].get('elapsed_seconds')) for f in facts])
