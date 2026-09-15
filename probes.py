from core.inference.ssh_policy import *
from core.inference.tools import _check_code_safety, _find_blocked_commands
from state.ssh_approvals import approve_hosts
approve_hosts('probe', ['approved.example'])
commands = [
'ssh approved.example uptime',
'ssh -B approved.example unapproved.example uptime',
'ssh -F alternate.conf approved.example uptime',
'scp -o HostName=unapproved.example file approved.example:/tmp/file',
'sftp -o HostName=unapproved.example approved.example',
'find . -maxdepth 0 -exec ssh unapproved.example uptime \\;',
'ssh deploy@$TARGET uptime',
'ssh approved.example echo -n hello',
]
for x in commands: print('CLI',repr(x),extract_ssh_hosts_from_command(x),check_ssh_command_access(x,'probe'),_find_blocked_commands(x))
codes = [
"import paramiko as p; c=p.SSHClient(); c.connect(hostname='unapproved.example')",
"from paramiko import SSHClient; c=SSHClient(); c.connect(hostname='unapproved.example')",
"import paramiko, requests; paramiko.SSHClient().connect('approved.example', password=requests.get('https://unapproved.example').text)",
"import subprocess; subprocess.run(['ssh', target, 'approved.example'])",
"import subprocess; subprocess.run(['env', 'ssh', 'unapproved.example'])",
"import paramiko; t=paramiko.Transport(('unapproved.example', 22)); t.connect(username='user')",
]
for x in codes: print('PY',repr(x),extract_ssh_hosts_from_python(x),_check_code_safety(x,session_id='probe'))
