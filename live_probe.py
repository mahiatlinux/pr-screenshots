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
        'unused_httpx_stream': f"import httpx\ncm=httpx.stream('GET',{proxy!r})\nresponse=None",
        'unused_client_stream': f"import httpx\nc=httpx.Client()\ncm=c.stream('GET',{proxy!r})\nresponse=None\nc.close()",
        'entered_httpx_stream': f"import httpx\ncm=httpx.stream('GET',{proxy!r})\nwith cm as response:\n    response.read()",
        'entered_async_stream': f"import asyncio,httpx\nasync def fetch():\n    async with httpx.AsyncClient() as c:\n        cm=c.stream('GET',{proxy!r})\n        async with cm as response:\n            await response.aread()\n            return response\nresponse=asyncio.run(fetch())",
        'stream_base_mutation': f"import httpx\nc=httpx.Client(base_url='https://pypi.org/')\ncm=c.stream('GET','/')\nc.base_url={proxy!r}\nwith cm as response:\n    response.read()\nc.close()",
        'unused_raw_http_connection': f"import http.client\nc=http.client.HTTPConnection('127.0.0.1',port={server.server_port})\nresponse=None\nc.close()",
        'raw_http_request': f"import http.client\nc=http.client.HTTPConnection('127.0.0.1',port={server.server_port})\nc.request('GET','/')\nresponse=c.getresponse()\nresponse.read()\nc.close()",
        'deleted_instance_override': f"import requests\ns=requests.Session()\ns.proxies={{'http': {proxy!r}}}\ns.get=lambda url:url\ndel s.get\nresponse=s.get('http://pypi.org/',timeout=2)",
        'setattr_request_preexisting': f"import requests\ns=requests.Session()\nr=s.prepare_request(requests.Request('GET','http://pypi.org/'))\nsetattr(r,'url',{proxy!r})\nresponse=s.send(r,timeout=2)",
        'setattr_base_url_preexisting': f"import httpx\nc=httpx.Client()\nsetattr(c,'base_url',{proxy!r})\nresponse=c.get('/',timeout=2)",
        'unbound_proxy_mutator': f"import requests\ns=requests.Session()\ndict.update(s.proxies,{{'http': {proxy!r}}})\nresponse=s.get('http://pypi.org/',timeout=2)",
        'instance_method_override': f"import requests\ns=requests.Session()\ns.get=lambda url: url\nresponse=s.get({proxy!r})",
        'assigned_local_override': f"import requests\ndef local(self,url):\n    return url\nclass Client(requests.Session):\n    get=local\nresponse=Client().get({proxy!r})",
        'partial_network_preexisting': f"import functools,requests\nf=functools.partial(requests.get, {proxy!r})\nresponse=f(timeout=2)",
        'unused_url_pool': f"import urllib3\npool=urllib3.connection_from_url({proxy!r})\nresponse=None\npool.close()",
        'url_pool_request': f"import urllib3\npool=urllib3.connection_from_url({proxy!r})\nresponse=pool.request('GET','/',timeout=2)\npool.close()",
        'unused_proxy_factory': f"import urllib3\npool=urllib3.proxy_from_url({proxy!r})\nresponse=None\npool.clear()",
        'proxy_factory_request': f"import urllib3\npool=urllib3.proxy_from_url({proxy!r})\nresponse=pool.request('GET','http://pypi.org/',timeout=2)\npool.clear()",
        'constructor_proxy_state': f"import requests\nclass Client(requests.Session):\n    def __init__(self):\n        super().__init__()\n        self.proxies={{'http': {proxy!r}}}\nresponse=Client().get('http://pypi.org/', timeout=2)",
        'constructor_base_url_state': f"import httpx\nclass Client(httpx.Client):\n    def __init__(self):\n        super().__init__()\n        self.base_url={proxy!r}\nresponse=Client().get('/', timeout=2)",
        'attribute_request_method': f"import requests\nclass Holder: pass\no=Holder()\ns=requests.Session()\no.fetch=s.get\ns.proxies={{'http': {proxy!r}}}\nresponse=o.fetch('http://pypi.org/', timeout=2)",
        'attribute_proxy_mutator': f"import requests\nclass Holder: pass\no=Holder()\ns=requests.Session()\no.configure=s.proxies.update\no.configure({{'http': {proxy!r}}})\nresponse=s.get('http://pypi.org/', timeout=2)",
        'bound_proxy_mutator': f"import requests\ns=requests.Session()\nconfigure=s.proxies.update\nconfigure({{'http': {proxy!r}}})\nresponse=s.get('http://pypi.org/', timeout=2)",
        'bound_request_mutator': f"import requests\ns=requests.Session()\nr=s.prepare_request(requests.Request('GET','http://pypi.org/'))\nretarget=r.prepare_url\nretarget({proxy!r}, None)\nresponse=s.send(r, timeout=2)",
        'urllib_request_full_url': f"import urllib.request\nr=urllib.request.Request('http://pypi.org/')\nr.full_url={proxy!r}\nresponse=urllib.request.urlopen(r, timeout=2)",
        'urllib_request_host': f"import urllib.request\nr=urllib.request.Request('http://pypi.org/')\nr.host='127.0.0.1:{server.server_port}'\nresponse=urllib.request.urlopen(r, timeout=2)",
        'urllib_request_proxy_mutation': f"import urllib.request\nr=urllib.request.Request('http://pypi.org/')\nr.set_proxy('127.0.0.1:{server.server_port}', 'http')\nresponse=urllib.request.urlopen(r, timeout=2)",
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
        'unused_connection_pool': f"import urllib3\npool=urllib3.HTTPConnectionPool('127.0.0.1', port={server.server_port})\nresponse=None\npool.close()",
        'connection_pool_request': f"import urllib3\npool=urllib3.HTTPConnectionPool('127.0.0.1', port={server.server_port})\nresponse=pool.request('GET', '/', timeout=2)\npool.close()",
        'changed_connection_pool_host': f"import urllib3\npool=urllib3.HTTPConnectionPool('pypi.org', port={server.server_port})\npool.host='127.0.0.1'\nresponse=pool.request('GET', '/', timeout=2)\npool.close()",
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
