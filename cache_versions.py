import os,json,sys
from pathlib import Path
from huggingface_hub import hf_hub_download,__version__
from core.training.provenance import _resolved_model_snapshot_file
from hub.utils.dataset_cache import resolved_dataset_snapshot_file
from routes.models import _get_snapshot_model_size_bytes
root=Path(__file__).resolve().parent
cache=root/('live-cache' if '--shared' in sys.argv else 'version-cache')
repo='hf-internal-testing/tiny-random-LlamaForCausalLM'
for name in ('config.json','model.safetensors'):
 weight=Path(hf_hub_download(repo,name,revision='9fb191250dd56d0ba7ec9785a025ed29c03d5998',cache_dir=cache,token=False,local_files_only='--offline' in sys.argv))
snapshot=weight.parent
assert _resolved_model_snapshot_file(snapshot,weight)
assert resolved_dataset_snapshot_file(snapshot,'model.safetensors')
assert _get_snapshot_model_size_bytes(str(snapshot))==4131280
print(json.dumps({'python':sys.version.split()[0],'hub':__version__,'offline':'--offline' in sys.argv,'resolved':str(weight.resolve().relative_to(cache)),'size':weight.stat().st_size}))
