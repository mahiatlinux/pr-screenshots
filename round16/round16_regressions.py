import pytest
from core.inference.tools import _check_code_safety
from state.ssh_approvals import approve_hosts,reset_ssh_approvals

@pytest.mark.parametrize('code',[
 "__import__('paramiko').SSHClient().connect(hostname='evil.example')",
 "import importlib; importlib.import_module('paramiko').SSHClient().connect(hostname='evil.example')",
 "from importlib import import_module as load; p=load('paramiko'); c=p.SSHClient(); c.connect(hostname='evil.example')",
 "p=__import__('paramiko'); c=p.SSHClient(); c.connect(hostname='evil.example')",
 "import importlib as il; il.import_module('asyncssh').connect('evil.example',config=None)",
 "import paramiko\nclass Pool: client=paramiko.SSHClient()\nPool.client.connect(hostname='evil.example')",
 "import paramiko\nclass Outer:\n class Pool: client=paramiko.SSHClient()\nOuter.Pool.client.connect(hostname='evil.example')",
 "import paramiko\nclass Pool: clients=[paramiko.SSHClient()]\nPool.clients[0].connect(hostname='evil.example')",
])
def test_imported_and_class_clients_require_approval(code):
 reset_ssh_approvals()
 assert _check_code_safety(code,session_id='round16') is not None
 approve_hosts('round16',['evil.example'])
 assert _check_code_safety(code,session_id='round16') is None


def test_unrelated_import_remains_allowed():
 reset_ssh_approvals()
 assert _check_code_safety("import importlib; math=importlib.import_module('math'); print(math.sqrt(4))",session_id='round16') is None
