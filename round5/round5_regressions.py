import pytest
from core.inference.tools import _check_code_safety
from state.ssh_approvals import approve_hosts, reset_ssh_approvals

@pytest.mark.parametrize('code',[
 "import asyncio; asyncio.run(asyncio.create_subprocess_exec('ssh','-F','none','approved.example'))",
 "import asyncio as a; a.run(a.create_subprocess_shell('ssh -F none approved.example'))",
 "from asyncio import create_subprocess_exec as launch; launch('ssh','-F','none','approved.example')",
 "import asyncio; launch=asyncio.create_subprocess_exec; launch('ssh','-F','none','approved.example')",
 "from asyncio.subprocess import create_subprocess_exec; create_subprocess_exec('ssh','-F','none','approved.example')",
 "import asyncio; asyncio.create_subprocess_shell(cmd='ssh -F none approved.example')",
])
def test_asyncio_requires_approval(code):
 reset_ssh_approvals()
 assert _check_code_safety(code,session_id='round5') is not None
 approve_hosts('round5',['approved.example'])
 assert _check_code_safety(code,session_id='round5') is None
