import json, socket, threading, time
from core.inference.tools import _check_code_safety, is_high_risk_tool_call
with socket.socket() as listener:
    listener.bind(('127.0.0.1', 0)); listener.listen(); listener.settimeout(.1)
    connections=[]; stopping=threading.Event()
    def serve():
        while not stopping.is_set():
            try: connection, address=listener.accept()
            except TimeoutError: continue
            connections.append(address[0]); connection.close()
    thread=threading.Thread(target=serve); thread.start()
    port=listener.getsockname()[1]
    for name, tail in [('unused', 'c.close()'), ('open', 'c.open()')]:
        code=f"import fabric\nc=fabric.Connection('127.0.0.1', port={port}, connect_timeout=1)\n{tail}"
        connections.clear()
        error=None
        try: exec(code, {})
        except Exception as exc: error=type(exc).__name__
        time.sleep(.05)
        print(json.dumps({'case':name,'blocked':_check_code_safety(code),'prompt':is_high_risk_tool_call('python',{'code':code}),'connections':len(connections),'error':error}))
    stopping.set(); thread.join()
