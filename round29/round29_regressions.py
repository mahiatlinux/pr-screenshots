import pytest
from core.inference import tools as tools_mod
from core.inference.ssh_policy import check_ssh_command_access,extract_ssh_hosts_from_command
from state.ssh_approvals import approve_hosts,reset_ssh_approvals

@pytest.mark.parametrize('command',[
 'echo ok&ssh -F none evil.example',
 'echo ok&&ssh -F none evil.example',
 'echo ok|ssh -F none evil.example',
 '(echo ok)&ssh -F none evil.example',
 'echo ok&"ssh.exe" -F none evil.example',
 'echo ok&scp -F none evil.example:/tmp/file copy',
 'cmd /c "echo ok&ssh -F none evil.example"',
])
def test_cmd_adjacent_separators_require_host_approval(monkeypatch,command):
 monkeypatch.setattr(tools_mod,'_shell_is_posix',lambda:False)
 reset_ssh_approvals()
 assert check_ssh_command_access(command,'review') is not None
 assert extract_ssh_hosts_from_command(command)==({'evil.example'},False)
 approve_hosts('review',['evil.example']);assert check_ssh_command_access(command,'review') is None

@pytest.mark.parametrize('command',[
 'echo "ok&ssh -F none evil.example"',
 'echo ok^&ssh -F none evil.example',
 'echo ^& ssh -F none evil.example',
 'echo ; ssh -F none evil.example',
])
def test_cmd_quoted_and_escaped_separators_remain_data(monkeypatch,command):
 monkeypatch.setattr(tools_mod,'_shell_is_posix',lambda:False)
 assert extract_ssh_hosts_from_command(command)==(set(),False)
