import pytest
from core.inference.tools import _check_code_safety
from state.ssh_approvals import approve_hosts, reset_ssh_approvals

@pytest.mark.parametrize('group', ['fabric.SerialGroup', 'fabric.ThreadingGroup', 'fabric.group.SerialGroup'])
def test_all_group_hosts_require_approval(group):
 reset_ssh_approvals();approve_hosts('round11',['approved.example'])
 code=f"import fabric; {group}('approved.example','review@evil.example:22',config=fabric.Config(lazy=True)).run('hostname')"
 assert _check_code_safety(code,session_id='round11') is not None
 approve_hosts('round11',['evil.example'])
 assert _check_code_safety(code,session_id='round11') is None

@pytest.mark.parametrize('factory', ["make=lambda: paramiko.SSHClient()", "first=lambda: paramiko.SSHClient(); make=lambda: first()"])
def test_lambda_client_requires_approval(factory):
 reset_ssh_approvals()
 code=f"import paramiko; {factory}; make().connect(hostname='evil.example')"
 assert _check_code_safety(code,session_id='round11') is not None
 approve_hosts('round11',['evil.example'])
 assert _check_code_safety(code,session_id='round11') is None


def test_inline_lambda_requires_approval():
 reset_ssh_approvals()
 code="import paramiko; (lambda: paramiko.SSHClient())().connect(hostname='evil.example')"
 assert _check_code_safety(code, session_id='round11') is not None
 approve_hosts('round11',['evil.example'])
 assert _check_code_safety(code, session_id='round11') is None
