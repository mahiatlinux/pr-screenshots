import importlib.util, itertools, json, pathlib, time, statistics
root = pathlib.Path(__file__).resolve().parent
paths = ['studio/backend/utils/datasets/format_detection.py','studio/backend/hub/utils/dataset_format.py']
def load(side, index):
 spec = importlib.util.spec_from_file_location(side+str(index), root/side/paths[index]); module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
mods = {side:[load(side,i) for i in range(2)] for side in ['base','fix','mirror']}
lengths = [0,1,49,50,51,199,200,201,999,1000,1001]
contexts = ['context','contexts','sql_context','retrieved_contexts','CONTEXT','con_text','con-text','con text']
counts = {'qa_cases':0,'compatibility_cases':0}
for ctx, lens, order in itertools.product(contexts,itertools.product(lengths,repeat=2),itertools.permutations(range(3))):
 row0={ctx:'c'*lens[0],'question':'q'*lens[1],'answer':'a'*120}; keys=list(row0); row={keys[i]:row0[keys[i]] for i in order}
 expected={ctx:'system','question':'user','answer':'assistant'}
 for side in ['fix','mirror']:
  for mod in mods[side]: assert mod.detect_custom_format_heuristic([row]) == expected, (side,row.keys(),lens)
 counts['qa_cases']+=1
schemas=[['context','answer'],['context','answer','explanation'],['context','response','target'],['fulltext','answer'],['input_text','target_text'],['instruction','input','output'],['system','output'],['persona','reply'],['task','input','output'],['userInput','assistantResponse'],['inputs','targets'],['foo','bar'],['question','answer']]
differences=[]
for cols in schemas:
 for lens in itertools.product(lengths,repeat=len(cols)):
  row=dict(zip(cols,('x'*n for n in lens)))
  for idx in range(2):
   old=mods['base'][idx].detect_custom_format_heuristic([row]); new=mods['fix'][idx].detect_custom_format_heuristic([row]); merged=mods['mirror'][idx].detect_custom_format_heuristic([row]); assert new==merged
   if old!=new: differences.append({'columns':cols,'lengths':lens,'module':idx,'base':old,'fix':new})
  counts['compatibility_cases']+=1
row={'context':'Passage. '*100,'question':'What is the answer?','answer':'The answer.'}
example={side:[m.detect_custom_format_heuristic([row]) for m in modules] for side,modules in mods.items()}
bench={}
for side,modules in mods.items():
 vals=[]
 for _ in range(5):
  start=time.perf_counter()
  for n in range(5000): modules[0].detect_custom_format_heuristic([row])
  vals.append((time.perf_counter()-start)/5000*1e6)
 bench[side]=round(statistics.median(vals),2)
result={'model':'context shadows text only for selection; preserve two-column fallback, explicit system-only manual mapping, recognized schemas and both implementations','counts':counts,'example':example,'median_microseconds':bench,'compatibility_difference_count':len(differences),'compatibility_differences':differences[:30]}
(root/'artifacts/probe-fixed.json').write_text(json.dumps(result,indent=2)); print(json.dumps(result,indent=2))
