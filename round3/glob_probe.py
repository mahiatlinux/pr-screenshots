import json, subprocess, tempfile
from pathlib import Path
from core.inference.ssh_policy import check_ssh_command_access, collect_ssh_hosts_for_approval
from state.ssh_approvals import approve_hosts
with tempfile.TemporaryDirectory() as directory:
    (Path(directory)/'evil.example').touch()
    expanded=subprocess.check_output(['bash','-c',"printf '%s\n' *"],cwd=directory,text=True).strip()
    assert expanded == 'evil.example'
    command='ssh -F none *'
    approve_hosts('glob-live',collect_ssh_hosts_for_approval('terminal',{'command':command}))
    refusal=check_ssh_command_access(command,'glob-live')
    assert refusal is not None
    print(json.dumps({'bash_expansion':expanded,'tool_policy':refusal},indent=2))
