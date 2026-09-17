import os, sys, pathlib, json, socket, threading, time, urllib.request, base64, platform
root = pathlib.Path(sys.argv[1]).resolve()
os.environ['UNSLOTH_STUDIO_HOME'] = str(root.parent / ('home-' + root.name))
sys.path.insert(0,str(root / 'studio/backend'))
from core.inference import tools, external_provider as ep
fetch = getattr(ep,'safe_fetch_remote_image_sync',ep._safe_fetch_image_for_gemini_sync)
for url in ['http://127.0.0.1/','https://127.0.0.1/','https://localhost/','https://169.254.169.254/','file:///etc/passwd','ftp://example.com/a.png']:
    assert fetch(url,'image/png') is None, url
url = 'https://raw.githubusercontent.com/python-pillow/Pillow/main/Tests/images/hopper.png'
start = time.monotonic()
result = fetch(url,'image/png')
assert result is not None, 'public HTTPS fetch failed'
raw = base64.b64decode(result[1])
assert raw.startswith(b'\x89PNG\r\n\x1a\n')
print(json.dumps({'os':platform.platform(),'python':sys.version,'side':root.name,'public_bytes':len(raw),'public_seconds':round(time.monotonic()-start,3)}),flush=True)
server = socket.create_server(('127.0.0.1',0))
stop = threading.Event()
def serve():
    conn,_=server.accept()
    with conn:
        conn.recv(4096)
        conn.sendall(b'HTTP/1.1 200 OK\r\nContent-Length: 20\r\n\r\n')
        try:
            for _ in range(20):
                if stop.is_set(): break
                conn.sendall(b'x')
                time.sleep(.05)
        except OSError: pass
thread = threading.Thread(target=serve,daemon=True)
thread.start()
response = urllib.request.build_opener(urllib.request.ProxyHandler({})).open('http://127.0.0.1:'+str(server.getsockname()[1]), timeout=2)
start = time.monotonic()
try:
    try: error,body=tools._read_capped_body(response,1000,2,start+.2,None)
    except TimeoutError: error,body='timeout',b''
finally:
    elapsed=time.monotonic()-start
    stop.set(); response.close(); server.close(); thread.join(3)
print(json.dumps({'side':root.name,'deadline_seconds':.2,'elapsed_seconds':round(elapsed,3),'refused':error is not None}),flush=True)
assert error is not None
if root.name == 'base':
    assert elapsed > .7, 'negative control no longer exposes the buffered-read overrun'
else:
    assert elapsed < .6, 'deadline exceeded'
print('PASS '+root.name,flush=True)
