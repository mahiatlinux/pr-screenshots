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
listener.bind(('127.0.0.2', 22222))
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
result_before = _bash_exec(command, session_id=session, timeout=10)
assert len(connections) == 0, (result_before, connections)
exec_code = f"import os; os.execv('/usr/bin/ssh', {shlex.split(command)!r})"
exec_before = _python_exec(exec_code, session_id=session, timeout=10)
assert 'unapproved' in exec_before and len(connections) == 0, exec_before
approve_hosts(session, ['approved.example'])
proxy_code = "import paramiko; c=paramiko.SSHClient(); c.connect('approved.example', sock=paramiko.ProxyCommand('ssh -F none 127.0.0.2 -W approved.example:22'))"
proxy_result = _python_exec(proxy_code, session_id=session, timeout=10)
assert 'Blocked:' in proxy_result and len(connections) == 0, proxy_result
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
report = dict(exec_before=exec_before, exec_after=exec_after, socket_override=proxy_result, fabric_after=fabric_after, asyncssh_after=asyncssh_after, command=command, blocked_before=result_before, terminal_after=result_after, python_after=python_after, connections=len(connections), paramiko=paramiko.__version__)
print(json.dumps(report,indent=2))
assert 'pr10642-live-ssh-ok' in fabric_after, fabric_after
assert 'pr10642-live-ssh-ok' in asyncssh_after, asyncssh_after
assert report['connections'] == 5
if report['connections']:
    assert 'pr10642-live-ssh-ok' in result_after and 'timed out' not in result_after
    assert 'pr10642-live-ssh-ok' in python_after
stop.set()
listener.close()
