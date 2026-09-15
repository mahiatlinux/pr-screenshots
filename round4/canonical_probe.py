import subprocess, json
from core.inference.ssh_policy import check_ssh_command_access
from state.ssh_approvals import approve_hosts
command='ssh -F none -o CanonicalizeHostname=always -o CanonicalDomains=evil.example approved'
approve_hosts('canonical',['approved'])
proc=subprocess.run(command.split()+['-G'],text=True,capture_output=True)
print(json.dumps({'policy':check_ssh_command_access(command,'canonical'), 'returncode':proc.returncode,'hostname':[s for s in proc.stdout.splitlines() if s.startswith('hostname ')], 'stderr':proc.stderr},indent=2))
