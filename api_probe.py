import json
from fastapi.testclient import TestClient
from fastapi import FastAPI
from routes.inference import studio_router
from auth.authentication import get_current_subject
from utils.account_context import AccountContext, run_as

app=FastAPI()
app.include_router(studio_router,prefix='/api/inference')
app.dependency_overrides[get_current_subject]=lambda:'test-subject'
with TestClient(app) as client:
    assert client.get('/api/inference/ssh-approved',params={'session_id':'api-probe'}).json()=={'hosts':[]}
    response=client.post('/api/inference/ssh-approve',json={'session_id':'api-probe','hosts':['Approved.Example.']})
    assert response.status_code==200 and response.json()=={'hosts':['approved.example']}
    response=client.get('/api/inference/ssh-approved',params={'session_id':'api-probe'})
    assert response.json()=={'hosts':['approved.example']}
    print(json.dumps({'approve_status':200,'normalized_hosts':response.json()['hosts']}))
