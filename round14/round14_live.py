import json
import shlex
import socket
import threading
import time
from pathlib import Path
import paramiko
from core.inference.tools import _bash_exec, _python_exec, _get_workdir

try:
    from state.ssh_approvals import approve_hosts
except ImportError:
    approve_hosts = lambda *args: None

host_key = paramiko.RSAKey.generate(2048)
client_key = paramiko.RSAKey.generate(2048)
listener = socket.socket()
listener.bind(('0.0.0.0', 22222))
listener.listen()
listener.settimeout(.1)
port = listener.getsockname()[1]
connections = []
stop = threading.Event()

class Server(paramiko.ServerInterface):
    def check_auth_publickey(self, username, key):
        return paramiko.AUTH_SUCCESSFUL if key == client_key else paramiko.AUTH_FAILED
    def check_auth_password(self, username, password):
        return paramiko.AUTH_SUCCESSFUL
    def get_allowed_auths(self, username):
        return 'publickey,password'
    def check_channel_request(self, kind, chanid):
        return paramiko.OPEN_SUCCEEDED
    def check_channel_exec_request(self, channel, command):
        def reply():
            channel.send(b'pr10642-live-ssh-ok\n')
            channel.send_exit_status(0)
            channel.shutdown_write()
            time.sleep(.1)
            channel.close()
        threading.Thread(target=reply, daemon=True).start()
        return True

def serve_client(sock):
    transport = paramiko.Transport(sock)
    transport.add_server_key(host_key)
    transport.set_subsystem_handler("sftp",paramiko.SFTPServer,paramiko.SFTPServerInterface)
    try:
        transport.start_server(server=Server())
        channel = transport.accept(8)
        if channel:
            while transport.is_active() and not stop.wait(.05):
                pass
    except Exception as exc:
        print(type(exc).__name__, str(exc))
    finally:
        transport.close()

def serve():
    while not stop.is_set():
        try:
            sock, addr = listener.accept()
        except socket.timeout:
            continue
        connections.append(addr)
        threading.Thread(target=serve_client,args=(sock,),daemon=True).start()
threading.Thread(target=serve,daemon=True).start()
session = 'ssh-live'
root = Path(_get_workdir(session))
client_key.write_private_key_file(str(root/'review-key'))
(root/'review-key').chmod(0o600)
command = f'ssh -F none -p {port} -i review-key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o IdentitiesOnly=yes review@127.0.0.2 uptime'
approve_hosts(session,['127.0.0.2'])
nested_command=command.replace('127.0.0.2','127.0.0.3')
sftp_argv=['sftp','-F','none','-P',str(port),'-i','review-key','-o','StrictHostKeyChecking=no','-o','UserKnownHostsFile=/dev/null','-o','LogLevel=ERROR','review@127.0.0.2']
input_text='!'+nested_command+'\nquit\n'
sftp_base=shlex.join(sftp_argv)
sftp_batch=shlex.join(sftp_argv[:-1]+['-b','-',sftp_argv[-1]])
sftp_cases={'batch':"printf %s "+shlex.quote(input_text)+" | "+sftp_batch,'stdin':"printf %s "+shlex.quote(input_text)+" | "+sftp_base}
sftp_results={name:_bash_exec(cmd,session_id=session,timeout=10) for name,cmd in sftp_cases.items()}
python_sftp=f"import subprocess; subprocess.run({sftp_argv!r},input={input_text!r},text=True)"
sftp_results['python_input']=_python_exec(python_sftp,session_id=session,timeout=10)
print('sftp results:',json.dumps(sftp_results),'connections:',len(connections),flush=True)
assert len(connections)==0 and all('Blocked' in value for value in sftp_results.values()),sftp_results
from state.ssh_approvals import reset_ssh_approvals
reset_ssh_approvals()
result_before = _bash_exec(command, session_id=session, timeout=10)
assert len(connections)==0,(result_before,connections)
exec_code = f"import os; os.execv('/usr/bin/ssh', {shlex.split(command)!r})"
exec_before = _python_exec(exec_code, session_id=session, timeout=10)
assert 'unapproved' in exec_before and len(connections) == 0, exec_before
approve_hosts(session, ['approved.example'])
proxy_code = "import paramiko; c=paramiko.SSHClient(); c.connect('approved.example', sock=paramiko.ProxyCommand('ssh -F none 127.0.0.2 -W approved.example:22'))"
proxy_result = _python_exec(proxy_code, session_id=session, timeout=10)
assert 'Blocked:' in proxy_result and len(connections) == 0, proxy_result
launcher_code = f"import subprocess; launch=subprocess.run; launch({shlex.split(command)!r}, check=True)"
helper_code = f"import paramiko\ndef make():\n return paramiko.SSHClient()\nc=make()\nc.set_missing_host_key_policy(paramiko.AutoAddPolicy())\nc.connect('127.0.0.2', port={port}, username='review', password='disposable', allow_agent=False, look_for_keys=False)\n_, out, _ = c.exec_command('uptime')\nprint(out.read().decode())\nc.close()"
transport_code = f"from paramiko.transport import Transport; t=Transport(('127.0.0.2', {port})); t.connect(username='review', password='disposable'); c=t.open_session(); c.exec_command('uptime'); print(c.recv(4096).decode()); t.close()"
async_exec_call = "asyncio.create_subprocess_exec(" + ', '.join(repr(part) for part in shlex.split(command)) + ", stdout=asyncio.subprocess.PIPE)"
async_shell_call = f"asyncio.create_subprocess_shell({command!r}, stdout=asyncio.subprocess.PIPE)"
def async_code(call):
    return f"import asyncio\nasync def main():\n p = await {call}\n out, _ = await p.communicate()\n print(out.decode())\nasyncio.run(main())"
indirect_codes = {'launcher': launcher_code, 'helper': helper_code, 'qualified_transport': transport_code, 'async_exec': async_code(async_exec_call), 'async_shell': async_code(async_shell_call)}
alias_factory_code = helper_code.replace("def make():\n return paramiko.SSHClient()\nc=make()", "Factory=paramiko.SSHClient\nc=Factory()")
alias_method_code = alias_factory_code.replace("c.connect(", "connect=c.connect\nconnect(")
alias_async_code = f"import asyncio, asyncssh\nconnect=asyncssh.connect\nasync def main():\n async with connect('127.0.0.2', port={port}, config=None, username='review', password='disposable', known_hosts=None) as c:\n  result=await c.run('uptime')\n  print(result.stdout)\nasyncio.run(main())"
indirect_codes.update(factory_alias=alias_factory_code, bound_method_alias=alias_method_code, asyncssh_alias=alias_async_code)
indirect_codes['proxy_command'] = f"import paramiko; proxy=paramiko.ProxyCommand({command!r}); print(proxy.recv(20)); proxy.close()"
context_body = helper_code[helper_code.index('c.set_missing_host_key_policy'):].replace("c.connect('127.0.0.2',", "c.connect(hostname='127.0.0.2',")
context_code = "import paramiko\nwith paramiko.SSHClient() as c:\n" + '\n'.join(' '+line for line in context_body.splitlines())
create_code = f"import asyncio,asyncssh\nasync def main():\n c, client = await asyncssh.create_connection(asyncssh.SSHClient, '127.0.0.2', port={port}, config=None, username='review', password='disposable', known_hosts=None)\n result = await c.run('uptime')\n print(result.stdout)\n c.close()\n await c.wait_closed()\nasyncio.run(main())"
key_code = f"import asyncio,asyncssh; key=asyncio.run(asyncssh.get_server_host_key('127.0.0.2', port={port}, config=None)); print('pr10642-live-ssh-ok' if key is not None else 'failed')"
auth_code = f"import asyncio,asyncssh; methods=asyncio.run(asyncssh.get_server_auth_methods('127.0.0.2', port={port}, username='review', config=None)); print('pr10642-live-ssh-ok' if 'password' in methods else 'failed')"
indirect_codes.update(context_client=context_code, asyncssh_create=create_code, asyncssh_host_key=key_code, asyncssh_auth_methods=auth_code)
kwargs_subprocess = f"import subprocess; subprocess.run(**{{'args':{shlex.split(command)!r},'check':True}})"
kwargs_proxy = f"import paramiko; proxy=paramiko.ProxyCommand(**{{'command_line':{command!r}}}); print(proxy.recv(20)); proxy.close()"
kwargs_async = async_code(f"asyncio.create_subprocess_shell(**{{'cmd':{command!r}}}, stdout=asyncio.subprocess.PIPE)")
indirect_codes.update(kwargs_subprocess=kwargs_subprocess, kwargs_proxy=kwargs_proxy, kwargs_async=kwargs_async)
subclass_code = alias_factory_code.replace('Factory=paramiko.SSHClient', 'class Factory(paramiko.SSHClient): pass').replace("c.connect('127.0.0.2',", "c.connect(hostname='127.0.0.2',")
super_code = f"import paramiko\nclass Client(paramiko.SSHClient):\n def connect(self, hostname):\n  return super().connect(hostname='127.0.0.2', port={port}, username='review', password='disposable', allow_agent=False, look_for_keys=False)\nc=Client()\nc.set_missing_host_key_policy(paramiko.AutoAddPolicy())\nc.connect(hostname='approved.example')\n_, out, _=c.exec_command('uptime')\nprint(out.read().decode())\nc.close()"
super_transport_code = f"import paramiko\nclass Transport(paramiko.Transport):\n def __init__(self, address):\n  super().__init__(('127.0.0.2', {port}))\nt=Transport(('approved.example',22)); t.connect(username='review',password='disposable'); c=t.open_session(); c.exec_command('uptime'); print(c.recv(4096).decode()); t.close()"
indirect_codes.update(subclass_client=subclass_code, subclass_override=super_code, subclass_transport=super_transport_code)
lambda_code = helper_code.replace("def make():\n return paramiko.SSHClient()", "make=lambda: paramiko.SSHClient()").replace("c.connect('127.0.0.2',", "c.connect(hostname='127.0.0.2',")
indirect_codes['lambda_client'] = lambda_code
indirect_codes['inline_lambda'] = lambda_code.replace('make=lambda: paramiko.SSHClient()\nc=make()', 'c=(lambda: paramiko.SSHClient())()')
for group in ['SerialGroup','ThreadingGroup']:
 indirect_codes[group] = f"import fabric; g=fabric.{group}('127.0.0.2',port={port},user='review',config=fabric.Config(lazy=True),connect_kwargs={{'password':'disposable','allow_agent':False,'look_for_keys':False}}); result=g.run('uptime',hide=True); print([r.stdout for r in result.values()]); g.close()"
container_code = alias_factory_code.replace('c=Factory()', 'clients=[Factory()]\nc=clients[0]').replace("c.connect('127.0.0.2',", "c.connect(hostname='127.0.0.2',")
container_before = _python_exec(container_code,session_id=session,timeout=10)
print('container before:',container_before,'connections:',len(connections),flush=True)
scp_command=f"printf '%s\\n' 'review@127.0.0.2:/dest' | xargs scp -3 -F none -P {port} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR approved.example:/source"
xargs_before=_bash_exec(scp_command,session_id=session,timeout=10)
print('xargs before:',xargs_before,'connections:',len(connections),flush=True)
assert len(connections)==0 and 'Blocked' in container_before and 'Blocked' in xargs_before
indirect_codes['container_client']=container_code
indirect_codes['container_transport']=transport_code.replace("t=Transport(('127.0.0.2', "+str(port)+"))", "clients=[Transport(('127.0.0.2', "+str(port)+"))]; t=clients[0]")
named_client_code=alias_factory_code.replace('c=Factory()', '(c:=Factory())').replace("c.connect('127.0.0.2',", "c.connect(hostname='127.0.0.2',")
indirect_codes['named_client']=named_client_code
heredoc_before=_bash_exec("bash -s <<'EOF'\n"+command+"\nEOF",session_id=session,timeout=10)
print('heredoc before:',heredoc_before,'connections:',len(connections),flush=True)
indirect_before = {name: _python_exec(code, session_id=session, timeout=10) for name, code in indirect_codes.items()}
assert len(connections)==0 and all('unapproved' in result for result in indirect_before.values()),indirect_before
approve_hosts(session, ['approved@127.0.0.2'])
multi_user_command = command.replace('review@127.0.0.2', 'review@approved@127.0.0.2')
coproc_command = 'coproc ' + command + '; pid=$COPROC_PID; cat <&"${COPROC[0]}"; wait "$pid"'
terminal_cases = {'multiple_at':multi_user_command, 'coproc':coproc_command, 'heredoc': "bash -s <<'EOF'\n"+command+"\nEOF"}
terminal_before = {name:_bash_exec(cmd,session_id=session,timeout=10) for name,cmd in terminal_cases.items()}
assert len(connections) == 0 and all('unapproved' in value for value in terminal_before.values()), terminal_before
approve_hosts(session, ['127.0.0.2'])
result_after = _bash_exec(command, session_id=session, timeout=10)
code = f"import paramiko\nc = paramiko.SSHClient()\nc.set_missing_host_key_policy(paramiko.AutoAddPolicy())\nc.connect('127.0.0.2', port={port}, username='review', password='disposable', allow_agent=False, look_for_keys=False)\n_, out, _ = c.exec_command('uptime')\nprint(out.read().decode())\nc.close()"
python_after = _python_exec(code, session_id=session, timeout=10)
fabric_code = f"import fabric; c = fabric.Connection('127.0.0.2', port={port}, user='review', config=fabric.Config(lazy=True), connect_kwargs={{'password': 'disposable', 'allow_agent': False, 'look_for_keys': False}}); print(c.run('uptime', hide=True).stdout); c.close()"
fabric_after = _python_exec(fabric_code, session_id=session, timeout=10)
asyncssh_code = f"import asyncio, asyncssh\nasync def main():\n    async with asyncssh.connect('127.0.0.2', port={port}, config=None, username='review', password='disposable', known_hosts=None) as c:\n        result = await c.run('uptime')\n        print(result.stdout)\nasyncio.run(main())"
asyncssh_after = _python_exec(asyncssh_code, session_id=session, timeout=10)
exec_after = _python_exec(exec_code, session_id=session, timeout=10)
assert 'pr10642-live-ssh-ok' in exec_after, exec_after
indirect_after = {name: _python_exec(code, session_id=session, timeout=10) for name, code in indirect_codes.items()}
assert all('pr10642-live-ssh-ok' in result for result in indirect_after.values()), indirect_after
terminal_after_cases = {name:_bash_exec(cmd,session_id=session,timeout=10) for name,cmd in terminal_cases.items()}
assert all('pr10642-live-ssh-ok' in value and 'Exit code' not in value for value in terminal_after_cases.values()), terminal_after_cases
report = dict(terminal_before_cases=terminal_before, terminal_after_cases=terminal_after_cases, indirect_before=indirect_before, indirect_after=indirect_after, exec_before=exec_before, exec_after=exec_after, socket_override=proxy_result, fabric_after=fabric_after, asyncssh_after=asyncssh_after, command=command, blocked_before=result_before, terminal_after=result_after, python_after=python_after, connections=len(connections), paramiko=paramiko.__version__)
print(json.dumps(report,indent=2))
assert 'pr10642-live-ssh-ok' in fabric_after, fabric_after
assert 'pr10642-live-ssh-ok' in asyncssh_after, asyncssh_after
assert report['connections'] == 34
if report['connections']:
    assert 'pr10642-live-ssh-ok' in result_after and 'timed out' not in result_after
    assert 'pr10642-live-ssh-ok' in python_after
stop.set()
listener.close()
