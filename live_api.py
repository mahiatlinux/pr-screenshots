import concurrent.futures, io, json, pathlib, statistics, time
import httpx, pyarrow as pa, pyarrow.parquet as pq
root=pathlib.Path(__file__).resolve().parent
schemas=[{'context':'Background passage. '*60,'question':'Who wrote this?','answer':'Mira.'},{'context':'Background passage. '*60,'answer':'Mira.'},{'context':'Background passage. '*60,'answer':'A'*120,'explanation':'E'*120},{'fulltext':'Full text '*20,'answer':'A'*120},{'input_text':'I'*120,'target_text':'T'*120},{'system':'S'*120,'output':'O'*120},{'instruction':'I'*120,'input':'More context','output':'O'*120},{'messages':[{'role':'user','content':'Who?'},{'role':'assistant','content':'Mira.'}]}]
results={}; raw={}
for side,port in [('base',19391),('head',19392)]:
 auth=json.loads((root/side/'.ui-session.json').read_text()); client=httpx.Client(base_url=f'http://127.0.0.1:{port}',headers={'Authorization':'Bearer '+auth['access_token']},timeout=60)
 rows=[]; paths=[]
 for index,row in enumerate(schemas):
  for fmt in ['jsonl','parquet']:
   if fmt=='jsonl': payload=(json.dumps(row)+'\n').encode()
   else:
    buffer=io.BytesIO();pq.write_table(pa.Table.from_pylist([row]),buffer);payload=buffer.getvalue()
   r=client.post('/api/hub/datasets/upload',files={'file':(f'case-{index}.{fmt}',payload,'application/octet-stream')});r.raise_for_status();path=r.json()['stored_path'];paths.append(path)
   r=client.post('/api/hub/datasets/check-format',json={'dataset_name':path});r.raise_for_status();data=r.json()
   assert data['preview_samples']==[row],(side,index,fmt,data['preview_samples'])
   rows.append({'case':index,'file_format':fmt,'detected_format':data['detected_format'],'mapping':data['suggested_mapping'],'manual':data['requires_manual_mapping']})
   if index==0:
    expected={'context':'user','question':'system','answer':'assistant'} if side=='base' else {'context':'system','question':'user','answer':'assistant'}
    assert data['suggested_mapping']==expected
   if index==5: assert data['requires_manual_mapping'] is True
 cache_path=paths[0]
 def request(_):
  start=time.perf_counter();r=client.post('/api/hub/datasets/check-format',json={'dataset_name':cache_path});r.raise_for_status();return r.json()['suggested_mapping'],time.perf_counter()-start
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: concurrent_results=list(pool.map(request,range(16)))
 assert all(x[0]==rows[0]['mapping'] for x in concurrent_results)
 results[side]={'serial_checks':len(rows),'concurrent_checks':len(concurrent_results),'concurrent_median_ms':round(statistics.median(x[1] for x in concurrent_results)*1000,2),'rows':rows}
assert results['base']['rows'][2:]==results['head']['rows'][2:]
(root/'artifacts/live-api.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
