import ast,json,random,sys,tempfile
from pathlib import Path
root=Path(__file__).resolve().parent
side=sys.argv[1]
resume=root/side/'studio/backend/core/training/resume.py'
worker=root/side/'studio/backend/core/training/worker.py'
r=ast.parse(resume.read_text());w=ast.parse(worker.read_text())
ns={'Optional':__import__('typing').Optional,'Path':Path,'json':json}
for name in ['_checkpoint_step','_checkpoint_state','session_eta_seconds']:
    nodes=[n for n in r.body if isinstance(n,ast.FunctionDef) and n.name==name]
    if nodes: exec(compile(ast.Module(body=nodes,type_ignores=[]),str(resume),'exec'),ns)
node=next(n for n in ast.walk(w) if isinstance(n,ast.FunctionDef) and n.name=='_on_step' and any(isinstance(x,ast.Name) and x.id=='eta' for x in ast.walk(n)))
exec(compile(ast.Module(body=[node],type_ignores=[]),str(worker),'exec'),ns)
events=[]
ns.update(_send=lambda kind,**kwargs: events.append({'type':kind,**kwargs}),wandb_run=None,tb_writer=None,num_epochs=1)
rng=random.Random(11297)
wrong=0
for i in range(1000):
    baseline=rng.randrange(10000);done=rng.randrange(1,1000);remain=rng.randrange(1,1000);elapsed=rng.randrange(1,10000)
    ns['start_step']=baseline
    ns['_on_step'](baseline+done,baseline+done+remain,.5,1e-4,25,1,elapsed,100,grad_norm=.1)
    e=events[-1];expected=elapsed/done*remain
    if abs(e['eta_seconds']-expected)>1e-8: wrong+=1
    assert e['step']==baseline+done and e['loss']==.5 and e['grad_norm']==.1
assert wrong==(1000 if side=='base' else 0),(side,wrong)
print(side,'1000 extracted MLX callback cases; incorrect ETA:',wrong)
(root/'artifacts'/f'mlx-{side}.json').write_text(json.dumps({'cases':1000,'wrong':wrong,'last_event':events[-1]},indent=2))
