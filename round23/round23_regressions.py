import pytest
from core.inference.tools import _check_code_safety
from state.ssh_approvals import approve_hosts,reset_ssh_approvals

@pytest.mark.parametrize('code',[
 "import paramiko\nclass Pool:\n def __init__(self): self.client=paramiko.SSHClient()\nPool().client.connect(hostname='evil.example')",
 "import paramiko\nclass Pool:\n def __init__(self): self.client=paramiko.SSHClient()\npool=Pool(); pool.client.connect(hostname='evil.example')",
 "import paramiko\nclass Pool:\n def __init__(self): self.client=paramiko.SSHClient()\npool=Pool(); alias=pool; alias.client.connect(hostname='evil.example')",
 "import paramiko\nclass Pool:\n def __init__(this): this.client=paramiko.SSHClient()\nPool().client.connect(hostname='evil.example')",
 "import paramiko\nclass Pool:\n def __init__(self,client): self.client=client\nPool(paramiko.SSHClient()).client.connect(hostname='evil.example')",
])
def test_constructed_instance_client_requires_approval(code):
 reset_ssh_approvals()
 assert _check_code_safety(code,session_id='review') is not None
 approve_hosts('review',['evil.example'])
 assert _check_code_safety(code,session_id='review') is None

def test_non_ssh_instance_is_unchanged():
 code="import paramiko\nclass Endpoint:\n def connect(self,hostname): return hostname\nclass Pool:\n def __init__(self): self.client=Endpoint()\nPool().client.connect(hostname='example.com')"
 assert _check_code_safety(code,session_id='review') is None
