import pytest
from core.inference.tools import _check_code_safety
from state.ssh_approvals import approve_hosts,reset_ssh_approvals

@pytest.mark.parametrize('assignment',[
 'client=next(iter([paramiko.SSHClient()]))',
 'pool=[paramiko.SSHClient()]; iterator=iter(pool); client=next(iterator)',
 'pick=next; iterate=iter; client=pick(iterate([paramiko.SSHClient()]))',
 'import builtins as b; client=b.next(b.iter([paramiko.SSHClient()]))',
 'from builtins import next as pick, iter as iterate; client=pick(iterate([paramiko.SSHClient()]))',
 'client=next(reversed([paramiko.SSHClient()]))',
 'client=next(iter([]),paramiko.SSHClient())',
])
def test_iterator_client_requires_approval(assignment):
 reset_ssh_approvals()
 code='import paramiko\n'+assignment+"\nclient.connect(hostname='evil.example')"
 assert _check_code_safety(code,session_id='review') is not None
 approve_hosts('review',['evil.example'])
 assert _check_code_safety(code,session_id='review') is None

def test_opaque_iterator_fails_closed():
 assert _check_code_safety("import paramiko; client=next(iterator); client.connect(hostname='evil.example')",session_id='review') is not None

def test_ordinary_iterator_is_unchanged():
 assert _check_code_safety("import paramiko; result=next(iter([1,2])); print(result)",session_id='review') is None
