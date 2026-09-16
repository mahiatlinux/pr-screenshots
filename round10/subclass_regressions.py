import pytest
from core.inference.tools import _check_code_safety
from state.ssh_approvals import approve_hosts,reset_ssh_approvals

@pytest.mark.parametrize('definition',[
 'class Client(paramiko.SSHClient): pass',
 'class Base(paramiko.SSHClient): pass\nclass Client(Base): pass',
 'Factory=paramiko.SSHClient\nclass Client(Factory): pass',
])
def test_subclass_requires_approval(definition):
 reset_ssh_approvals()
 code=f"import paramiko\n{definition}\nClient().connect(hostname='approved.example')"
 assert _check_code_safety(code,session_id='subclass') is not None
 approve_hosts('subclass',['approved.example'])
 assert _check_code_safety(code,session_id='subclass') is None


def test_super_connect_uses_actual_destination():
 reset_ssh_approvals();approve_hosts('subclass',['approved.example'])
 code="import paramiko\nclass Client(paramiko.SSHClient):\n def connect(self, hostname):\n  return super().connect(hostname='evil.example')\nClient().connect(hostname='approved.example')"
 assert _check_code_safety(code,session_id='subclass') is not None
 approve_hosts('subclass',['evil.example'])
 assert _check_code_safety(code,session_id='subclass') is None
