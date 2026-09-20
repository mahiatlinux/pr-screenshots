import json,os,sys,time,statistics,shutil
from pathlib import Path
from core.training import provenance as p
from hub.utils.dataset_cache import resolved_dataset_snapshot_file
from routes.models import _get_snapshot_model_size_bytes
root=Path(os.environ['TMPDIR'])/'probe'
if root.exists(): shutil.rmtree(root)
root.mkdir()
results=[]
for layout in ('regular','own','shared','mixed','external','other-repo','prefix-collision','broken','loop','shared-escape'):
 cache=root/layout/'cache ü space'
 snapshot=cache/'models--org--model'/'snapshots'/'commit'
 snapshot.mkdir(parents=True)
 (snapshot/'config.json').write_text('{}')
 weight=snapshot/'model.safetensors'
 if layout=='regular': weight.write_bytes(b'w'*4096)
 else:
  targets={'own':snapshot.parent.parent/'blobs'/'hash','shared':cache/'blobs'/'ab'/'hash','mixed':cache/'blobs'/'ab'/'hash','external':root/'outside'/layout/'weights','other-repo':cache/'models--org--other'/'blobs'/'hash','prefix-collision':cache/'blobs-extra'/'hash','broken':cache/'blobs'/'missing','loop':snapshot/'loop','shared-escape':cache/'blobs'/'ab'/'hash'}
  target=targets[layout]; target.parent.mkdir(parents=True,exist_ok=True)
  if layout=='shared-escape':
   outside=root/'escape'; outside.write_bytes(b'w'*4096); target.symlink_to(outside)
  elif layout=='loop': target.symlink_to(weight)
  elif layout!='broken': target.write_bytes(b'w'*4096)
  repo_blob=snapshot.parent.parent/'blobs'/'via';repo_blob.parent.mkdir(exist_ok=True)
  repo_blob.symlink_to(os.path.relpath(target,repo_blob.parent)); weight.symlink_to(os.path.relpath(repo_blob,weight.parent))
  if layout=='mixed': (snapshot/'pytorch_model.bin').write_bytes(b'x'*1024)
 model=p._resolved_model_snapshot_file(snapshot,weight)
 dataset=resolved_dataset_snapshot_file(snapshot,'model.safetensors')
 size=_get_snapshot_model_size_bytes(str(snapshot))
 accepted=layout in ('regular','own') or (layout in ('shared','mixed') and '--base' not in sys.argv)
 assert bool(model)==accepted,(layout,'model',model)
 assert bool(dataset)==accepted,(layout,'dataset',dataset)
 assert size==((5120 if layout=='mixed' else 4096) if accepted else (1024 if layout=='mixed' else None)),(layout,size)
 for bad in ('../model.safetensors','/etc/passwd','a/../../model.safetensors','C:\\windows\\file'):
  assert resolved_dataset_snapshot_file(snapshot,bad) is None,(layout,bad)
 results.append({'layout':layout,'model':bool(model),'dataset':bool(dataset),'size':size})
print(json.dumps(results,indent=2))
if '--require-shared' in sys.argv:
 assert all(r['model'] and r['dataset'] and r['size'] for r in results if r['layout']=='shared'),'shared blobs rejected'
