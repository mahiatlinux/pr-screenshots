import pytest
from core.inference.tools import _check_code_safety
from state.ssh_approvals import approve_hosts,reset_ssh_approvals

@pytest.mark.parametrize('code',[
 "import subprocess; subprocess.run(**{'args':['ssh','-F','none','approved.example']})",
 "import subprocess; subprocess.run(**{**{'args':['ssh','-F','none','approved.example']}})",
 "import asyncio; asyncio.run(asyncio.create_subprocess_shell(**{'cmd':'ssh -F none approved.example'}))",
 "import paramiko; paramiko.ProxyCommand(**{'command_line':'ssh -F none approved.example'})",
])
def test_keyword_dictionary_commands_require_approval(code):
 reset_ssh_approvals()
 assert _check_code_safety(code,session_id='round10') is not None
 approve_hosts('round10',['approved.example'])
 assert _check_code_safety(code,session_id='round10') is None
