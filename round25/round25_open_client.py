import paramiko
from core.inference.tools import _python_exec
print('Paramiko',paramiko.__version__)
result=_python_exec("import paramiko; paramiko.Transport.open_client(('127.0.0.2',22222))",session_id='unsupported-api',timeout=5)
print(result)
assert 'AttributeError' in result and 'open_client' in result
