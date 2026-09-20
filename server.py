import os,secrets,sys
from pathlib import Path
os.environ['UNSLOTH_STUDIO_DISABLE_TORCH_WARM']='1'
os.environ['UNSLOTH_STUDIO_DISABLE_DEVICE_PROBE']='1'
os.environ['UNSLOTH_STUDIO_DISABLE_HELPER_PRECACHE']='1'
from auth import storage
password_file=Path(os.environ['HOME'])/'test-password'
if not password_file.exists():
    password=secrets.token_urlsafe(24)
    storage.create_initial_user('unsloth',password,secrets.token_urlsafe(32))
    password_file.write_text(password)
    password_file.chmod(0o600)
import main,uvicorn
main.setup_frontend(main.app,Path.cwd()/'studio/frontend/dist')
if __name__ == '__main__':
    uvicorn.run(main.app,host='127.0.0.1',port=int(sys.argv[1]),log_level='warning')
