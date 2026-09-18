import ast
import json
from pathlib import Path
from utils.models import unsloth_mirror as m
source=Path('unsloth/models/loader_utils.py')
tree=ast.parse(source.read_text())
names={'__get_model_name','_resolve_with_mappers','get_model_name'}
body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
int_float,float_int,float16=m._mapper_tables()
ns=dict(INT_TO_FLOAT_MAPPER=int_float,FLOAT_TO_INT_MAPPER=float_int,MAP_TO_UNSLOTH_16bit=float16,BAD_MAPPINGS=m._bad_mappings(),SUPPORTS_FOURBIT=True,FLOAT_TO_FP8_BLOCK_MAPPER={},FLOAT_TO_FP8_ROW_MAPPER={},_env_says_offline=lambda:True)
exec(compile(ast.Module(body=body,type_ignores=[]),str(source),'exec'),ns)
keys=set(int_float)|set(float_int)|set(float16)|set(m._bad_mappings())
mismatches=[]
for name in keys:
 for mode in (True,False):
  expected=ns['get_model_name'](name,mode)
  actual=m.unsloth_public_mirror(name,mode) or name
  if expected.lower()!=actual.lower(): mismatches.append([name,mode,expected,actual])
print(json.dumps({'lookups':len(keys)*2,'mismatches':mismatches}))
assert not mismatches
