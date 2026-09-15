import pytest
from core.inference.tools import _check_code_safety
from state.ssh_approvals import approve_hosts
@pytest.mark.parametrize('code', [
 "from paramiko import SSHClient as Client; Client().connect(hostname='evil.example')",
 "from paramiko import *; c=SSHClient(); c.connect(hostname='evil.example')",
 "import paramiko as p; p.SSHClient().connect('approved.example', sock=p.ProxyCommand('ssh -F none evil.example -W approved.example:22'))",
])
def test_inline_aliases(code):
 approve_hosts('aliases',['approved.example'])
 assert _check_code_safety(code,session_id='aliases') is not None
