import json, sys, time
from pathlib import Path
import torch, transformers
from transformers import Trainer, TrainingArguments, LlamaConfig, LlamaForCausalLM, set_seed
root=Path(__file__).resolve().parent
side=sys.argv[1]
sys.path.insert(0,str(root/side/'studio/backend'))
sys.path.insert(0,str(root/side/'studio/backend/tests'))
import test_training_progress_callback as callbacks
for name,attrs in callbacks._STUBS.items(): callbacks._stub_if_missing(name,attrs)
import core.training.trainer
from core.training.resume import _checkpoint_state
assert torch.cuda.is_available()
print(json.dumps({'gpu':torch.cuda.get_device_name(), 'torch':torch.__version__,'transformers':transformers.__version__},sort_keys=True))
class Inputs(torch.utils.data.Dataset):
    def __len__(self): return 32
    def __getitem__(self,index):
        ids=torch.tensor([(index+i)%64 for i in range(16)])
        return {'input_ids':ids,'labels':ids.clone()}
results=[]
def run(label, resume=None):
    set_seed(314159)
    owner=callbacks._make_owner()
    owner._update_progress(total_steps=6)
    owner.training_start_time=time.time()
    queue=callbacks._FakeQueue()
    owner.add_progress_callback(callbacks._create_trainer_progress_callback(queue))
    embedding_queue=callbacks._FakeQueue()
    emb=callbacks._create_embedding_progress_callback(embedding_queue,total_steps=6,training_start_time=owner.training_start_time,should_stop=lambda:False)
    config=LlamaConfig(vocab_size=64,hidden_size=32,intermediate_size=64,num_hidden_layers=2,num_attention_heads=4,num_key_value_heads=2,max_position_embeddings=64)
    model=LlamaForCausalLM(config)
    args=TrainingArguments(output_dir=str(root/'gpu'/label),max_steps=6,per_device_train_batch_size=2,gradient_accumulation_steps=2,learning_rate=1e-4,logging_steps=1,save_steps=3,save_total_limit=2,report_to='none',disable_tqdm=True,seed=314159,dataloader_num_workers=0)
    trainer=Trainer(model=model,args=args,train_dataset=Inputs(),callbacks=[owner._create_progress_callback(),emb])
    trainer.train(resume_from_checkpoint=resume)
    events=[e for e in queue.events if e.get('type')=='progress' and e.get('loss') is not None]
    ee=[e for e in embedding_queue.events if e.get('type')=='progress' and e.get('loss') is not None]
    assert events and ee
    assert trainer.state.global_step==6
    baseline=3 if resume else 0
    if side=='base':
        for event in events+ee:
            if event['step']<6:
                assert abs(event['eta_seconds']-event['elapsed_seconds']/event['step']*(6-event['step']))<1e-9
    else:
        assert owner.session_start_step==baseline
        for event in events+ee:
            assert event['session_start_step']==baseline
            if event['step']<6:
                expected=event['elapsed_seconds']/(event['step']-baseline)*(6-event['step'])
                assert abs(event['eta_seconds']-expected)<1e-9
    result={'label':label,'baseline':getattr(owner,'session_start_step',None),'cuda_events':events,'embedding_events':ee,'losses':[e['loss'] for e in events]}
    results.append(result)
    state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
    del trainer,model
    torch.cuda.empty_cache()
    return state
full=run('full-'+side)
checkpoint=root/'gpu'/('full-'+side)/'checkpoint-3'
assert _checkpoint_state(checkpoint)==3
resumed=run('resumed-'+side,str(checkpoint))
assert all(torch.equal(full[k],resumed[k]) for k in full), 'resume changed final model weights'
assert results[0]['losses'][3:]==results[1]['losses'], 'resume changed losses'
print('PASS: checkpoint step 3 restored; '+('legacy ETA confirmed; ' if side=='base' else 'session baseline confirmed in both callbacks; ')+'six-step final weights and resumed losses match uninterrupted training exactly')
(root/'artifacts'/('gpu-'+side+'.json')).write_text(json.dumps(results,indent=2))
