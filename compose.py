from pathlib import Path
import sys
prefix=sys.argv[1] if len(sys.argv)>1 else ""
from PIL import Image,ImageDraw,ImageFont
r=Path(__file__).resolve().parent/'artifacts'
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
for slug,title,box in [('deepseek-reasoning','DeepSeek V4 Pro: thinking controls',(450,390,1230,690)),('gemini-reasoning','Gemini Pro latest: thinking controls',(450,390,1230,690)),('flash-reasoning','Gemini 3.5 Flash: thinking controls',(450,390,1230,710)),('image','DeepSeek V4 Pro: image attachment',None),('tokens','DeepSeek V4 Pro: output limit',None)]:
 pics=[Image.open(r/f'{prefix}{side}-{slug}.png').convert('RGB') for side in ['base','fix']]
 if box:pics=[im.crop(box) for im in pics]
 w,h=pics[0].size
 canvas=Image.new('RGB',(2*w,h+82),'#f3f4f6');draw=ImageDraw.Draw(canvas)
 for i,pic in enumerate(pics):
  canvas.paste(pic,(w*i,82));draw.text((i*w+16,12),'BEFORE: merge base' if i==0 else 'AFTER: repaired PR',font=font,fill='#111827');draw.text((i*w+16,44),title,font=font,fill='#111827')
 assert pics[0].tobytes()!=pics[1].tobytes()
 canvas.save(r/f'{prefix}comparison-{slug}.png',optimize=True)
print('5 composites created')
