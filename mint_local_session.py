import os
import sys

side = sys.argv[1]
os.environ['UNSLOTH_STUDIO_HOME'] = f'/task/studio-{side}-e2e'
sys.path.insert(0, f'/task/{side}/studio/backend')
from auth.authentication import create_access_token
print(create_access_token('unsloth'))
