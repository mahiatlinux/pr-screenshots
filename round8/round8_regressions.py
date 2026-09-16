import pytest
from core.inference.tools import _check_code_safety
from state.ssh_approvals import approve_hosts,reset_ssh_approvals

@pytest.mark.parametrize('code',[
 "import asyncssh; asyncssh.create_connection(factory, 'approved.example', config=None)",
 "from asyncssh import create_connection as connect; connect(factory, host='approved.example', config=None)",
 "import asyncssh; asyncssh.get_server_host_key('approved.example', config=None)",
 "import asyncssh; asyncssh.get_server_auth_methods('approved.example', config=None)",
 "import paramiko\nwith paramiko.SSHClient() as client:\n client.connect(hostname='approved.example')",
 "from paramiko import SSHClient as Client\nwith Client() as client:\n client.connect(hostname='approved.example')",
])
def test_ssh_api_and_context_bindings(code):
 reset_ssh_approvals()
 assert _check_code_safety(code,session_id='round8') is not None
 approve_hosts('round8',['approved.example'])
 assert _check_code_safety(code,session_id='round8') is None
