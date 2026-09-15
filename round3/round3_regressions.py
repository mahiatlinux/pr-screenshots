import pytest
from core.inference.ssh_policy import check_ssh_command_access, check_ssh_python_access, collect_ssh_hosts_for_approval
from core.inference.tools import _check_code_safety
from state.ssh_approvals import approve_hosts, reset_ssh_approvals

@pytest.mark.parametrize('code', [
 "import os; os.execv('/usr/bin/ssh', ['ssh', '-F', 'none', 'evil.example'])",
 "from os import execlp as launch; launch('ssh', 'ssh', '-F', 'none', 'evil.example')",
 "import paramiko; first = client = paramiko.SSHClient(); client.connect(hostname='evil.example')",
 "import paramiko; client, other = paramiko.SSHClient(), None; client.connect(hostname='evil.example')",
 "import paramiko; first = paramiko.SSHClient(); client = first; client.connect(hostname='evil.example')",
 "import paramiko\nclass Wrapper:\n def connect(self):\n  self.client = paramiko.SSHClient()\n  self.client.connect(hostname='evil.example')\nWrapper().connect()",
 "import paramiko; client = paramiko.SSHClient(); client.connect('approved.example', sock=paramiko.ProxyCommand('ssh -F none evil.example -W approved.example:22'))",
])
def test_python_bypasses(code):
 reset_ssh_approvals(); approve_hosts('round3', ['approved.example'])
 assert _check_code_safety(code, session_id='round3') is not None

@pytest.mark.parametrize('target', ['*', 'evil.?xample', '[e]vil.example', '{evil,other}.example', '*@approved.example'])
def test_expanded_destinations(target):
 reset_ssh_approvals()
 command=f'ssh -F none {target}'
 approve_hosts('round3', collect_ssh_hosts_for_approval('terminal', {'command':command}))
 assert check_ssh_command_access(command,'round3') is not None
