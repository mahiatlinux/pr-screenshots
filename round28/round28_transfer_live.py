import sys
import io
import stat
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

payload=b'pr10642-scp-file-ok\n'
class Files(paramiko.SFTPServerInterface):
    def stat(self,path):
        attrs=paramiko.SFTPAttributes();attrs.st_mode=stat.S_IFREG|0o644;attrs.st_size=len(payload);return attrs
    lstat=stat
    def open(self,path,flags,attr):
        handle=paramiko.SFTPHandle(flags);handle.readfile=io.BytesIO(payload);handle.stat=lambda:self.stat(path);return handle

class TransferServer(paramiko.SFTPServer):
    def start_subsystem(self,name,transport,channel):
        super().start_subsystem(name,transport,channel)
        channel.send_exit_status(0)

def serve_client(sock):
    transport = paramiko.Transport(sock)
    transport.add_server_key(host_key)
    transport.set_subsystem_handler("sftp",TransferServer,Files)
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
for target in ['copied','file@approved.example']:
    (root/target).unlink(missing_ok=True)
command = f'ssh -F none -p {port} -i review-key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o IdentitiesOnly=yes review@127.0.0.2 uptime'
approve_hosts(session,['approved.example'])
args=['-F','none','-P',str(port),'-i','review-key','-o','StrictHostKeyChecking=no','-o','UserKnownHostsFile=/dev/null','-o','LogLevel=ERROR','-o','IdentitiesOnly=yes']
scp_command=shlex.join(['scp',*args,'review@127.0.0.2:/tmp/file@approved.example','./copied'])
sftp_command=shlex.join(['sftp',*args,'review@127.0.0.2:/tmp/file@approved.example'])
results={name:_bash_exec(cmd,session_id=session,timeout=5) for name,cmd in [('scp',scp_command),('sftp',sftp_command)]}
print(json.dumps({'before':results,'connections':len(connections),'copied':(root/'copied').read_text() if (root/'copied').exists() else None}),flush=True)
assert all('Blocked' in result for result in results.values()) and not connections
if '--base' in sys.argv:
    stop.set();listener.close();raise SystemExit(0)
approve_hosts(session,['127.0.0.2'])
results={name:_bash_exec(cmd,session_id=session,timeout=5) for name,cmd in [('scp',scp_command),('sftp',sftp_command)]}
print(json.dumps({'after':results,'connections':len(connections),'copied':(root/'copied').read_text()}),flush=True)
assert all('Exit code' not in result for result in results.values())
assert len(connections)==2 and (root/'copied').read_bytes()==payload
assert (root/'file@approved.example').read_bytes()==payload
stop.set();listener.close()
