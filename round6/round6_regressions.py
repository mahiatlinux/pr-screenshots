import pytest
from core.inference.tools import _check_code_safety
from state.ssh_approvals import approve_hosts,reset_ssh_approvals

@pytest.mark.parametrize('code',[
 "import paramiko; Factory=paramiko.SSHClient; Factory().connect(hostname='approved.example')",
 "import paramiko; Factory=paramiko.SSHClient; c=Factory(); c.connect(hostname='approved.example')",
 "import asyncssh; fn=asyncssh.connect; fn('approved.example',config=None)",
 "import fabric; Factory=fabric.Connection; Factory('approved.example',config=fabric.Config(lazy=True))",
])
def test_assigned_apis_require_approval(code):
 reset_ssh_approvals()
 assert _check_code_safety(code,session_id='round6') is not None
 approve_hosts('round6',['approved.example'])
 assert _check_code_safety(code,session_id='round6') is None

@pytest.mark.parametrize('kwargs',[
 "{'sock': paramiko.ProxyCommand('ssh -F none evil.example -W approved.example:22')}",
 "options",
 "{**options}",
])
def test_fabric_socket_override_requires_block(kwargs):
 reset_ssh_approvals();approve_hosts('round6',['approved.example'])
 code=f"import fabric,paramiko; fabric.Connection('approved.example',config=fabric.Config(lazy=True),connect_kwargs={kwargs}).run('true')"
 assert _check_code_safety(code,session_id='round6') is not None
