import pytest
from core.inference.ssh_policy import extract_ssh_hosts_from_command

@pytest.mark.parametrize('command',[
 'watch -n 60 ssh -F none evil.example',
 'timeout 1s ssh -F none evil.example',
 'timeout 0.5m ssh -F none evil.example',
 'watch --interval 60 ssh -F none evil.example',
 "watch -n 60 'ssh -F none evil.example'",
 'env TERM=xterm watch -t -n 60 ssh -F none evil.example',
 'strace -o trace.log ssh -F none evil.example',
 'perf stat ssh -F none evil.example',
 'parallel ssh -F none evil.example ::: uptime',
 'watch -n 60 git ls-remote ssh://evil.example/repo',
])
def test_forwarding_launcher_gates_ssh(command):
 hosts,dynamic=extract_ssh_hosts_from_command(command)
 assert hosts or dynamic

@pytest.mark.parametrize('command',[
 "printf '%s' 'watch -n 60 ssh -F none evil.example'",
 'watch -n 60 uptime',
 "watch -n 0.5 printf '%s' 'ssh -F none evil.example'",
 'find . -name ssh',
 'printf watch ssh',
])
def test_forwarding_data_is_unchanged(command):
 assert extract_ssh_hosts_from_command(command)==(set(),False)
