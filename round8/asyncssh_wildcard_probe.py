from core.inference.tools import _check_code_safety
for module in ['asyncssh','asyncssh.connection']:
 code=f"from {module} import *; create_connection(factory, 'evil.example', config=None)"
 result=_check_code_safety(code,session_id='wildcard-asyncssh')
 print({'code':code,'result':result})
 assert result is not None
