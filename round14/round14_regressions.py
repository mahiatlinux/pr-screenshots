import pytest
from core.inference.ssh_policy import check_ssh_command_access
from core.inference.tools import _check_code_safety
from state.ssh_approvals import approve_hosts,reset_ssh_approvals

@pytest.mark.parametrize('command',[
 "bash -s <<'EOF'\nssh -F none evil.example uptime\nEOF",
 "bash -s <<'EOF'\n# comment\nssh -F none evil.example uptime\nEOF",
 "echo ready\nssh -F none evil.example uptime",
])
def test_newline_ssh_requires_approval(command):
 reset_ssh_approvals()
 assert check_ssh_command_access(command,'round14') is not None
 approve_hosts('round14',['evil.example'])
 assert check_ssh_command_access(command,'round14') is None

@pytest.mark.parametrize('code',[
 "import paramiko; (client:=paramiko.SSHClient()).connect(hostname='evil.example')",
 "import paramiko; (client:=paramiko.SSHClient()); client.connect(hostname='evil.example')",
])
def test_named_client_requires_approval(code):
 reset_ssh_approvals()
 assert _check_code_safety(code,session_id='round14') is not None
 approve_hosts('round14',['evil.example'])
 assert _check_code_safety(code,session_id='round14') is None


def test_ssh_line_continuation_preserves_arguments():
 reset_ssh_approvals();approve_hosts('round14',['approved.example'])
 assert check_ssh_command_access('ssh -F none '+chr(92)+'\n approved.example uptime','round14') is None


def test_blank_lines_preserve_command_boundaries():
 reset_ssh_approvals()
 command="bash -s <<'EOF'\n\nssh -F none evil.example uptime\nEOF"
 assert check_ssh_command_access(command,'round14') is not None
 approve_hosts('round14',['evil.example'])
 assert check_ssh_command_access(command,'round14') is None


def test_quoted_newline_is_still_data():
 reset_ssh_approvals()
 command="printf '%s' 'hello\nssh -F none evil.example\n'"
 assert check_ssh_command_access(command,'round14') is None
