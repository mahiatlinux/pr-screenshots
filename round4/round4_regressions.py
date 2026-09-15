import pytest
from core.inference.ssh_policy import check_ssh_command_access
from core.inference.tools import _check_code_safety, _find_blocked_commands
from state.ssh_approvals import approve_hosts

@pytest.mark.parametrize('command', ['cmd=ssh; "$cmd" -F none evil.example', 'cmd=/usr/bin/ssh; env "$cmd" -F none evil.example', '$(printf ssh) -F none evil.example'])
def test_indirect_commands(command):
 assert _find_blocked_commands(command)

@pytest.mark.parametrize('code', [
 "import subprocess; launch=subprocess.run; launch(['ssh','-F','none','evil.example'])",
 "import os; launch=os.execv; launch('/usr/bin/ssh',['ssh','-F','none','evil.example'])",
 "import paramiko\ndef make():\n return paramiko.SSHClient()\nmake().connect(hostname='evil.example')",
 "import paramiko\ndef make():\n return paramiko.SSHClient()\nc=make(); c.connect(hostname='evil.example')",
 "import paramiko\ndef make():\n c=paramiko.SSHClient()\n return c\nmake().connect(hostname='evil.example')",
 "from paramiko.transport import Transport; Transport(('evil.example',22))",
 "import paramiko; paramiko.transport.Transport(('evil.example',22))",
])
def test_python_indirection(code):
 assert _check_code_safety(code,session_id='round4') is not None

@pytest.mark.parametrize('command', ['ssh -F none approved.example -o HostName=evil.example', 'ssh -F none -o CanonicalizeHostname=always -o CanonicalDomains=evil.example approved.example'])
def test_cli_redirects(command):
 approve_hosts('round4',['approved.example'])
 assert check_ssh_command_access(command,'round4') is not None
