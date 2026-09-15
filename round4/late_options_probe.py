import json,subprocess
from core.inference.ssh_policy import check_ssh_command_access
from state.ssh_approvals import approve_hosts
approve_hosts('late-options',['approved.example'])
for command in ['ssh -F none -G approved.example -o HostName=evil.example', 'sftp -F none -o ConnectTimeout=1 approved.example -o HostName=evil.example']:
 p=subprocess.run(command.split(),text=True,capture_output=True,timeout=5)
 print(json.dumps({'command':command,'policy':check_ssh_command_access(command,'late-options'),'returncode':p.returncode,'hostname':[s for s in p.stdout.splitlines() if s.startswith('hostname ')],'stderr':p.stderr},indent=2))
