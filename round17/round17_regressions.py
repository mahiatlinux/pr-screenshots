import pytest
from core.inference.tools import _check_code_safety
from state.ssh_approvals import approve_hosts,reset_ssh_approvals

@pytest.mark.parametrize('code',[
 "import functools,paramiko; make=functools.partial(paramiko.SSHClient); make().connect(hostname='evil.example')",
 "from functools import partial as bind; import paramiko; make=bind(paramiko.SSHClient); c=make(); c.connect(hostname='evil.example')",
 "import functools,asyncssh; connect=functools.partial(asyncssh.connect,'evil.example',config=None); connect()",
 "import functools,paramiko; c=paramiko.SSHClient(); connect=functools.partial(c.connect,hostname='evil.example'); connect()",
 "import functools,paramiko; c=paramiko.SSHClient(); connect=functools.partial(c.connect,hostname='approved.example'); connect(hostname='evil.example')",
 "import functools,paramiko; functools.partial(paramiko.SSHClient)().connect(hostname='evil.example')",
 "import functools,fabric; connect=functools.partial(fabric.Connection,'evil.example',config=fabric.Config(lazy=True)); connect()",
])
def test_partial_ssh_requires_approval(code):
 reset_ssh_approvals();approve_hosts('round17',['approved.example'])
 assert _check_code_safety(code,session_id='round17') is not None
 approve_hosts('round17',['evil.example'])
 assert _check_code_safety(code,session_id='round17') is None


def test_partial_keyword_override_uses_actual_host():
 reset_ssh_approvals();approve_hosts('round17',['approved.example'])
 code="import functools,paramiko; c=paramiko.SSHClient(); connect=functools.partial(c.connect,hostname='evil.example'); connect(hostname='approved.example')"
 assert _check_code_safety(code,session_id='round17') is None


def test_unrelated_partial_remains_allowed():
 reset_ssh_approvals()
 assert _check_code_safety("import functools; print(functools.partial(pow,2)(3))",session_id='round17') is None
