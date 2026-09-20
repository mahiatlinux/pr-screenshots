import os, pathlib, subprocess, sys
root = pathlib.Path(__file__).resolve().parent
side = sys.argv[1]
for p in ['homes/'+side, 'tmp', 'cache/'+side, 'artifacts']:
    (root/p).mkdir(parents=True, exist_ok=True)
cmd = ['bwrap','--die-with-parent','--unshare-user','--unshare-pid','--unshare-ipc','--unshare-uts','--new-session','--cap-drop','ALL','--ro-bind','/usr','/usr','--symlink','usr/bin','/bin','--symlink','usr/lib','/lib','--symlink','usr/lib64','/lib64','--proc','/proc','--dev','/dev','--bind',str(root),'/task','--tmpfs','/tmp','--clearenv']
for p in ['/etc/resolv.conf','/etc/hosts','/etc/ssl','/etc/fonts']:
    if os.path.exists(p): cmd += ['--ro-bind',p,p]
env = dict(PATH=f'/task/{side}/.venv/bin:/task/bin:/usr/bin',HOME=f'/task/homes/{side}',XDG_CACHE_HOME=f'/task/cache/{side}',UV_CACHE_DIR='/task/uv-cache',UV_PYTHON_INSTALL_DIR='/task/python',UV_NATIVE_TLS='true',NEMO_TELEMETRY_ENABLED='false',UNSLOTH_STUDIO_HOME=f'/task/homes/{side}/studio',HF_HOME=f'/task/cache/{side}/hf',HF_HUB_CACHE=f'/task/cache/{side}/hf/hub',HF_XET_CACHE=f'/task/cache/{side}/hf/xet',PLAYWRIGHT_BROWSERS_PATH='/task/playwright/browsers',npm_config_cache='/task/npm-cache',LANG='C.UTF-8',PYTHONPATH=f'/task/{side}/studio/backend',PYTHONUNBUFFERED='1')
for k,v in env.items(): cmd += ['--setenv',k,v]
cmd += ['--chdir',f'/task/{side}',*sys.argv[2:]]
raise SystemExit(subprocess.call(cmd))
