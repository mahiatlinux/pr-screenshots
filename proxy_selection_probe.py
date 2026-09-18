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
