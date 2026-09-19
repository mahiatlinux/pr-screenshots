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
        'unused_httpx_base_url': f"import httpx\nclient=httpx.Client(base_url={proxy!r})\nresponse=client.base_url\nclient.close()",
        'relative_httpx_base_url': f"import httpx\nclient=httpx.Client(base_url={proxy!r})\nresponse=client.get('/', timeout=2)\nclient.close()",
        'prepared_url_method': f"import requests\ns=requests.Session()\nr=s.prepare_request(requests.Request('GET', 'https://pypi.org/'))\nr.prepare_url({proxy!r}, None)\nresponse=s.send(r, timeout=2)",
        'httpx_base_reassignment': f"import httpx\nclient=httpx.Client()\nclient.base_url={proxy!r}\nresponse=client.get('/', timeout=2)\nclient.close()",
        'unused_httpx_proxy': f"import httpx\nclient=httpx.Client(proxy={proxy!r})\nresponse=None\nclient.close()",
        'mounted_httpx_proxy': f"import httpx\nt=httpx.HTTPTransport(proxy={proxy!r})\nclient=httpx.Client(mounts={{'http://': t}})\nresponse=client.get('http://pypi.org/', timeout=2)\nclient.close()",
        'direct_httpx_transport': f"import httpx\nt=httpx.HTTPTransport(proxy={proxy!r})\nresponse=t.handle_request(httpx.Request('GET','http://pypi.org/'))\nresponse.read()\nt.close()",
        'aiohttp_network_path': f"import asyncio,aiohttp\nasync def fetch():\n    async with aiohttp.ClientSession(base_url='http://pypi.org/') as client:\n        async with client.get('//127.0.0.1:{server.server_port}/path') as result:\n            await result.read()\n            return result\nresponse=asyncio.run(fetch())",
        'unbound_request': f"import requests\ns=requests.Session()\nresponse=requests.Session.request(s, 'GET', {proxy!r}, timeout=2)",
        'unbound_proxy': f"import requests\ns=requests.Session()\ns.proxies={{'http': {proxy!r}}}\nresponse=requests.Session.get(s, 'http://pypi.org/', timeout=2)",
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
        'super_method': f"import requests\nclass Client(requests.Session):\n    def fetch(self):\n        return super().get({proxy!r}, timeout=2)\nresponse=Client().fetch()",
        'explicit_super_method': f"import requests\nclass Client(requests.Session):\n    def fetch(self):\n        return super(Client, self).get({proxy!r}, timeout=2)\nresponse=Client().fetch()",
        'getattr_proxy': f"import requests\ns=requests.Session()\ns.proxies={{'http': {proxy!r}}}\nresponse=getattr(s, 'get')('http://pypi.org/', timeout=2)",
        'initial_proxy_alias': f"import requests\ns=requests.Session()\np=s.proxies\np['http']={proxy!r}\nresponse=s.get('http://pypi.org/', timeout=2)",
        'prepared_url_mutation': f"import requests\ns=requests.Session()\nr=s.prepare_request(requests.Request('GET', 'http://pypi.org/'))\nr.url={proxy!r}\nresponse=s.send(r, timeout=2)",
        'first_mixin_override': f"import requests\nclass Local:\n    def get(self, url):\n        return url\nclass Client(Local, requests.Session):\n    pass\nresponse=Client().get({proxy!r})",
        'mixin_ancestor_control': f"import requests\nclass Local:\n    def get(self, url):\n        return url\nclass First(Local):\n    pass\nclass Second(requests.Session, Local):\n    pass\nclass Client(First, Second):\n    pass\nresponse=Client().get({proxy!r}, timeout=2)",
        'setattr_proxy_preexisting': f"import requests\ns=requests.Session()\nsetattr(s, 'proxies', {{'http': {proxy!r}}})\nresponse=s.get('http://pypi.org/', timeout=2)",
        'environment_proxy_preexisting': f"import os, requests\nos.environ['HTTP_PROXY']={proxy!r}\nresponse=requests.get('http://pypi.org/', timeout=2)",
    })
    for name, code in cases.items():
        blocked = _check_code_safety(code)
        prompt = is_high_risk_tool_call('python', {'code': code})
        server.requests.clear()
        scope = {}
        exec(code, scope)
        print(json.dumps({'case': name, 'blocked': blocked, 'prompt': prompt, 'status': getattr(scope['response'], 'status_code', getattr(scope['response'], 'status', None)), 'proxy_requests': server.requests}))
    server.shutdown()
    thread.join()
