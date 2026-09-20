import os,json
from pathlib import Path
from huggingface_hub import hf_hub_download,__version__
root=Path(__file__).resolve().parent
cache=root/'live-cache'
rows=[]
for repo,kind,files in [('hf-internal-testing/tiny-random-LlamaForCausalLM','model',['config.json','model.safetensors']),('hf-internal-testing/librispeech_asr_dummy','dataset',['clean/validation-00000-of-00001.parquet'])]:
 for name in files:
  value=Path(hf_hub_download(repo,name,repo_type=kind,cache_dir=cache,token=False))
  rows.append({'repo':repo,'type':kind,'filename':name,'snapshot':str(value.relative_to(cache)),'resolved':str(value.resolve().relative_to(cache)),'bytes':value.stat().st_size,'is_symlink':value.is_symlink()})
(root/'artifacts/live-download.json').write_text(json.dumps({'hub_version':__version__,'files':rows},indent=2))
print(json.dumps(rows,indent=2))
