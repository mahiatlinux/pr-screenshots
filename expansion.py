import sys, pathlib, base64, hashlib, json, random
sys.path.insert(0,str(pathlib.Path.cwd()/'studio/backend'))
from routes import inference as route
from PIL import Image
from io import BytesIO
raw=random.Random(11160).randbytes(2048*2048*3)
img=Image.frombytes('RGB',(2048,2048),raw)
buf=BytesIO();img.save(buf,format='JPEG',quality=80)
jpeg=buf.getvalue()
png=base64.b64decode(route._image_bytes_to_png_b64(jpeg))
assert len(jpeg)<10*1024*1024<len(png)
print(json.dumps({'side':sys.argv[1],'jpeg_bytes':len(jpeg),'png_bytes':len(png),'png_sha256':hashlib.sha256(png).hexdigest()}))
