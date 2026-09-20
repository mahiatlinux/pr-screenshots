import json,os,threading
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
import httpx
from models.data_recipe import RecipePayload
from routes.data_recipe.validate import validate
requests=[]
class Handler(BaseHTTPRequestHandler):
 def do_GET(self): self.proxy()
 def do_HEAD(self): self.proxy()
 def log_message(self,*args): pass
 def proxy(self):
  requests.append(self.path)
  with httpx.Client(follow_redirects=True,timeout=30) as c:
   headers={k:v for k,v in self.headers.items() if k.lower() in ['range','accept']}
   r=c.request(self.command,'https://huggingface.co'+self.path,headers=headers)
   self.send_response(r.status_code)
   for k,v in r.headers.items():
    if k.lower() not in ['transfer-encoding','content-encoding','connection','content-length']:self.send_header(k,v)
   self.send_header('Content-Length',str(len(r.content)))
   self.end_headers()
   if self.command!='HEAD':self.wfile.write(r.content)
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
os.environ['HF_ENDPOINT']=f'http://127.0.0.1:{server.server_port}'
recipe={'seed_config':{'source':{'seed_type':'hf','path':'datasets/lhoestq/demo1/data/train.csv','endpoint':None}},'columns':[{'column_type':'expression','name':'result','expr':'verified'}]}
try:
 response=validate(RecipePayload(recipe=recipe));assert response.valid,response
 assert len(requests)>0
 result={'valid':response.valid,'resolved_to_loopback':recipe['seed_config']['source']['endpoint']==os.environ['HF_ENDPOINT'],'proxy_requests':len(requests)}
 assert result['resolved_to_loopback']
 Path('/task/artifacts/loopback-proxy.json').write_text(json.dumps(result,indent=2));print(result)
finally:server.shutdown()
