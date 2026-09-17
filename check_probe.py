import json, pathlib, sys
rows=json.loads(pathlib.Path(sys.argv[1]).read_text())
failures=[]
for row in rows:
    safe=row['case'] in ('inline','public') or (row['case']=='https_loopback' and row['shape']=='count')
    expected=200 if safe else 400
    payload=row['dispatched']+row['counted']
    if row['status']!=expected or any(item['kind']!='inline' for item in payload):
        failures.append((row['case'],row['shape'],row['status'],expected))
if failures:
    print(f'{len(failures)} unsafe route results: {failures}')
    raise SystemExit(1)
print(f'{len(rows)} route safety assertions passed')
