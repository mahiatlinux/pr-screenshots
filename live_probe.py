import http.server
import json
import threading
from core.inference.tools import _check_code_safety, is_high_risk_tool_call
class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.requests.append(self.path)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'proxy reached')
    def log_message(self, *args):
        pass
with http.server.HTTPServer(('127.0.0.1', 0), Handler) as server:
    server.requests = []
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    proxy = f'http://127.0.0.1:{server.server_port}'
    cases = {
        'conditional_receiver': f"import requests\ns=requests.Session()\ns.proxies={{'http': {proxy!r}}}\nif False:\n    s=requests.Session()\nresponse=s.get('http://pypi.org/', timeout=2)",
        'kwargs_proxy': f"import requests\noptions={{'proxies': {{'http': {proxy!r}}}}}\nresponse=requests.get('http://pypi.org/', timeout=2, **options)",
    }
    cases.update({
        'subclass': f"import requests\nclass Client(requests.Session):\n    pass\nresponse=Client().get({proxy!r}, timeout=2)",
        'schemeless_proxy': f"import requests\nresponse=requests.get('http://pypi.org/', proxies={{'http': {proxy.removeprefix('http://')!r}}}, timeout=2)",
        'augmented_proxy': f"import requests\ns=requests.Session()\ns.proxies |= {{'http': {proxy!r}}}\nresponse=s.get('http://pypi.org/', timeout=2)",
    })
    cases.update({
        'session_alias': f"import requests\ns=requests.Session()\nalias=s\nalias.proxies={{'http': {proxy!r}}}\nresponse=s.get('http://pypi.org/', timeout=2)",
        'httpx_transport': f"import httpx\nresponse=httpx.Client(transport=httpx.HTTPTransport(proxy={proxy!r})).get('http://pypi.org/', timeout=2)",
        'lowercase_send': f"import requests\ns=requests.session()\nresponse=s.send(s.prepare_request(requests.Request('GET', {proxy!r})), timeout=2)",
        'mapping_alias': f"import requests\ns=requests.Session()\np={{}}\ns.proxies=p\np['http']={proxy!r}\nresponse=s.get('http://pypi.org/', timeout=2)",
        'bound_method': f"import requests\ns=requests.Session()\nfetch=s.get\ns.proxies={{'http': {proxy!r}}}\nresponse=fetch('http://pypi.org/', timeout=2)",
        'environment_proxy_preexisting': f"import os, requests\nos.environ['HTTP_PROXY']={proxy!r}\nresponse=requests.get('http://pypi.org/', timeout=2)",
    })
    for name, code in cases.items():
        blocked = _check_code_safety(code)
        prompt = is_high_risk_tool_call('python', {'code': code})
        server.requests.clear()
        scope = {}
        exec(code, scope)
        print(json.dumps({'case': name, 'blocked': blocked, 'prompt': prompt, 'status': scope['response'].status_code, 'proxy_requests': server.requests}))
    server.shutdown()
    thread.join()
