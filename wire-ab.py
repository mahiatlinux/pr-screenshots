import asyncio,json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'studio/backend'))
import httpx
from core.inference import external_provider as mod
async def run():
 failures=[];seen=[]
 for effort in ['minimal','low','medium','high','xhigh','max']:
  body={}
  def handler(request):
   body.update(json.loads(request.content));return httpx.Response(200,content='data: {"choices":[{"delta":{"content":"ok"}}]}\n\ndata: [DONE]\n\n',headers={'content-type':'text/event-stream'})
  async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as transport:
   mod._http_client=transport
   client=mod.ExternalProviderClient(provider_type='openrouter',base_url='https://openrouter.ai/api/v1',api_key='test')
   async for _ in client.stream_chat_completion(messages=[{'role':'user','content':'hello'}],model='deepseek/deepseek-v4-pro',reasoning_effort=effort,enable_thinking=True):pass
  result={'effort':effort,'wire':body.get('reasoning')};seen.append(result)
  if body.get('reasoning')!={'effort':effort}:failures.append(result)
 print(json.dumps({'results':seen,'failures':failures},indent=2));return bool(failures)
raise SystemExit(asyncio.run(run()))
