from core.inference.tools import _check_code_safety
code="import paramiko; client=paramiko.SSHClient(); connect=client.connect; connect(hostname='evil.example')"
print({'code':code,'policy':_check_code_safety(code,session_id='alias-probe')})
assert _check_code_safety(code,session_id='alias-probe') is not None
