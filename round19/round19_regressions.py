import pytest
from core.inference.tools import _check_code_safety
from state.ssh_approvals import approve_hosts,reset_ssh_approvals

@pytest.mark.parametrize('code',[
 "import paramiko\nclass D:\n def deploy(self,client): client.connect(hostname='evil.example')\nD().deploy(paramiko.SSHClient())",
 "import paramiko\nclass D:\n def deploy(self,client): client.connect(hostname='evil.example')\nd=D(); d.deploy(paramiko.SSHClient())",
 "import paramiko\nclass D:\n @classmethod\n def deploy(cls,client): client.connect(hostname='evil.example')\nD.deploy(paramiko.SSHClient())",
 "import paramiko\nclass D:\n @staticmethod\n def deploy(client): client.connect(hostname='evil.example')\nD.deploy(paramiko.SSHClient())",
 "import paramiko\nclass D:\n @staticmethod\n def deploy(client): client.connect(hostname='evil.example')\nD().deploy(paramiko.SSHClient())",
 "import paramiko\nclass D:\n def deploy(self,client): client.connect(hostname='evil.example')\nd=D(); D.deploy(d,paramiko.SSHClient())",
 "import paramiko\nclass D:\n def deploy(self,client): client.connect(hostname='evil.example')\nd=D(); run=d.deploy; run(paramiko.SSHClient())",
 "import paramiko\ndef deploy(client): client.connect(hostname='evil.example')\nrun=deploy; run(paramiko.SSHClient())",
 "import paramiko\nclass D:\n def __init__(self,client): client.connect(hostname='evil.example')\nD(paramiko.SSHClient())",
])
def test_method_clients_require_approval(code):
 reset_ssh_approvals()
 assert _check_code_safety(code,session_id='round19') is not None
 approve_hosts('round19',['evil.example'])
 assert _check_code_safety(code,session_id='round19') is None
