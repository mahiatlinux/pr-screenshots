import http.server
import json
import select
import socket
import socketserver
import threading
from core.inference.tools import _check_code_safety,is_high_risk_tool_call

class Origin(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.requests.append((self.command,self.path,''))
        self.reply()
    def do_POST(self):
        body=self.rfile.read(int(self.headers.get('Content-Length',0))).decode()
        self.server.requests.append((self.command,self.path,body))
        self.reply()
    def reply(self):
        self.send_response(200);self.send_header('Content-Length','2');self.end_headers();self.wfile.write(b'ok')
    def log_message(self,*args):pass

class Tunnel(socketserver.StreamRequestHandler):
    def handle(self):
        line=self.rfile.readline().decode().strip()
        while self.rfile.readline() not in (b'\r\n',b'\n',b''):pass
        self.server.connects.append(line)
        host,port=line.split()[1].rsplit(':',1)
        with socket.create_connection((host,int(port))) as remote:
            self.wfile.write(b'HTTP/1.1 200 Connection Established\r\n\r\n');self.wfile.flush()
            while True:
                readable,_,_=select.select([self.connection,remote],[],[],3)
                if not readable:return
                for source in readable:
                    data=source.recv(65536)
                    if not data:return
                    (remote if source is self.connection else self.connection).sendall(data)

resolve=socket.getaddrinfo
socket.getaddrinfo=lambda host,port,*args,**kwargs:resolve('127.0.0.1' if host=='pypi.org' else host,port,*args,**kwargs)
with http.server.ThreadingHTTPServer(('127.0.0.1',0),Origin) as origin, socketserver.ThreadingTCPServer(('127.0.0.1',0),Tunnel) as proxy:
    origin.requests=[];proxy.connects=[]
    for server in (origin,proxy):threading.Thread(target=server.serve_forever,daemon=True).start()
    destination=f'http://127.0.0.1:{origin.server_port}/'
    allowed=f'http://pypi.org:{origin.server_port}/'
    cases={
      'tunnel_preexisting':f"import http.client\nc=http.client.HTTPConnection('pypi.org', {proxy.server_address[1]},timeout=2)\nc.set_tunnel('127.0.0.1',{origin.server_port})\nc.request('GET','/')\nresponse=c.getresponse()\nresponse.read()\nc.close()",
      'unused_aiohttp':f"import aiohttp,asyncio\nasync def run():\n    async with aiohttp.ClientSession() as c:\n        pending=c.get({destination!r})\n        pending.close()\nresponse=asyncio.run(run())",
      'awaited_aiohttp':f"import aiohttp,asyncio\nasync def run():\n    async with aiohttp.ClientSession() as c:\n        pending=c.get({destination!r})\n        result=await pending\n        await result.read()\n        return result\nresponse=asyncio.run(run())",
      'entered_aiohttp_module':f"import aiohttp,asyncio\nasync def run():\n    async with aiohttp.request('GET',{destination!r}) as result:\n        await result.read()\n        return result\nresponse=asyncio.run(run())",
      'unused_request_builder':f"import requests\ns=requests.Session()\ns.trust_env=False\nr=s.prepare_request(requests.Request('POST',{allowed!r},data=b'x'))\nresponse=None",
      'sent_request_builder':f"import requests\ns=requests.Session()\ns.trust_env=False\nr=s.prepare_request(requests.Request('POST',{allowed!r},data=b'x'))\nresponse=s.send(r,timeout=2)",
      'unused_httpx_builder':f"import httpx\nc=httpx.Client()\nr=c.build_request('POST',{allowed!r},data=b'x')\nc.close()\nresponse=None",
      'sent_httpx_builder':f"import httpx\nc=httpx.Client()\nr=c.build_request('POST',{allowed!r},data=b'x')\nresponse=c.send(r)\nc.close()",
    }
    for name,code in cases.items():
        origin.requests.clear();proxy.connects.clear();namespace={}
        blocked=_check_code_safety(code);prompt=is_high_risk_tool_call('python',{'code':code})
        exec(code,namespace)
        response=namespace['response']
        print(json.dumps({'case':name,'blocked':blocked,'prompt':prompt,'status':getattr(response,'status',getattr(response,'status_code',None)),'origin_requests':origin.requests,'connects':proxy.connects}))
    origin.shutdown();proxy.shutdown()
