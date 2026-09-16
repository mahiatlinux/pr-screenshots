import pytest
from core.inference.tools import _check_code_safety
from state.ssh_approvals import approve_hosts,reset_ssh_approvals

@pytest.mark.parametrize('assignment',[
 'client = paramiko.SSHClient() if use_paramiko else fallback',
 'client = fallback if use_fallback else paramiko.SSHClient()',
 'client = paramiko.SSHClient() if first else (fallback if second else paramiko.SSHClient())',
 'client = paramiko.SSHClient() or fallback',
 'client = enabled and paramiko.SSHClient()',
 'Factory = paramiko.SSHClient if enabled else fallback; client=Factory()',
 'Factory = enabled and paramiko.SSHClient; client=Factory()',
])
def test_conditional_client_requires_approval(assignment):
 reset_ssh_approvals()
 code='import paramiko\n'+assignment+"\nclient.connect(hostname='evil.example')"
 assert _check_code_safety(code,session_id='review') is not None
 approve_hosts('review',['evil.example'])
 assert _check_code_safety(code,session_id='review') is None

def test_conditional_data_is_unchanged():
 assert _check_code_safety("import paramiko; result='yes' if enabled else 'no'; print(result)",session_id='review') is None
