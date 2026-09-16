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
direct_result=_bash_exec(sftp_base,session_id=session,timeout=10)
print('direct approved sftp:',direct_result,'connections:',len(connections),flush=True)
assert len(connections)==1 and 'Connected to 127.0.0.2' in direct_result and 'Exit code' not in direct_result
stop.set();listener.close()
