import http.server
import json
import threading
import requests
from requests.utils import select_proxy
from core.inference.tools import _check_code_safety, is_high_risk_tool_call
code="import requests\nrequests.get('https://pypi.org/', proxies={'no_proxy': '203.0.113.5'})"
print(json.dumps({'case':'no_proxy', 'selected':select_proxy('https://pypi.org/', {'no_proxy':'203.0.113.5'}), 'blocked':_check_code_safety(code),'prompt':is_high_risk_tool_call('python',{'code':code})}))
class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.paths.append(self.path)
        if self.server.redirect:
            self.send_response(302)
            self.send_header('Location','http://localhost:1/final')
            self.end_headers()
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'proxy reached after redirect')
    def log_message(self,*args):
        pass
with http.server.HTTPServer(('127.0.0.1',0),Handler) as origin, http.server.HTTPServer(('127.0.0.1',0),Handler) as proxy:
    for server,redirect in [(origin,True),(proxy,False)]:
        server.paths=[]
        server.redirect=redirect
        threading.Thread(target=server.serve_forever,daemon=True).start()
    url=f'http://127.0.0.1:{origin.server_port}/'
    proxies={'http://localhost':f'http://127.0.0.1:{proxy.server_port}'}
    response=requests.get(url,proxies=proxies,timeout=3)
    print(json.dumps({'case':'initially_unused_proxy', 'initial_selected':select_proxy(url,proxies),'status':response.status_code,'origin_requests':origin.paths,'proxy_requests':proxy.paths}))
    origin.shutdown()
    proxy.shutdown()

for removal in ["clear()", "pop('https')", "popitem()"]:
    code = "import requests\ns=requests.Session()\ns.trust_env=False\ns.proxies={'https':'http://203.0.113.5/'}\ns.proxies." + removal
    namespace = {}
    exec(code, namespace)
    print(json.dumps({'case':removal,'selected':select_proxy('https://pypi.org/', namespace['s'].proxies),'blocked':_check_code_safety(code + "\ns.get('https://pypi.org/')"),'prompt':is_high_risk_tool_call('python',{'code':code + "\ns.get('https://pypi.org/')"})}))

code = "import requests\ns=requests.Session()\ns.trust_env=False\ns.proxies={'https':'http://203.0.113.5/'}\ndel s.proxies['https']"
namespace = {}
exec(code, namespace)
print(json.dumps({'case':'del','selected':select_proxy('https://pypi.org/',namespace['s'].proxies),'blocked':_check_code_safety(code + "\ns.get('https://pypi.org/')"),'prompt':is_high_risk_tool_call('python',{'code':code + "\ns.get('https://pypi.org/')"})}))

code = "import requests\ns=requests.Session()\ns.trust_env=False\ns.proxies={'https':'http://203.0.113.5/'}\ns.proxies['https']=None"
namespace = {}
exec(code, namespace)
print(json.dumps({'case':'overwrite_none','selected':select_proxy('https://pypi.org/',namespace['s'].proxies),'blocked':_check_code_safety(code + "\ns.get('https://pypi.org/')"),'prompt':is_high_risk_tool_call('python',{'code':code + "\ns.get('https://pypi.org/')"})}))

code = "import requests\ns=requests.Session()\ns.trust_env=False\ns.proxies={'https':'http://203.0.113.5/'}\ns.proxies.update({'https':None})"
namespace = {}
exec(code, namespace)
print(json.dumps({'case':'update_none','selected':select_proxy('https://pypi.org/',namespace['s'].proxies),'blocked':_check_code_safety(code + "\ns.get('https://pypi.org/')"),'prompt':is_high_risk_tool_call('python',{'code':code + "\ns.get('https://pypi.org/')"})}))

code = "import requests\ns=requests.Session()\ns.trust_env=False\ns.proxies={'https':'https://pypi.org/'}\ns.proxies.setdefault('https','http://203.0.113.5/')"
namespace = {}
exec(code, namespace)
print(json.dumps({'case':'setdefault_existing','selected':select_proxy('https://pypi.org/',namespace['s'].proxies),'blocked':_check_code_safety(code + "\ns.get('https://pypi.org/')"),'prompt':is_high_risk_tool_call('python',{'code':code + "\ns.get('https://pypi.org/')"})}))

for invocation in ['', 'configure()']:
    code="import requests\ns=requests.Session()\ns.trust_env=False\ndef configure():\n    s.proxies={'https':'http://203.0.113.5/'}\n"+invocation
    namespace={}
    exec(code, namespace)
    checked=code+"\ns.get('https://pypi.org/')"
    print(json.dumps({'case':'helper_called' if invocation else 'helper_uncalled','selected':select_proxy('https://pypi.org/',namespace['s'].proxies),'blocked':_check_code_safety(checked),'prompt':is_high_risk_tool_call('python',{'code':checked})}))
