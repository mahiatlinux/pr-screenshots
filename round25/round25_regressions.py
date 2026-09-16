import pytest
from core.inference.tools import _check_code_safety
from state.ssh_approvals import approve_hosts,reset_ssh_approvals

@pytest.mark.parametrize('assignment',[
 'client=min([paramiko.SSHClient()])',
 'pool=[paramiko.SSHClient()]; client=min(pool)',
 'client=max([paramiko.SSHClient()])',
 'pool=[paramiko.SSHClient()]; client=pool.pop()',
 'import random; client=random.choice([paramiko.SSHClient()])',
 'import operator; client=operator.itemgetter(0)([paramiko.SSHClient()])',
 'import copy; original=paramiko.SSHClient(); client=copy.copy(original)',
])
def test_unknown_client_selection_fails_closed(assignment):
 reset_ssh_approvals()
 code='import paramiko\n'+assignment+"\nclient.connect(hostname='evil.example')"
 assert _check_code_safety(code,session_id='review') is not None
 approve_hosts('review',['evil.example'])
 assert _check_code_safety(code,session_id='review') is not None

def test_known_identity_helper_remains_supported():
 code="import paramiko\ndef identity(client): return client\nselected=identity(paramiko.SSHClient())\nselected.connect(hostname='evil.example')"
 reset_ssh_approvals()
 assert _check_code_safety(code,session_id='review') is not None
 approve_hosts('review',['evil.example'])
 assert _check_code_safety(code,session_id='review') is None

def test_ordinary_selection_is_unchanged():
 assert _check_code_safety('import paramiko; result=min([1,2]); print(result)',session_id='review') is None
