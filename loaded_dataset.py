import json,os
from pathlib import Path
from datasets import load_dataset,__version__
from core.training.provenance import attest_loaded_dataset
root=Path(__file__).resolve().parent
side=Path.cwd().name
snapshot=next((Path(os.environ['HF_HOME'])/'hub/datasets--hf-internal-testing--librispeech_asr_dummy/snapshots').iterdir())
data=load_dataset('parquet',data_files=str(snapshot/'clean/validation-00000-of-00001.parquet'),split='train',cache_dir=str(root/'runtime'/side/'datasets'))
attested,reason=attest_loaded_dataset('hf-internal-testing/librispeech_asr_dummy',data)
assert bool(attested)==(side!='base'),(attested,reason)
print(json.dumps({'side':side,'datasets':__version__,'rows':len(data),'attested':bool(attested),'reason':reason}))
