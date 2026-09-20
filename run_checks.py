import subprocess, sys, os
from pathlib import Path
root=Path(__file__).resolve().parent
focused=['test_training_progress_callback.py','test_training_progress_stream_nan.py','test_final_loss_not_average.py']
for side in sys.argv[1:]:
    python=root/side/'.venv/bin/python'
    files=focused if os.environ.get('FOCUSED') else sorted(p.name for p in (root/side/'studio/backend/tests').glob('test_*.py') if any(x in p.name for x in ('training_progress','training_resume','training_runs','mlx_training_worker','training_pump','training_nan','training_finalizing','training_status_terminal','final_loss_not_average')))
    with (root/'artifacts'/f'backend-{side}.log').open('w') as out:
        env=dict(os.environ,UNSLOTH_STUDIO_HOME=str(root/'studio-homes'/side),HF_HOME=str(root/'hf'/side),XDG_CACHE_HOME=str(root/'cache'/side))
        r=subprocess.run([str(python),str(root/'pytest_bootstrap.py'),'-q',*[f'tests/{p}' for p in files]],cwd=root/side/'studio/backend',stdout=out,stderr=subprocess.STDOUT,env=env)
    print(side, 'exit',r.returncode,flush=True)
