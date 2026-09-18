import json
import timeit
from core.inference.tools import is_high_risk_tool_call
cases = {
    'simple_compute': 'print(sum(range(100)))',
    'trusted_http': "import requests\nrequests.get(url='https://pypi.org/simple/')",
    'session_aliases': "import requests\ns = requests.Session()\nf = s.get\nf('https://pypi.org/')",
}
for name, code in cases.items():
    action = lambda: is_high_risk_tool_call('python', {'code': code})
    action()
    samples = timeit.repeat(action, number=500, repeat=3)
    print(json.dumps({'case': name, 'milliseconds_per_analysis': min(samples)*2}))
