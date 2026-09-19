import http.server
import json
import socket
import threading
from core.inference.tools import _check_code_safety, is_high_risk_tool_call

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.paths.append(self.path)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ok')
    def log_message(self, *args):
        pass

resolve = socket.getaddrinfo
def local_dns(host, port, *args, **kwargs):
    return resolve('127.0.0.1' if host == 'pypi.org' else host, port, *args, **kwargs)
socket.getaddrinfo = local_dns
with http.server.HTTPServer(('127.0.0.1', 0), Handler) as origin, http.server.HTTPServer(('127.0.0.1', 0), Handler) as proxy:
    for server in (origin, proxy):
        server.paths = []
        threading.Thread(target=server.serve_forever, daemon=True).start()
    for calls in ('run()', 'run()\nrun()'):
        code = f"import requests\ns=requests.Session()\ns.trust_env=False\ndef configure():\n    s.proxies={{'http':'http://127.0.0.1:{proxy.server_port}'}}\ndef run():\n    s.get('http://pypi.org:{origin.server_port}/',timeout=2)\n    configure()\n{calls}"
        origin.paths.clear(); proxy.paths.clear()
        blocked = _check_code_safety(code)
        prompt = is_high_risk_tool_call('python', {'code': code})
        exec(code, {})
        print(json.dumps({'calls': calls, 'blocked': blocked, 'prompt': prompt, 'origin_requests': origin.paths, 'proxy_requests': proxy.paths}))
    origin.shutdown(); proxy.shutdown()
