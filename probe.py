import concurrent.futures, copy, json, os, platform, sys, time
from pathlib import Path
from models.data_recipe import RecipePayload
from routes.data_recipe.validate import validate
from core.data_recipe.service import preview_recipe
from routes.data_recipe.jobs import _resolve_seed_endpoint
side = sys.argv[1]
recipe = {'seed_config': {'source': {'seed_type': 'hf', 'path': 'datasets/lhoestq/demo1/data/train.csv', 'endpoint': None}}, 'columns': [{'column_type': 'expression', 'name': 'result', 'expr': 'verified'}]}
rows = []
def check(name, item, expected):
    start=time.monotonic()
    try:
        response=validate(RecipePayload(recipe=copy.deepcopy(item)))
    except Exception as exc:
        if expected is not None: raise
        record={'case':name,'exception':type(exc).__name__,'error':str(exc).splitlines()[0]}
        rows.append(record); print(json.dumps(record),flush=True); return
    record={'case':name,'valid':response.valid,'errors':[e.message for e in response.errors], 'seconds':round(time.monotonic()-start,3)}
    rows.append(record)
    print(json.dumps(record),flush=True)
    assert expected is None or response.valid == expected, record
    return response
for name, value in [('null',None),('empty',''),('whitespace','   '),('explicit','https://huggingface.co'),('omitted','OMIT')]:
    item=copy.deepcopy(recipe)
    if value=='OMIT': del item['seed_config']['source']['endpoint']
    else: item['seed_config']['source']['endpoint']=value
    check(name,item, (True if side!='base' or name in ['explicit','omitted'] else False if name=='null' else None))
seedless={'columns':recipe['columns']}
check('seedless',seedless,True)
check('missing-columns',{},False)
check('invalid-expression',{'columns':[{'column_type':'expression','name':'result','expr':'{{ not_a_column }}'}]},False)
check('github-invalid',{'seed_config':{'source':{'seed_type':'github_repo','repos':[],'item_types':['issues'],'limit':1}},'columns':recipe['columns']},False)
explicit=copy.deepcopy(recipe)
explicit['seed_config']['source']['endpoint']='https://huggingface.co'
os.environ['HF_ENDPOINT']='http://127.0.0.1:9700'
check('explicit-preserved-despite-env',explicit,True)
for val in [None,'','   ']:
    item=copy.deepcopy(recipe); item['seed_config']['source']['endpoint']=val
    _resolve_seed_endpoint(item)
    assert item['seed_config']['source']['endpoint']=='http://127.0.0.1:9700'
os.environ.pop('HF_ENDPOINT')
if side!='base':
    check('repeat-warm',recipe,True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        result=list(executor.map(lambda _:validate(RecipePayload(recipe=copy.deepcopy(recipe))).valid,range(8)))
    assert all(result)
    ready=copy.deepcopy(recipe); _resolve_seed_endpoint(ready)
    generated,_,_=preview_recipe(ready,2)
    assert len(generated)==2 and all(r['result']=='verified' for r in generated)
    rows.append({'case':'concurrent-validation','passed':len(result)})
    rows.append({'case':'generation','rows':len(generated),'result_values':[r['result'] for r in generated]})
Path('/task/artifacts/'+side+'-probe.json').write_text(json.dumps({'side':side,'python':platform.python_version(),'platform':platform.platform(),'results':rows},indent=2))
