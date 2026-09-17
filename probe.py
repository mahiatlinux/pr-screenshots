import sys, pathlib, copy, json, base64, hashlib, time
sys.path.insert(0, str(pathlib.Path.cwd()))
sys.path.insert(0, str(pathlib.Path.cwd() / 'studio/backend'))
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest import MonkeyPatch
from auth.authentication import get_current_subject
from studio.backend.tests.llama_backend_double import FakeLlamaCppBackend
from routes import inference as route
from PIL import Image
from io import BytesIO

class Backend(FakeLlamaCppBackend):
    is_vision = True
    def __init__(self):
        self.dispatched = []
        self.counted = []
    def generate_chat_completion(self, **kwargs):
        self.dispatched.append({'messages':copy.deepcopy(kwargs['messages'])})
        yield 'ok'
        yield {'type': 'metadata', 'usage': {}, 'timings': {}}
    generate_chat_completion_with_tools = generate_chat_completion
    def count_chat_tokens(self, messages, *a, **kw):
        self.counted.append(copy.deepcopy(messages))
        return 100

def urls(messages):
    return [p['image_url']['url'] for m in messages if isinstance(m.get('content'), list) for p in m['content'] if isinstance(p, dict) and p.get('type') == 'image_url']

def summarize(values):
    return [({'kind': 'inline', 'bytes': len(base64.b64decode(u.split(',',1)[1])), 'sha256': hashlib.sha256(base64.b64decode(u.split(',',1)[1])).hexdigest()} if u.startswith('data:') else {'kind':'remote','url':u}) for u in values]

async def no_switch(*args, **kwargs): pass
backend = Backend()
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
class Capture(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        backend.dispatched.append(body)
        answer = json.dumps({'id':'chatcmpl-probe','object':'chat.completion','created':0,'model':'test/model.gguf','choices':[{'index':0,'message':{'role':'assistant','content':'ok'},'finish_reason':'stop'}],'usage':{'prompt_tokens':1,'completion_tokens':1,'total_tokens':2}}).encode()
        self.send_response(200)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(answer)))
        self.end_headers()
        self.wfile.write(answer)
    def log_message(self,*args): pass
server = ThreadingHTTPServer(('127.0.0.1',0),Capture)
threading.Thread(target=server.serve_forever,daemon=True).start()
backend.base_url = 'http://127.0.0.1:' + str(server.server_port)
backend._auth_headers = {}
backend.supports_tool_passthrough = True
backend.context_length = 4096
backend._request_reasoning_kwargs = lambda *args, **kwargs: {}

patch = MonkeyPatch()
patch.setattr(route, 'get_llama_cpp_backend', lambda: backend)
patch.setattr(route, '_maybe_auto_switch_model', no_switch)
app = FastAPI()
app.include_router(route.router, prefix='/v1')
app.dependency_overrides[get_current_subject] = lambda: 'tester'
client = TestClient(app, raise_server_exceptions=False)
buf = BytesIO()
Image.new('RGB',(2,2),(7,8,9)).save(buf,format='PNG')
inline = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
public = 'https://raw.githubusercontent.com/python-pillow/Pillow/main/Tests/images/hopper.png'
inputs = [('http_loopback','http://127.0.0.1:9/image.png'), ('https_loopback','https://127.0.0.1:9/image.png'), ('metadata','http://169.254.169.254/latest/meta-data/'), ('inline',inline)]
if '--live' in sys.argv:
    inputs += [('public',public)]
records = []
for case, url in inputs:
    for shape in ['chat', 'tools', 'anthropic', 'responses', 'count']:
        backend.dispatched.clear(); backend.counted.clear()
        if shape in ('chat','tools'):
            path = '/v1/chat/completions'
            body = {'model':'test/model.gguf','stream':False,'messages':[{'role':'user','content':[{'type':'text','text':'describe'},{'type':'image_url','image_url':{'url':url}}]}]}
            if shape == 'tools':
                body['tools'] = [{'type':'function','function':{'name':'lookup','description':'lookup','parameters':{'type':'object','properties':{}}}}]
        elif shape in ('anthropic','count'):
            path = '/v1/messages' if shape == 'anthropic' else '/v1/messages/count_tokens'
            source = {'type':'base64','media_type':'image/png','data':url.split(',',1)[1]} if url.startswith('data:') else {'type':'url','url':url}
            body = {'model':'test/model.gguf','max_tokens':16,'stream':False,'messages':[{'role':'user','content':[{'type':'text','text':'describe'},{'type':'image','source':source}]}]}
        else:
            path = '/v1/responses'
            body = {'model':'test/model.gguf','stream':False,'input':[{'role':'user','content':[{'type':'input_text','text':'describe'},{'type':'input_image','image_url':url}]}]}
        start = time.monotonic()
        response = client.post(path,json=body)
        sent = [u for d in backend.dispatched for u in urls(d['messages'])]
        counted = [u for m in backend.counted for u in urls(m)]
        records.append({'case':case,'shape':shape,'status':response.status_code,'dispatched':summarize(sent),'counted':summarize(counted),'seconds':round(time.monotonic()-start,3)})
        print(json.dumps(records[-1]), flush=True)
pathlib.Path('/task/artifacts/'+sys.argv[1]+'-probe.json').write_text(json.dumps(records,indent=2))
patch.undo()
server.shutdown()
server.server_close()
