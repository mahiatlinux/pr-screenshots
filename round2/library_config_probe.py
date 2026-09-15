import asyncio, json
from pathlib import Path
import fabric, asyncssh
from core.inference.ssh_policy import check_ssh_python_access
from state.ssh_approvals import approve_hosts
config=Path.home()/'.ssh/config'
config.parent.mkdir(exist_ok=True)
config.write_text('Host approved.example\n  HostName 127.0.0.2\n')
config.chmod(0o600)
try:
    unsafe_fabric = fabric.Connection('approved.example')
    safe_fabric = fabric.Connection('approved.example', config=fabric.Config(lazy=True))
    async def inspect():
        unsafe = await asyncssh.SSHClientConnectionOptions.construct(host='approved.example', config=())
        safe = await asyncssh.SSHClientConnectionOptions.construct(host='approved.example', config=None)
        return unsafe.host, safe.host
    unsafe_async, safe_async=asyncio.run(inspect())
    assert unsafe_fabric.host == unsafe_async == '127.0.0.2'
    assert safe_fabric.host == safe_async == 'approved.example'
    approve_hosts('library-config', ['approved.example'])
    report={'fabric':fabric.__version__,'asyncssh':asyncssh.__version__,'default_fabric':unsafe_fabric.host,'configured_asyncssh':unsafe_async,'disabled_fabric':safe_fabric.host,'disabled_asyncssh':safe_async}
    for name,code in [('fabric', "import fabric; fabric.Connection('approved.example')"),('asyncssh', "import asyncssh; asyncssh.connect('approved.example')")]:
        report[name+'_policy'] = check_ssh_python_access(code, 'library-config')
    assert report['fabric_policy'] and report['asyncssh_policy']
    assert check_ssh_python_access("import fabric; fabric.Connection('approved.example', config=fabric.Config(lazy=True))", 'library-config') is None
    assert check_ssh_python_access("import asyncssh; asyncssh.connect('approved.example', config=None)", 'library-config') is None
    print(json.dumps(report,indent=2))
finally:
    config.unlink()
