import pytest
from core.inference.tools import _check_code_safety
from state.ssh_approvals import approve_hosts,reset_ssh_approvals

@pytest.mark.parametrize('code',[
 "import paramiko; paramiko.ProxyCommand('ssh -F none approved.example')",
 "from paramiko import ProxyCommand as Proxy; Proxy('ssh -F none approved.example')",
 "from paramiko.proxy import ProxyCommand; ProxyCommand('ssh -F none approved.example')",
 "import paramiko.proxy as proxy; proxy.ProxyCommand(command='ssh -F none approved.example')",
 "import paramiko; Proxy=paramiko.ProxyCommand; Proxy('ssh -F none approved.example')",
])
def test_proxy_command_requires_approval(code):
 reset_ssh_approvals()
 assert _check_code_safety(code,session_id='round7') is not None
 approve_hosts('round7',['approved.example'])
 assert _check_code_safety(code,session_id='round7') is None
