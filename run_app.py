import os,sys
from pathlib import Path
root=Path(__file__).resolve().parent
side=sys.argv[1];port=int(sys.argv[2])
os.environ['UNSLOTH_STUDIO_HOME']=str(root/('home-'+side))
os.environ['HF_HOME']=str(root/('cache-'+side)/'hf')
os.environ['HF_HUB_CACHE']=str(root/('cache-'+side)/'hf/hub')
os.environ['HF_XET_CACHE']=str(root/('cache-'+side)/'hf/xet')
os.environ['XDG_CACHE_HOME']=str(root/('cache-'+side))
os.environ['UNSLOTH_STUDIO_DISABLE_DEVICE_PROBE']='1'
sys.path.insert(0,str(root/side/'studio/backend'))
from main import app,setup_frontend
setup_frontend(app,root/side/'studio/frontend/dist')
import uvicorn
uvicorn.run(app,host='127.0.0.1',port=port,log_level='warning')
