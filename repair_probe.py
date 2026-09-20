import importlib.util,itertools,json,pathlib
root=pathlib.Path(__file__).resolve().parent
files=['studio/backend/utils/datasets/format_detection.py','studio/backend/hub/utils/dataset_format.py']
mods={}
for side in ['base','head','fix']:
 mods[side]=[]
 for index,file in enumerate(files):
  spec=importlib.util.spec_from_file_location(side+str(index),root/side/file);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mods[side].append(mod)
cases=0;broken=0
for context,prompt,question,answer,order in itertools.product([1,20,49],[1,20,49],[1,20,49],[1,120,1001],itertools.permutations(['context','prompt','question','answer'])):
 values={'context':'c'*context,'prompt':'p'*prompt,'question':'q'*question,'answer':'a'*answer};row={col:values[col] for col in order}
 for i in range(2):
  old=mods['base'][i].detect_custom_format_heuristic([row]);pr=mods['head'][i].detect_custom_format_heuristic([row]);fixed=mods['fix'][i].detect_custom_format_heuristic([row]);assert fixed==old,(row,fixed,old);broken+=pr!=old
 cases+=1
print(json.dumps({'short_user_cases':cases,'implementations':2,'original_head_regressions':broken,'repaired_regressions':0},indent=2))
