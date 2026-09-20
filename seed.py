import os,json,shutil,pickle,zipfile,time
from pathlib import Path
from core.training.provenance import build_worker_provenance_event,normalize_worker_provenance_event,resource_provenance_resume_blocker
from core.training.resume import can_resume_run
from storage import studio_db
from utils.paths import outputs_root
from routes.models import _get_snapshot_model_size_bytes
from safetensors.numpy import save_file
import numpy as np
root=Path(__file__).resolve().parent
side=Path.cwd().name
cache=Path(os.environ['HF_HOME'])/'hub'
shutil.copytree(root/'live-cache',cache,dirs_exist_ok=True,symlinks=True)
model=next((cache/'models--hf-internal-testing--tiny-random-LlamaForCausalLM'/'snapshots').iterdir())
dataset=next((cache/'datasets--hf-internal-testing--librispeech_asr_dummy'/'snapshots').iterdir())
config={'model_name':'hf-internal-testing/tiny-random-LlamaForCausalLM','model_snapshot_path':str(model),'hf_dataset':'hf-internal-testing/librispeech_asr_dummy','dataset_snapshot_path':str(dataset),'load_in_4bit':False,'training_type':'LoRA','dataset_source':'huggingface'}
event=build_worker_provenance_event(config,object(),model_load_target=str(model),model_load_in_4bit=False,dataset_loaded_from_exact_snapshot=True)
persisted={**config,**normalize_worker_provenance_event(event,config)}
output=outputs_root()/'shared-cache-resume'
ckpt=output/'checkpoint-5'; ckpt.mkdir(parents=True,exist_ok=True)
(ckpt/'trainer_state.json').write_text(json.dumps({'global_step':5}))
save_file({'weight':np.ones(1,dtype=np.float32)},str(ckpt/'adapter_model.safetensors'))
for name in ('optimizer.pt','scheduler.pt'):
 with zipfile.ZipFile(ckpt/name,'w') as z: z.writestr('archive/data.pkl',pickle.dumps({'state':{}},protocol=2))
run={'status':'stopped','final_step':5,'total_steps':20,'output_dir':str(output),'config_json':json.dumps(persisted)}
can_resume=can_resume_run(run)
for run_id,run_config,model_name in [('shared-cache-run',persisted,config['model_name']),('previously-unattested',{**persisted,'resource_provenance':{'version':1,'status':'incomplete','model_status':'incomplete','dataset_status':'incomplete'}},'Previous unattested run')]:
 if not studio_db.get_run(run_id):
  studio_db.create_run(id=run_id,model_name=model_name,dataset_name=config['hf_dataset'],config_json=json.dumps(run_config),started_at='2026-09-20T00:00:00Z',total_steps=20,output_dir=str(output))
  studio_db.finish_run(id=run_id,status='stopped',ended_at='2026-09-20T00:01:00Z',final_step=5,final_loss=2.0,duration_seconds=60,output_dir=str(output))
times=[]
for _ in range(100):
 t=time.perf_counter(); _get_snapshot_model_size_bytes(str(model)); times.append((time.perf_counter()-t)*1000)
facts={'side':side,'event':event,'can_resume':can_resume,'blocked_reason':resource_provenance_resume_blocker(persisted),'size':_get_snapshot_model_size_bytes(str(model)),'size_mean_ms':sum(times)/len(times),'persisted':persisted}
(root/'artifacts'/f'{side}-facts.json').write_text(json.dumps(facts,indent=2))
print(json.dumps({k:v for k,v in facts.items() if k not in ('event','persisted')},indent=2))
assert can_resume==(side!='base'),facts
assert facts['size']==(None if side=='base' else 4131280),facts
assert not can_resume_run({**run,'config_json':json.dumps(run_config)})
